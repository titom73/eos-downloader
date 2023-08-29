#!/usr/bin/python
# coding: utf-8 -*-

"""
EOS Downloader module.
"""

from __future__ import (
    absolute_import,
    annotations,
    division,
    print_function,
    unicode_literals,
)

import dataclasses
import importlib.metadata
import json
from typing import Any

__author__ = "@titom73"
__email__ = "tom@inetsix.net"
__date__ = "2022-03-16"
__version__ = importlib.metadata.version("eos-downloader")

# __all__ = ["CvpAuthenticationItem", "CvFeatureManager", "EOSDownloader", "ObjectDownloader", "reverse"]

ARISTA_GET_SESSION = "https://www.arista.com/custom_data/api/cvp/getSessionCode/"

ARISTA_SOFTWARE_FOLDER_TREE = (
    "https://www.arista.com/custom_data/api/cvp/getFolderTree/"
)

ARISTA_DOWNLOAD_URL = "https://www.arista.com/custom_data/api/cvp/getDownloadLink/"

MSG_TOKEN_EXPIRED = """The API token has expired. Please visit arista.com, click on your profile and
select Regenerate Token then re-run the script with the new token.
"""

MSG_TOKEN_INVALID = """The API token is incorrect. Please visit arista.com, click on your profile and
check the Access Token. Then re-run the script with the correct token.
"""

MSG_INVALID_DATA = """Invalid data returned by server
"""

EVE_QEMU_FOLDER_PATH = "/opt/unetlab/addons/qemu/"


class EnhancedJSONEncoder(json.JSONEncoder):
    """Custom JSon encoder."""

    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
