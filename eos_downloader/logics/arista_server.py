#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=too-many-positional-arguments
# pylint: disable=dangerous-default-value

"""Server module for handling interactions with Arista software download portal.

This module provides the AristaServer class which manages authentication and
file retrieval operations with the Arista software download portal. It handles
session management, XML data retrieval, and download URL generation.

Classes
-------
AristaServer
    Main class for interacting with the Arista software portal.

Dependencies
-----------
- base64: For encoding authentication tokens
- json: For handling JSON data in requests
- xml.etree.ElementTree: For parsing XML responses
- loguru: For logging
- requests: For making HTTP requests

Example
-------
    >>> from eos_downloader.logics.server import AristaServer
    >>> server = AristaServer(token='my_auth_token')
    >>> server.authenticate()
    >>> xml_data = server.get_xml_data()
    >>> download_url = server.get_url('/path/to/file')

Notes
-----
The module requires valid authentication credentials to interact with the Arista portal.
All server interactions are performed over HTTPS and follow Arista's API specifications.
"""

from __future__ import annotations

import base64
import logging
import json
from typing import Dict, Union, Any

import xml.etree.ElementTree as ET
from loguru import logger
import requests

import eos_downloader.exceptions
import eos_downloader.defaults


class AristaServer:
    """AristaServer class to handle authentication and interactions with Arista software download portal.

    This class provides methods to authenticate with the Arista software portal,
    retrieve XML data containing available software packages, and generate download URLs
    for specific files.

    Attributes
    ----------
    token : str, optional
        Authentication token for Arista portal access
    timeout : int, default=5
        Timeout in seconds for HTTP requests
    session_server : str
        URL of the authentication server
    headers : Dict[str, any]
        HTTP headers to use in requests
    xml_url : str
        URL to retrieve software package XML data
    download_server : str
        Base URL for file downloads
    _session_id : str
        Session ID obtained after authentication

    Methods
    -------
    authenticate(token: Union[bool, None] = None) -> bool
        Authenticates with the Arista portal using provided or stored token
    get_xml_data() -> ET.ElementTree
        Retrieves XML data containing available software packages
    get_url(remote_file_path: str) -> Union[str, None]
        Generates download URL for a specific file path

    Raises
    ------
    eos_downloader.exceptions.AuthenticationError
        When authentication fails due to invalid or expired token
    """

    def __init__(
        self,
        token: Union[str, None] = None,
        timeout: int = 5,
        session_server: str = eos_downloader.defaults.DEFAULT_SERVER_SESSION,
        headers: Dict[str, Any] = eos_downloader.defaults.DEFAULT_REQUEST_HEADERS,
        xml_url: str = eos_downloader.defaults.DEFAULT_SOFTWARE_FOLDER_TREE,
        download_server: str = eos_downloader.defaults.DEFAULT_DOWNLOAD_URL,
    ) -> None:
        """Initialize the Server class with optional parameters.

        Parameters
        ----------
        token : Union[str, None], optional
            Authentication token. Defaults to None.
        timeout : int, optional
            Request timeout in seconds. Defaults to 5.
        session_server : str, optional
            URL of the session server. Defaults to DEFAULT_SERVER_SESSION.
        headers : Dict[str, any], optional
            HTTP headers for requests. Defaults to DEFAULT_REQUEST_HEADERS.
        xml_url : str, optional
            URL of the software folder tree XML. Defaults to DEFAULT_SOFTWARE_FOLDER_TREE.
        download_server : str, optional
            Base URL for downloads. Defaults to DEFAULT_DOWNLOAD_URL.

        Returns
        -------
        None
        """
        self.token: Union[str, None] = token
        self._session_server = session_server
        self._headers = headers
        self._timeout = timeout
        self._xml_url = xml_url
        self._download_server = download_server
        self._session_id = None

        logging.info(f"Initialized AristaServer with headers: {self._headers}")

    def authenticate(self, token: Union[str, None] = None) -> bool:
        """Authenticate to the API server using access token.

        The token is encoded in base64 and sent to the server for authentication.
        A session ID is retrieved from the server response if authentication is successful.

        Parameters
        ----------
        token : Union[str, None], optional
            Access token for authentication. If None, uses existing token stored in instance. Defaults to None.

        Returns
        -------
        bool
            True if authentication successful, False otherwise

        Raises
        ------
        eos_downloader.exceptions.AuthenticationError
            If access token is invalid or expired
        """

        if token is not None:
            self.token = token
        if self.token is None:
            logger.error("No token provided for authentication")
            return False
        credentials = (base64.b64encode(self.token.encode())).decode("utf-8")
        jsonpost = {"accessToken": credentials}
        result = requests.post(
            self._session_server,
            data=json.dumps(jsonpost),
            timeout=self._timeout,
            headers=self._headers,
        )
        if result.json()["status"]["message"] in [
            "Access token expired",
            "Invalid access token",
        ]:
            logging.critical(
                f"Authentication failed: {result.json()['status']['message']}"
            )
            raise eos_downloader.exceptions.AuthenticationError
            # return False
        try:
            if "data" in result.json():
                self._session_id = result.json()["data"]["session_code"]
                logging.info(f"Authenticated with session ID: {self._session_id}")
                return True
        except KeyError as error:
            logger.error(
                f"Key Error in parsing server response ({result.json()}): {error}"
            )
            return False
        return False

    def get_xml_data(self) -> Union[ET.ElementTree, None]:
        """Retrieves XML data from the server.

        This method fetches XML data by making a POST request to the server's XML endpoint.
        If not already authenticated, it will initiate the authentication process first.

        Returns
        -------
        ET.ElementTree
            An ElementTree object containing the parsed XML data from the server response.

        Raises
        ------
        KeyError
            If the server response doesn't contain the expected data structure.

        Notes
        -----
        The method requires a valid session ID which is obtained through authentication.
        The XML data is expected to be in the response JSON under data.xml path.
        """

        logging.info(f"Getting XML data from server {self._session_server}")
        if self._session_id is None:
            logging.debug("Not authenticated to server, start authentication process")
            self.authenticate()
        jsonpost = {"sessionCode": self._session_id}
        result = requests.post(
            self._xml_url,
            data=json.dumps(jsonpost),
            timeout=self._timeout,
            headers=self._headers,
        )
        try:
            folder_tree = result.json()["data"]["xml"]
            logging.debug("XML data received from Arista server")
            root_element = ET.fromstring(folder_tree)
            if root_element is None:
                logger.error("Failed to parse XML data from server response")
                return None
            return ET.ElementTree(root_element)
        except KeyError as error:
            logger.error(f"Unkown key in server response: {error}")
            return None
        except ET.ParseError as error:
            logger.error(f"Failed to parse XML from server response: {error}")
            return None

    def get_url(self, remote_file_path: str) -> Union[str, None]:
        """Get download URL for a remote file from server.

        This method retrieves the download URL for a specified remote file by making a POST request
        to the server. If not authenticated, it will first authenticate before making the request.

        Parameters
        ----------
        remote_file_path : str
            Path to the remote file on server to get download URL for

        Returns
        -------
        Union[str, None]
            The download URL if successful, None if request fails or URL not found in response

        Raises
        ------
        requests.exceptions.RequestException
            If the request to server fails
        json.JSONDecodeError
            If server response is not valid JSON
        requests.exceptions.Timeout
            If server request times out
        """

        logging.info(f"Getting download URL for {remote_file_path}")
        if self._session_id is None:
            logging.debug("Not authenticated to server, start authentication process")
            self.authenticate()
        jsonpost = {"sessionCode": self._session_id, "filePath": remote_file_path}
        result = requests.post(
            self._download_server,
            data=json.dumps(jsonpost),
            timeout=self._timeout,
            headers=self._headers,
        )
        if "data" in result.json() and "url" in result.json()["data"]:
            # logger.debug('URL to download file is: {}', result.json())
            logging.info("Download URL received from server")
            logging.debug(f'URL to download file is: {result.json()["data"]["url"]}')
            return result.json()["data"]["url"]
        return None
