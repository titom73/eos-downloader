#!/usr/bin/python
# coding: utf-8 -*-
# flake8: noqa: F811
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

"""
eos_downloader class definition
"""

from __future__ import (
    absolute_import,
    annotations,
    division,
    print_function,
    unicode_literals,
)

import base64
import glob
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Union

import requests
import rich
from loguru import logger
from rich import console
from tqdm import tqdm

from eos_downloader import (
    ARISTA_DOWNLOAD_URL,
    ARISTA_GET_SESSION,
    ARISTA_SOFTWARE_FOLDER_TREE,
    EVE_QEMU_FOLDER_PATH,
    MSG_INVALID_DATA,
    MSG_TOKEN_EXPIRED,
)
from eos_downloader.data import DATA_MAPPING
from eos_downloader.download import DownloadProgressBar

# logger = logging.getLogger(__name__)

console = rich.get_console()


class ObjectDownloader:
    """
    ObjectDownloader Generic Object to download from Arista.com
    """

    def __init__(
        self,
        image: str,
        version: str,
        token: str,
        software: str = "EOS",
        hash_method: str = "md5sum",
    ):
        """
        __init__ Class constructor

        generic class constructor

        Parameters
        ----------
        image : str
            Type of image to download
        version : str
            Version of the package to download
        token : str
            Arista API token
        software : str, optional
            Package name to download (vEOS-lab, cEOS, EOS, ...), by default 'EOS'
        hash_method : str, optional
            Hash protocol to use to check download, by default 'md5sum'
        """
        self.software = software
        self.image = image
        self._version = version
        self.token = token
        self.folder_level = 0
        self.session_id = None
        self.filename = self._build_filename()
        self.hash_method = hash_method
        self.timeout = 5
        # Logging
        logger.debug(f"Filename built by _build_filename is {self.filename}")

    def __str__(self) -> str:
        return f"{self.software} - {self.image} - {self.version}"

    # def __repr__(self):
    #     return str(self.__dict__)

    @property
    def version(self) -> str:
        """Get version."""
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        """Set version."""
        self._version = value
        self.filename = self._build_filename()

    # ------------------------------------------------------------------------ #
    # Internal METHODS
    # ------------------------------------------------------------------------ #

    def _build_filename(self) -> str:
        """
        _build_filename Helper to build filename to search on arista.com

        Returns
        -------
        str:
            Filename to search for on Arista.com
        """
        logger.info("start build")
        if self.software in DATA_MAPPING:
            logger.info(f"software in data mapping: {self.software}")
            if self.image in DATA_MAPPING[self.software]:
                logger.info(f"image in data mapping: {self.image}")
                return f"{DATA_MAPPING[self.software][self.image]['prepend']}-{self.version}{DATA_MAPPING[self.software][self.image]['extension']}"
            return f"{DATA_MAPPING[self.software]['default']['prepend']}-{self.version}{DATA_MAPPING[self.software]['default']['extension']}"
        raise ValueError(f"Incorrect value for software {self.software}")

    def _parse_xml_for_path(
        self, root_xml: ET.ElementTree, xpath: str, search_file: str
    ) -> str:
        # sourcery skip: remove-unnecessary-cast
        """
        _parse_xml Read and extract data from XML using XPATH

        Get all interested nodes using XPATH and then get node that match search_file

        Parameters
        ----------
        root_xml : ET.ElementTree
            XML document
        xpath : str
            XPATH expression to filter XML
        search_file : str
            Filename to search for

        Returns
        -------
        str
            File Path on Arista server side
        """
        logger.debug(f"Using xpath {xpath}")
        logger.debug(f"Search for file {search_file}")
        console.print(f"🔎  Searching file {search_file}")
        for node in root_xml.findall(xpath):
            # logger.debug('Found {}', node.text)
            if str(node.text).lower() == search_file.lower():
                path = node.get("path")
                console.print(f"    -> Found file at {path}")
                logger.info(f'Found {node.text} at {node.get("path")}')
                return str(node.get("path")) if node.get("path") is not None else ""
        logger.error(f"Requested file ({self.filename}) not found !")
        return ""

    def _get_hash(self, file_path: str) -> str:
        """
        _get_hash Download HASH file from Arista server

        Parameters
        ----------
        file_path : str
            Path of the HASH file

        Returns
        -------
        str
            Hash string read from HASH file downloaded from Arista.com
        """
        remote_hash_file = self._get_remote_hashpath(hash_method=self.hash_method)
        hash_url = self._get_url(remote_file_path=remote_hash_file)
        # hash_downloaded = self._download_file_raw(url=hash_url, file_path=file_path + "/" + os.path.basename(remote_hash_file))
        dl_rich_progress_bar = DownloadProgressBar()
        dl_rich_progress_bar.download(urls=[hash_url], dest_dir=file_path)
        hash_downloaded = f"{file_path}/{os.path.basename(remote_hash_file)}"
        hash_content = "unset"
        with open(hash_downloaded, "r", encoding="utf-8") as f:
            hash_content = f.read()
        return hash_content.split(" ")[0]

    @staticmethod
    def _compute_hash_md5sum(file: str, hash_expected: str) -> bool:
        """
        _compute_hash_md5sum Compare MD5 sum

        Do comparison between local md5 of the file and value provided by arista.com

        Parameters
        ----------
        file : str
            Local file to use for MD5 sum
        hash_expected : str
            MD5 from arista.com

        Returns
        -------
        bool
            True if both are equal, False if not
        """
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        if hash_md5.hexdigest() == hash_expected:
            return True
        logger.warning(
            f"Downloaded file is corrupt: local md5 ({hash_md5.hexdigest()}) is different to md5 from arista ({hash_expected})"
        )
        return False

    @staticmethod
    def _compute_hash_sh512sum(file: str, hash_expected: str) -> bool:
        """
        _compute_hash_sh512sum Compare SHA512 sum

        Do comparison between local sha512 of the file and value provided by arista.com

        Parameters
        ----------
        file : str
            Local file to use for MD5 sum
        hash_expected : str
            SHA512 from arista.com

        Returns
        -------
        bool
            True if both are equal, False if not
        """
        hash_sha512 = hashlib.sha512()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha512.update(chunk)
        if hash_sha512.hexdigest() == hash_expected:
            return True
        logger.warning(
            f"Downloaded file is corrupt: local sha512 ({hash_sha512.hexdigest()}) is different to sha512 from arista ({hash_expected})"
        )
        return False

    def get_folder_tree(self) -> ET.ElementTree:
        """
        _get_folder_tree Download XML tree from Arista server

        Returns
        -------
        ET.ElementTree
            XML document
        """
        if self.session_id is None:
            self.authenticate()
        jsonpost = {"sessionCode": self.session_id}
        result = requests.post(
            ARISTA_SOFTWARE_FOLDER_TREE, data=json.dumps(jsonpost), timeout=self.timeout
        )
        try:
            folder_tree = result.json()["data"]["xml"]
            return ET.ElementTree(ET.fromstring(folder_tree))
        except KeyError as error:
            logger.error(MSG_INVALID_DATA)
            logger.error(f"Server returned: {error}")
            console.print(f"❌  {MSG_INVALID_DATA}", style="bold red")
            sys.exit(1)

    def _get_remote_filepath(self) -> str:
        """
        _get_remote_filepath Helper to get path of the file to download

        Set XPATH and return result of _parse_xml for the file to download

        Returns
        -------
        str
            Remote path of the file to download
        """
        root = self.get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        xpath = f'.//dir[@label="{self.software}"]//file'
        return self._parse_xml_for_path(
            root_xml=root, xpath=xpath, search_file=self.filename
        )

    def _get_remote_hashpath(self, hash_method: str = "md5sum") -> str:
        """
        _get_remote_hashpath Helper to get path of the hash's file to download

        Set XPATH and return result of _parse_xml for the file to download

        Returns
        -------
        str
            Remote path of the hash's file to download
        """
        root = self.get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        xpath = f'.//dir[@label="{self.software}"]//file'
        return self._parse_xml_for_path(
            root_xml=root,
            xpath=xpath,
            search_file=f"{self.filename}.{hash_method}",
        )

    def _get_url(self, remote_file_path: str) -> str:
        """
        _get_url Get URL to use for downloading file from Arista server

        Send remote_file_path to get correct URL to use for download

        Parameters
        ----------
        remote_file_path : str
            Filepath from XML to use to get correct download link

        Returns
        -------
        str
            URL link to use for download
        """
        if self.session_id is None:
            self.authenticate()
        jsonpost = {"sessionCode": self.session_id, "filePath": remote_file_path}
        result = requests.post(
            ARISTA_DOWNLOAD_URL, data=json.dumps(jsonpost), timeout=self.timeout
        )
        if "data" in result.json() and "url" in result.json()["data"]:
            # logger.debug('URL to download file is: {}', result.json())
            return result.json()["data"]["url"]
        logger.critical(f"Server returns following message: {result.json()}")
        return ""

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

    def _download_file(
        self, file_path: str, filename: str, rich_interface: bool = True
    ) -> Union[None, str]:
        remote_file_path = self._get_remote_filepath()
        logger.info(f"File found on arista server: {remote_file_path}")
        file_url = self._get_url(remote_file_path=remote_file_path)
        if file_url is not False:
            if not rich_interface:
                return self._download_file_raw(
                    url=file_url, file_path=os.path.join(file_path, filename)
                )
            rich_downloader = DownloadProgressBar()
            rich_downloader.download(urls=[file_url], dest_dir=file_path)
            return os.path.join(file_path, filename)
        logger.error(f"Cannot download file {file_path}")
        return None

    @staticmethod
    def _create_destination_folder(path: str) -> None:
        # os.makedirs(path, mode, exist_ok=True)
        os.system(f"mkdir -p {path}")

    @staticmethod
    def _disable_ztp(file_path: str) -> None:
        pass

    # ------------------------------------------------------------------------ #
    # Public METHODS
    # ------------------------------------------------------------------------ #

    def authenticate(self) -> bool:
        """
        authenticate Authenticate user on Arista.com server

        Send API token and get a session-id from remote server.
        Session-id will be used by all other functions.

        Returns
        -------
        bool
            True if authentication succeeds=, False in all other situations.
        """
        credentials = (base64.b64encode(self.token.encode())).decode("utf-8")
        session_code_url = ARISTA_GET_SESSION
        jsonpost = {"accessToken": credentials}

        result = requests.post(
            session_code_url, data=json.dumps(jsonpost), timeout=self.timeout
        )

        if result.json()["status"]["message"] in [
            "Access token expired",
            "Invalid access token",
        ]:
            console.print(f"❌  {MSG_TOKEN_EXPIRED}", style="bold red")
            logger.error(MSG_TOKEN_EXPIRED)
            return False

        try:
            if "data" in result.json():
                self.session_id = result.json()["data"]["session_code"]
                logger.info("Authenticated on arista.com")
                return True
            logger.debug(f"{result.json()}")
            return False
        except KeyError as error_arista:
            logger.error(f"Error: {error_arista}")
            sys.exit(1)

    def download_local(self, file_path: str, checksum: bool = False) -> bool:
        # sourcery skip: move-assign
        """
        download_local Entrypoint for local download feature

        Do local downnload feature:
        - Get remote file path
        - Get URL from Arista.com
        - Download file
        - Do HASH comparison (optional)

        Parameters
        ----------
        file_path : str
            Local path to save downloaded file
        checksum : bool, optional
            Execute checksum or not, by default False

        Returns
        -------
        bool
            True if everything went well, False if any problem appears
        """
        file_downloaded = str(
            self._download_file(file_path=file_path, filename=self.filename)
        )

        # Check file HASH
        hash_result = False
        if checksum:
            logger.info("🚀  Running checksum validation")
            console.print("🚀  Running checksum validation")
            if self.hash_method == "md5sum":
                hash_expected = self._get_hash(file_path=file_path)
                hash_result = self._compute_hash_md5sum(
                    file=file_downloaded, hash_expected=hash_expected
                )
            elif self.hash_method == "sha512sum":
                hash_expected = self._get_hash(file_path=file_path)
                hash_result = self._compute_hash_sh512sum(
                    file=file_downloaded, hash_expected=hash_expected
                )
        if not hash_result:
            logger.error("Downloaded file is corrupted, please check your connection")
            console.print(
                "❌  Downloaded file is corrupted, please check your connection"
            )
            return False
        logger.info("Downloaded file is correct.")
        console.print("✅  Downloaded file is correct.")
        return True

    def provision_eve(self, noztp: bool = False, checksum: bool = True) -> None:
        # pylint: disable=unused-argument
        """
        provision_eve Entrypoint for EVE-NG download and provisioning

        Do following actions:
        - Get remote file path
        - Get URL from file path
        - Download file
        - Convert file to qcow2 format
        - Create new version to EVE-NG
        - Disable ZTP (optional)

        Parameters
        ----------
        noztp : bool, optional
            Flag to deactivate ZTP in EOS image, by default False
        checksum : bool, optional
            Flag to ask for hash validation, by default True
        """
        # Build image name to use in folder path
        eos_image_name = self.filename.rstrip(".vmdk").lower()
        if noztp:
            eos_image_name = f"{eos_image_name}-noztp"
        # Create full path for EVE-NG
        file_path = os.path.join(EVE_QEMU_FOLDER_PATH, eos_image_name.rstrip())
        # Create folders in filesystem
        self._create_destination_folder(path=file_path)

        # Download file to local destination
        file_downloaded = self._download_file(
            file_path=file_path, filename=self.filename
        )

        # Convert to QCOW2 format
        file_qcow2 = os.path.join(file_path, "hda.qcow2")
        logger.info("Converting VMDK to QCOW2 format")
        console.print("🚀  Converting VMDK to QCOW2 format...")

        os.system(
            f"$(which qemu-img) convert -f vmdk -O qcow2 {file_downloaded} {file_qcow2}"
        )

        logger.info("Applying unl_wrapper to fix permissions")
        console.print("Applying unl_wrapper to fix permissions")

        os.system("/opt/unetlab/wrappers/unl_wrapper -a fixpermissions")
        os.system(f"rm -f {file_downloaded}")

        if noztp:
            self._disable_ztp(file_path=file_path)

    def docker_import(
        self, image_name: str = "arista/ceos", is_latest: bool = False
    ) -> None:
        """
        Import docker container to your docker server.

        Import downloaded container to your local docker engine.

        Args:
            version (str):
            image_name (str, optional): Image name to use. Defaults to "arista/ceos".
        """
        docker_image = f"{image_name}:{self.version}"
        logger.info(f"Importing image {self.filename} to {docker_image}")
        console.print(f"🚀 Importing image {self.filename} to {docker_image}")
        os.system(f"$(which docker) import {self.filename} {docker_image}")
        if is_latest:
            console.print(f"🚀 Configuring {docker_image}:{self.version} to be latest")
            os.system(f"$(which docker) tag {docker_image} {image_name}:latest")
        for filename in glob.glob(f"{self.filename}*"):
            try:
                os.remove(filename)
            except FileNotFoundError:
                console.print(f"File not found: {filename}")
