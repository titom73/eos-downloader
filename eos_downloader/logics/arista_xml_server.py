# coding: utf-8 -*-

"""This module provides classes for managing and querying Arista XML data.

Classes:
    AristaXmlBase: Base class for Arista XML data management.
    AristaXmlQuerier: Class to query Arista XML data for Software versions.
    AristaXmlObject: Base class for Arista XML data management with specific software and version.
    EosXmlObject: Class to query Arista XML data for EOS versions.
"""  # noqa: E501

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import ClassVar, Union, List, Dict

import eos_downloader.logics.arista_server
import eos_downloader.models.version
import eos_downloader.models.data
from eos_downloader.models.types import AristaPackage, AristaVersions, AristaMapping


class AristaXmlBase:
    # pylint: disable=too-few-public-methods
    """Base class for Arista XML data management."""

    # File extensions supported to be downloaded from arista server.
    # Should cover: image file (image) and has files (md5sum and/or sha512sum)
    supported_role_types: ClassVar[List[str]] = ["image", "md5sum", "sha512sum"]

    def __init__(
        self, token: Union[str, None] = None, xml_path: Union[str, None] = None
    ) -> None:
        """
        Initialize the AristaXmlBase class.

        Parameters
        ----------
        token : Union[str, None], optional
            Authentication token. Defaults to None.
        xml_path : Union[str, None], optional
            Path to the XML file. Defaults to None.

        Returns
        -------
        None
        """
        logging.info("Initializing AristXmlBase.")
        self.server = eos_downloader.logics.arista_server.AristaServer(token=token)
        if xml_path is not None:
            try:
                self.xml_data = ET.parse(xml_path)
            except ET.ParseError as error:
                logging.error(f"Error while parsing XML data: {error}")
        else:
            if self.server.authenticate():
                data = self._get_xml_root()
                if data is None:
                    logging.error("Unable to get XML data from Arista server")
                    raise ValueError("Unable to get XML data from Arista server")
                # Ensure the XML data has a valid root element
                if data.getroot() is None:
                    logging.error("XML data has no root element")
                    raise ValueError("XML data has no root element")
                # At this point, we've validated that data has a valid root
                self.xml_data = data  # type: ignore[assignment]
            else:
                logging.error("Unable to authenticate to Arista server")
                raise ValueError("Unable to authenticate to Arista server")

    def _get_xml_root(self) -> Union[ET.ElementTree, None]:
        """
        Retrieves the XML root from the Arista server.

        Returns
        -------
        Union[ET.ElementTree, None]
            The XML root element tree if successful, None otherwise.
        """
        logging.info("Getting XML root from Arista server.")
        try:
            return self.server.get_xml_data()
        except Exception as error:  # pylint: disable=broad-except
            logging.error(f"Error while getting XML data from Arista server: {error}")
            return None


