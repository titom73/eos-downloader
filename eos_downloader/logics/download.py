# coding: utf-8 -*-
"""ObjectDownloader class to manage file downloads with an option to use rich interface.

This class provides methods to download files from URLs with progress tracking using either
tqdm or rich interface. It supports both raw downloads and enhanced visual feedback during
the download process.

Methods
--------
download_file(url: str, file_path: str, filename: str, rich_interface: bool = True) -> Union[None, str]
    Downloads a file from the given URL to the specified path with optional rich interface.

_download_file_raw(url: str, file_path: str) -> str
    Static method that performs the actual file download with tqdm progress bar.

Attributes
--------
None

Example
--------
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
from typing import Union, Literal, Dict, Optional
from pathlib import Path

import logging
import requests
from tqdm import tqdm

import eos_downloader.models.types
import eos_downloader.defaults
import eos_downloader.helpers
import eos_downloader.logics
import eos_downloader.logics.arista_xml_server
import eos_downloader.models.version


class SoftManager:
    """SoftManager helps to download files from a remote location.

    This class provides methods to download files using either a simple progress bar
    or a rich interface with enhanced visual feedback.

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

    def __init__(self, dry_run: bool = False, force_download: bool = False) -> None:
        """
        Initialize SoftManager.

        Parameters
        ----------
        dry_run : bool, optional
            If True, simulate operations without executing them, by default False
        force_download : bool, optional
            If True, bypass cache and force download/import, by default False
        """
        self.file: Dict[str, Union[str, None]] = {}
        self.file["name"] = None
        self.file["md5sum"] = None
        self.file["sha512sum"] = None
        self.dry_run = dry_run
        self.force_download = force_download
        logging.info(
            "SoftManager initialized%s%s",
            " in dry-run mode" if dry_run else "",
            " with force download" if force_download else ""
        )

    def _file_exists_and_valid(
        self,
        file_path: Path,
        checksum_file: Optional[Path] = None,
        check_type: Literal["md5sum", "sha512sum", "skip"] = "skip"
    ) -> bool:
        """
        Check if file exists and optionally validate its checksum.

        Parameters
        ----------
        file_path : Path
            Path to the file to check
        checksum_file : Optional[Path]
            Path to checksum file for validation
        check_type : Literal["md5sum", "sha512sum", "skip"]
            Type of checksum validation to perform

        Returns
        -------
        bool
            True if file exists and passes validation, False otherwise

        Examples
        --------
        >>> manager = SoftManager()
        >>> manager._file_exists_and_valid(Path("EOS-4.29.3M.swi"))
        True
        """
        # Check if file exists
        if not file_path.exists():
            logging.debug(f"File not found in cache: {file_path}")
            return False

        # If no checksum validation requested, file is valid
        if check_type == "skip" or checksum_file is None:
            logging.info(
                f"File found in cache (no validation): {file_path}"
            )
            return True

        # Validate checksum if requested
        try:
            # Store current file info
            original_name = self.file["name"]
            original_checksum = self.file.get(check_type)

            # Set file info for checksum validation
            self.file["name"] = str(file_path)
            self.file[check_type] = str(checksum_file)

            # Perform checksum validation
            is_valid = self.checksum(check_type=check_type)

            # Restore original file info
            self.file["name"] = original_name
            if original_checksum:
                self.file[check_type] = original_checksum

            if is_valid:
                logging.info(
                    f"File found in cache (checksum valid): {file_path}"
                )
                return True
            else:
                logging.warning(
                    f"Cached file checksum invalid: {file_path}"
                )
                return False
        except Exception as e:
            logging.warning(f"Checksum validation failed: {e}")
            return False

    @staticmethod
    def _download_file_raw(url: str, file_path: str) -> str:
        """Downloads a file from a URL and saves it to a local file.

        Parameters
        ----------
        url : str
            The URL of the file to download.
        file_path : str
            The local path where the file will be saved.

        Returns
        -------
        str
            The path to the downloaded file.

        Notes
        -----
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
        """Creates a directory path if it doesn't already exist.

        Parameters
        ----------
        path : str
            The directory path to create.

        Returns
        -------
        None
        """
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.critical(f"Error creating folder: {e}")

    def _compute_hash_md5sum(self, file: str, hash_expected: str) -> bool:
        """
        Compare MD5 sum.

        Do comparison between local md5 of the file and value provided by arista.com.

        Parameters
        ----------
        file : str
            Local file to use for MD5 sum.
        hash_expected : str
            MD5 from arista.com.

        Returns
        -------
        bool
            True if both are equal, False if not.
        """
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hash_md5.update(chunk)
        if hash_md5.hexdigest() == hash_expected:
            return True
        logging.warning(
            f"Downloaded file is corrupt: local md5 ({hash_md5.hexdigest()}) is different to md5 from arista ({hash_expected})"
        )
        return False

    def checksum(self, check_type: Literal["md5sum", "sha512sum", "md5"]) -> bool:
        """
        Verifies the integrity of a downloaded file using a specified checksum algorithm.

        Parameters
        ----------
        check_type : Literal['md5sum', 'sha512sum', 'md5']
            The type of checksum to perform. Currently supports 'md5sum' or 'sha512sum'.

        Returns
        -------
        bool
            True if the checksum verification passes.

        Raises
        ------
        ValueError
            If the calculated checksum does not match the expected checksum.
        FileNotFoundError
            If either the checksum file or the target file cannot be found.

        Examples
        --------
        >>> client.checksum('sha512sum')  # Returns True if checksum matches
        """
        logging.info(f"Checking checksum for {self.file['name']} using {check_type}")

        if self.dry_run:
            logging.debug("Dry-run mode enabled, skipping checksum verification")
            return True

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
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    hash_sha512.update(chunk)
            if hash_sha512.hexdigest() != hash_expected:
                logging.error(
                    f"Checksum failed for {self.file['name']}: computed {hash_sha512.hexdigest()} - expected {hash_expected}"
                )
                raise ValueError("Incorrect checksum")
            return True

        if check_type in ["md5sum", "md5"]:
            md5sum_file = self.file["md5sum"]
            file_name = self.file["name"]

            if md5sum_file is None:
                raise ValueError(f"md5sum is not found: {md5sum_file}")

            with open(md5sum_file, "r", encoding="utf-8") as f:
                hash_expected = f.read().split()[0]

            if hash_expected is None:
                raise ValueError("MD5Sum is empty, cannot compute file.")

            if file_name is None:
                raise ValueError("Filename is None. Please fix it")

            if not self._compute_hash_md5sum(file_name, hash_expected=hash_expected):
                logging.error(
                    f"Checksum failed for {self.file['name']}: expected {hash_expected}"
                )

                raise ValueError("Incorrect checksum")

            return True

        logging.error(f"Checksum type {check_type} not yet supported")
        raise ValueError(f"Checksum type {check_type} not yet supported")

    def download_file(
        self,
        url: str,
        file_path: str,
        filename: str,
        rich_interface: bool = True,
        force: bool = False
    ) -> Union[None, str]:
        """
        Downloads a file from a URL with caching support.

        Parameters
        ----------
        url : str
            The URL from which to download the file.
        file_path : str
            The directory path where the file should be saved.
        filename : str
            The name to be given to the downloaded file.
        rich_interface : bool, optional
            Whether to use rich progress bar interface. Defaults to True.
        force : bool, optional
            If True, download even if file exists locally. Defaults to False.

        Returns
        -------
        Union[None, str]
            Path to the downloaded or cached file, or None on error.

        Examples
        --------
        >>> manager = SoftManager()
        >>> manager.download_file(
        ...     url="https://example.com/file.swi",
        ...     file_path="/downloads",
        ...     filename="EOS-4.29.3M.swi"
        ... )
        '/downloads/EOS-4.29.3M.swi'
        """
        full_path = Path(file_path) / filename

        # Check cache unless force flag is set
        if not force and not self.force_download:
            if full_path.exists():
                logging.info(f"Using cached file: {full_path}")
                return str(full_path)

        # Log download action
        logging.info(
            f"{'[DRY-RUN] Would download' if self.dry_run else 'Downloading'} {filename} from {url}"
        )

        # Handle dry-run mode
        if self.dry_run:
            return os.path.join(file_path, filename)

        # Proceed with download
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
        object_arista: eos_downloader.logics.arista_xml_server.AristaXmlObjects,
        file_path: str,
        rich_interface: bool = True,
    ) -> Union[None, str]:
        """
        Downloads files from Arista EOS server with caching support.

        Downloads the EOS image and optional md5/sha512 files based on the
        provided EOS XML object. Each file is downloaded to the specified path
        with appropriate filenames. Uses cache to skip already downloaded files
        unless force_download is enabled.

        Parameters
        ----------
        object_arista : eos_downloader.logics.arista_xml_server.AristaXmlObjects
            Object containing EOS image and hash file URLs.
        file_path : str
            Directory path where files should be downloaded.
        rich_interface : bool, optional
            Whether to use rich console output. Defaults to True.

        Returns
        -------
        Union[None, str]
            The file path where files were downloaded/cached, or None if failed.

        Examples
        --------
        Download new files or use cache:

        >>> client = SoftManager()
        >>> client.downloads(eos_obj, "/tmp/downloads")
        '/tmp/downloads'

        Force re-download even if cached:

        >>> client = SoftManager(force_download=True)
        >>> client.downloads(eos_obj, "/tmp/downloads")
        '/tmp/downloads'
        """
        logging.info(
            f"Processing files for {object_arista.version} "
            f"(force_download={self.force_download})"
        )

        if len(object_arista.urls) == 0:
            logging.error("No URLs found for download")
            raise ValueError("No URLs found for download")

        for file_type, url in sorted(object_arista.urls.items(), reverse=True):
            logging.debug(f"Processing {file_type} from {url}")
            if file_type == "image":
                filename = object_arista.filename
                self.file["name"] = filename
            else:
                filename = object_arista.hash_filename()
                self.file[file_type] = filename
            if url is None:
                logging.error(f"URL not found for {file_type}")
                raise ValueError(f"URL not found for {file_type}")
            if filename is None:
                logging.error(f"Filename not found for {file_type}")
                raise ValueError(f"Filename not found for {file_type}")
            if not self.dry_run:
                # download_file will check cache automatically
                # unless self.force_download is True
                self.download_file(
                    url,
                    file_path,
                    filename,
                    rich_interface,
                    force=self.force_download
                )
            else:
                full_path = Path(file_path) / filename
                if full_path.exists() and not self.force_download:
                    logging.info(
                        f"[DRY-RUN] Would use cached file: {filename}"
                    )
                else:
                    logging.info(
                        f"[DRY-RUN] Would download file {filename} "
                        f"for version {object_arista.version}"
                    )

        return file_path

    @staticmethod
    def _docker_image_exists(image_name: str, image_tag: str) -> bool:
        """
        Check if Docker image with specified tag exists locally.

        Parameters
        ----------
        image_name : str
            Docker image name (e.g., 'arista/ceos')
        image_tag : str
            Docker image tag (e.g., '4.29.3M')

        Returns
        -------
        bool
            True if image:tag exists in local registry, False otherwise

        Examples
        --------
        >>> SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
        True

        Notes
        -----
        This method tries both 'docker' and 'podman' commands in order.
        It uses 'docker images -q' to check for image existence.
        """
        import subprocess

        # Try docker first, then podman
        for cmd in ['docker', 'podman']:
            # Check if command is available
            if not shutil.which(cmd):
                logging.debug(f"{cmd} command not found in PATH")
                continue

            try:
                # Query for specific image:tag
                result = subprocess.run(
                    [cmd, 'images', '-q', f'{image_name}:{image_tag}'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )

                # If output is not empty, image exists
                if result.stdout.strip():
                    logging.info(
                        f"Docker image {image_name}:{image_tag} "
                        f"found in local registry"
                    )
                    return True
                else:
                    logging.debug(
                        f"Docker image {image_name}:{image_tag} "
                        f"not found in local registry"
                    )
                    return False

            except subprocess.TimeoutExpired:
                logging.warning(f"{cmd} command timed out after 5 seconds")
                continue

            except Exception as e:
                logging.debug(f"Error checking {cmd} images: {e}")
                continue

        # If we get here, neither docker nor podman worked
        logging.warning(
            "Unable to check Docker images (docker/podman not available)"
        )
        return False

    def import_docker(
        self,
        local_file_path: str,
        docker_name: str = "arista/ceos",
        docker_tag: str = "latest",
        force: bool = False
    ) -> None:
        """
        Import local file into Docker with caching support.

        Parameters
        ----------
        local_file_path : str
            Path to the local file to import
        docker_name : str, optional
            Docker image name, by default "arista/ceos"
        docker_tag : str, optional
            Docker image tag, by default "latest"
        force : bool, optional
            If True, import even if image:tag already exists.
            Defaults to False.

        Raises
        ------
        FileNotFoundError
            If the local file does not exist

        Examples
        --------
        >>> manager = SoftManager()
        >>> manager.import_docker(
        ...     local_file_path="/downloads/cEOS-4.29.3M.tar.xz",
        ...     docker_name="arista/ceos",
        ...     docker_tag="4.29.3M"
        ... )
        """
        # Check if file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File {local_file_path} not found")

        # Check cache unless force flag is set
        if not force and not self.force_download:
            if self._docker_image_exists(docker_name, docker_tag):
                logging.info(
                    f"Docker image {docker_name}:{docker_tag} already "
                    f"exists locally. Use --force to re-import."
                )
                return

        # Log import action
        logging.info(
            f"{'[DRY-RUN] Would import' if self.dry_run else 'Importing'} "
            f"{docker_name}:{docker_tag}"
        )

        # Handle dry-run mode
        if self.dry_run:
            return

        # Check if docker is available
        if not shutil.which("docker"):
            raise FileNotFoundError("Docker binary not found in PATH")

        # Proceed with import
        try:
            cmd = (
                f"$(which docker) import {local_file_path} "
                f"{docker_name}:{docker_tag}"
            )
            logging.debug(f"Executing: {cmd}")
            os.system(cmd)
            logging.info(
                f"Docker image {docker_name}:{docker_tag} "
                f"imported successfully"
            )
        except Exception as e:
            logging.error(f"Error importing docker image: {e}")
            raise e

    # pylint: disable=too-many-branches
    def provision_eve(
        self,
        object_arista: eos_downloader.logics.arista_xml_server.EosXmlObject,
        noztp: bool = False,
    ) -> None:
        """
        Provisions EVE-NG with the specified Arista EOS object.

        Parameters
        ----------
        object_arista : eos_downloader.logics.arista_xml_server.EosXmlObject
            The Arista EOS object containing version, filename, and URLs.
        noztp : bool, optional
            If True, disables ZTP (Zero Touch Provisioning). Defaults to False.

        Raises
        ------
        ValueError
            If no URLs are found for download or if a URL or filename is None.

        Returns
        -------
        None
        """

        # EVE-NG provisioning page for vEOS
        # https://www.eve-ng.net/index.php/documentation/howtos/howto-add-arista-veos/

        logging.info(
            f"Provisioning EVE-NG with {object_arista.version} / {object_arista.filename}"
        )

        file_path = f"{eos_downloader.defaults.EVE_QEMU_FOLDER_PATH}/veos-{object_arista.version}"

        filename: Union[str, None] = None
        eos_filename = object_arista.filename

        if len(object_arista.urls) == 0:
            logging.error("No URLs found for download")
            raise ValueError("No URLs found for download")

        for file_type, url in sorted(object_arista.urls.items(), reverse=True):
            logging.debug(f"Downloading {file_type} from {url}")
            if file_type == "image":
                fname = object_arista.filename
                if fname is not None:
                    filename = fname
                    if noztp:
                        filename = f"{os.path.splitext(fname)[0]}-noztp{os.path.splitext(fname)[1]}"
                    eos_filename = filename
                    logging.debug(f"filename is {filename}")
                    self.file["name"] = filename
            else:
                filename = object_arista.hash_filename()
                if filename is not None:
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
