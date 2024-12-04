#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import sys
import os
import pytest
from loguru import logger
from eos_downloader.logics.arista_server import AristaXmlQuerier
from eos_downloader.models.version import EosVersion, CvpVersion
from eos_downloader.logics.arista_server import AristaXmlBase
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


logger.remove()
logger.add(sys.stderr, level="DEBUG")

# ------------------- #
# Tests AristaXmlBase
# ------------------- #
def test_arista_xml_base_initialization(xml_path):
    arista_xml_base = AristaXmlBase(xml_path=str(xml_path))
    assert arista_xml_base.xml_data.getroot().tag == "cvpFolderList", (
        f"Root tag should be 'cvpFolderList' but got"
    )

# ---------------------- #
# Tests AristaXmlQuerier
# ---------------------- #

# ---------------------- #
# Tests AristaXmlQuerier available_public_versions for eos

def test_AristaXmlQuerier_available_public_versions_eos(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos")
    assert len(versions) == 309, "Incorrect number of versions"
    assert versions[0] == EosVersion().from_str("4.33.0F"), "First version should be 4.33.0F - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_f_release(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", rtype="F")
    assert len(versions) == 95, "Incorrect number of versions: got {len(versions)} expected 207"
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
        # logger.debug(f"Checking version {version}")
        assert version.is_in_branch("4.29"), f"Version {version} is not in branch 4.29"
    assert versions[0] == EosVersion().from_str("4.29.10M"), "First version should be 4.29.10M - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_f_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", rtype="F", branch="4.29")
    assert len(versions) == 6, "Incorrect number of versions - expected 6"
    for version in versions:
        # logger.debug(f"Checking version {version}")
        assert version.is_in_branch("4.29"), f"Version {version} is not in branch 4.29"
    assert versions[0] == EosVersion().from_str(
        "4.29.2F"
    ), "First version should be 4.29.2F - got {versions[0]}"


def test_AristaXmlQuerier_available_public_versions_eos_m_release_branch_4_29(xml_path):
    xml_querier = AristaXmlQuerier(xml_path=xml_path)
    versions = xml_querier.available_public_versions(package="eos", rtype="M", branch="4.29")
    assert len(versions) == 28, "Incorrect number of versions - expected 28"
    for version in versions:
        # logger.debug(f"Checking version {version}")
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
    assert len(versions) == 14, "Incorrect number of branches, got {len(versions)} expected 14"
    assert EosVersion().from_str("4.33.0F").branch in versions, "4.33 should be in branches {versions}"


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
