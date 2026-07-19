#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access

"""Tests for the download progress reporter layer in helpers/__init__.py.

Covers reporter selection, the plain (non-TTY) reporter, the rich reporter,
signal-handler scoping, single-file streaming and concurrent downloads.
"""

import re
import signal
import time
from threading import Event
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, mock_open, patch

import pytest
import requests
from loguru import logger
from rich.console import Console

from eos_downloader.helpers import (
    DownloadReporter,
    NoopReporter,
    PlainReporter,
    RichReporter,
    download_files_concurrently,
    resolve_reporter,
    sigint_guard,
    _stream_to_file,
)

ANSI_RE = re.compile(r"\x1b\[")


def _mock_response(chunks: List[bytes], content_length: Optional[str]) -> Mock:
    """Build a mock streaming ``requests`` response."""
    resp = Mock(spec=requests.Response)
    resp.headers = {} if content_length is None else {"Content-Length": content_length}
    resp.iter_content = lambda chunk_size: iter(chunks)
    return resp


class TestReporterSelection:
    """resolve_reporter picks the right implementation."""

    @pytest.fixture
    def tty_console(self) -> Console:
        return Console(force_terminal=True)

    @pytest.fixture
    def notty_console(self) -> Console:
        return Console(force_terminal=False)

    def test_auto_on_terminal_selects_rich(self, tty_console: Console) -> None:
        assert isinstance(resolve_reporter("auto", tty_console), RichReporter)

    def test_auto_off_terminal_selects_plain(self, notty_console: Console) -> None:
        assert isinstance(resolve_reporter("auto", notty_console), PlainReporter)

    def test_explicit_rich_overrides_detection(self, notty_console: Console) -> None:
        assert isinstance(resolve_reporter("rich", notty_console), RichReporter)

    def test_explicit_plain_overrides_detection(self, tty_console: Console) -> None:
        assert isinstance(resolve_reporter("plain", tty_console), PlainReporter)

    def test_none_selects_noop(self, tty_console: Console) -> None:
        assert isinstance(resolve_reporter("none", tty_console), NoopReporter)


class TestNoopReporter:
    """NoopReporter does nothing and never raises."""

    def test_noop_lifecycle(self) -> None:
        reporter = NoopReporter()
        with reporter:
            handle = reporter.add_file("file.swi", 100)
            reporter.advance(handle, 50)
            reporter.complete(handle)
        assert handle is None


class TestPlainReporter:
    """PlainReporter emits ANSI-free loguru lifecycle lines."""

    @pytest.fixture
    def captured(self) -> List[str]:
        """Capture the raw (unformatted) loguru message text of each record."""
        messages: List[str] = []
        sink_id = logger.add(
            lambda message: messages.append(message.record["message"]), colorize=False
        )
        yield messages
        logger.remove(sink_id)

    def test_lifecycle_lines_emitted(self, captured: List[str]) -> None:
        reporter = PlainReporter()
        with reporter:
            handle = reporter.add_file("EOS.swi", 100)
            for _ in range(10):
                reporter.advance(handle, 10)
            reporter.complete(handle)

        joined = "\n".join(captured)
        assert "Downloading EOS.swi" in joined
        assert "done in" in joined

    def test_progress_reported_every_10_percent(self, captured: List[str]) -> None:
        reporter = PlainReporter()
        handle = reporter.add_file("EOS.swi", 100)
        for _ in range(10):
            reporter.advance(handle, 10)
        reporter.complete(handle)

        joined = "\n".join(captured)
        # 10%..90% milestones (100% is covered by the completion line).
        for milestone in range(10, 100, 10):
            assert f"{milestone}%" in joined

    def test_no_ansi_escape_sequences(self, captured: List[str]) -> None:
        reporter = PlainReporter()
        handle = reporter.add_file("EOS.swi", 100)
        reporter.advance(handle, 50)
        reporter.advance(handle, 50)
        reporter.complete(handle)

        for message in captured:
            assert not ANSI_RE.search(message), f"ANSI sequence found in: {message!r}"

    def test_unknown_size_does_not_crash(self, captured: List[str]) -> None:
        reporter = PlainReporter()
        handle = reporter.add_file("EOS.swi", None)
        reporter.advance(handle, 500)
        reporter.complete(handle)

        joined = "\n".join(captured)
        assert "unknown size" in joined


class TestRichReporter:
    """RichReporter aggregates files into one shared Progress."""

    @pytest.fixture
    def reporter(self) -> RichReporter:
        return RichReporter(Console(force_terminal=True))

    def test_add_file_aggregates_total(self, reporter: RichReporter) -> None:
        reporter.add_file("a", 100)
        reporter.add_file("b", 50)
        total_task = next(
            t for t in reporter._progress.tasks if t.id == reporter._total_task
        )
        assert total_task.total == 150

    def test_unknown_size_makes_total_indeterminate(
        self, reporter: RichReporter
    ) -> None:
        reporter.add_file("a", None)
        total_task = next(
            t for t in reporter._progress.tasks if t.id == reporter._total_task
        )
        assert total_task.total is None

    def test_advance_updates_file_and_total(self, reporter: RichReporter) -> None:
        handle = reporter.add_file("a", 100)
        reporter.advance(handle, 40)
        file_task = next(t for t in reporter._progress.tasks if t.id == handle)
        total_task = next(
            t for t in reporter._progress.tasks if t.id == reporter._total_task
        )
        assert file_task.completed == 40
        assert total_task.completed == 40


