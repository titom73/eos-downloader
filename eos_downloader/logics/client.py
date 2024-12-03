"""Implement Download Client Logic."""

import os
import requests
from typing import Union
from loguru import logger
import eos_downloader.console
from tqdm import tqdm

class ObjectDownloader():

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
