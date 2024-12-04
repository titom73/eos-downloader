# coding: utf-8 -*-
"""Custom types for the eos_downloader package."""

from typing import Literal, Union

import eos_downloader.models.version

# Define the product type using Literal
AristaPackage = Literal["eos", "cvp"]
AristaMapping = Literal["CloudVision", "EOS"]

# Define list of support SemVer object type
AristaVersions = Union[
    eos_downloader.models.version.EosVersion, eos_downloader.models.version.CvpVersion
]

# List of supported release codes
ReleaseType = Literal["M", "F"]
