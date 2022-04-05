#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
import os
import platform
from loguru import logger
import pytest
import eos_downloader
from eos_downloader.eos import EOSDownloader
from eos_downloader.data import DATA_MAPPING
from tests.lib.dataset import eos_dataset_valid, eos_dataset_invalid, eos_token, eos_token_invalid
from tests.lib.fixtures import create_download_instance
from tests.lib.helpers import default_filename


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_valid, ids=['EOS-sha512', 'EOS-md5' ,'vEOS-lab-no-hash'])
@pytest.mark.eos_download
class TestEosDownload_valid():
    def test_data(self, DOWNLOAD_INFO):
        print(str(DOWNLOAD_INFO))

    def test_eos_download_create(self, DOWNLOAD_INFO):
        my_download = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO['image'],
            software=DOWNLOAD_INFO['software'],
            version=DOWNLOAD_INFO['version'],
            token=eos_token,
            hash_method='sha512sum')
        print(my_download)
        assert type(my_download) is eos_downloader.eos.EOSDownloader

    def test_eos_download_repr_string(self, DOWNLOAD_INFO):
        expected = '{} - {} - {}'.format(DOWNLOAD_INFO['software'], DOWNLOAD_INFO['image'], DOWNLOAD_INFO['version'])
        print(self.eos_downloader)
        assert str(self.eos_downloader) == expected

    def test_eos_download_build_filename(self, DOWNLOAD_INFO):
        assert self.eos_downloader._build_filename() == DOWNLOAD_INFO['filename']

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(eos_token == eos_token_invalid, reason="Token is not set correctly")
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Incorrect Hardware")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    @pytest.mark.webtest
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.webtest
    def test_eos_download_get_remote_file_path(self, DOWNLOAD_INFO):
        assert self.eos_downloader._get_remote_filepath() == DOWNLOAD_INFO['remote_path']

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.webtest
    def test_eos_download_get_file_url(self, DOWNLOAD_INFO):
        url = self.eos_downloader._get_url(remote_file_path = DOWNLOAD_INFO['remote_path'])
        print(str(url))
        assert 'https://downloads.arista.com/EOS-USA/Active%20Releases/' in url

@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_invalid, ids=['EOS-FAKE'])
class TestEosDownload_invalid():
    def test_eos_download_login_error(self, DOWNLOAD_INFO):
        my_download = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO['image'],
            software=DOWNLOAD_INFO['software'],
            version=DOWNLOAD_INFO['version'],
            token=eos_token_invalid,
            hash_method=DOWNLOAD_INFO['expected_hash'])
        assert my_download.authenticate() is False

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(eos_token == 'unset_token', reason="Token is not set correctly")
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Incorrect Hardware")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    @pytest.mark.webtest
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    # SOFTWARE/PLATFORM TESTING

    # @pytest.mark.skip(reason="Not yet implemented in lib")
    def test_eos_file_name_with_incorrect_software(self, DOWNLOAD_INFO):
        self.eos_downloader.software = 'EOS_FAKE'
        logger.info('Platform set to: {}'.format(self.eos_downloader.software))
        assert self.eos_downloader._build_filename() is None
        self.eos_downloader.software = DOWNLOAD_INFO['software']

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_get_remote_file_path_for_invlaid_software(self, DOWNLOAD_INFO):
        self.eos_downloader.software = 'EOS_FAKE'
        logger.info('Platform set to: {}'.format(self.eos_downloader.software))
        assert self.eos_downloader.authenticate() is True
        assert self.eos_downloader._get_remote_filepath() is False
        self.eos_downloader.software = DOWNLOAD_INFO['software']

    # IMAGE TESTING

    def test_eos_file_name_with_incorrect_image(self, DOWNLOAD_INFO):
        self.eos_downloader.image = 'EOS_FAKE'
        logger.info('Image set to: {}'.format(self.eos_downloader.image))
        logger.debug('Filename should is:'.format(self.eos_downloader._build_filename()))
        assert self.eos_downloader._build_filename() == default_filename(version=self.eos_downloader.version, info=DOWNLOAD_INFO)
        self.eos_downloader.software = DOWNLOAD_INFO['image']

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_get_remote_file_path_for_invlaid_image(self, DOWNLOAD_INFO):
        self.eos_downloader.image = 'EOS_FAKE'
        logger.info('Image set to: {}'.format(self.eos_downloader.image))
        assert self.eos_downloader.authenticate() is True
        assert default_filename(version=self.eos_downloader.version, info=DOWNLOAD_INFO) in self.eos_downloader._get_remote_filepath()
        self.eos_downloader.image = DOWNLOAD_INFO['image']

    # VERSION TESTING

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_get_remote_file_path_for_invlaid_version(self, DOWNLOAD_INFO):
        self.eos_downloader.version = 'EOS_FAKE'
        logger.info('Version set to: {}'.format(self.eos_downloader.version))
        assert self.eos_downloader._get_remote_filepath() is False
