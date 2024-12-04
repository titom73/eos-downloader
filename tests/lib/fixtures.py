#!/usr/bin/python
# coding: utf-8 -*-
"""Fixtures for tests"""

import pytest
import os
import xml.etree.ElementTree as ET

# Fixtures
@pytest.fixture
def xml_path() -> str:
    """Fixture to provide path to test XML file"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.xml")


@pytest.fixture
def xml_data():
    xml_file = os.path.join(os.path.dirname(__file__), "data.xml")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root
