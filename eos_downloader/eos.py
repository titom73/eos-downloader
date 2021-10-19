#!/usr/bin/python
# coding: utf-8 -*-

import os
from loguru import logger
from eos_downloader import ObjectDownloader


class EOSDownloader(ObjectDownloader):
    """
    EOSDownloader Object to download EOS images from Arista.com website

    Supercharge ObjectDownloader to support EOS specific actions

    Parameters
    ----------
    ObjectDownloader : ObjectDownloader
        Base object
    """
    def get_remote_filepath(self):
        """
        _get_remote_filepath Helper to get path of the file to download

        Set XPATH and return result of _parse_xml for the file to download.
        XPATH are EOS software oriented

        Returns
        -------
        str
            Remote path of the file to download
        """
        root = self.get_folder_tree()
        logger.debug("GET XML content from ARISTA.com")
        if self.image == 'EOS':
            xpath = './/dir[@label="' + self.software + '"]//dir[@label="EOS-' + self.version + '"]//file'
        else:
            xpath = './/dir[@label="' + self.software + '"]//dir[@label="EOS-' + self.version + '"]//dir[@label="' + self.image + '"]/file'
        return self._parse_xml(root_xml=root, xpath=xpath, search_file=self.filename)

    @staticmethod
    def _disable_ztp(file_path: str):
        """
        _disable_ztp Method to disable ZTP in EOS image

        Create a file in the EOS image to disable ZTP process during initial boot

        Parameters
        ----------
        file_path : str
            Path where EOS image is located
        """
        logger.info('Mounting volume to disable ZTP')
        raw_folder = os.path.join(file_path, "raw")
        os.system(f"rm -rf {raw_folder}")
        os.system(f"mkdir -p {raw_folder}")
        os.system(
            f'guestmount -a {os.path.join(file_path, "hda.qcow2")} -m /dev/sda2 {os.path.join(file_path, "raw")}')
        ztp_file = os.path.join(file_path, 'raw/zerotouch-config')
        with open(ztp_file, 'w', encoding='ascii') as zfile:
            zfile.write('DISABLE=True')
        logger.info('Unmounting volume in {}', file_path)
        os.system("guestunmount {}".format(os.path.join(file_path, 'raw')))
        os.system('rm -rf {}'.format(os.path.join(file_path, 'raw')))
        logger.info("Volume has been successfully unmounted at {}", file_path)
