#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import absolute_import, division, print_function

import os
from typing import Any, Dict, List

import pytest

import eos_downloader
from tests.lib.dataset import (
    eos_dataset_invalid,
    eos_dataset_valid,
    eos_token,
    eos_token_invalid,
)


@pytest.fixture
@pytest.mark.parametrize("DOWNLOAD_INFO", eos_dataset_valid)
def create_download_instance(request, DOWNLOAD_INFO):
    # logger.info("Execute fixture to create class elements")
    request.cls.eos_downloader = eos_downloader.eos.EOSDownloader(
        image=DOWNLOAD_INFO["image"],
        software=DOWNLOAD_INFO["software"],
        version=DOWNLOAD_INFO["version"],
        token=eos_token,
        hash_method="sha512sum",
    )
    yield
    # logger.info('Cleanup test environment')
    os.system("rm -f {}*".format(DOWNLOAD_INFO["filename"]))


def generate_test_ids_dict(val: Dict[str, Any], key: str = "name") -> str:
    """
    generate_test_ids Helper to generate test ID for parametrize

    Only related to SYSTEM_CONFIGLETS_TESTS structure

    Parameters
    ----------
    val : dict
        A configlet test structure

    Returns
    -------
    str
        Name of the configlet
    """
    if key in val.keys():
        # note this wouldn't show any hours/minutes/seconds
        return val[key]
    return "undefined_test"


def generate_test_ids_list(val: List[Dict[str, Any]], key: str = "name") -> str:
    """
    generate_test_ids Helper to generate test ID for parametrize

    Only related to SYSTEM_CONFIGLETS_TESTS structure

    Parameters
    ----------
    val : dict
        A configlet test structure

    Returns
    -------
    str
        Name of the configlet
    """
    return [entry[key] if key in entry.keys() else "unset_entry" for entry in val]
