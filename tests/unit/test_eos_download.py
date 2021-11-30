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


# Get Auth token
eos_token = os.getenv('ARISTA_TOKEN', 'unset_token')
eos_token_invalid = 'invalid_token'

# --------------------------------------------------------------- #
# MOOCK data to use for testing
# --------------------------------------------------------------- #

eos_dataset_valid = [
    {
        'image': 'EOS',
        'version': '4.26.3M',
        'software': 'EOS',
        'filename': 'EOS-4.26.3M.swi',
        'expected_hash': 'sha512sum',
        'remote_path': '/support/download/EOS-USA/Active Releases/4.26/EOS-4.26.3M/EOS-4.26.3M.swi',
        'compute_checksum': True
    },
    {
        'image': 'EOS',
        'version': '4.25.6M',
        'software': 'EOS',
        'filename': 'EOS-4.25.6M.swi',
        'expected_hash': 'md5sum',
        'remote_path': '/support/download/EOS-USA/Active Releases/4.25/EOS-4.25.6M/EOS-4.25.6M.swi',
        'compute_checksum': True
    },
    {
        'image': 'vEOS-lab',
        'version': '4.25.6M',
        'software': 'EOS',
        'filename': 'vEOS-lab-4.25.6M.vmdk',
        'expected_hash': 'md5sum',
        'remote_path': '/support/download/EOS-USA/Active Releases/4.25/EOS-4.25.6M/vEOS-lab/vEOS-lab-4.25.6M.vmdk',
        'compute_checksum': False
    }
]

eos_dataset_invalid = [
    {
        'image': 'EOS',
        'version': '4.26.3M',
        'software': 'EOS',
        'filename': 'EOS-4.26.3M.swi',
        'expected_hash': 'sha512sum',
        'remote_path': '/support/download/EOS-USA/Active Releases/4.26/EOS-4.26.3M/EOS-4.26.3M.swi',
        'compute_checksum': True
    }
]

# --------------------------------------------------------------- #
# HELPERS
# --------------------------------------------------------------- #


def default_filename(version: str, info):
    """
    default_filename Helper to build default filename

    Parameters
    ----------
    version : str
        EOS version
    info : dict
        TEST Inputs

    Returns
    -------
    str
        Filename
    """
    if version is None or info is None:
        return None
    return DATA_MAPPING[info['software']]['default']['prepend'] + '-' + version + '.swi'


# --------------------------------------------------------------- #
# FIXTURES
# --------------------------------------------------------------- #


@pytest.fixture
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_valid)
def create_download_instance(request, DOWNLOAD_INFO):
    # logger.info("Execute fixture to create class elements")
    request.cls.eos_downloader = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO['image'],
            software=DOWNLOAD_INFO['software'],
            version=DOWNLOAD_INFO['version'],
            token=eos_token,
            hash_method='sha512sum')
    yield
    # logger.info('Cleanup test environment')
    os.system('rm -f {}*'.format(DOWNLOAD_INFO['filename']))


# --------------------------------------------------------------- #
# TEST CASES
# --------------------------------------------------------------- #


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_valid, ids=['EOS-sha512', 'EOS-md5' ,'vEOS-lab-no-hash'])
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
        assert str(self.eos_downloader) == expected

    def test_eos_download_build_filename(self, DOWNLOAD_INFO):
        assert self.eos_downloader._build_filename() == DOWNLOAD_INFO['filename']

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(eos_token == 'unset_token', reason="Token is not set correctly")
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

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.slow
    def test_eos_download_dl_local(self, DOWNLOAD_INFO):
        assert self.eos_downloader.download_local(file_path='.', checksum=DOWNLOAD_INFO['compute_checksum']) is DOWNLOAD_INFO['compute_checksum']


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
