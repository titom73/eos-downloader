#!/usr/bin/python
# coding: utf-8 -*-

from loguru import logger
from eos_downloader import ObjectDownloader


class EOSDownloader(ObjectDownloader):

    def get_remote_filepath(self):
        root = self.get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        if self.image == 'EOS':
            xpath = './/dir[@label="' + self.software + '"]//dir[@label="EOS-' + self.version + '"]//file'
        else:
            xpath = './/dir[@label="' + self.software + '"]//dir[@label="EOS-' + self.version + '"]//dir[@label="' + self.image + '"]/file'
        return self._parse_xml(root_xml=root, xpath=xpath, search_file=self.filename)
