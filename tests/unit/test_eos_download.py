#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
import sys
import os
import platform
import logging
import pytest
import eos_downloader
from eos_downloader.eos import EOSDownloader

# Get Auth token
eos_token = os.getenv('ARISTA_TOKEN', 'unset_token')

# Moock data to use for testing
eos_data = [
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

# Parametrize data
def generate_dict(eos_data = eos_data):
    for v in eos_data:
        return v


@pytest.fixture
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_data)
def create_download_instance(request, DOWNLOAD_INFO):
    logging.info("Execute fixture to create class elements")
    request.cls.eos_downloader = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO['image'],
            software=DOWNLOAD_INFO['software'],
            version=DOWNLOAD_INFO['version'],
            token=eos_token,
            hash_method='sha512sum')
    yield
    logging.info('Cleanup test environment')
    os.system('rm -f {}*'.format(DOWNLOAD_INFO['filename']))


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_data, ids=['EOS-sha512', 'EOS-md5' ,'vEOS-lab-no-hash'])
class TestEosDownload_Valid():
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
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Not Macos Laptop")
    @pytest.mark.skipif(eos_token == 'unset_token', reason="Token is not set correctly")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_get_remote_file_path(self, DOWNLOAD_INFO):
        assert self.eos_downloader._get_remote_filepath() == DOWNLOAD_INFO['remote_path']

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_get_file_url(self, DOWNLOAD_INFO):
        url = self.eos_downloader._get_url(remote_file_path = DOWNLOAD_INFO['remote_path'])
        print(str(url))
        assert 'https://downloads.arista.com/EOS-USA/Active%20Releases/' in url

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    def test_eos_download_dl_local(self, DOWNLOAD_INFO):
        assert self.eos_downloader.download_local(file_path='.', checksum=DOWNLOAD_INFO['compute_checksum']) is DOWNLOAD_INFO['compute_checksum']
