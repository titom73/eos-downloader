# coding: utf-8 -*-

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
        - available_public_eos_version(self, branch: Union[str, None] = None, rtype: Union[str, None] = None)
                -> List[eos_downloader.models.version.EosVersion]: Extracts a list of available EOS versions from Arista.com.
        - latest(self, branch: Union[str, None] = None, rtype: str = eos_downloader.models.version.RTYPE_FEATURE)
                -> eos_downloader.models.version.EosVersion: Gets the latest branch from a semver standpoint.
        - branches(self, latest: bool = False) -> List[str]: Returns a list of valid EOS version branches.
        - _get_branches(self, versions: Union[List[eos_downloader.models.version.EosVersion], List[eos_downloader.models.version.CvpVersion]])
                -> Union[List[eos_downloader.models.version.EosVersion], List[eos_downloader.models.version.CvpVersion]]: Extracts unique branch names from a list of version objects.

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
"""  # noqa: E501

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import ClassVar, Union, List, Dict

from loguru import logger

import eos_downloader.logics.server
import eos_downloader.models.version
import eos_downloader.models.data
from eos_downloader.models.types import AristaPackage, AristaVersions


class AristaXmlBase:
    # pylint: disable=too-few-public-methods
    """Base class for Arista XML data management."""

    supported_role_types: List[str] = ["image", "md5sum", "sha512sum"]

    def __init__(
        self, token: Union[str, None] = None, xml_path: Union[str, None] = None
    ) -> None:
        self.server = eos_downloader.logics.server.AristaServer(token=token)
        if xml_path is not None:
            try:
                self.xml_data = ET.parse(xml_path)
            except ET.ParseError as error:
                logger.error(f"Error while parsing XML data: {error}")
        else:
            if self.server.authenticate():
                data = self._get_xml_root()
                if data is None:
                    raise ValueError("Unable to get XML data from Arista server")
                self.xml_data = data
            else:
                raise ValueError("Unable to authenticate to Arista server")

    def _get_xml_root(self) -> Union[ET.ElementTree, None]:
        try:
            return self.server.get_xml_data()
        except Exception as error:  # pylint: disable=broad-except
            logger.error(f"Error while getting XML data from Arista server: {error}")
            return None


class AristaXmlQuerier(AristaXmlBase):
    """Class to query Arista XML data for Software versions."""

    def available_public_versions(
        self,
        branch: Union[str, None] = None,
        rtype: Union[str, None] = None,
        package: AristaPackage = "eos",
    ) -> List[AristaVersions]:
        """Get list of available public EOS versions from Arista website.

        This method parses XML data to extract available EOS or CVP versions based on specified criteria.

        Args:
            branch (Union[str, None], optional): Branch number to filter versions (e.g. "4.29").
                Defaults to None.
            rtype (Union[str, None], optional): Release type to filter versions.
                Must be one of the valid release types defined in RTYPES. Defaults to None.
            package (AristaPackage, optional): Type of package to look for - either 'eos' or 'cvp'.
                Defaults to 'eos'.
        Returns:
            List[eos_downloader.models.types.AristaVersions]: List of version objects (EosVersion or CvpVersion) matching the criteria.
            List[AristaVersions]: List of version objects (EosVersion or CvpVersion) matching the criteria.

        Raises:
            ValueError: If provided rtype is not in the list of valid release types.

        Example:
            >>> server.available_public_eos_version(branch="4.29", rtype="INT", package="eos")
            [EosVersion('4.29.0F-INT'), EosVersion('4.29.1F-INT'), ...]
        """
        xpath_query = './/dir[@label="Active Releases"]//dir[@label]'
        regexp = eos_downloader.models.version.EosVersion.regex_version

        if package == "cvp":
            xpath_query = './/dir[@label="Active Releases"]//dir[@label]'
            regexp = eos_downloader.models.version.CvpVersion.regex_version

        package_versions = []

        if rtype is not None and rtype not in eos_downloader.models.data.RTYPES:
            raise ValueError(
                f"Invalid release type: {rtype}. Expected one of {eos_downloader.models.data.RTYPES}"
            )
        nodes = self.xml_data.findall(xpath_query)
        for node in nodes:
            if "label" in node.attrib and node.get("label") is not None:
                label = node.get("label")
                if label is not None and regexp.match(label):
                    package_version = None
                    if package == "eos":
                        package_version = (
                            eos_downloader.models.version.EosVersion.from_str(label)
                        )
                    elif package == "cvp":
                        package_version = (
                            eos_downloader.models.version.CvpVersion.from_str(label)
                        )
                    package_versions.append(package_version)
        if rtype is not None or branch is not None:
            package_versions = [
                version
                for version in package_versions
                if version is not None
                and (rtype is None or version.rtype == rtype)
                and (branch is None or str(version.branch) == branch)
            ]

        return package_versions

    def latest(
        self,
        package: eos_downloader.models.types.AristaPackage = "eos",
        branch: Union[str, None] = None,
        rtype: Union[eos_downloader.models.types.ReleaseType, None] = None,
    ) -> eos_downloader.models.version.EosVersion:
        """
        Get latest branch from semver standpoint

        Args:
            branch (str): Branch to search for
            rtype (str): Release type to search for

        Returns:
            eos_downloader.models.version.EosVersion: Latest version found
        """
        if rtype is not None and rtype not in eos_downloader.models.data.RTYPES:
            raise ValueError(
                f"Invalid release type: {rtype}. Expected {eos_downloader.models.data.RTYPES}"
            )

        versions = self.available_public_versions(
            package=package, branch=branch, rtype=rtype
        )

        return max(versions)

    def branches(
        self,
        package: eos_downloader.models.types.AristaPackage = "eos",
        latest: bool = False,
    ) -> List[str]:
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
            latest_branch = max(
                self._get_branches(self.available_public_versions(package=package))
            )
            return [str(latest_branch)]
        return sorted(
            self._get_branches(self.available_public_versions(package=package)),
            reverse=True,
        )

    def _get_branches(
        self,
        versions: Union[
            List[eos_downloader.models.version.EosVersion],
            List[eos_downloader.models.version.CvpVersion],
        ],
    ) -> eos_downloader.models.types.AristaVersions:
        """
        Extracts unique branch names from a list of version objects.
        Args:
            versions (Union[List[EosVersion], List[CvpVersion]]): A list of version objects,
                either EosVersion or CvpVersion types.
        Returns:
            Union[List[EosVersion], List[CvpVersion]]: A list of unique branch names.
        """
        branch = [version.branch for version in versions]
        return list(set(branch))


class AristaXmlObject(AristaXmlBase):
    """Base class for Arista XML data management."""

    software: ClassVar[str]
    base_xpath_active_version: ClassVar[str]
    base_xpath_filepath: ClassVar[str]

    def __init__(
        self,
        searched_version: str,
        image_type: str,
        token: Union[str, None] = None,
        xml_path: Union[str, None] = None,
    ) -> None:
        self.search_version = searched_version
        self.image_type = image_type
        self.version = eos_downloader.models.version.EosVersion().from_str(
            searched_version
        )
        super().__init__(token=token, xml_path=xml_path)

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

    def hashfile(self, hashtype: str = "md5sum") -> Union[str, None]:
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

        if self.filename is None:
            raise ValueError("Filename not found")

        for role in self.supported_role_types:
            hashfile = self.hashfile(role)
            if hashfile is None:
                raise ValueError("Hash file not found")
            if role == "image":
                file_path = self.path_from_xml(self.filename)
            else:
                file_path = self.path_from_xml(hashfile)
            if file_path is not None:
                urls[role] = self._url(file_path)
        return urls


class EosXmlObject(AristaXmlObject):
    """Class to query Arista XML data for EOS versions."""

    software: ClassVar[str] = "EOS"
    base_xpath_active_version: ClassVar[
        str
    ] = './/dir[@label="Active Releases"]/dir/dir/[@label]'
    base_xpath_filepath: ClassVar[str] = './/file[.="{}"]'


class CvpXmlObject(AristaXmlObject):
    """Class to query Arista XML data for CVP versions."""

    software: ClassVar[str] = "CVP"
    base_xpath_active_version: ClassVar[
        str
    ] = './/dir[@label="Active Releases"]/dir/dir/[@label]'
    base_xpath_filepath: ClassVar[str] = './/file[.="{}"]'