class TestSigintGuard:
    """Signal handling is scoped, with no import-time side effect."""

    def test_import_does_not_replace_sigint_handler(self) -> None:
        # Re-importing the module must not have installed a global handler.
        import importlib

        import eos_downloader.helpers as helpers_module

        before = signal.getsignal(signal.SIGINT)
        importlib.reload(helpers_module)
        after = signal.getsignal(signal.SIGINT)
        assert before == after

    def test_guard_installs_then_restores_handler(self) -> None:
        original = signal.getsignal(signal.SIGINT)
        done = Event()
        with sigint_guard(done):
            during = signal.getsignal(signal.SIGINT)
            assert during != original
        assert signal.getsignal(signal.SIGINT) == original

    def test_guard_sets_event_on_signal(self) -> None:
        done = Event()
        with sigint_guard(done):
            handler = signal.getsignal(signal.SIGINT)
            handler(signal.SIGINT, None)  # type: ignore[misc]
        assert done.is_set()


class TestStreamToFile:
    """_stream_to_file streams a single file into a reporter."""

    @patch("eos_downloader.helpers.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_success(self, mock_file: Mock, mock_get: Mock) -> None:
        mock_get.return_value = _mock_response([b"data" * 64] * 4, "1024")
        reporter = NoopReporter()
        interrupted = _stream_to_file(
            ("http://x/file.txt", "/tmp/file.txt", "file.txt"), reporter, Event()
        )
        assert interrupted is False
        mock_file.assert_called_once_with("/tmp/file.txt", "wb")
        assert mock_file().write.call_count > 0

    @patch("eos_downloader.helpers.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_interrupted_by_event(self, mock_file: Mock, mock_get: Mock) -> None:
        done = Event()

        def chunks(chunk_size: int) -> Any:
            yield b"data1"
            done.set()
            yield b"data2"

        resp = Mock()
        resp.headers = {"Content-Length": "1024"}
        resp.iter_content = chunks
        mock_get.return_value = resp

        interrupted = _stream_to_file(
            ("http://x/file.txt", "/tmp/file.txt", "file.txt"), NoopReporter(), done
        )
        assert interrupted is True

    @patch("eos_downloader.helpers.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_missing_content_length_does_not_crash(
        self, mock_file: Mock, mock_get: Mock
    ) -> None:
        mock_get.return_value = _mock_response([b"data"], None)
        interrupted = _stream_to_file(
            ("http://x/file.txt", "/tmp/file.txt", "file.txt"), NoopReporter(), Event()
        )
        assert interrupted is False

    @patch("eos_downloader.helpers.requests.get")
    def test_default_headers_sent(self, mock_get: Mock) -> None:
        mock_get.return_value = _mock_response([b"data"], "4")
        with patch("builtins.open", new_callable=mock_open):
            _stream_to_file(
                ("http://x/file.txt", "/tmp/file.txt", "file.txt"),
                NoopReporter(),
                Event(),
            )
        assert mock_get.call_args[1]["headers"] is not None


class _RecordingReporter(DownloadReporter):
    """Reporter that records add_file/advance/complete calls thread-safely."""

    def __init__(self) -> None:
        self.added: List[str] = []
        self.completed: List[str] = []
        self._names: Dict[int, str] = {}
        self._counter = 0

    def add_file(self, name: str, total: Optional[int]) -> int:
        handle = self._counter
        self._counter += 1
        self._names[handle] = name
        self.added.append(name)
        return handle

    def advance(self, handle: int, n_bytes: int) -> None:
        return None

    def complete(self, handle: int) -> None:
        self.completed.append(self._names[handle])


class TestDownloadFilesConcurrently:
    """download_files_concurrently drives one shared reporter over many files."""

    @patch("eos_downloader.helpers.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_all_files_completed(self, mock_file: Mock, mock_get: Mock) -> None:
        mock_get.return_value = _mock_response([b"data"], "4")
        reporter = _RecordingReporter()
        items = [
            ("http://x/image.swi", "/tmp/image.swi", "image.swi"),
            ("http://x/image.sha512", "/tmp/image.sha512", "image.sha512"),
        ]
        download_files_concurrently(items, reporter)

        assert set(reporter.added) == {"image.swi", "image.sha512"}
        assert set(reporter.completed) == {"image.swi", "image.sha512"}

    def test_empty_list_is_noop(self) -> None:
        reporter = _RecordingReporter()
        download_files_concurrently([], reporter)
        assert reporter.added == []

    @patch("eos_downloader.helpers.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_runs_concurrently(self, mock_file: Mock, mock_get: Mock) -> None:
        def slow_get(*args: Any, **kwargs: Any) -> Mock:
            resp = Mock()
            resp.headers = {"Content-Length": "4"}

            def chunks(chunk_size: int) -> Any:
                time.sleep(0.1)
                yield b"data"

            resp.iter_content = chunks
            return resp

        mock_get.side_effect = slow_get
        items = [(f"http://x/file{i}", f"/tmp/file{i}", f"file{i}") for i in range(4)]
        start = time.time()
        download_files_concurrently(items, NoopReporter())
        # 4 files sequential ≈ 0.4s; concurrent (4 workers) should be well under.
        assert time.time() - start < 0.3
