#!/usr/bin/python
# coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import sys
import os
import pytest
from loguru import logger
from eos_downloader.logics.arista_server import AristaXmlQuerier
from eos_downloader.models.version import EosVersion
import xml.etree.ElementTree as ET

logger.remove()
logger.add(sys.stderr, level="DEBUG")

# Fixtures
@pytest.fixture
def test_xml_path():
    """Fixture to provide path to test XML file"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../data.xml')

@pytest.fixture
def xml_querier(test_xml_path):
    """Fixture to provide an initialized AristaXmlQuerier"""
    return AristaXmlQuerier(xml_file=test_xml_path)

@pytest.fixture
def test_version():
    """Fixture to provide a test EOS version"""
    return EosVersion.from_str("4.28.3M")

@pytest.fixture
def xml_data():
    xml_file = os.path.join(os.path.dirname(__file__), "../../data.xml")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root

# Tests
def test_xml_root_tag(xml_data):
    assert (
        xml_data.tag == "cvpFolderList"
    ), f"Root tag should be 'expected_root_tag' but got {xml_data.tag}"


def test_xml_child_count(xml_data):
    expected_count = 4  # replace with the expected number of children
    assert (
        len(xml_data) == expected_count
    ), f"Expected {expected_count} children but got {len(xml_data)}"


def test_xml_specific_element(xml_data):
    element = xml_data.find("file")
    assert element is not None, "file should be present in the XML"


def test_xml_querier_initialization(test_xml_path):
    """Test basic initialization of AristaXmlQuerier"""
    querier = AristaXmlQuerier(xml_file=test_xml_path)
    assert querier is not None
    assert os.path.exists(querier.xml_file)

def test_xml_querier_invalid_file():
    """Test initialization with invalid XML file"""
    with pytest.raises(FileNotFoundError):
        AristaXmlQuerier(xml_file="nonexistent.xml")

def test_get_software_list(xml_querier):
    """Test getting software list from XML"""
    software_list = xml_querier.get_software_list()
    assert isinstance(software_list, list)
    assert len(software_list) > 0
    assert all('version' in item for item in software_list)

def test_get_software_by_version(xml_querier, test_version):
    """Test getting specific software version"""
    software = xml_querier.get_software_by_version(test_version)
    assert software is not None
    assert software.get('version') == str(test_version)

def test_get_software_by_invalid_version(xml_querier):
    """Test getting non-existent software version"""
    invalid_version = EosVersion.from_str("4.99.9F")
    software = xml_querier.get_software_by_version(invalid_version)
    assert software is None

def test_get_software_by_branch(xml_querier):
    """Test getting software by branch"""
    branch = "4.28"
    software_list = xml_querier.get_software_by_branch(branch)
    assert isinstance(software_list, list)
    assert all('version' in item for item in software_list)
    assert all(item['version'].startswith(branch) for item in software_list)

def test_get_software_by_invalid_branch(xml_querier):
    """Test getting software from non-existent branch"""
    software_list = xml_querier.get_software_by_branch("9.99")
    assert isinstance(software_list, list)
    assert len(software_list) == 0

def test_get_latest_software_in_branch(xml_querier):
    """Test getting latest software in a branch"""
    branch = "4.28"
    latest = xml_querier.get_latest_software_in_branch(branch)
    assert latest is not None
    assert latest['version'].startswith(branch)

def test_get_latest_software_in_invalid_branch(xml_querier):
    """Test getting latest software from non-existent branch"""
    latest = xml_querier.get_latest_software_in_branch("9.99")
    assert latest is None
