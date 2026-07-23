"""File transfer orchestration helpers."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Iterable, List, Tuple

import requests

import eos_downloader.defaults
from eos_downloader.helpers.progress import DownloadReporter
from eos_downloader.helpers.signals import sigint_guard


DownloadItem = Tuple[str, str, str]


def _stream_to_file(
    item: DownloadItem,
    reporter: DownloadReporter,
    done_event: Event,
    block_size: int = 1024,
) -> bool:
    """Stream one file to disk while updating ``reporter``."""
    url, dest_path, display_name = item
    response = requests.get(
        url,
        stream=True,
        timeout=5,
        headers=eos_downloader.defaults.DEFAULT_REQUEST_HEADERS,
    )
    interrupted = False
    try:
        response.raise_for_status()
        content_length = response.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        handle = reporter.add_file(display_name, total)
        with open(dest_path, "wb") as dest_file:
            for data in response.iter_content(chunk_size=block_size):
                if not data:
                    continue
                dest_file.write(data)
                reporter.advance(handle, len(data))
                if done_event.is_set():
                    interrupted = True
                    break
    finally:
        response.close()

    if interrupted:
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
    """Download several files in parallel, updating a single shared reporter."""
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
                future.result()
