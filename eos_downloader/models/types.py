# coding: utf-8 -*-
"""
This module defines various type aliases using the `Literal` and `Union` types from the `typing` module.

Type Aliases:
    - AristaPackage: A literal type that can be either "eos" or "cvp".
    - AristaMapping: A literal type that can be either "CloudVision" or "EOS".
    - AristaVersions: A union type that can be either `EosVersion` or `CvpVersion` from the `eos_downloader.models.version` module.
    - ReleaseType: A literal type that can be either "M" or "F".
"""

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
