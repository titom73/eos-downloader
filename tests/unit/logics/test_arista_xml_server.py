#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import sys
import os
import pytest
from loguru import logger
from unittest.mock import patch, MagicMock, Mock
from eos_downloader.models.version import EosVersion, CvpVersion
from eos_downloader.logics.arista_xml_server import (
    AristaXmlBase,
    AristaXmlObject,
    EosXmlObject,
    CvpXmlObject,
    AristaXmlQuerier,
)
import xml.etree.ElementTree as ET


# Fixtures
@pytest.fixture
def xml_path() -> str:
    """Fixture to provide path to test XML file"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "../data.xml")


@pytest.fixture
def xml_data():
    xml_file = os.path.join(os.path.dirname(__file__), "../data.xml")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root


# ------------------- #
# Tests AristaXmlBase
# ------------------- #
def test_arista_xml_base_initialization(xml_path):
    arista_xml_base = AristaXmlBase(xml_path=str(xml_path))
    assert (
        arista_xml_base.xml_data.getroot().tag == "cvpFolderList"
    ), f"Root tag should be 'cvpFolderList' but got"


# ---------------------- #
# Tests AristaXmlQuerier
# ---------------------- #

# ---------------------- #
# Tests AristaXmlQuerier available_public_versions for eos


def test_AristaXmlQuerier_available_public_versions_eos(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos")
    assert len(versions) == 309, "Incorrect number of versions"
    assert versions[0] == EosVersion().from_str(
        "4.33.0F"
    ), "First version should be 4.33.0F - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_f_release(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", rtype="F")
    assert (
        len(versions) == 95
    ), "Incorrect number of versions: got {len(versions)} expected 207"
    assert versions[0] == EosVersion().from_str(
        "4.33.0F"
    ), "First version should be 4.33.0F - got {len(versions)}"


def test_AristaXmlQuerier_available_public_versions_eos_m_release(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", rtype="M")
    assert (
        len(versions) == 207
    ), "Incorrect number of versions: got {len(versions)} expected 207"
    assert versions[0] == EosVersion().from_str(
        "4.32.3M"
    ), "First version should be 4.32.3M - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", branch="4.29")
    assert len(versions) == 34, "Incorrect number of versions"
    for version in versions:
        # logging.debug(f"Checking version {version}")
        assert version.is_in_branch("4.29"), f"Version {version} is not in branch 4.29"
    assert versions[0] == EosVersion().from_str(
        "4.29.10M"
    ), "First version should be 4.29.10M - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_f_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(
        package="eos", rtype="F", branch="4.29"
    )
    assert len(versions) == 6, "Incorrect number of versions - expected 6"
    for version in versions:
        # logging.debug(f"Checking version {version}")
        assert version.is_in_branch("4.29"), f"Version {version} is not in branch 4.29"
    assert versions[0] == EosVersion().from_str(
        "4.29.2F"
    ), "First version should be 4.29.2F - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_m_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(
        package="eos", rtype="M", branch="4.29"
    )
    assert len(versions) == 28, "Incorrect number of versions - expected 28"
    for version in versions:
        # logging.debug(f"Checking version {version}")
        assert version.is_in_branch("4.29"), f"Version {version} is not in branch 4.29"
    assert versions[0] == EosVersion().from_str(
        "4.29.10M"
    ), "First version should be 4.29.10M - got {versions[0]}"


# ---------------------- #
# Tests AristaXmlQuerier available_public_versions for cvp


def test_AristaXmlQuerier_available_public_versions_cvp(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="cvp")
    assert (
        len(versions) == 12
    ), "Incorrect number of versions: got {len(versions)} expected 12"
    assert versions[0] == CvpVersion().from_str(
        "2024.3.0"
    ), "First version should be 2024.3.0 - got {versions[0]}"


# ---------------------- #
# Tests AristaXmlQuerier branches for eos


def test_AristaXmlQuerier_branch_eos(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.branches(package="eos")
    assert (
        len(versions) == 14
    ), "Incorrect number of branches, got {len(versions)} expected 14"
    assert (
        EosVersion().from_str("4.33.0F").branch in versions
    ), "4.33 should be in branches {versions}"


def test_AristaXmlQuerier_branch_eos_latest(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.branches(package="eos", latest=True)
    assert (
        len(versions) == 1
    ), "Incorrect number of branches, got {len(versions)} expected 1"
    assert (
        EosVersion().from_str("4.33.0F").branch in versions
    ), "4.33 should be in branches {versions}"


# ---------------------- #
# Tests AristaXmlQuerier branches for cvp


def test_AristaXmlQuerier_branch_cvp(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.branches(package="cvp")
    assert (
        len(versions) == 5
    ), "Incorrect number of branches, got {len(versions)} expected 5"
    assert (
        CvpVersion().from_str("2024.3.0").branch in versions
    ), "2024.3 should be in branches {versions}"


def test_AristaXmlQuerier_branch_cvp_latest(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.branches(package="cvp", latest=True)
    assert (
        len(versions) == 1
    ), "Incorrect number of branches, got {len(versions)} expected 1"
    assert (
        CvpVersion().from_str("2024.3.0").branch in versions
    ), "2024.3 should be in branches {versions}"


# ---------------------- #
# Tests AristaXmlQuerier latest for eos


def test_AristaXmlQuerier_latest_eos(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="eos")
    assert (
        EosVersion().from_str("4.33.0F") == versions
    ), "4.33.0F should be the latest, got {versions}"


def test_AristaXmlQuerier_latest_eos_f_release(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="eos", rtype="F")
    assert (
        EosVersion().from_str("4.33.0F") == versions
    ), "4.33.0F should be the latest, got {versions}"


def test_AristaXmlQuerier_latest_eos_m_release(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="eos", rtype="M")
    assert (
        EosVersion().from_str("4.32.3M") == versions
    ), "4.32.3M should be the latest, got {versions}"


def test_AristaXmlQuerier_latest_eos_f_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="eos", rtype="F", branch="4.29")
    assert (
        EosVersion().from_str("4.29.2F") == versions
    ), "4.29.2F should be the latest, got {versions}"


def test_AristaXmlQuerier_latest_eos_m_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="eos", rtype="M", branch="4.29")
    assert (
        EosVersion().from_str("4.29.10M") == versions
    ), "4.29.10M should be the latest, got {versions}"


# ---------------------- #
# Tests AristaXmlQuerier latest for cvp


def test_AristaXmlQuerier_latest_cvp(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="cvp")
    assert (
        CvpVersion().from_str("2024.3.0") == versions
    ), "2024.3.0 should be the latest, got {versions}"


def test_AristaXmlQuerier_latest_cvp(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.latest(package="cvp", branch="2024.2")
    assert (
        CvpVersion().from_str("2024.2.1") == versions
    ), "2024.2.1 should be the latest, got {versions}"


# ---------------------- #
# Tests AristaXmlObject
# ---------------------- #


def test_arista_xml_object_initialization(xml_path):
    arista_xml_object = AristaXmlObject(
        searched_version="4.29.2F", image_type="image", xml_path=xml_path
    )
    assert arista_xml_object.search_version == "4.29.2F", "Incorrect search version"
    assert arista_xml_object.image_type == "image", "Incorrect image type"


def test_arista_xml_object_filename_for_ceos(xml_path):
    arista_xml_object = EosXmlObject(
        searched_version="4.29.2F",
        image_type="cEOS",
        xml_path=xml_path,
    )
    filename = arista_xml_object.filename
    assert filename == "cEOS-lab-4.29.2F.tar.xz", f"Incorrect filename, got {filename}"


def test_arista_xml_object_hashfile(xml_path):
    arista_xml_object = EosXmlObject(
        searched_version="4.29.2F",
        image_type="cEOS",
        xml_path=xml_path,
    )
    hashfile = arista_xml_object.hash_filename()
    assert (
        hashfile == "cEOS-lab-4.29.2F.tar.xz.sha512sum"
    ), f"Incorrect hashfile, got {hashfile}"
    hashfile = arista_xml_object.hash_filename()
    assert (
        hashfile == "cEOS-lab-4.29.2F.tar.xz.sha512sum"
    ), f"Incorrect hashfile, got {hashfile}"


def test_arista_xml_object_path_from_xml(xml_path):
    arista_xml_object = EosXmlObject(
        searched_version="4.29.2F",
        image_type="cEOS",
        xml_path=xml_path,
    )
    path = arista_xml_object.path_from_xml(search_file="EOS-4.29.2F.swi")
    assert (
        path
        == "/support/download/EOS-USA/Active Releases/4.29/EOS-4.29.2F/EOS-4.29.2F.swi"
    ), f"Incorrect path, got {path}"


def test_arista_xml_object_url(xml_path):
    with patch(
        "eos_downloader.logics.arista_xml_server.AristaXmlObject._url"
    ) as mock_url:
        mock_url.return_value = "https://testserver.com/path/to/EOS-4.29.2F.swi"
        arista_xml_object = EosXmlObject(
            searched_version="4.29.2F",
            image_type="cEOS",
            xml_path=xml_path,
        )
        url = arista_xml_object._url(xml_path="/path/to/EOS-4.29.2F.swi")
        assert (
            url == "https://testserver.com/path/to/EOS-4.29.2F.swi"
        ), f"Incorrect URL, got {url}"


def test_arista_xml_object_urls(xml_path):
    with patch(
        "eos_downloader.logics.arista_xml_server.AristaXmlObject._url"
    ) as mock_url:
        mock_url.side_effect = [
            "https://arista.com/path/to/EOS-4.29.2F.swi",
            "https://arista.com/path/to/EOS-4.29.2F.swi.sha512sum",
        ]
        arista_xml_object = EosXmlObject(
            searched_version="4.29.2F",
            image_type="default",
            xml_path=xml_path,
        )
        urls = arista_xml_object.urls
        logger.warning(f"URLs are: {urls}")
        expected_urls = {
            "image": "https://arista.com/path/to/EOS-4.29.2F.swi",
            "sha512sum": "https://arista.com/path/to/EOS-4.29.2F.swi.sha512sum",
        }
        assert urls == expected_urls, f"Incorrect URLs, got {urls}"


def test_arista_xml_object_urls_with_invalid_hash(xml_path):
    with patch(
        "eos_downloader.logics.arista_xml_server.AristaXmlObject._url"
    ) as mock_url:
        mock_url.side_effect = [
            "https://arista.com/path/to/EOS-4.29.2F.swi",
            "https://arista.com/path/to/EOS-4.29.2F.swi.sha512sum",
        ]
        arista_xml_object = EosXmlObject(
            searched_version="4.29.2F",
            image_type="default",
            xml_path=xml_path,
        )
        urls = arista_xml_object.urls
        expected_urls = {
            "image": "https://arista.com/path/to/EOS-4.29.2F.swi",
            "sha512sum": "https://arista.com/path/to/EOS-4.29.2F.swi.sha512sum",
        }
        assert urls == expected_urls, f"Incorrect URLs, got {urls}"


def test_arista_xml_object_urls_with_missing_files(xml_path):
    with patch(
        "eos_downloader.logics.arista_xml_server.AristaXmlObject._url"
    ) as mock_url:
        mock_url.side_effect = [None, None, None]
        arista_xml_object = EosXmlObject(
            searched_version="4.29.2F",
            image_type="default",
            xml_path=xml_path,
        )
        urls = arista_xml_object.urls
        expected_urls = {"image": None, "sha512sum": None}
        assert urls == expected_urls, f"Incorrect URLs, got {urls}"


# ---------------------- #
# Tests for error paths and edge cases
# ---------------------- #


class TestAristaXmlBaseErrorPaths:
    """Test error paths in AristaXmlBase.__init__."""

    def test_xml_parse_error(self, tmp_path):
        """Test XML parse error with invalid XML file (lines 54-55)."""
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("this is not valid xml <<<<")

        # Should not raise, but xml_data won't be set
        base = AristaXmlBase(xml_path=str(invalid_xml))
        # The object is created but xml_data may not be set
        assert not hasattr(base, "xml_data") or base.xml_data is not None

    @patch("eos_downloader.logics.arista_server.AristaServer.authenticate")
    def test_authenticate_returns_false(self, mock_auth):
        """Test ValueError when authenticate fails (lines 68-70)."""
        mock_auth.return_value = False

        with pytest.raises(ValueError, match="Unable to authenticate"):
            AristaXmlBase(token="bad-token")

    @patch("eos_downloader.logics.arista_server.AristaServer.authenticate")
    @patch("eos_downloader.logics.arista_server.AristaServer.get_xml_data")
    def test_get_xml_root_returns_none(self, mock_get_xml, mock_auth):
        """Test ValueError when _get_xml_root returns None (lines 59-61)."""
        mock_auth.return_value = True
        mock_get_xml.return_value = None

        with pytest.raises(ValueError, match="Unable to get XML data"):
            AristaXmlBase(token="test-token")

    @patch("eos_downloader.logics.arista_server.AristaServer.authenticate")
    @patch("eos_downloader.logics.arista_server.AristaServer.get_xml_data")
    def test_xml_no_root_element(self, mock_get_xml, mock_auth):
        """Test ValueError when XML has no root element (lines 63-65)."""
        mock_auth.return_value = True
        mock_tree = MagicMock(spec=ET.ElementTree)
        mock_tree.getroot.return_value = None
        mock_get_xml.return_value = mock_tree

        with pytest.raises(ValueError, match="XML data has no root element"):
            AristaXmlBase(token="test-token")

    @patch("eos_downloader.logics.arista_server.AristaServer.authenticate")
    @patch("eos_downloader.logics.arista_server.AristaServer.get_xml_data")
    def test_get_xml_root_exception(self, mock_get_xml, mock_auth):
        """Test _get_xml_root returns None on exception (lines 84-86)."""
        mock_auth.return_value = True
        mock_get_xml.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Unable to get XML data"):
            AristaXmlBase(token="test-token")


class TestAristaXmlQuerierErrorPaths:
    """Test error paths in AristaXmlQuerier."""

    def test_available_public_versions_invalid_rtype(self, xml_path):
        """Test ValueError for invalid rtype (line 140)."""
        querier = AristaXmlQuerier(xml_path=xml_path)

        with pytest.raises(ValueError, match="Invalid release type"):
            querier.available_public_versions(package="eos", rtype="INVALID")

    def test_latest_invalid_rtype(self, xml_path):
        """Test latest raises ValueError for invalid rtype (line 199)."""
        querier = AristaXmlQuerier(xml_path=xml_path)

        with pytest.raises(ValueError, match="Invalid release type"):
            querier.latest(package="eos", rtype="INVALID")

    def test_latest_no_versions_found(self, xml_path):
        """Test latest raises ValueError when no versions match (line 207)."""
        querier = AristaXmlQuerier(xml_path=xml_path)

        with pytest.raises(ValueError, match="No versions found"):
            querier.latest(package="eos", branch="99.99", rtype="F")


class TestAristaXmlObjectErrorPaths:
    """Test error paths in AristaXmlObject."""

    def test_filename_value_error(self, xml_path):
        """Test filename returns None on ValueError (lines 323-325)."""
        obj = EosXmlObject(
            searched_version="4.29.2F",
            image_type="INVALID_TYPE",
            xml_path=xml_path,
        )
        # Invalid image type should make software_mapping.filename raise ValueError
        result = obj.filename
        assert result is None

    def test_hash_filename_returns_none_when_filename_none(self, xml_path):
        """Test hash_filename returns None when filename is None (line 341)."""
        obj = EosXmlObject(
            searched_version="4.29.2F",
            image_type="INVALID_TYPE",
            xml_path=xml_path,
        )
        # Since filename returns None for invalid type
        result = obj.hash_filename()
        assert result is None

    def test_urls_filename_none_raises(self, xml_path):
        """Test urls raises ValueError when filename is None (line 413)."""
        obj = EosXmlObject(
            searched_version="4.29.2F",
            image_type="INVALID_TYPE",
            xml_path=xml_path,
        )
        with pytest.raises(ValueError, match="Filename not found"):
            _ = obj.urls

    def test_url_calls_server_get_url(self, xml_path):
        """Test _url method calls server.get_url (lines 386-388)."""
        obj = EosXmlObject(
            searched_version="4.29.2F",
            image_type="cEOS",
            xml_path=xml_path,
        )
        with patch.object(obj.server, "get_url", return_value="https://example.com/file") as mock_get_url:
            result = obj._url("/path/to/file")
            assert result == "https://example.com/file"
            mock_get_url.assert_called_once_with("/path/to/file")


class TestCvpXmlObjectInit:
    """Test CvpXmlObject initialization (lines 526-532)."""

    def test_cvp_xml_object_init(self, xml_path):
        """Test CvpXmlObject initializes correctly with CVP version."""
        obj = CvpXmlObject(
            searched_version="2024.3.0",
            image_type="ova",
            xml_path=xml_path,
        )
        assert obj.search_version == "2024.3.0"
        assert obj.image_type == "ova"
        assert str(obj.version) == "2024.3.0"
        assert obj.software == "CloudVision"
