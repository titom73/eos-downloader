#!/usr/bin/python
# coding: utf-8 -*-
# flake8: noqa: F811

"""
Specific EOS inheritance from object_download
"""

import os

import rich
from loguru import logger
from rich import console
import xml.etree.ElementTree as ET
from typing import List

from eos_downloader.object_downloader import ObjectDownloader
from eos_downloader.models.version import eos_version_reg, EosVersion, BASE_VERSION_STR, BASE_BRANCH_STR

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
        logger.info('Unmounting volume in {}', file_path)
        os.system(f"guestunmount {os.path.join(file_path, 'raw')}")
        os.system(f"rm -rf {os.path.join(file_path, 'raw')}")
        logger.info(f"Volume has been successfully unmounted at {file_path}")

    def _parse_xml_for_version(self,root_xml: ET.ElementTree, xpath: str = './/dir[@label="Active Releases"]/dir/dir/[@label]') -> List[str]:
        # XPATH: .//dir[@label="Active Releases"]/dir/dir/[@label]
        logger.debug(f'Using xpath {xpath}')
        eos_versions = []
        for node in root_xml.findall(xpath):
            if 'label' in node.attrib and eos_version_reg.match(node.get('label')):
                eos_version = EosVersion.from_str(node.get("label"))
                eos_versions.append(eos_version)
                logger.debug(f"Found {node.get('label')} - {eos_version}")
        return eos_versions

    def _get_branches(self):
        root = self._get_folder_tree()
        versions = self._parse_xml_for_version(root_xml=root)
        return list(set(version.branch() for version in versions))

    def latest_branch(self):
        selected_branch = EosVersion.from_str(BASE_BRANCH_STR)
        for branch in self._get_branches():
            branch = EosVersion.from_str(branch)
            if branch > selected_branch:
                selected_branch = branch
        return selected_branch

    def get_eos_versions(self, branch: str = None):
        root = self._get_folder_tree()
        result = []
        for version in self._parse_xml_for_version(root_xml=root):
            if branch is None:
                result.append(version)
            elif version.is_in_branch(branch):
                result.append(version)
        return result

    def latest_eos(self, branch: str = None, rtype: str = None):
        selected_version = EosVersion.from_str(BASE_VERSION_STR)
        if branch is None:
            latest_branch = self.latest_branch()
        else:
            latest_branch = EosVersion.from_str(branch)
        for version in self.get_eos_versions(branch=str(latest_branch.branch())):
            if version > selected_version:
                if rtype is not None and version.rtype == rtype:
                    selected_version = version
                if rtype is None:
                    selected_version = version
        return selected_version
