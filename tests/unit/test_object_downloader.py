#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

# import platform
import sys

import pytest
from loguru import logger

import eos_downloader
from eos_downloader.data import DATA_MAPPING
from eos_downloader.eos import EOSDownloader
from tests.lib.dataset import (
    eos_dataset_invalid,
    eos_dataset_valid,
    eos_token,
    eos_token_invalid,
)
from tests.lib.fixtures import create_download_instance
from tests.lib.helpers import default_filename, is_on_github_actions

logger.remove()
logger.add(sys.stderr, level="DEBUG")


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize(
    "DOWNLOAD_INFO",
    eos_dataset_valid,
    ids=["EOS-sha512", "EOS-md5", "vEOS-lab-no-hash"],
)
@pytest.mark.eos_download
class TestEosDownload_valid:
    def test_data(self, DOWNLOAD_INFO):
        logger.info(f"test input: {DOWNLOAD_INFO}")
        logger.info(f"test build: {self.eos_downloader.__dict__}")

    def test_eos_download_create(self, DOWNLOAD_INFO):
        my_download = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO["image"],
            software=DOWNLOAD_INFO["software"],
            version=DOWNLOAD_INFO["version"],
            token=eos_token,
            hash_method="sha512sum",
        )
        logger.info(my_download)
        assert isinstance(my_download, eos_downloader.eos.EOSDownloader)

    def test_eos_download_repr_string(self, DOWNLOAD_INFO):
        expected = f"{DOWNLOAD_INFO['software']} - {DOWNLOAD_INFO['image']} - {DOWNLOAD_INFO['version']}"
        logger.info(self.eos_downloader)
        assert str(self.eos_downloader) == expected

    def test_eos_download_build_filename(self, DOWNLOAD_INFO):
        assert self.eos_downloader._build_filename() == DOWNLOAD_INFO["filename"]

    @pytest.mark.dependency(name="authentication")
    @pytest.mark.skipif(
        eos_token == eos_token_invalid, reason="Token is not set correctly"
    )
    @pytest.mark.skipif(is_on_github_actions(), reason="Running on Github Runner")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    @pytest.mark.webtest
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    @pytest.mark.dependency(depends=["authentication"], scope="class")
    @pytest.mark.webtest
    def test_eos_download_get_remote_file_path(self, DOWNLOAD_INFO):
        assert (
            self.eos_downloader._get_remote_filepath() == DOWNLOAD_INFO["remote_path"]
        )

    @pytest.mark.dependency(depends=["authentication"], scope="class")
    @pytest.mark.webtest
    def test_eos_download_get_file_url(self, DOWNLOAD_INFO):
        url = self.eos_downloader._get_url(
            remote_file_path=DOWNLOAD_INFO["remote_path"]
        )
        logger.info(url)
        assert "https://downloads.arista.com/EOS-USA/Active%20Releases/" in url


@pytest.mark.usefixtures("create_download_instance")
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_invalid, ids=["EOS-FAKE"])
class TestEosDownload_invalid:
    def test_data(self, DOWNLOAD_INFO):
        logger.info(f"test input: {dict(DOWNLOAD_INFO)}")
        logger.info(f"test build: {self.eos_downloader.__dict__}")

    def test_eos_download_login_error(self, DOWNLOAD_INFO):
        my_download = eos_downloader.eos.EOSDownloader(
            image=DOWNLOAD_INFO["image"],
            software=DOWNLOAD_INFO["software"],
            version=DOWNLOAD_INFO["version"],
            token=eos_token_invalid,
            hash_method=DOWNLOAD_INFO["expected_hash"],
        )
        assert my_download.authenticate() is False

    @pytest.mark.dependency(name="authentication")
    @pytest.mark.skipif(
        eos_token == eos_token_invalid, reason="Token is not set correctly"
    )
    @pytest.mark.skipif(is_on_github_actions(), reason="Running on Github Runner")
    # @pytest.mark.xfail(reason="Deliberate - CI not set for testing AUTH")
    @pytest.mark.webtest
    def test_eos_download_authenticate(self):
        assert self.eos_downloader.authenticate() is True

    # SOFTWARE/PLATFORM TESTING

    # @pytest.mark.skip(reason="Not yet implemented in lib")
    def test_eos_file_name_with_incorrect_software(self, DOWNLOAD_INFO):
        self.eos_downloader.software = "FAKE"
        logger.info(f"test build: {self.eos_downloader.__dict__}")
        with pytest.raises(ValueError) as e_info:
            result = self.eos_downloader._build_filename()
            logger.info(f"receive exception: {e_info}")
            self.eos_downloader.software = DOWNLOAD_INFO["software"]

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope="class")
    def test_eos_download_get_remote_file_path_for_invlaid_software(
        self, DOWNLOAD_INFO
    ):
        self.eos_downloader.software = "FAKE"
        logger.info(f"Platform set to: {self.eos_downloader.software}")
        logger.info(f"test build: {self.eos_downloader.__dict__}")
        with pytest.raises(ValueError) as e_info:
            result = self.eos_downloader._build_filename()
            logger.info(f"receive exception: {e_info}")
        self.eos_downloader.software = DOWNLOAD_INFO["software"]

    # IMAGE TESTING

    def test_eos_file_name_with_incorrect_image(self, DOWNLOAD_INFO):
        self.eos_downloader.image = "FAKE"
        logger.info(f"Image set to: {self.eos_downloader.image}")
        assert DOWNLOAD_INFO["filename"] == self.eos_downloader._build_filename()
        self.eos_downloader.software == DOWNLOAD_INFO["image"]

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope="class")
    def test_eos_download_get_remote_file_path_for_invlaid_image(self, DOWNLOAD_INFO):
        self.eos_downloader.image = "FAKE"
        logger.info(f"Image set to: {self.eos_downloader.image}")
        assert self.eos_downloader.authenticate() is True
        assert DOWNLOAD_INFO["filename"] == self.eos_downloader._build_filename()
        self.eos_downloader.image = DOWNLOAD_INFO["image"]

    # VERSION TESTING

    @pytest.mark.webtest
    @pytest.mark.dependency(depends=["authentication"], scope="class")
    def test_eos_download_get_remote_file_path_for_invlaid_version(self, DOWNLOAD_INFO):
        self.eos_downloader.version = "FAKE"
        logger.info(f"Version set to: {self.eos_downloader.version}")
        assert self.eos_downloader._get_remote_filepath() == ""