class AristaXmlQuerier(AristaXmlBase):
    """Class to query Arista XML data for Software versions."""

    def available_public_versions(
        self,
        branch: Union[str, None] = None,
        rtype: Union[str, None] = None,
        package: AristaPackage = "eos",
    ) -> List[AristaVersions]:
        """
        Get list of available public EOS versions from Arista website.

        This method parses XML data to extract available EOS or CVP versions based on specified criteria.

        Parameters
        ----------
        branch : Union[str, None], optional
            Branch number to filter versions (e.g. "4.29"). Defaults to None.
        rtype : Union[str, None], optional
            Release type to filter versions. Must be one of the valid release types defined in RTYPES. Defaults to None.
        package : AristaPackage, optional
            Type of package to look for - either 'eos' or 'cvp'. Defaults to 'eos'.

        Returns
        -------
        List[AristaVersions]
            List of version objects (EosVersion or CvpVersion) matching the criteria.

        Raises
        ------
        ValueError
            If provided rtype is not in the list of valid release types.

        Examples
        --------
        >>> server.available_public_eos_version(branch="4.29", rtype="INT", package="eos")
        [EosVersion('4.29.0F-INT'), EosVersion('4.29.1F-INT'), ...]
        """

        logging.info(f"Getting available versions for {package} package")

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
    ) -> AristaVersions:
        """
        Get latest branch from semver standpoint.

        Parameters
        ----------
        package : eos_downloader.models.types.AristaPackage, optional
            Type of package to look for - either 'eos' or 'cvp'. Defaults to 'eos'.
        branch : Union[str, None], optional
            Branch to search for. Defaults to None.
        rtype : Union[eos_downloader.models.types.ReleaseType, None], optional
            Release type to search for. Defaults to None.

        Returns
        -------
        AristaVersions
            Latest version found.

        Raises
        ------
        ValueError
            If no versions are found to run the max() function.
        """
        if package == "eos":
            if rtype is not None and rtype not in eos_downloader.models.data.RTYPES:
                raise ValueError(
                    f"Invalid release type: {rtype}. Expected {eos_downloader.models.data.RTYPES}"
                )

        versions = self.available_public_versions(
            package=package, branch=branch, rtype=rtype
        )
        if len(versions) == 0:
            raise ValueError("No versions found to run the max() function")
        return max(versions)

    def branches(
        self,
        package: eos_downloader.models.types.AristaPackage = "eos",
        latest: bool = False,
    ) -> List[str]:
        """
        Returns a list of valid EOS version branches.

        The branches are determined based on the available public EOS versions.
        When latest=True, only the most recent branch is returned.

        Parameters
        ----------
        package : eos_downloader.models.types.AristaPackage, optional
            Type of package to look for - either 'eos' or 'cvp'. Defaults to 'eos'.
        latest : bool, optional
            If True, returns only the latest branch version. Defaults to False.

        Returns
        -------
        List[str]
            A list of branch version strings. Contains single latest version if latest=True,
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
    ) -> List[str]:
        """
        Extracts unique branch names from a list of version objects.

        Parameters
        ----------
        versions : Union[List[eos_downloader.models.version.EosVersion], List[eos_downloader.models.version.CvpVersion]]
            A list of version objects, either EosVersion or CvpVersion types.

        Returns
        -------
        List[str]
            A list of unique branch names.
        """
        branch = [version.branch for version in versions]
        return list(set(branch))


class AristaXmlObject(AristaXmlBase):
    """Base class for Arista XML data management."""

    software: ClassVar[AristaMapping]
    base_xpath_active_version: ClassVar[str]
    base_xpath_filepath: ClassVar[str]
    checksum_file_extension: ClassVar[str] = "sha512sum"

    def __init__(
        self,
        searched_version: str,
        image_type: str,
        token: Union[str, None] = None,
        xml_path: Union[str, None] = None,
    ) -> None:
        """
        Initialize the AristaXmlObject class.

        Parameters
        ----------
        searched_version : str
            The version of the software to search for.
        image_type : str
            The type of image to download.
        token : Union[str, None], optional
            Authentication token. Defaults to None.
        xml_path : Union[str, None], optional
            Path to the XML file. Defaults to None.

        Returns
        -------
        None
        """
        self.search_version = searched_version
        self.image_type = image_type
        super().__init__(token=token, xml_path=xml_path)

    @property
    def filename(self) -> Union[str, None]:
        """
        Helper to build filename to search on arista.com.

        Returns
        -------
        Union[str, None]
            Filename to search for on Arista.com.
        """
        logging.info(
            f"Building filename for {self.image_type} package: {self.search_version}."
        )
        try:
            filename = eos_downloader.models.data.software_mapping.filename(
                self.software, self.image_type, self.search_version
            )
            return filename
        except ValueError as e:
            logging.error(f"Error: {e}")
        return None

    def hash_filename(self) -> Union[str, None]:
        """
        Helper to build filename for checksum to search on arista.com.

        Returns
        -------
        Union[str, None]
            Filename to search for on Arista.com.
        """

        logging.info(f"Building hash filename for {self.software} package.")

        if self.filename is not None:
            return f"{self.filename}.{self.checksum_file_extension}"
        return None

    def path_from_xml(self, search_file: str) -> Union[str, None]:
        """
        Parse XML to find path for a given file.

        Parameters
        ----------
        search_file : str
            File to search for.

        Returns
        -------
        Union[str, None]
            Path from XML if found, None otherwise.
        """

        logging.info(f"Building path from XML for {search_file}.")

        # Build xpath with provided file
        xpath_query = self.base_xpath_filepath.format(search_file)
        # Find the element using XPath
        path_element = self.xml_data.find(xpath_query)

        if path_element is not None:
            logging.debug(f'found path: {path_element.get("path")} for {search_file}')

        # Return the path if found, otherwise return None
        return path_element.get("path") if path_element is not None else None

    def _url(self, xml_path: str) -> Union[str, None]:
        """
        Get URL to download a file from Arista server.

        Parameters
        ----------
        xml_path : str
            Path to the file in the XML.

        Returns
        -------
        Union[str, None]
            URL to download the file.
        """

        logging.info(f"Getting URL for {xml_path}.")

        return self.server.get_url(xml_path)

    @property
    def urls(self) -> Dict[str, Union[str, None]]:
        """
        Get URLs to download files from Arista server for given software and version.

        This method will return a dictionary with file type as key and URL as value.
        It returns URL for the following items: 'image', 'md5sum', and 'sha512sum'.

        Returns
        -------
        Dict[str, Union[str, None]]
            Dictionary with file type as key and URL as value.

        Raises
        ------
        ValueError
            If filename or hash file is not found.
        """
        logging.info(f"Getting URLs for {self.software} package.")

        urls = {}

        if self.filename is None:
            raise ValueError("Filename not found")

        for role in self.supported_role_types:
            file_path = None
            logging.debug(f"working on {role}")
            hash_filename = self.hash_filename()
            if hash_filename is None:
                raise ValueError("Hash file not found")
            if role == "image":
                file_path = self.path_from_xml(self.filename)
            elif role == self.checksum_file_extension:
                file_path = self.path_from_xml(hash_filename)
            if file_path is not None:
                logging.info(f"Adding {role} with {file_path} to urls dict")
                urls[role] = self._url(file_path)
        logging.debug(f"URLs dict contains: {urls}")
        return urls


class EosXmlObject(AristaXmlObject):
    """Class to query Arista XML data for EOS versions."""

    software: ClassVar[AristaMapping] = "EOS"
    base_xpath_active_version: ClassVar[
        str
    ] = './/dir[@label="Active Releases"]/dir/dir/[@label]'
    base_xpath_filepath: ClassVar[str] = './/file[.="{}"]'

    # File extensions supported to be downloaded from arista server.
    # Should cover: image file (image) and has files (md5sum and/or sha512sum)
    supported_role_types: ClassVar[List[str]] = ["image", "md5sum", "sha512sum"]
    checksum_file_extension: ClassVar[str] = "sha512sum"

    def __init__(
        self,
        searched_version: str,
        image_type: str,
        token: Union[str, None] = None,
        xml_path: Union[str, None] = None,
    ) -> None:
        """
        Initialize an instance of the EosXmlObject class.

        Parameters
        ----------
        searched_version : str
            The version of the software to search for.
        image_type : str
            The type of image to download.
        token : Union[str, None], optional
            The authentication token. Defaults to None.
        xml_path : Union[str, None], optional
            The path to the XML file. Defaults to None.

        Returns
        -------
        None
        """

        self.search_version = searched_version
        self.image_type = image_type
        self.version = eos_downloader.models.version.EosVersion().from_str(
            searched_version
        )

        super().__init__(
            searched_version=searched_version,
            image_type=image_type,
            token=token,
            xml_path=xml_path,
        )


class CvpXmlObject(AristaXmlObject):
    """Class to query Arista XML data for CVP versions."""

    software: ClassVar[AristaMapping] = "CloudVision"
    base_xpath_active_version: ClassVar[
        str
    ] = './/dir[@label="Active Releases"]/dir/dir/[@label]'
    base_xpath_filepath: ClassVar[str] = './/file[.="{}"]'

    # File extensions supported to be downloaded from arista server.
    # Should cover: image file (image) and has files (md5sum and/or sha512sum)
    supported_role_types: ClassVar[List[str]] = ["image", "md5"]
    checksum_file_extension: ClassVar[str] = "md5"

    def __init__(
        self,
        searched_version: str,
        image_type: str,
        token: Union[str, None] = None,
        xml_path: Union[str, None] = None,
    ) -> None:
        """
        Initialize an instance of the CvpXmlObject class.

        Parameters
        ----------
        searched_version : str
            The version of the software to search for.
        image_type : str
            The type of image to download.
        token : Union[str, None], optional
            The authentication token. Defaults to None.
        xml_path : Union[str, None], optional
            The path to the XML file. Defaults to None.

        Returns
        -------
        None
        """

        self.search_version = searched_version
        self.image_type = image_type
        self.version = eos_downloader.models.version.CvpVersion().from_str(
            searched_version
        )

        super().__init__(
            searched_version=searched_version,
            image_type=image_type,
            token=token,
            xml_path=xml_path,
        )


# Create the custom type
AristaXmlObjects = Union[CvpXmlObject, EosXmlObject]
