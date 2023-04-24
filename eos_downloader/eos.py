#!/usr/bin/python
# coding: utf-8 -*-
# flake8: noqa: F811

"""
Specific EOS inheritance from object_download
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Union

import rich
from loguru import logger
from rich import console

from eos_downloader.models.version import BASE_BRANCH_STR, BASE_VERSION_STR, REGEX_EOS_VERSION, RTYPE_FEATURE, EosVersion
from eos_downloader.object_downloader import ObjectDownloader

# logger = logging.getLogger(__name__)

console = rich.get_console()

class EOSDownloader(ObjectDownloader):
    """
    EOSDownloader Object to download EOS images from Arista.com website

    Supercharge ObjectDownloader to support EOS specific actions

    Parameters
    ----------
    ObjectDownloader : ObjectDownloader
        Base object
    """

    eos_versions: Union[List[EosVersion], None] = None

    @staticmethod
    def _disable_ztp(file_path: str) -> None:
        """
        _disable_ztp Method to disable ZTP in EOS image

        Create a file in the EOS image to disable ZTP process during initial boot

        Parameters
        ----------
        file_path : str
            Path where EOS image is located
        """
        logger.info('Mounting volume to disable ZTP')
        console.print('🚀 Mounting volume to disable ZTP')
        raw_folder = os.path.join(file_path, "raw")
        os.system(f"rm -rf {raw_folder}")
        os.system(f"mkdir -p {raw_folder}")
        os.system(
            f'guestmount -a {os.path.join(file_path, "hda.qcow2")} -m /dev/sda2 {os.path.join(file_path, "raw")}')
        ztp_file = os.path.join(file_path, 'raw/zerotouch-config')
        with open(ztp_file, 'w', encoding='ascii') as zfile:
            zfile.write('DISABLE=True')
        logger.info(f'Unmounting volume in {file_path}')
        os.system(f"guestunmount {os.path.join(file_path, 'raw')}")
        os.system(f"rm -rf {os.path.join(file_path, 'raw')}")
        logger.info(f"Volume has been successfully unmounted at {file_path}")

    def _parse_xml_for_version(self,root_xml: ET.ElementTree, xpath: str = './/dir[@label="Active Releases"]/dir/dir/[@label]') -> List[EosVersion]:
        """
        Extract list of available EOS versions from Arista.com website

        Create a list of EosVersion object for all versions available on Arista.com

        Args:
            root_xml (ET.ElementTree): XML file with all versions available
            xpath (str, optional): XPATH to use to extract EOS version. Defaults to './/dir[@label="Active Releases"]/dir/dir/[@label]'.

        Returns:
            List[EosVersion]: List of EosVersion representing all available EOS versions
        """
        # XPATH: .//dir[@label="Active Releases"]/dir/dir/[@label]
        if self.eos_versions is None:
            logger.debug(f'Using xpath {xpath}')
            eos_versions = []
            for node in root_xml.findall(xpath):
                if 'label' in node.attrib and node.get('label') is not None:
                    label = node.get('label')
                    if label is not None and REGEX_EOS_VERSION.match(label):
                        eos_version = EosVersion.from_str(label)
                        eos_versions.append(eos_version)
                        logger.debug(f"Found {label} - {eos_version}")
            logger.debug(f'List of versions found on arista.com is: {eos_versions}')
            self.eos_versions = eos_versions
        else:
            logger.debug('receiving instruction to download versions, but already available')
        return self.eos_versions

    def _get_branches(self, with_rtype: str = RTYPE_FEATURE) -> List[str]:
        """
        Extract all EOS branches available from arista.com

        Call self._parse_xml_for_version and then build list of available branches

        Args:
            rtype (str, optional): Release type to find. Can be M or F, default to F

        Returns:
            List[str]: A lsit of string that represent all availables EOS branches
        """
        root = self._get_folder_tree()
        versions = self._parse_xml_for_version(root_xml=root)
        return list({version.branch for version in versions if version.rtype == with_rtype})

    def latest_branch(self, rtype: str = RTYPE_FEATURE) -> EosVersion:
        """
        Get latest branch from semver standpoint

        Args:
            rtype (str, optional): Release type to find. Can be M or F, default to F

        Returns:
            EosVersion: Latest Branch object
        """
        selected_branch = EosVersion.from_str(BASE_BRANCH_STR)
        for branch in self._get_branches(with_rtype=rtype):
            branch = EosVersion.from_str(branch)
            if branch > selected_branch:
                selected_branch = branch
        return selected_branch

    def get_eos_versions(self, branch: Union[str,None] = None, rtype: Union[str,None] = None) -> List[EosVersion]:
        """
        Get a list of available EOS version available on arista.com

        If a branch is provided, only version in this branch are listed.
        Otherwise, all versions are provided.

        Args:
            branch (str, optional): An EOS branch to filter. Defaults to None.
            rtype (str, optional): Release type to find. Can be M or F, default to F

        Returns:
            List[EosVersion]: A list of versions available
        """
        root = self._get_folder_tree()
        result = []
        for version in self._parse_xml_for_version(root_xml=root):
            if branch is None and (version.rtype == rtype or rtype is None):
                result.append(version)
            elif branch is not None and version.is_in_branch(branch) and version.rtype == rtype:
                result.append(version)
        return result

    def latest_eos(self, branch: Union[str,None] = None, rtype: str = RTYPE_FEATURE) -> EosVersion:
        """
        Get latest version of EOS

        If a branch is provided, only version in this branch are listed.
        Otherwise, all versions are provided.
        You can select what type of version to consider: M or F

        Args:
            branch (str, optional): An EOS branch to filter. Defaults to None.
            rtype (str, optional): An EOS version type to filter, Can be M or F. Defaults to None.

        Returns:
            EosVersion: latest version selected
        """
        selected_version = EosVersion.from_str(BASE_VERSION_STR)
        if branch is None:
            latest_branch = self.latest_branch(rtype=rtype)
        else:
            latest_branch = EosVersion.from_str(branch)
        for version in self.get_eos_versions(branch=str(latest_branch.branch), rtype=rtype):
            if version > selected_version:
                if rtype is not None and version.rtype == rtype:
                    selected_version = version
                if rtype is None:
                    selected_version = version
        return selected_version
