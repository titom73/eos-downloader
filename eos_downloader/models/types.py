#!/usr/bin/python
# coding: utf-8 -*-
"""
This module defines type aliases and literals used in the eos_downloader project.

Attributes
----------
AristaPackage : Literal
    Literal type for Arista package types. Can be either "eos" or "cvp".
AristaMapping : Literal
    Literal type for Arista mapping types. Can be either "CloudVision" or "EOS".
AristaVersions : Union
    Union type for supported SemVer object types. Can be either EosVersion or CvpVersion.
ReleaseType : Literal
    Literal type for release types. Can be either "M" (maintenance) or "F" (feature).

Examples
--------
    # Example usage of AristaPackage
    def get_package_type(package: AristaPackage):
        if package == "eos":
            return "Arista EOS package"
        elif package == "cvp":
            return "CloudVision Portal package"

    # Example usage of AristaVersions
    def print_version(version: AristaVersions):
        print(f"Version: {version}")

    # Example usage of ReleaseType
    def is_feature_release(release: ReleaseType) -> bool:
        return release == "F"
"""

from typing import Literal, Union

import eos_downloader.logics

# import eos_downloader.logics.arista_server
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
