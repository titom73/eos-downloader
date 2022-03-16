#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# from builtins import *
import os
import base64
import hashlib
import requests
from loguru import logger
import logging
import json
import xml.etree.ElementTree as ET
from eos_downloader.data import DATA_MAPPING
from eos_downloader import ARISTA_GET_SESSION, ARISTA_SOFTWARE_FOLDER_TREE, ARISTA_DOWNLOAD_URL, MSG_TOKEN_EXPIRED
from tqdm import tqdm


class ObjectDownloader():
    """
    ObjectDownloader Generic Object to download from Arista.com
    """
    def __init__(self, image: str, version: str, token: str, software: str = 'EOS', hash_method: str = 'md5sum'):
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

    def __rpr__(self):
        return {
            'software': self.software,
            'image': self.image,
            'version': self.version,
        }

    def __str__(self):
        return self.software + ' - ' + self.image + ' - ' + self.version

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value: str):
        self._version = value
        self.filename = self._build_filename()

    # ------------------------------------------------------------------------ #
    # Private METHODS
    # ------------------------------------------------------------------------ #

    def _build_filename(self):
        """
        _build_filename Helper to build filename to search on arista.com

        Returns
        -------
        str:
            Filename to search for on Arista.com
        """
        if self.software in DATA_MAPPING:
            if self.image in DATA_MAPPING[self.software]:
                return DATA_MAPPING[self.software][self.image]['prepend'] + "-" + self.version + DATA_MAPPING[self.software][self.image]['extension']
            else:
                return DATA_MAPPING[self.software]['default']['prepend'] + "-" + self.version + DATA_MAPPING[self.software]['default']['extension']
        return None

    def _parse_xml(self, root_xml: ET.ElementTree, xpath: str, search_file: str):
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
        logger.debug('Using xpath {}', xpath)
        logger.debug('Search for file {}', search_file)
        for node in root_xml.findall(xpath):
            # logger.debug('Found {}', node.text)
            if node.text.lower() == search_file.lower():
                logger.info('Found {} at {}', node.text, node.get('path'))
                return node.get('path')
        logger.error('🚫 Requested file ({}) not found !', self.filename)
        return False

    def _get_hash(self, file_path: str):
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
        hash_downloaded = self._download_file_raw(url=hash_url, file_path=file_path + "/" + os.path.basename(remote_hash_file))
        hash_content = 'unset'
        with open(hash_downloaded, 'r') as f:
            hash_content = f.read()
        return hash_content.split(' ')[0]

    @staticmethod
    def _compute_hash_md5sum(file: str, hash_expected: str):
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
        if str(hash_md5.hexdigest()) == hash_expected:
            return True
        logger.warning('⛔ Downloaded file is corrupt: local md5 ({}) is different to md5 from arista ({})',
                       hash_md5.hexdigest(),
                       hash_expected)
        return False

    @staticmethod
    def _compute_hash_sh512sum(file: str, hash_expected: str):
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
        if str(hash_sha512.hexdigest()) == hash_expected:
            return True
        logger.warning('⛔ Downloaded file is corrupt: local sha512 ({}) is different to sha512 from arista ({})',
                       hash_sha512.hexdigest(),
                       hash_expected)
        return False

    def _get_folder_tree(self):
        """
        _get_folder_tree Download XML tree from Arista server

        Returns
        -------
        ET.ElementTree
            XML document
        """
        if self.session_id is None:
            self.authenticate()
        jsonpost = {'sessionCode': self.session_id}
        result = requests.post(ARISTA_SOFTWARE_FOLDER_TREE, data=json.dumps(jsonpost))
        folder_tree = (result.json()["data"]["xml"])
        return ET.ElementTree(ET.fromstring(folder_tree))

    def _get_remote_filepath(self):
        """
        _get_remote_filepath Helper to get path of the file to download

        Set XPATH and return result of _parse_xml for the file to download

        Returns
        -------
        str
            Remote path of the file to download
        """
        root = self._get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        xpath = './/dir[@label="' + self.software + '"]//file'
        return self._parse_xml(root_xml=root, xpath=xpath, search_file=self.filename)

    def _get_remote_hashpath(self, hash_method: str = 'md5sum'):
        """
        _get_remote_hashpath Helper to get path of the hash's file to download

        Set XPATH and return result of _parse_xml for the file to download

        Returns
        -------
        str
            Remote path of the hash's file to download
        """
        root = self._get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        xpath = './/dir[@label="' + self.software + '"]//file'
        return self._parse_xml(root_xml=root, xpath=xpath, search_file=self.filename + '.' + hash_method)

    def _get_url(self, remote_file_path: str):
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
        jsonpost = {'sessionCode': self.session_id, 'filePath': remote_file_path}
        result = requests.post(ARISTA_DOWNLOAD_URL, data=json.dumps(jsonpost))
        if 'data' in result.json() and 'url' in result.json()['data']:
            # logger.debug('URL to download file is: {}', result.json())
            return result.json()["data"]["url"]
        logger.critical('Server returns following message: {}', result.json())
        return False

    @staticmethod
    def _download_file_raw(url: str, file_path: str):
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
        r = requests.get(url, stream=True)
        with open(file_path, 'wb') as f:
            pbar = tqdm(unit="B", total=int(r.headers['Content-Length']), unit_scale=True, unit_divisor=1024)
            for chunk in r.iter_content(chunk_size=chunkSize):
                if chunk:
                    pbar.update(len(chunk))
                f.write(chunk)
        return file_path

    def _download_file(self, file_path: str, filename: str, ):
        remote_file_path = self._get_remote_filepath()
        logger.info('🔎 File found on arista server: {}', remote_file_path)
        file_url = self._get_url(remote_file_path=remote_file_path)
        if file_url is not False:
            return self._download_file_raw(url=file_url, file_path=os.path.join(file_path, filename))
        logger.error('❌ Cannot download file {}', file_path)
        return None

    @staticmethod
    def _create_destination_folder(path):
        # os.makedirs(path, mode, exist_ok=True)
        os.system('mkdir -p ' + path)

    @staticmethod
    def _disable_ztp(file_path: str):
        pass

    # ------------------------------------------------------------------------ #
    # Public METHODS
    # ------------------------------------------------------------------------ #

    def authenticate(self):
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
        jsonpost = {'accessToken': credentials}

        result = requests.post(session_code_url, data=json.dumps(jsonpost))

        if result.json()["status"]["message"] == 'Access token expired':
            logger.error(MSG_TOKEN_EXPIRED)
            return False
        elif result.json()["status"]["message"] == 'Invalid access token':
            logger.error(MSG_TOKEN_EXPIRED)
            return False

        if 'data' in result.json():
            self.session_id = (result.json()["data"]["session_code"])
            logger.info('✅ Authenticated on arista.com')
            return True
        logger.debug('{}'.format(result.json()))
        return False

    def download_local(self, file_path: str, checksum: bool = False):
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
        file_downloaded = self._download_file(file_path=file_path, filename=self.filename)

        # Check file HASH
        hash_result = False
        if checksum:
            logging.info('🚀 Running checksum validation')
            if self.hash_method == 'md5sum':
                hash_expected = self._get_hash(file_path=file_path)
                hash_result = self._compute_hash_md5sum(file=file_downloaded, hash_expected=hash_expected)
            elif self.hash_method == 'sha512sum':
                hash_expected = self._get_hash(file_path=file_path)
                hash_result = self._compute_hash_sh512sum(file=file_downloaded, hash_expected=hash_expected)
        if not hash_result:
            logger.error('❌ Downloaded file is corrupted, please check your connection')
            return False
        logger.warning('✅ Downloaded file is correct.')
        return True

    def provision_eve(self, noztp: bool = False, checksum: bool = True):
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
            eos_image_name = eos_image_name + '-noztp'
        # Create full path for EVE-NG
        file_path = os.path.join(EVE_QEMU_FOLDER_PATH, eos_image_name.rstrip())
        # Create folders in filesystem
        self._create_destination_folder(path=file_path)

        # Download file to local destination
        file_downloaded = self._download_file(
            file_path=file_path, filename=self.filename)

        # Convert to QCOW2 format
        file_qcow2 = os.path.join(file_path, "hda.qcow2")
        logger.info('🚀 Converting VMDK to QCOW2 format')
        os.system(f'$(which qemu-img) convert -f vmdk -O qcow2 {file_downloaded} {file_qcow2}')
        logger.info('Applying unl_wrapper to fix permissions')
        os.system('/opt/unetlab/wrappers/unl_wrapper -a fixpermissions')
        os.system(f'rm -f {file_downloaded}')

        if noztp:
            self._disable_ztp(file_path=file_path)


    def docker_import(self, version: str, image_name: str = "arista/ceos"):
        docker_image = f'{image_name}:{self.version}'
        logger.info(f'🚀 Importing image {self.filename} to {docker_image}')
        os.system(f'$(which docker) import {self.filename} {docker_image}')
