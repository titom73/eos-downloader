# flake8: noqa: F811
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods

"""download module"""

import os.path
import signal
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any, Iterable

import requests
import rich
from rich import console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)

console = rich.get_console()
done_event = Event()


def handle_sigint(signum: Any, frame: Any) -> None:
    """Progress bar handler"""
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


class DownloadProgressBar:
    """
    Object to manage Download process with Progress Bar from Rich
    """

    def __init__(self) -> None:
        """
        Class Constructor
        """
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
        """Copy data from a url to a local file."""
        response = requests.get(url, stream=True, timeout=5)
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
        """Download multuple files to the given directory."""
        with self.progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for url in urls:
                    filename = url.split("/")[-1].split("?")[0]
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = self.progress.add_task(
                        "download", filename=filename, start=False
                    )
                    pool.submit(self._copy_url, task_id, url, dest_path)
