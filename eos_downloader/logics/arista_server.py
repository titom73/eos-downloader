"""This module provides classes for managing and querying Arista XML data.

Classes:
    AristaXmlBase: Base class for Arista XML data management.
    AristaXmlQuerier: Class to query Arista XML data for Software versions.
    AristaXmlObject: Base class for Arista XML data management with specific software and version.
    EosXmlObject: Class to query Arista XML data for EOS versions.

Classes and Methods:
    AristaXmlBase:
        - __init__(self, token: str) -> None: Initializes the AristaXmlBase class with a token.
        - _get_xml_root(self): Retrieves the XML root from the Arista server.

    AristaXmlQuerier(AristaXmlBase):
        - available_public_eos_version(self, branch: Union[str, None] = None, rtype: Union[str, None] = None) -> List[eos_downloader.models.version.EosVersion]: Extracts a list of available EOS versions from Arista.com.
        - latest(self, branch: Union[str, None] = None, rtype: str = eos_downloader.models.version.RTYPE_FEATURE) -> eos_downloader.models.version.EosVersion: Gets the latest branch from a semver standpoint.
        - branches(self, latest: bool = False) -> List[str]: Returns a list of valid EOS version branches.
        - _get_branches(self, versions: Union[List[eos_downloader.models.version.EosVersion], List[eos_downloader.models.version.CvpVersion]]) -> Union[List[eos_downloader.models.version.EosVersion], List[eos_downloader.models.version.CvpVersion]]: Extracts unique branch names from a list of version objects.

    AristaXmlObject(AristaXmlBase):
        - __init__(self, searched_version: str, image_type: str, token: str) -> None: Initializes the AristaXmlObject class with a searched version, image type, and token.
        - filename(self) -> Union[str, None]: Builds the filename to search on arista.com.
        - hashfile(self, hashtype: str = 'md5sum') -> Union[str, None]: Builds the hash filename to search on arista.com.
        - path_from_xml(self, search_file: str) -> Union[str, None]: Parses XML to find the path for a given file.
        - _url(self, xml_path: str) -> str: Gets the URL to download a file from the Arista server.
        - urls(self) -> Dict[str, str]: Gets URLs to download files from the Arista server for given software and version.
        - available_public_eos_version(self): Raises NotImplementedError.

    EosXmlObject(AristaXmlObject):
        - Class to query Arista XML data for EOS versions.
"""

from __future__ import annotations

from loguru import logger
from abc import ABC, abstractmethod
from typing import ClassVar, Union, List, Dict

import xml.etree.ElementTree as ET

import eos_downloader.logics.server
import eos_downloader.models.version
import eos_downloader.models.data


class AristaXmlBase():
    """Base class for Arista XML data management."""

    supported_role_types: List[str] = ["image", "md5sum", "sha512sum"]

    def __init__(self, token: str) -> None:
        self.server = eos_downloader.logics.server.AristaServer(token=token)
        if self.server.authenticate():
            self.xml_data =  self._get_xml_root()
        else:
            raise ValueError("Unable to authenticate to Arista server")
        pass

    def _get_xml_root(self):
        try:
            return self.server.get_xml_data()
        except Exception as error:
            logger.error(f'Error while getting XML data from Arista server: {error}')


class AristaXmlQuerier(AristaXmlBase):
    """Class to query Arista XML data for Software versions."""

    def available_public_eos_version(
        self,
        branch: Union[str, None] = None,
        rtype: Union[str, None] = None,
    ) -> List[eos_downloader.models.version.EosVersion]:
        """
        Extract list of available EOS versions from Arista.com website

        Create a list of EosVersion object for all versions available on Arista.com

        Args:
            root_xml (ET.ElementTree): XML file with all versions available
            xpath (str, optional): XPATH to use to extract EOS version. Defaults to './/dir[@label="Active Releases"]/dir/dir/[@label]'.

        Returns:
            List[EosVersion]: List of EosVersion representing all available EOS versions
        """
        xpath = './/dir[@label="Active Releases"]/dir/dir[@label]'
        eos_versions = []
        # Check function parameters.
        if rtype is not None and rtype not in eos_downloader.models.version.RTYPES:
            raise ValueError(
                f"Invalid release type: {rtype}. Expected {eos_downloader.models.version.RTYPES}"
            )

        for node in self.xml_data.findall(xpath):
            if "label" in node.attrib and node.get("label") is not None:
                label = node.get("label")
                if label is not None and eos_downloader.models.version.EosVersion.regex_version.match(label):
                    eos_version = eos_downloader.models.version.EosVersion.from_str(label)
                    eos_versions.append(eos_version)
        if rtype is not None:
            eos_versions = [
                version for version in eos_versions if version.rtype == rtype
            ]
        if branch is not None:
            eos_versions = [
                version for version in eos_versions if str(version.branch) == branch
            ]
        return eos_versions

    def latest(self, branch: Union[str, None] = None, rtype: str = eos_downloader.models.version.RTYPE_FEATURE) -> eos_downloader.models.version.EosVersion:
        """
        Get latest branch from semver standpoint

        Args:
            branch (str): Branch to search for
            rtype (str): Release type to search for

        Returns:
            eos_downloader.models.version.EosVersion: Latest version found
        """
        if rtype is not None and rtype not in eos_downloader.models.version.RTYPES:
            raise ValueError(
                f"Invalid release type: {rtype}. Expected {eos_downloader.models.version.RTYPES}"
            )

        versions = self.available_public_eos_version(branch=branch, rtype=rtype)

        return max(versions)

    def branches(self, latest: bool = False) -> List[str]:
        """Returns a list of valid EOS version branches.

        The branches are determined based on the available public EOS versions.
        When latest=True, only the most recent branch is returned.

        Args:
            latest: If True, returns only the latest branch version.
                   If False, returns all available branches sorted in descending order.

        Returns:
            List[str]: A list of branch version strings.
                      Contains single latest version if latest=True,
                      otherwise all available versions sorted descendingly.
        """
        if latest:
            latest_branch = max(self._get_branches(self.available_public_eos_version()))
            return [str(latest_branch)]
        return sorted(
            self._get_branches(self.available_public_eos_version()), reverse=True
        )

    def _get_branches(self, versions: Union[List[eos_downloader.models.version.EosVersion],List[eos_downloader.models.version.CvpVersion]]) -> Union[List[eos_downloader.models.version.EosVersion],List[eos_downloader.models.version.CvpVersion]]:
        """
        Extracts unique branch names from a list of version objects.
        Args:
            versions (Union[List[EosVersion], List[CvpVersion]]): A list of version objects,
                either EosVersion or CvpVersion types.
        Returns:
            Union[List[EosVersion], List[CvpVersion]]: A list of unique branch names.
        """
        branch = [ version.branch for version in versions]
        return list(set(branch))


