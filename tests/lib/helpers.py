#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=logger-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import (absolute_import, division, print_function)
from eos_downloader.data import DATA_MAPPING



def default_filename(version: str, info):
    """
    default_filename Helper to build default filename

    Parameters
    ----------
    version : str
        EOS version
    info : dict
        TEST Inputs

    Returns
    -------
    str
        Filename
    """
    if version is None or info is None:
        return None
    return DATA_MAPPING[info['software']]['default']['prepend'] + '-' + version + '.swi'
