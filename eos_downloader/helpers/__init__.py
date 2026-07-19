# flake8: noqa: F811
"""Download progress reporting for the console.

This module renders the progress of file downloads through a small
:class:`DownloadReporter` abstraction with two concrete implementations that are
selected automatically depending on whether output is an interactive terminal:

- :class:`RichReporter` — a grouped, animated display (one Rich ``Progress``
  shared by every file of a download, wrapped in a titled ``Panel`` with an
  aggregated *Total* bar). Used on a TTY.
- :class:`PlainReporter` — plain ``loguru`` log lines with no ANSI escape
  sequences. Used in CI / non-interactive output.

A :class:`NoopReporter` is used when progress rendering is disabled. The helper
:func:`download_files_concurrently` downloads the files of a single download in
parallel while updating one shared reporter.

Classes
-------
    DownloadReporter: Abstract progress reporter interface.
    RichReporter: Animated grouped display for interactive terminals.
    PlainReporter: ANSI-free log-line reporter for non-TTY / CI.
    NoopReporter: Reporter that renders nothing.

Functions
---------
    resolve_reporter: Build the concrete reporter for a progress mode + console.
    download_files_concurrently: Download several files in parallel under a reporter.
"""

# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods

import os
import signal
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event, Lock
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import requests
from loguru import logger
from rich.console import Console
from rich.filesize import decimal
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

import eos_downloader.defaults
from eos_downloader.models.types import ProgressMode

# Files that make up a single download, as (url, destination_path, display_name).
DownloadItem = Tuple[str, str, str]


@contextmanager
def sigint_guard(done_event: Event) -> Iterator[None]:
    """Route ``SIGINT`` to a done event, then defer to the previous handler.

    On Ctrl+C the workers are asked to stop promptly (via ``done_event``) and the
    previous handler is then invoked so the interruption still propagates — a
    default handler raises ``KeyboardInterrupt`` in the main thread rather than
    letting the download look like a clean completion. The previous handler is
    saved and restored on exit, so importing this module has no process-wide side
    effect. If a handler cannot be installed (e.g. the caller is not in the main
    thread), the block still runs without interception.

    Parameters
    ----------
    done_event : Event
        Event set when ``SIGINT`` (Ctrl+C) is received, signalling workers to stop.

    Yields
    ------
    None
    """
    previous: Any = None
    installed = False

    def handler(signum: int, frame: Any) -> None:
        done_event.set()
        if callable(previous):
            previous(signum, frame)
        elif previous == signal.SIG_DFL:
            # Reproduce the default behaviour: raise KeyboardInterrupt.
            signal.default_int_handler(signum, frame)
        # signal.SIG_IGN: intentionally leave the signal ignored.

    try:
        previous = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, handler)
        installed = True
    except ValueError:
        # Not in the main thread: leave signal handling untouched.
        installed = False
    try:
        yield
    finally:
        if installed:
            signal.signal(signal.SIGINT, previous)


class DownloadReporter(ABC):
    """Abstract progress reporter for file downloads.

    A reporter is a context manager: entering starts the display (if any) and
    exiting stops it. Each file is registered with :meth:`add_file`, streamed
    with :meth:`advance`, and finalised with :meth:`complete`.
    """

    def __enter__(self) -> "DownloadReporter":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        return None

    @abstractmethod
    def add_file(self, name: str, total: Optional[int]) -> Any:
        """Register a file and return an opaque handle used for later updates."""

    @abstractmethod
    def advance(self, handle: Any, n_bytes: int) -> None:
        """Report that ``n_bytes`` more bytes of ``handle`` have been written."""

    @abstractmethod
    def complete(self, handle: Any) -> None:
        """Mark the file identified by ``handle`` as finished."""


class NoopReporter(DownloadReporter):
    """Reporter that renders nothing (used for ``progress="none"``)."""

    def add_file(self, name: str, total: Optional[int]) -> Any:
        return None

    def advance(self, handle: Any, n_bytes: int) -> None:
        return None

    def complete(self, handle: Any) -> None:
        return None


