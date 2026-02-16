# coding: utf-8 -*-
"""Tests for the eos_downloader.models.data.DataMapping class."""

import pytest

from eos_downloader.models.data import DataMapping, ImageInfo, software_mapping


@pytest.fixture
def data_mapping():
    return DataMapping(
        CloudVision={"ova": ImageInfo(extension=".ova", prepend="cvp")},
        EOS={
            "64": ImageInfo(extension=".swi", prepend="EOS64"),
            "default": ImageInfo(extension=".swi", prepend="EOS"),
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
    assert (
        str(exc_info.value) == "No default configuration found for image type unknown"
    )


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


# =============================================================================
# Tests for vEOS64-lab 64-bit formats (Issue #175)
# =============================================================================


class TestVeos64LabFormats:
    """Test suite for vEOS64-lab 64-bit image formats."""

    def test_veos64_lab_vmdk_format(self):
        """Test vEOS64-lab generates correct vmdk filename."""
        result = software_mapping.filename("EOS", "vEOS64-lab", "4.35.1F")
        assert result == "vEOS64-lab-4.35.1F.vmdk"

    def test_veos64_lab_qcow2_format(self):
        """Test vEOS64-lab-qcow2 generates correct qcow2 filename."""
        result = software_mapping.filename("EOS", "vEOS64-lab-qcow2", "4.35.1F")
        assert result == "vEOS64-lab-4.35.1F.qcow2"

    def test_veos64_lab_swi_format(self):
        """Test vEOS64-lab-swi generates correct swi filename."""
        result = software_mapping.filename("EOS", "vEOS64-lab-swi", "4.35.1F")
        assert result == "vEOS64-lab-4.35.1F.swi"

    def test_veos64_lab_with_maintenance_release(self):
        """Test vEOS64-lab with M release type."""
        result = software_mapping.filename("EOS", "vEOS64-lab", "4.32.3M")
        assert result == "vEOS64-lab-4.32.3M.vmdk"

    def test_veos64_lab_qcow2_with_maintenance_release(self):
        """Test vEOS64-lab-qcow2 with M release type."""
        result = software_mapping.filename("EOS", "vEOS64-lab-qcow2", "4.32.3M")
        assert result == "vEOS64-lab-4.32.3M.qcow2"

    def test_veos64_formats_in_mapping(self):
        """Test that all vEOS64 formats are present in the mapping."""
        eos_formats = software_mapping.EOS.keys()
        assert "vEOS64-lab" in eos_formats
        assert "vEOS64-lab-qcow2" in eos_formats
        assert "vEOS64-lab-swi" in eos_formats
