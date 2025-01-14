#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import absolute_import, division, print_function

import os

import eos_downloader
from eos_downloader.data import DATA_MAPPING
from eos_downloader.eos import EOSDownloader

# --------------------------------------------------------------- #
# MOOCK data to use for testing
# --------------------------------------------------------------- #

# Get Auth token
# eos_token = os.getenv('ARISTA_TOKEN')
eos_token = os.getenv("ARISTA_TOKEN", "invalid_token")
eos_token_invalid = "invalid_token"

eos_dataset_valid = [
    {
        "image": "EOS",
        "version": "4.26.3M",
        "software": "EOS",
        "filename": "EOS-4.26.3M.swi",
        "expected_hash": "sha512sum",
        "remote_path": "/support/download/EOS-USA/Active Releases/4.26/EOS-4.26.3M/EOS-4.26.3M.swi",
        "compute_checksum": True,
    },
    {
        "image": "EOS",
        "version": "4.25.6M",
        "software": "EOS",
        "filename": "EOS-4.25.6M.swi",
        "expected_hash": "md5sum",
        "remote_path": "/support/download/EOS-USA/Active Releases/4.25/EOS-4.25.6M/EOS-4.25.6M.swi",
        "compute_checksum": True,
    },
    {
        "image": "vEOS-lab",
        "version": "4.25.6M",
        "software": "EOS",
        "filename": "vEOS-lab-4.25.6M.vmdk",
        "expected_hash": "md5sum",
        "remote_path": "/support/download/EOS-USA/Active Releases/4.25/EOS-4.25.6M/vEOS-lab/vEOS-lab-4.25.6M.vmdk",
        "compute_checksum": False,
    },
]


eos_dataset_invalid = [
    {
        "image": "default",
        "version": "4.26.3M",
        "software": "EOS",
        "filename": "EOS-4.26.3M.swi",
        "expected_hash": "sha512sum",
        "remote_path": "/support/download/EOS-USA/Active Releases/4.26/EOS-4.26.3M/EOS-4.26.3M.swi",
        "compute_checksum": True,
    }
]

eos_version = [
    {
        "version": "EOS-4.23.1F",
        "is_valid": True,
        "major": 4,
        "minor": 23,
        "patch": 1,
        "rtype": "F",
    },
    {
        "version": "EOS-4.23.0",
        "is_valid": True,
        "major": 4,
        "minor": 23,
        "patch": 0,
        "rtype": None,
    },
    {
        "version": "EOS-4.23",
        "is_valid": True,
        "major": 4,
        "minor": 23,
        "patch": 0,
        "rtype": None,
    },
    {
        "version": "EOS-4.23.1M",
        "is_valid": True,
        "major": 4,
        "minor": 23,
        "patch": 1,
        "rtype": "M",
    },
    {
        "version": "EOS-4.23.1.F",
        "is_valid": True,
        "major": 4,
        "minor": 23,
        "patch": 1,
        "rtype": "F",
    },
]