class RichReporter(DownloadReporter):
    """Animated grouped display for interactive terminals.

    All files share a single Rich ``Progress`` rendered inside a titled ``Panel``
    via ``Live``, alongside an aggregated *Total* task.

    Parameters
    ----------
    console : Console
        The shared Rich console to render on.
    title : str
        Panel title.
    """

    def __init__(self, console: Console, title: str = "Downloading") -> None:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console,
        )
        self._live = Live(
            Panel(self._progress, title=title, border_style="blue"),
            console=console,
            refresh_per_second=10,
        )
        self._total_task = self._progress.add_task("Total", total=0)
        self._total_known = 0
        self._total_indeterminate = False
        self._lock = Lock()

    def __enter__(self) -> "RichReporter":
        self._live.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self._live.stop()

    def _total_completed(self) -> float:
        """Return the bytes already counted on the Total task."""
        task = next((t for t in self._progress.tasks if t.id == self._total_task), None)
        return task.completed if task is not None else 0

    def add_file(self, name: str, total: Optional[int]) -> TaskID:
        task_id = self._progress.add_task(name, total=total)
        with self._lock:
            if total is None:
                if not self._total_indeterminate:
                    # A file of unknown size makes the aggregate indeterminate.
                    # ``Progress.update(total=None)`` means "leave unchanged", so
                    # the Total task is re-created (public API), preserving the
                    # bytes already counted.
                    completed = self._total_completed()
                    self._progress.remove_task(self._total_task)
                    self._total_task = self._progress.add_task(
                        "Total", total=None, completed=completed
                    )
                    self._total_indeterminate = True
            else:
                self._total_known += total
                if not self._total_indeterminate:
                    self._progress.update(self._total_task, total=self._total_known)
        return task_id

    def advance(self, handle: TaskID, n_bytes: int) -> None:
        self._progress.update(handle, advance=n_bytes)
        try:
            self._progress.update(self._total_task, advance=n_bytes)
        except KeyError:
            # The Total task may be mid-recreation (an unknown-size file is
            # registering and switching the aggregate to indeterminate).
            pass

    def complete(self, handle: TaskID) -> None:
        task = next((t for t in self._progress.tasks if t.id == handle), None)
        if task is not None and task.total is not None:
            # Snap the bar to 100% even if the reported total was approximate.
            self._progress.update(handle, completed=task.total)


class PlainReporter(DownloadReporter):
    """ANSI-free reporter emitting ``loguru`` lifecycle lines (non-TTY / CI).

    For each file: a start line (name + size), a progress line at every 10%
    milestone, and a completion line (size, duration, average speed).
    """

    _MILESTONE_STEP = 10

    def __init__(self) -> None:
        self._files: Dict[int, Dict[str, Any]] = {}
        self._counter = 0
        self._lock = Lock()

    def add_file(self, name: str, total: Optional[int]) -> int:
        with self._lock:
            handle = self._counter
            self._counter += 1
        self._files[handle] = {
            "name": name,
            "total": total,
            "downloaded": 0,
            "next_milestone": self._MILESTONE_STEP,
            "start": time.monotonic(),
        }
        size = decimal(total) if total else "unknown size"
        logger.info(f"Downloading {name} ({size})")
        return handle

    def advance(self, handle: int, n_bytes: int) -> None:
        info = self._files[handle]
        info["downloaded"] += n_bytes
        total = info["total"]
        if not total:
            return
        pct = info["downloaded"] * 100 // total
        while info["next_milestone"] <= 90 and pct >= info["next_milestone"]:
            logger.info(
                f"{info['name']}: {info['next_milestone']}% "
                f"({decimal(info['downloaded'])}/{decimal(total)})"
            )
            info["next_milestone"] += self._MILESTONE_STEP

    def complete(self, handle: int) -> None:
        info = self._files[handle]
        duration = time.monotonic() - info["start"]
        speed = info["downloaded"] / duration if duration > 0 else 0
        logger.info(
            f"{info['name']}: done in {duration:.1f}s "
            f"({decimal(info['downloaded'])}, {decimal(int(speed))}/s)"
        )


