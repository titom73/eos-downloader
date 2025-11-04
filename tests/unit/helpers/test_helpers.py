#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access

"""
Comprehensive tests for helpers/__init__.py module.

Tests the DownloadProgressBar class and signal handling for file downloads.
"""

import signal
from pathlib import Path
from threading import Event
from typing import List
from unittest.mock import Mock, MagicMock, patch, mock_open

import pytest
import requests

from eos_downloader.helpers import (
    DownloadProgressBar,
    handle_sigint,
    done_event,
    console,
)


class TestSignalHandling:
    """Test suite for signal handling functions."""

    def test_handle_sigint_sets_done_event(self) -> None:
        """Test that handle_sigint sets the done_event."""
        # Arrange - create fresh event for testing
        test_event = Event()
        assert not test_event.is_set()

        # Act - simulate SIGINT with mock event
        with patch("eos_downloader.helpers.done_event", test_event):
            handle_sigint(signal.SIGINT, None)

        # Assert
        assert test_event.is_set()

    def test_handle_sigint_callable(self) -> None:
        """Test that handle_sigint is callable with signal args."""
        # Should not raise any exceptions
        handle_sigint(signal.SIGINT, None)
        handle_sigint(15, Mock())  # Any signal number

    def test_console_instance_exists(self) -> None:
        """Test that console instance is available."""
        from eos_downloader.helpers import console
        from rich.console import Console

        assert console is not None
        assert isinstance(console, Console)

    def test_done_event_instance_exists(self) -> None:
        """Test that done_event instance is available."""
        from eos_downloader.helpers import done_event

        assert done_event is not None
        assert isinstance(done_event, Event)


