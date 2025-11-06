# coding: utf-8 -*-
"""Tests for the eos_downloader.models.version module."""

import sys
import pytest
from loguru import logger
from eos_downloader.models.version import SemVer, EosVersion, CvpVersion

logger.remove()
logger.add(sys.stderr, level="DEBUG")


def test_semver_from_str():
    version = SemVer.from_str("4.23.3M")
    assert version.major == 4
    assert version.minor == 23
    assert version.patch == 3
    assert version.rtype == "M"


def test_semver_str():
    version = SemVer(major=4, minor=23, patch=3, rtype="M")
    assert str(version) == "4.23.3M"


def test_semver_branch():
    version = SemVer(major=4, minor=23, patch=3, rtype="M")
    assert version.branch == "4.23"


def test_semver_comparison():
    version1 = SemVer(major=4, minor=23, patch=3, rtype="M")
    version2 = SemVer.from_str("4.24.1F")
    assert version1 < version2
    assert version1 != version2
    assert version2 > version1
    assert version1 <= version2
    assert version2 >= version1


def test_semver_match():
    version = SemVer.from_str("4.23.3M")
    assert version.match("<=4.23.3M")
    assert not version.match("==4.24.0F")


def test_semver_is_in_branch():
    version = SemVer.from_str("4.23.3M")
    assert version.is_in_branch("4.23")
    assert not version.is_in_branch("4.24")


def test_eosversion_from_str():
    version = EosVersion.from_str("4.32.1F")
    assert version.major == 4
    assert version.minor == 32
    assert version.patch == 1
    assert version.rtype == "F"


def test_cvpversion_from_str():
    version = CvpVersion.from_str("2024.1.0")
    assert version.major == 2024
    assert version.minor == 1
    assert version.patch == 0
    assert version.rtype is None


def test_semver_invalid_str():
    version = SemVer.from_str("invalid.version")
    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 0
    assert version.rtype is None


def test_semver_compare_invalid_type():
    version = SemVer(major=4, minor=23, patch=3, rtype="M")
    with pytest.raises(ValueError):
        version._compare("invalid")


def test_eosversion_invalid_str():
    version = EosVersion.from_str("invalid.version")
    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 0
    assert version.rtype is None


def test_cvpversion_invalid_str():
    version = CvpVersion.from_str("invalid.version")
    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 0
    assert version.rtype is None


def test_semver_match_invalid_operator():
    version = SemVer.from_str("4.23.3M")
    with pytest.raises(ValueError):
        version.match("+=4.23.3M")


def test_semver_is_in_branch_invalid():
    version = SemVer.from_str("4.23.3M")
    assert not version.is_in_branch("invalid.branch")


def test_semver_compare_none():
    version1 = SemVer(major=4, minor=23, patch=3, rtype="M")
    version2 = SemVer(major=4, minor=23, patch=3, rtype=None)
    assert version1._compare(version2) == 0
