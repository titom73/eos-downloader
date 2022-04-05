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
from tests.lib.dataset import eos_dataset_valid, eos_token, eos_token_invalid
from tests.lib.fixtures import create_download_instance
from tests.lib.helpers import default_filename


# --------------------------------------------------------------- #
# TEST CASES
# --------------------------------------------------------------- #


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_valid, ids=['EOS-sha512', 'EOS-md5' ,'vEOS-lab-no-hash'])
@pytest.mark.eos_download
class TestEosDownload_valid():
    def test_data(self, DOWNLOAD_INFO):
        print(str(DOWNLOAD_INFO))

    @pytest.mark.dependency(name='authentication')
    @pytest.mark.skipif(eos_token == eos_token_invalid, reason="Token is not set correctly")
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Incorrect Hardware")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    @pytest.mark.webtest
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    @pytest.mark.dependency(depends=["authentication"], scope='class')
    @pytest.mark.webtest
    @pytest.mark.slow
    @pytest.mark.eos_download
    def test_download_local(self, DOWNLOAD_INFO):
        self.eos_downloader.download_local(file_path='.', checksum=DOWNLOAD_INFO['compute_checksum'])

