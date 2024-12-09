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
import shutil
import hashlib
from typing import Union, Literal, Dict

import logging
import requests
from tqdm import tqdm

import eos_downloader.defaults
import eos_downloader.helpers
import eos_downloader.logics
import eos_downloader.logics.arista_server
import eos_downloader.models.version


class SoftManager:
    """SoftManager helps to download files from a remote location.

    This class provides methods to download files using either a simple progress bar
    or a rich interface with enhanced visual feedback.

    Methods
    download_file(url: str, file_path: str, filename: str, rich_interface: bool = True) -> Union[None, str]
        Downloads a file from the given URL to the specified path
    _download_file_raw(url: str, file_path: str) -> str
        Internal method to download file with basic progress bar

    Examples
    --------
    >>> downloader = SoftManager()
    >>> downloader.download_file(
    ...     url="http://example.com/file.txt",
    ...     file_path="/tmp",
    ...     filename="file.txt"
    ... )
    '/tmp/file.txt'
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.file: Dict[str, Union[str, None]] = {}
        self.file["name"] = None
        self.file["md5sum"] = None
        self.file["sha512sum"] = None
        self.dry_run = dry_run
        logging.info("SoftManager initialized%s", " in dry-run mode" if dry_run else "")

    @staticmethod
    def _download_file_raw(url: str, file_path: str) -> str:
        """Downloads a file from a URL and saves it to a local file.

        Args:
            url (str): The URL of the file to download.
            file_path (str): The local path where the file will be saved.

        Returns:
            str: The path to the downloaded file.

        Notes:
            - Uses requests library to stream download in chunks of 1024 bytes
            - Shows download progress using tqdm progress bar
            - Sets timeout of 5 seconds for initial connection
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

    @staticmethod
    def _create_destination_folder(path: str) -> None:
        """Creates a directory path if it doesn't already exist."""
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.critical(f"Error creating folder: {e}")

    def checksum(self, check_type: Literal["md5sum", "sha512sum"]) -> bool:
        """
        Verifies the integrity of a downloaded file using a specified checksum algorithm.

        Args:
            check_type (Literal['md5sum', 'sha512sum']): The type of checksum to perform. Currently supports 'md5sum' or 'sha512sum'.

        Returns:
            bool: True if the checksum verification passes.

        Raises:
            ValueError: If the calculated checksum does not match the expected checksum.
            FileNotFoundError: If either the checksum file or the target file cannot be found.

        Example:
            ```python
            client.checksum('sha512sum')  # Returns True if checksum matches
            ```
        """
        logging.info(f"Checking checksum for {self.file['name']} using {check_type}")
        if check_type == "sha512sum":
            hash_sha512 = hashlib.sha512()
            hash512sum = self.file["sha512sum"]
            file_name = self.file["name"]

            logging.debug(f"checksum sha512sum file is: {hash512sum}")

            if file_name is None or hash512sum is None:
                logging.error("File or checksum not found")
                raise ValueError("File or checksum not found")

            with open(hash512sum, "r", encoding="utf-8") as f:
                hash_expected = f.read().split()[0]
            with open(file_name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha512.update(chunk)
            if hash_sha512.hexdigest() != hash_expected:
                logging.error(
                    f"Checksum failed for {self.file['name']}: computed {hash_sha512.hexdigest()} - expected {hash_expected}"
                )
                raise ValueError("Incorrect checksum")
            return True
        logging.error(f"Checksum type {check_type} not yet supported")
        raise ValueError(f"Checksum type {check_type} not yet supported")

    def download_file(
        self, url: str, file_path: str, filename: str, rich_interface: bool = True
    ) -> Union[None, str]:
        """
        Downloads a file from a given URL to a specified location.

        Args:
            url (str): The URL from which to download the file.
            file_path (str): The directory path where the file should be saved.
            filename (str): The name to be given to the downloaded file.
            rich_interface (bool, optional): Whether to use rich progress bar interface. Defaults to True.

        Returns:
            Union[None, str]: The full path to the downloaded file if successful, None if download fails.
        """
        logging.info(
            f"{'[DRY-RUN] Would download' if self.dry_run else 'Downloading'} {filename} from {url}"
        )
        if self.dry_run:
            return os.path.join(file_path, filename)

        if url is not False:
            if not rich_interface:
                return self._download_file_raw(
                    url=url, file_path=os.path.join(file_path, filename)
                )
            rich_downloader = eos_downloader.helpers.DownloadProgressBar()
            rich_downloader.download(urls=[url], dest_dir=file_path)
            return os.path.join(file_path, filename)
        logging.error(f"Cannot download file {file_path}")
        return None

    def downloads(
        self,
        object_arista: eos_downloader.logics.arista_server.EosXmlObject,
        file_path: str,
        rich_interface: bool = True,
    ) -> Union[None, str]:
        """Downloads files from Arista EOS server.

        Downloads the EOS image and optional md5/sha512 files based on the provided EOS XML object.
        Each file is downloaded to the specified path with appropriate filenames.

        Args:
            object_arista (EosXmlObject): Object containing EOS image and hash file URLs
            file_path (str): Directory path where files should be downloaded
            rich_interface (bool, optional): Whether to use rich console output. Defaults to True.

        Returns:
            Union[None, str]: The file path where files were downloaded, or None if download failed

        Example:
            >>> client.downloads(eos_obj, "/tmp/downloads")
            '/tmp/downloads'
        """
        logging.info(f"Downloading files from {object_arista.version}")

        if len(object_arista.urls) == 0:
            logging.error("No URLs found for download")
            raise ValueError("No URLs found for download")

        for file_type, url in sorted(object_arista.urls.items(), reverse=True):
            logging.debug(f"Downloading {file_type} from {url}")
            if file_type == "image":
                filename = object_arista.filename
                self.file["name"] = filename
            else:
                filename = object_arista.hashfile(file_type)
                self.file[file_type] = filename
            if url is None:
                logging.error(f"URL not found for {file_type}")
                raise ValueError(f"URL not found for {file_type}")
            if filename is None:
                logging.error(f"Filename not found for {file_type}")
                raise ValueError(f"Filename not found for {file_type}")
            self.download_file(url, file_path, filename, rich_interface)
        return file_path

    def import_docker(
        self,
        local_file_path: str,
        docker_name: str = "arista/ceos",
        docker_tag: str = "latest",
    ) -> None:
        """Import a local file into a Docker image.

        This method imports a local file into Docker with a specified image name and tag.
        It checks for the existence of both the local file and docker binary before proceeding.

        Args:
            local_file_path (str): Path to the local file to import
            docker_name (str, optional): Name for the Docker image. Defaults to 'arista/ceos'
            docker_tag (str, optional): Tag for the Docker image. Defaults to 'latest'

        Raises:
            FileNotFoundError: If the local file doesn't exist or docker binary is not found
            Exception: If the docker import operation fails

        Returns:
            None
        """

        logging.info(
            f"Importing {local_file_path} to {docker_name}:{docker_tag} in local docker enginge"
        )

        if os.path.exists(local_file_path) is False:
            raise FileNotFoundError(f"File {local_file_path} not found")
        if not shutil.which("docker"):
            raise FileNotFoundError(f"File {local_file_path} not found")

        try:
            cmd = f"$(which docker) import {local_file_path} {docker_name}:{docker_tag}"
            if self.dry_run:
                logging.info(f"[DRY-RUN] Would execute: {cmd}")
            else:
                logging.debug("running docker import process")
                os.system(cmd)
        except Exception as e:
            logging.error(f"Error importing docker image: {e}")
            raise e

    def provision_eve(
        self,
        object_arista: eos_downloader.logics.arista_server.EosXmlObject,
        noztp: bool = False,
    ) -> None:
        """
        Provisions EVE-NG with the specified Arista EOS object.

        Args:
            object_arista (eos_downloader.logics.arista_server.EosXmlObject): The Arista EOS object containing version, filename, and URLs.
            noztp (bool, optional): If True, disables ZTP (Zero Touch Provisioning). Defaults to False.
            checksum (bool, optional): If True, verifies the checksum of the downloaded files. Defaults to True.

        Raises:
            ValueError: If no URLs are found for download or if a URL or filename is None.

        """

        # EVE-NG provisioning page for vEOS
        # https://www.eve-ng.net/index.php/documentation/howtos/howto-add-arista-veos/

        logging.info(
            f"Provisioning EVE-NG with {object_arista.version} / {object_arista.filename}"
        )

        file_path = f"{eos_downloader.defaults.EVE_QEMU_FOLDER_PATH}/veos-{object_arista.version}"

        filename: str = ""
        eos_filename = object_arista.filename

        if len(object_arista.urls) == 0:
            logging.error("No URLs found for download")
            raise ValueError("No URLs found for download")

        for file_type, url in sorted(object_arista.urls.items(), reverse=True):
            logging.debug(f"Downloading {file_type} from {url}")
            if file_type == "image":
                filename = object_arista.filename
                if noztp:
                    filename = f"{os.path.splitext(object_arista.filename)[0]}-noztp{os.path.splitext(object_arista.filename)[1]}"
                eos_filename = filename
                logging.debug(f"filename is {filename}")
                self.file["name"] = filename
            else:
                filename = object_arista.hashfile(file_type)
                self.file[file_type] = filename
            if url is None:
                logging.error(f"URL not found for {file_type}")
                raise ValueError(f"URL not found for {file_type}")
            if filename is None:
                logging.error(f"Filename not found for {file_type}")
                raise ValueError(f"Filename not found for {file_type}")

            if not os.path.exists(file_path):
                logging.warning(f"creating folder on eve-ng server : {file_path}")
                self._create_destination_folder(path=file_path)

            logging.debug(
                f"downloading file {filename} for version {object_arista.version}"
            )
            self.download_file(url, file_path, filename, rich_interface=True)

        # Convert to QCOW2 format
        file_qcow2 = os.path.join(file_path, "hda.qcow2")

        if not self.dry_run:
            os.system(
                f"$(which qemu-img) convert -f vmdk -O qcow2 {file_path}/{eos_filename} {file_path}/{file_qcow2}"
            )
        else:
            logging.info(
                f"{'[DRY-RUN] Would convert' if self.dry_run else 'Converting'} VMDK to QCOW2 format: {file_path}/{eos_filename} to {file_qcow2} "
            )

        logging.info("Applying unl_wrapper to fix permissions")
        if not self.dry_run:
            os.system("/opt/unetlab/wrappers/unl_wrapper -a fixpermissions")
        else:
            logging.info("[DRY-RUN] Would execute unl_wrapper to fix permissions")
        # os.system(f"rm -f {file_downloaded}")

        # if noztp:
        #     self._disable_ztp(file_path=file_path)
