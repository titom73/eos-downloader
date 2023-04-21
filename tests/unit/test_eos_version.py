#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)

import sys
from loguru import logger
import pytest
from eos_downloader.models.version import EosVersion, BASE_VERSION_STR
from tests.lib.dataset import eos_version

logger.remove()
logger.add(sys.stderr, level="DEBUG")

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_from_str(EOS_VERSION):
    version = EosVersion.from_str(EOS_VERSION['version'])
    if EOS_VERSION['is_valid']:
        assert version.major == EOS_VERSION['major']
        assert version.minor == EOS_VERSION['minor']
        assert version.patch == EOS_VERSION['patch']
        assert version.rtype == EOS_VERSION['rtype']
    else:
        assert str(version) == BASE_VERSION_STR


@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_to_str(EOS_VERSION):
    version = EosVersion(**EOS_VERSION)
    if EOS_VERSION['is_valid']:
        assert version.major == EOS_VERSION['major']
        assert version.minor == EOS_VERSION['minor']
        assert version.patch == EOS_VERSION['patch']
        assert version.rtype == EOS_VERSION['rtype']

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_branch(EOS_VERSION):
    if EOS_VERSION['is_valid']:
        version = EosVersion(**EOS_VERSION)
        assert version.branch == f'{EOS_VERSION["major"]}.{EOS_VERSION["minor"]}'

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_eq_operator(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    logger.warning(f'version is: {version.dict()}')
    assert version == version

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_ge_operator(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    version_b = EosVersion.from_str(BASE_VERSION_STR)
    assert version >= version_b

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_gs_operator(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    version_b = EosVersion.from_str(BASE_VERSION_STR)
    assert version > version_b

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_le_operator(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    version_b = EosVersion.from_str(BASE_VERSION_STR)
    assert version_b <= version

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_ls_operator(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    version_b = EosVersion.from_str(BASE_VERSION_STR)
    assert version_b < version

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_match(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    version = EosVersion(**EOS_VERSION)
    assert version.match(f'=={EOS_VERSION["version"]}')
    assert version.match(f'!={BASE_VERSION_STR}')
    assert version.match(f'>={BASE_VERSION_STR}')
    assert version.match(f'>{BASE_VERSION_STR}')
    assert version.match('<=4.99.0F')
    assert version.match('<4.99.0F')

# @pytest.mark.parametrize("EOS_VERSION", eos_version)
# def test_eos_version_is_in_branch(EOS_VERSION):
#     if not EOS_VERSION['is_valid']:
#         pytest.skip('not a valid version to test')
#     version = EosVersion(**EOS_VERSION)
#     assert version.is_in_branch(f"{EOS_VERSION['major']}.{EOS_VERSION['minor']}")

@pytest.mark.parametrize("EOS_VERSION", eos_version)
def test_eos_version_match_exception(EOS_VERSION):
    if not EOS_VERSION['is_valid']:
        pytest.skip('not a valid version to test')
    with pytest.raises(Exception) as e_info:
        version = EosVersion(**EOS_VERSION)
        assert version.match(f'+={EOS_VERSION["version"]}')
        logger.info(f'receive exception: {e_info}')
