# coding: utf-8 -*-
"""ObjectDownloader class to manage file downloads with an option to use rich interface.

This class provides methods to download files from URLs with progress tracking using either
tqdm or rich interface. It supports both raw downloads and enhanced visual feedback during
the download process.

Methods
download_file(url: str, file_path: str, filename: str, rich_interface: bool = True) -> Union[None, str]
    Downloads a file from the given URL to the specified path with optional rich interface.

_download_file_raw(url: str, file_path: str) -> str
    Static method that performs the actual file download with tqdm progress bar.

Attributes
None

Example
>>> downloader = ObjectDownloader()
>>> result = downloader.download_file(
...     url='http://example.com/file.zip',
...     file_path='/downloads',
...     filename='file.zip',
...     rich_interface=True
... )
"""

import os
import requests
import hashlib
from typing import Union, Dict, Literal
from loguru import logger
import eos_downloader.console
from tqdm import tqdm

import eos_downloader.logics
import eos_downloader.logics.arista_server
import eos_downloader.models.version

class SoftManager():
    """ObjectDownloader helps to download files from a remote location.

    This class provides methods to download files using either a simple progress bar
    or a rich interface with enhanced visual feedback.

    Methods
    download_file(url: str, file_path: str, filename: str, rich_interface: bool = True) -> Union[None, str]
        Downloads a file from the given URL to the specified path
    _download_file_raw(url: str, file_path: str) -> str
        Internal method to download file with basic progress bar

    Examples
    --------
    >>> downloader = ObjectDownloader()
    >>> downloader.download_file(
    ...     url="http://example.com/file.txt",
    ...     file_path="/tmp",
    ...     filename="file.txt"
    ... )
    '/tmp/file.txt'
    """

    def __init__(self) -> None:
        self.file = {}
        self.file['name'] = None
        self.file['md5sum'] = None
        self.file['sha512sum'] = None
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

    def checksum(self, check_type: Literal['md5sum', 'sha512sum']) -> str:
        if check_type == 'sha512sum':
            hash_sha512 = hashlib.sha512()
            with open(self.file['sha512sum'], "rb") as f:
                hash_expected = f.read()
            with open(self.file['name'], "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha512.update(chunk)
            if hash_sha512.hexdigest() == hash_expected:
                return True
            else:
                raise ValueError(f"Checksum failed for {self.file['name']}")

    def download_file(
        self, url: str ,file_path: str, filename: str, rich_interface: bool = True
    ) -> Union[None, str]:
        if url is not False:
            if not rich_interface:
                return self._download_file_raw(
                    url=url, file_path=os.path.join(file_path, filename)
                )
            rich_downloader = eos_downloader.console.DownloadProgressBar()
            rich_downloader.download(urls=[url], dest_dir=file_path)
            return os.path.join(file_path, filename)
        logger.error(f"Cannot download file {file_path}")
        return None

    def downloads(
        self,
        object_arista: eos_downloader.logics.arista_server.EosXmlObject,
        file_path: str,
        rich_interface: bool = True,
    ) -> Union[None, str]:
        for file_type, url in object_arista.urls.items():
            if file_type == "image":
                filename = object_arista.filename
                self.file['name'] = filename
            else:
                filename = object_arista.hashfile(file_type)
                self.file[file_type] = filename
            self.download_file(url, file_path, filename, rich_interface)
        return file_path