class TestDownloadProgressBar:
    """Test suite for DownloadProgressBar class."""

    @pytest.fixture(autouse=True)
    def reset_done_event(self) -> None:
        """Ensure done_event is cleared before each test."""
        done_event.clear()
        yield
        done_event.clear()  # Also clear after test

    @pytest.fixture
    def progress_bar(self) -> DownloadProgressBar:
        """Provide DownloadProgressBar instance."""
        return DownloadProgressBar()

    @pytest.fixture
    def mock_response(self) -> Mock:
        """Provide mock HTTP response."""
        mock_resp = Mock(spec=requests.Response)
        mock_resp.headers = {"Content-Length": "1024"}

        # iter_content should return a fresh iterator each time
        def make_chunks(chunk_size):
            """Generate chunks for each call."""
            return iter([b"data" * 64 for _ in range(4)])

        mock_resp.iter_content = make_chunks
        return mock_resp

    def test_progress_bar_initialization(
        self, progress_bar: DownloadProgressBar
    ) -> None:
        """Test DownloadProgressBar initializes correctly."""
        from rich.progress import Progress

        assert progress_bar is not None
        assert hasattr(progress_bar, "progress")
        assert isinstance(progress_bar.progress, Progress)

    def test_progress_bar_has_custom_columns(
        self, progress_bar: DownloadProgressBar
    ) -> None:
        """Test that progress bar has custom columns configured."""
        # Verify progress object has columns
        assert progress_bar.progress is not None
        # Should have multiple columns (text, bar, percentage, etc.)
        assert len(progress_bar.progress.columns) > 0

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_copy_url_success(
        self,
        mock_file: Mock,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
        mock_response: Mock,
    ) -> None:
        """Test _copy_url downloads file successfully."""
        # Arrange
        mock_get.return_value = mock_response
        task_id = progress_bar.progress.add_task("test", start=False)

        # Act
        result = progress_bar._copy_url(
            task_id, "http://example.com/file.txt", "/tmp/file.txt"
        )

        # Assert
        assert result is False  # False means completed successfully
        mock_get.assert_called_once()
        mock_file.assert_called_once_with("/tmp/file.txt", "wb")
        # Verify data was written
        assert mock_file().write.call_count > 0

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_copy_url_with_custom_block_size(
        self,
        mock_file: Mock,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
        mock_response: Mock,
    ) -> None:
        """Test _copy_url with custom block size."""
        mock_get.return_value = mock_response
        task_id = progress_bar.progress.add_task("test", start=False)

        # Wrap iter_content to track calls while keeping functionality
        original_iter_content = mock_response.iter_content
        mock_response.iter_content = Mock(side_effect=original_iter_content)

        result = progress_bar._copy_url(
            task_id,
            "http://example.com/file.txt",
            "/tmp/file.txt",
            block_size=2048,
        )

        assert result is False
        # Verify iter_content called with custom block size
        mock_response.iter_content.assert_called_with(chunk_size=2048)

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_copy_url_interrupted_by_done_event(
        self,
        mock_file: Mock,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
    ) -> None:
        """Test _copy_url respects done_event interruption."""
        # Arrange - create response that sets done_event mid-download
        mock_resp = Mock()
        mock_resp.headers = {"Content-Length": "1024"}

        def iter_with_interrupt(chunk_size: int):
            """Simulate interrupt after first chunk."""
            yield b"data1"
            done_event.set()  # Interrupt
            yield b"data2"  # This shouldn't be written

        mock_resp.iter_content = iter_with_interrupt
        mock_get.return_value = mock_resp
        task_id = progress_bar.progress.add_task("test", start=False)

        try:
            # Act
            result = progress_bar._copy_url(
                task_id, "http://example.com/file.txt", "/tmp/file.txt"
            )

            # Assert - should return True for interrupted
            assert result is True
        finally:
            # Cleanup - clear the event
            done_event.clear()

    @patch("requests.get")
    def test_copy_url_handles_missing_content_length(
        self,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
    ) -> None:
        """Test _copy_url raises error when Content-Length missing."""
        # Arrange
        mock_resp = Mock()
        mock_resp.headers = {}  # No Content-Length
        mock_get.return_value = mock_resp
        task_id = progress_bar.progress.add_task("test", start=False)

        # Act & Assert
        with pytest.raises(KeyError):
            progress_bar._copy_url(
                task_id, "http://example.com/file.txt", "/tmp/file.txt"
            )

    @patch("requests.get")
    def test_copy_url_handles_network_error(
        self,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
    ) -> None:
        """Test _copy_url handles network errors."""
        # Arrange
        mock_get.side_effect = requests.RequestException("Network error")
        task_id = progress_bar.progress.add_task("test", start=False)

        # Act & Assert
        with pytest.raises(requests.RequestException):
            progress_bar._copy_url(
                task_id, "http://example.com/file.txt", "/tmp/file.txt"
            )

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_copy_url_updates_progress(
        self,
        mock_file: Mock,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
        mock_response: Mock,
    ) -> None:
        """Test that _copy_url updates progress correctly."""
        mock_get.return_value = mock_response
        task_id = progress_bar.progress.add_task("test", start=False)

        with patch.object(progress_bar.progress, "update") as mock_update:
            progress_bar._copy_url(
                task_id, "http://example.com/file.txt", "/tmp/file.txt"
            )

            # Verify progress.update was called
            assert mock_update.call_count > 0
            # First call should set total
            first_call = mock_update.call_args_list[0]
            assert "total" in first_call[1]

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_single_url(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test download method with single URL."""
        # Arrange
        mock_copy.return_value = False
        urls = ["http://example.com/file.txt"]

        # Act
        progress_bar.download(urls, str(tmp_path))

        # Assert
        mock_copy.assert_called_once()
        call_args = mock_copy.call_args
        assert "http://example.com/file.txt" in call_args[0]
        assert str(tmp_path) in call_args[0][2]

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_multiple_urls(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test download method with multiple URLs."""
        mock_copy.return_value = False
        urls = [
            "http://example.com/file1.txt",
            "http://example.com/file2.txt",
            "http://example.com/file3.txt",
        ]

        progress_bar.download(urls, str(tmp_path))

        assert mock_copy.call_count == 3

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_extracts_filename_from_url(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test that download correctly extracts filename from URL."""
        mock_copy.return_value = False
        urls = ["http://example.com/path/to/myfile.zip?param=value"]

        progress_bar.download(urls, str(tmp_path))

        # Verify filename was extracted correctly
        call_args = mock_copy.call_args[0]
        dest_path = call_args[2]
        assert "myfile.zip" in dest_path
        assert "param" not in dest_path  # Query params removed

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_handles_url_without_extension(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test download handles URLs without file extension."""
        mock_copy.return_value = False
        urls = ["http://example.com/download"]

        progress_bar.download(urls, str(tmp_path))

        call_args = mock_copy.call_args[0]
        dest_path = call_args[2]
        assert "download" in dest_path

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_concurrent_execution(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test that download uses ThreadPoolExecutor."""
        # Make _copy_url slower to test concurrency
        import time

        def slow_copy(*args, **kwargs):
            time.sleep(0.1)
            return False

        mock_copy.side_effect = slow_copy
        urls = [f"http://example.com/file{i}.txt" for i in range(5)]

        import time

        start = time.time()
        progress_bar.download(urls, str(tmp_path))
        duration = time.time() - start

        # With ThreadPoolExecutor, should be faster than sequential
        # Sequential would be ~0.5s, concurrent should be ~0.1-0.2s
        assert duration < 0.3  # Allow some overhead
        assert mock_copy.call_count == 5

    @patch.object(DownloadProgressBar, "_copy_url")
    def test_download_waits_for_all_futures(
        self,
        mock_copy: Mock,
        progress_bar: DownloadProgressBar,
        tmp_path: Path,
    ) -> None:
        """Test that download waits for all downloads to complete."""
        completed: List[int] = []

        def track_completion(task_id, url, path):
            import time

            time.sleep(0.05)
            completed.append(1)
            return False

        mock_copy.side_effect = track_completion
        urls = [f"http://example.com/file{i}.txt" for i in range(3)]

        progress_bar.download(urls, str(tmp_path))

        # All should be completed
        assert len(completed) == 3

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_copy_url_includes_default_headers(
        self,
        mock_file: Mock,
        mock_get: Mock,
        progress_bar: DownloadProgressBar,
        mock_response: Mock,
    ) -> None:
        """Test that _copy_url includes default request headers."""
        mock_get.return_value = mock_response
        task_id = progress_bar.progress.add_task("test", start=False)

        progress_bar._copy_url(task_id, "http://example.com/file.txt", "/tmp/file.txt")

        # Verify headers were passed
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        # Should include default headers
        assert call_kwargs["headers"] is not None
