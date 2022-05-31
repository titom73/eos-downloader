#!/usr/bin/python
# coding: utf-8 -*-

import os
import rich
from loguru import logger
from eos_downloader.object_downloader import ObjectDownloader
from rich import console

console = rich.get_console()


class SWIXDownloader(ObjectDownloader):
    """
    SWIXDownloader Object to download SWIX packages from Arista.com website

    Supercharge ObjectDownloader to support SWIX specific actions

    Parameters
    ----------
    ObjectDownloader : ObjectDownloader
        Base object
    """
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
        xpath = './/dir[@label="' + self.image + '"]//file'
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
        xpath = './/dir[@label="' + self.image + '"]//file'
        return self._parse_xml(root_xml=root, xpath=xpath, search_file=self.filename + '.' + hash_method)