def resolve_reporter(
    mode: ProgressMode,
    console: Console,
    *,
    title: str = "Downloading",
) -> DownloadReporter:
    """Build the concrete reporter for a progress ``mode`` and ``console``.

    Parameters
    ----------
    mode : ProgressMode
        One of ``"auto"``, ``"rich"``, ``"plain"``, ``"none"``. ``"auto"`` picks
        the rich reporter on an interactive terminal and the plain one otherwise.
    console : Console
        The shared Rich console (its ``is_terminal`` drives ``"auto"``).
    title : str
        Panel title for the rich reporter.

    Returns
    -------
    DownloadReporter
        The reporter matching the requested mode.
    """
    if mode == "none":
        return NoopReporter()
    if mode == "rich":
        use_rich = True
    elif mode == "plain":
        use_rich = False
    else:  # "auto"
        use_rich = console.is_terminal
    if use_rich:
        return RichReporter(console, title=title)
    return PlainReporter()


def _stream_to_file(
    item: DownloadItem,
    reporter: DownloadReporter,
    done_event: Event,
    block_size: int = 1024,
) -> bool:
    """Stream one file to disk while updating ``reporter``.

    Parameters
    ----------
    item : DownloadItem
        ``(url, destination_path, display_name)`` triple.
    reporter : DownloadReporter
        Reporter receiving progress updates for this file.
    done_event : Event
        When set (e.g. by Ctrl+C), the download stops early.
    block_size : int, optional
        Chunk size in bytes. Defaults to 1024.

    Returns
    -------
    bool
        True if the download was interrupted, False if it completed.

    Raises
    ------
    requests.HTTPError
        If the server returns an error status code.
    """
    url, dest_path, display_name = item
    response = requests.get(
        url,
        stream=True,
        timeout=5,
        headers=eos_downloader.defaults.DEFAULT_REQUEST_HEADERS,
    )
    interrupted = False
    try:
        # Surface HTTP errors before writing an error page to disk.
        response.raise_for_status()
        content_length = response.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        handle = reporter.add_file(display_name, total)
        with open(dest_path, "wb") as dest_file:
            for data in response.iter_content(chunk_size=block_size):
                if not data:
                    # Skip empty keep-alive chunks so they don't inflate progress.
                    continue
                dest_file.write(data)
                reporter.advance(handle, len(data))
                if done_event.is_set():
                    interrupted = True
                    break
    finally:
        response.close()

    if interrupted:
        # Drop the partial file so a later run does not mistake it for a
        # complete, cached download.
        try:
            os.remove(dest_path)
        except OSError:
            pass
        return True
    reporter.complete(handle)
    return False


def download_files_concurrently(
    items: Iterable[DownloadItem],
    reporter: DownloadReporter,
    *,
    max_workers: int = 4,
    block_size: int = 1024,
) -> None:
    """Download several files in parallel, updating a single shared reporter.

    Parameters
    ----------
    items : Iterable[DownloadItem]
        The files to download as ``(url, destination_path, display_name)`` triples.
    reporter : DownloadReporter
        The shared reporter; entered once around the whole batch.
    max_workers : int, optional
        Maximum number of concurrent downloads. Defaults to 4.
    block_size : int, optional
        Chunk size in bytes. Defaults to 1024.

    Returns
    -------
    None
    """
    file_list: List[DownloadItem] = list(items)
    if not file_list:
        return
    done_event = Event()
    with sigint_guard(done_event), reporter:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [
                pool.submit(_stream_to_file, item, reporter, done_event, block_size)
                for item in file_list
            ]
            for future in futures:
                future.result()  # Propagate exceptions and wait for completion.