class AristaXmlObject(AristaXmlBase):
    """Base class for Arista XML data management."""

    software: ClassVar[str]
    base_xpath_active_version: ClassVar[str]
    base_xpath_filepath: ClassVar[str]

    def __init__(self, searched_version: str, image_type: str, token: str) -> None:
        self.search_version = searched_version
        self.image_type = image_type
        self.version = eos_downloader.models.version.EosVersion().from_str(searched_version)
        self.server = eos_downloader.logics.server.AristaServer(token=token)
        if self.server.authenticate():
            self.xml_data =  self._get_xml_root()
        else:
            raise ValueError("Unable to authenticate to Arista server")
        pass

    @property
    def filename(self) -> Union[str, None]:
        """
        _build_filename Helper to build filename to search on arista.com

        Returns
        -------
        str:
            Filename to search for on Arista.com
        """
        try:
            filename = eos_downloader.models.data.software_mapping.filename(
                self.software, self.image_type, self.search_version
            )
            return filename
        except ValueError as e:
            logger.error(f"Error: {e}")
        return None

    def hashfile(self, hashtype: str = 'md5sum') -> Union[str,None]:
        """
        hashfilename Helper to build filename to search on arista.com

        Args:
            hashtype (str, optional): Hash type to search for. Defaults to 'md5sum'.

        Returns
        -------
        str:
            Filename to search for on Arista.com
        """
        if hashtype in self.supported_role_types:
            if self.filename is not None:
                return f"{self.filename}.{hashtype}"
        return None

    def path_from_xml(self, search_file: str) -> Union[str, None]:
        """Parse XML to find path for a given file.

        Args:
            search_file (str): File to search for

        Returns:
            Union[str, None]: Path from XML if found, None otherwise
        """
        # Build xpath with provided file
        xpath_query = self.base_xpath_filepath.format(search_file)
        # Find the element using XPath
        path_element = self.xml_data.find(xpath_query)

        # Return the path if found, otherwise return None
        return path_element.get("path") if path_element is not None else None

    def _url(self, xml_path: str) -> str:
        """Get URL to download a file from Arista server.

        Args:
            xml_path (str): Path to the file in the XML

        Returns:
            str: URL to download the file
        """
        return self.server.get_url(xml_path)

    @property
    def urls(self) -> Dict[str, str]:
        """Get URLs to download files from Arista server for given software and version.

        This method will return a dictionary with file type as key and URL as value.
        It returns URL for the following items: 'image', 'md5sum', and 'sha512sum'.

        Returns:
            Dict[str, str]: Dictionary with file type as key and URL as value
        """
        urls = {}
        for role in self.supported_role_types:
            if role == 'image':
                file_path = self.path_from_xml(self.filename)
            else:
                file_path = self.path_from_xml(self.hashfile(role))
            if file_path is not None:
                urls[role] = self._url(file_path)
        return urls

    def available_public_eos_version(self):
        raise NotImplementedError("Method not implemented")


class EosXmlObject(AristaXmlObject):
    """Class to query Arista XML data for EOS versions."""

    software: ClassVar[str] = "EOS"
    base_xpath_active_version: ClassVar[str] = (
        './/dir[@label="Active Releases"]/dir/dir/[@label]'
    )
    base_xpath_filepath: ClassVar[str] = './/file[.="{}"]'
