# coding: utf-8 -*-
"""Implement Download Client Logic."""

import os
from typing import Union

import requests
from loguru import logger
from tqdm import tqdm

import eos_downloader.helpers


class ObjectDownloader:
    # pylint: disable=too-few-public-methods
    """A class for handling file downloads from URLs.

    This class provides methods for downloading files from URLs, with support for both
    raw downloads and rich interface progress tracking.

    Methods:
        download_file(url: str, file_path: str, filename: str, rich_interface: bool = True) -> Union[None, str]:
            Downloads a file from a URL with optional rich progress interface.

        _download_file_raw(url: str, file_path: str) -> str:
            Static method that downloads a file without rich interface, showing basic progress bar.

    Attributes:
        None

    Example:
        downloader = ObjectDownloader()
        file_path = downloader.download_file(
            "http://example.com/file.zip",
            "/downloads",
            "file.zip",
            rich_interface=True
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def _download_file_raw(url: str, file_path: str) -> str:
        """
        _download_file Helper to download file from Arista.com

        [extended_summary]

        Parameters
        ----------
        url : str
            URL provided by server for remote_file_path
        file_path : str
            Location where to save local file

        Returns
        -------
        str
            File path
        """
        chunkSize = 1024
        r = requests.get(url, stream=True, timeout=5)
        with open(file_path, "wb") as f:
            pbar = tqdm(
                unit="B",
                total=int(r.headers["Content-Length"]),
                unit_scale=True,
                unit_divisor=1024,
            )
            for chunk in r.iter_content(chunk_size=chunkSize):
                if chunk:
                    pbar.update(len(chunk))
                f.write(chunk)
        return file_path

    def download_file(
        self, url: str, file_path: str, filename: str, rich_interface: bool = True
    ) -> Union[None, str]:
        """Download a file from a given URL.

        This method handles file downloading with or without a rich progress interface.

        Args:
            url (str): The URL from which to download the file
            file_path (str): The destination directory path where the file will be saved
            filename (str): The name to give to the downloaded file
            rich_interface (bool, optional): Whether to use rich progress interface. Defaults to True

        Returns:
            Union[None, str]: The full path to the downloaded file if successful, None otherwise

        Raises:
            None explicitly, but underlying download operations may raise exceptions
        """
        if url is not False:
            if not rich_interface:
                return self._download_file_raw(
                    url=url, file_path=os.path.join(file_path, filename)
                )
            rich_downloader = eos_downloader.helpers.DownloadProgressBar()
            rich_downloader.download(urls=[url], dest_dir=file_path)
            return os.path.join(file_path, filename)
        logger.error(f"Cannot download file {file_path}")
        return None
