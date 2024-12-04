# coding: utf-8 -*-
"""Default values for eos_downloader.

This module contains default configuration values used by the eos_downloader package.

Constants:
    DEFAULT_REQUEST_HEADERS (dict): Default HTTP headers used for API requests
        Contains Content-Type and User-Agent headers

    DEFAULT_SOFTWARE_FOLDER_TREE (str): API endpoint URL for retrieving the EOS software folder structure

    DEFAULT_DOWNLOAD_URL (str): API endpoint URL for getting download links for EOS images

    DEFAULT_SERVER_SESSION (str): API endpoint URL for obtaining session codes from Arista's servers
"""


DEFAULT_REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Chrome/123.0.0.0",
}
DEFAULT_SOFTWARE_FOLDER_TREE = (
    "https://www.arista.com/custom_data/api/cvp/getFolderTree/"
)

DEFAULT_DOWNLOAD_URL = "https://www.arista.com/custom_data/api/cvp/getDownloadLink/"

DEFAULT_SERVER_SESSION = "https://www.arista.com/custom_data/api/cvp/getSessionCode/"
