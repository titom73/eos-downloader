# flake8: noqa: F811
"""A module for managing file downloads with progress tracking in the console.

This module provides functionality for downloading files with visual progress indicators
using the Rich library. It includes a signal handler for graceful interruption and
a DownloadProgressBar class for concurrent file downloads with progress tracking.

Classes
-------
    DownloadProgressBar: A class that provides visual progress tracking for file downloads.

Functions
-------
    handle_sigint: Signal handler for SIGINT (Ctrl+C) to enable graceful termination.
    console (Console): Rich Console instance for output rendering.
    done_event (Event): Threading Event used for signaling download interruption.
"""

# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods

import os.path
import signal
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any, Iterable

import requests
from rich.console import Console

# from eos_downloader.console.client import DownloadProgressBar
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)

import eos_downloader.defaults


console = Console()
done_event = Event()


def handle_sigint(signum: Any, frame: Any) -> None:
    """
    Signal handler for SIGINT (Ctrl+C).

    This function sets the done_event flag when SIGINT is received,
    allowing for graceful termination of the program.

    Parameters
    ----------
    signum : Any
        Signal number.
    frame : Any
        Current stack frame object.

    Returns
    -------
    None
    """
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


class DownloadProgressBar:
    """A progress bar for downloading files.

    This class provides a visual progress indicator for file downloads using the Rich library.
    It supports downloading multiple files concurrently with a progress bar showing download
    speed, completion percentage, and elapsed time.

    Attributes
    ----------
    progress : Progress
        A Rich Progress instance configured with custom columns for displaying download information.

    Examples
    --------
    >>> downloader = DownloadProgressBar()
    >>> urls = ['http://example.com/file1.zip', 'http://example.com/file2.zip']
    >>> downloader.download(urls, '/path/to/destination')
    """

    def __init__(self) -> None:
        self.progress = Progress(
            TextColumn(
                "💾  Downloading [bold blue]{task.fields[filename]}", justify="right"
            ),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TransferSpeedColumn(),
            "•",
            DownloadColumn(),
            "•",
            TimeElapsedColumn(),
            "•",
            console=console,
        )

    def _copy_url(
        self, task_id: TaskID, url: str, path: str, block_size: int = 1024
    ) -> bool:
        """Download a file from a URL and save it to a local path with progress tracking.

        This method performs a streaming download of a file from a given URL, saving it to the
        specified local path while updating a progress bar. The download can be interrupted via
        a done event.

        Parameters
        ----------
        task_id : TaskID
            Identifier for the progress tracking task.
        url : str
            URL to download the file from.
        path : str
            Local path where the file should be saved.
        block_size : int, optional
            Size of chunks to download at a time. Defaults to 1024 bytes.

        Returns
        -------
        bool
            True if download was interrupted by done_event, False if completed successfully.

        Raises
        ------
        requests.exceptions.RequestException
            If the download request fails.
        IOError
            If there are issues writing to the local file.
        KeyError
            If the response doesn't contain Content-Length header.
        """
        response = requests.get(
            url,
            stream=True,
            timeout=5,
            headers=eos_downloader.defaults.DEFAULT_REQUEST_HEADERS,
        )
        # This will break if the response doesn't contain content length
        self.progress.update(task_id, total=int(response.headers["Content-Length"]))
        with open(path, "wb") as dest_file:
            self.progress.start_task(task_id)
            for data in response.iter_content(chunk_size=block_size):
                dest_file.write(data)
                self.progress.update(task_id, advance=len(data))
                if done_event.is_set():
                    return True
        # console.print(f"Downloaded {path}")
        return False

    def download(self, urls: Iterable[str], dest_dir: str) -> None:
        """Download files from URLs concurrently to a destination directory.

        This method downloads files from the provided URLs in parallel using a thread pool,
        displaying progress for each download in the console.

        Parameters
        ----------
        urls : Iterable[str]
            An iterable of URLs to download files from.
        dest_dir : str
            The destination directory where files will be saved.

        Returns
        -------
        None

        Examples
        --------
        >>> downloader = DownloadProgressBar()
        >>> urls = ["http://example.com/file1.txt", "http://example.com/file2.txt"]
        >>> downloader.download(urls, "/path/to/destination")
        """
        with self.progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = []
                for url in urls:
                    filename = url.split("/")[-1].split("?")[0]
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = self.progress.add_task(
                        "download", filename=filename, start=False
                    )
                    futures.append(pool.submit(self._copy_url, task_id, url, dest_path))

                for future in futures:
                    future.result()  # Wait for all downloads to complete
