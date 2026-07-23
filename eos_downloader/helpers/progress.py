"""Download progress reporters."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Dict, Optional

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

from eos_downloader.models.types import ProgressMode


class DownloadReporter(ABC):
    """Abstract progress reporter for file downloads."""

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
    """Reporter that renders nothing."""

    def add_file(self, name: str, total: Optional[int]) -> Any:
        return None

    def advance(self, handle: Any, n_bytes: int) -> None:
        return None

    def complete(self, handle: Any) -> None:
        return None


class RichReporter(DownloadReporter):
    """Animated grouped display for interactive terminals."""

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
        task = next((t for t in self._progress.tasks if t.id == self._total_task), None)
        return task.completed if task is not None else 0

    def add_file(self, name: str, total: Optional[int]) -> TaskID:
        task_id = self._progress.add_task(name, total=total)
        with self._lock:
            if total is None:
                if not self._total_indeterminate:
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
            pass

    def complete(self, handle: TaskID) -> None:
        task = next((t for t in self._progress.tasks if t.id == handle), None)
        if task is not None and task.total is not None:
            self._progress.update(handle, completed=task.total)


class PlainReporter(DownloadReporter):
    """ANSI-free reporter emitting ``loguru`` lifecycle lines."""

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
    """Build the concrete reporter for a progress ``mode`` and ``console``."""
    if mode == "none":
        return NoopReporter()
    if mode == "rich":
        use_rich = True
    elif mode == "plain":
        use_rich = False
    else:
        use_rich = console.is_terminal
    if use_rich:
        return RichReporter(console, title=title)
    return PlainReporter()
