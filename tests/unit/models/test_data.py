# coding: utf-8 -*-
"""Tests for the eos_downloader.models.data.DataMapping class."""

import pytest
from eos_downloader.models.data import DataMapping, ImageInfo


@pytest.fixture
def data_mapping():
    return DataMapping(
        CloudVision={"ova": ImageInfo(extension=".ova", prepend="cvp", folder_level=0)},
        EOS={
            "64": ImageInfo(extension=".swi", prepend="EOS64", folder_level=0),
            "default": ImageInfo(extension=".swi", prepend="EOS", folder_level=0),
        },
    )


def test_filename_valid_cloudvision(data_mapping):
    result = data_mapping.filename("CloudVision", "ova", "1.2.3")
    assert result == "cvp-1.2.3.ova"


def test_filename_valid_eos(data_mapping):
    result = data_mapping.filename("EOS", "64", "4.28.0F")
    assert result == "EOS64-4.28.0F.swi"


def test_filename_eos_default(data_mapping):
    with pytest.raises(ValueError) as exc_info:
        data_mapping.filename("EOS", "unknown", "4.28.0F")
    assert str(exc_info.value) == "No default configuration found for image type unknown"


def test_filename_invalid_software(data_mapping):
    with pytest.raises(
        ValueError, match="Incorrect value for software InvalidSoftware"
    ):
        data_mapping.filename("InvalidSoftware", "ova", "1.2.3")


def test_filename_invalid_type_no_default(data_mapping):
    with pytest.raises(
        ValueError, match="No default configuration found for image type invalid"
    ):
        data_mapping.filename("CloudVision", "invalid", "1.2.3")
