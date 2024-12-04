#!/usr/bin/python
# coding: utf-8 -*-
"""The module implements version management following semantic versioning principles with custom adaptations for
Arista EOS and CloudVision Portal (CVP) software versioning schemes.

    SemVer: Base class implementing semantic versioning with comparison and matching capabilities.
    EosVersion: Specialized version handling for Arista EOS software releases.
    CvpVersion: Specialized version handling for CloudVision Portal releases.

Each class provides methods to:
- Parse version strings into structured objects
- Compare versions
- Extract branch information
- Match version patterns
- Convert versions to string representations

    Basic SemVer usage:
    >>> version = SemVer(major=4, minor=23, patch=3)
    '4.23.3'

    EOS version handling:
    >>> eos = EosVersion.from_str('4.23.3M')
    >>> eos.branch
    '4.23'

    CVP version handling:
    >>> cvp = CvpVersion.from_str('2024.1.0')
    >>> str(cvp)

The module enforces version format validation through regular expressions and provides
comprehensive comparison operations (==, !=, <, <=, >, >=) between versions.

Note:
    - EOS versions follow the format: <major>.<minor>.<patch>[M|F]
    - CVP versions follow the format: <year>.<minor>.<patch>
"""

from __future__ import annotations

import re
import typing
from typing import Any, Optional, Pattern, ClassVar

from loguru import logger
from pydantic import BaseModel

from eos_downloader.tools import exc_to_str

# logger = logging.getLogger(__name__)


class SemVer(BaseModel):
    """A class to represent a Semantic Version (SemVer) based on pydanntic.

    This class provides methods to parse, compare, and manipulate semantic versions.
    It supports standard semantic versioning with optional release type and additional version information.

    Examples:
        >>> version = SemVer(major=4, minor=23, patch=3, rtype="M")
        >>> str(version)
        '4.23.3M'

        >>> version2 = SemVer.from_str('4.24.1F')
        >>> version2.branch
        '4.24'

        >>> version < version2
        True

        >>> version.match("<=4.24.0")
        True

        >>> version.is_in_branch("4.23")
        True

    Attributes:
        major (int): Major version number.
        minor (int): Minor version number.
        patch (int): Patch version number.
        rtype (Optional[str]): Release type (e.g., 'M' for maintenance, 'F' for feature).
        other (Any): Additional version information.
        regex_version (ClassVar[Pattern[str]]): Regular expression to extract version information.
        regex_branch (ClassVar[Pattern[str]]): Regular expression to extract branch information.
        description (str): A basic description of this class.

    Methods:
        from_str(cls, semver: str) -> SemVer:
            Create a SemVer instance from a version string.

        branch(self) -> str:
            Extract the branch of the version.

        __str__(self) -> str:
            Return a standard string representation of the version.

        _compare(self, other: SemVer) -> float:
            Compare this SemVer instance with another.

        __eq__(self, other):
            Implement equality comparison (==).

        __ne__(self, other):
            Implement inequality comparison (!=).

        __lt__(self, other):
            Implement less than comparison (<).

        __le__(self, other):
            Implement less than or equal comparison (<=).

        __gt__(self, other):
            Implement greater than comparison (>).

        __ge__(self, other):
            Implement greater than or equal comparison (>=).

        match(self, match_expr: str) -> bool:

        is_in_branch(self, branch_str: str) -> bool:
            Check if the current version is part of a branch version.
    """

    major: int = 0
    minor: int = 0
    patch: int = 0
    rtype: Optional[str] = None
    other: Any = None
    # Regular Expression to extract version information.
    regex_version: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d{1,2})(?P<other>\.\d*)*(?P<rtype>[M,F])*$"
    )
    regex_branch: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>\d+)\.(?P<minor>\d+)(\.?P<patch>\d)*(\.\d)*(?P<rtype>[M,F])*$"
    )
    # A Basic description of this class
    description: str = "A Generic SemVer implementation"

    @classmethod
    def from_str(cls, semver: str) -> SemVer:
        """Parse a string into a SemVer object.

        This method parses a semantic version string or branch name into a SemVer object.
        It supports both standard semver format (x.y.z) and branch format.

        Args:
            semver (str): The version string to parse. Can be either a semantic version
                string (e.g., "1.2.3") or a branch format.

        Returns:
            SemVer: A SemVer object representing the parsed version.
                Returns an empty SemVer object if parsing fails.

        Examples:
            >>> SemVer.from_str("1.2.3")
            SemVer(major=1, minor=2, patch=3)
            >>> SemVer.from_str("branch-1.2.3")
            SemVer(major=1, minor=2, patch=3)
        """

        if cls.regex_version.match(semver):
            matches = cls.regex_version.match(semver)
            # assert matches is not None
            assert matches is not None
            return cls(**matches.groupdict())
        if cls.regex_branch.match(semver):
            matches = cls.regex_branch.match(semver)
            # assert matches is not None
            assert matches is not None
            return cls(**matches.groupdict())
        logger.error(f"Error occured with {semver}")
        return SemVer()

    @property
    def branch(self) -> str:
        """
        Extract branch of version

        Returns:
            str: branch from version
        """
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        """
        Standard str representation

        Return string for EOS version like 4.23.3M

        Returns:
            str: A standard EOS version string representing <MAJOR>.<MINOR>.<PATCH><RTYPE>
        """
        return f"{self.major}.{self.minor}.{self.patch}{self.other if self.other is not None else ''}{self.rtype if self.rtype is not None else ''}"

    def _compare(self, other: SemVer) -> float:
        """
        An internal comparison function to compare 2 EosVersion objects

        Do a deep comparison from Major to Release Type
        The return value is
        - negative if ver1 < ver2,
        - zero if ver1 == ver2
        - strictly positive if ver1 > ver2

        Args:
            other (EosVersion): An EosVersion to compare with this object

        Raises:
            ValueError: Raise ValueError if input is incorrect type

        Returns:
            float: -1 if ver1 < ver2, 0 if ver1 == ver2, 1 if ver1 > ver2
        """
        if not isinstance(other, SemVer):
            raise ValueError(
                f"could not compare {other} as it is not an EosVersion object"
            )
        comparison_flag: float = 0
        for key, _ in self.dict().items():
            if (
                comparison_flag == 0
                and self.dict()[key] is None
                or other.dict()[key] is None
            ):
                return comparison_flag
            if comparison_flag == 0 and self.dict()[key] < other.dict()[key]:
                comparison_flag = -1
            if comparison_flag == 0 and self.dict()[key] > other.dict()[key]:
                comparison_flag = 1
            if comparison_flag != 0:
                return comparison_flag
        return comparison_flag

    @typing.no_type_check
    def __eq__(self, other):
        """Implement __eq__ function (==)"""
        return self._compare(other) == 0

    @typing.no_type_check
    def __ne__(self, other):
        # type: ignore
        """Implement __nw__ function (!=)"""
        return self._compare(other) != 0

    @typing.no_type_check
    def __lt__(self, other):
        # type: ignore
        """Implement __lt__ function (<)"""
        return self._compare(other) < 0

    @typing.no_type_check
    def __le__(self, other):
        # type: ignore
        """Implement __le__ function (<=)"""
        return self._compare(other) <= 0

    @typing.no_type_check
    def __gt__(self, other):
        # type: ignore
        """Implement __gt__ function (>)"""
        return self._compare(other) > 0

    @typing.no_type_check
    def __ge__(self, other):
        # type: ignore
        """Implement __ge__ function (>=)"""
        return self._compare(other) >= 0

    def match(self, match_expr: str) -> bool:
        """
        Compare self to match a match expression.

        Example:
        >>> eos_version.match("<=4.23.3M")
        True
        >>> eos_version.match("==4.23.3M")
        False

        Args:
            match_expr (str):  optional operator and version; valid operators are
              ``<``   smaller than
              ``>``   greater than
              ``>=``  greator or equal than
              ``<=``  smaller or equal than
              ``==``  equal
              ``!=``  not equal

        Raises:
            ValueError: If input has no match_expr nor match_ver

        Returns:
            bool: True if the expression matches the version, otherwise False
        """
        prefix = match_expr[:2]
        if prefix in (">=", "<=", "==", "!="):
            match_version = match_expr[2:]
        elif prefix and prefix[0] in (">", "<"):
            prefix = prefix[0]
            match_version = match_expr[1:]
        elif match_expr and match_expr[0] in "0123456789":
            prefix = "=="
            match_version = match_expr
        else:
            raise ValueError(
                "match_expr parameter should be in format <op><ver>, "
                "where <op> is one of "
                "['<', '>', '==', '<=', '>=', '!=']. "
                f"You provided: {match_expr}"
            )
        possibilities_dict = {
            ">": (1,),
            "<": (-1,),
            "==": (0,),
            "!=": (-1, 1),
            ">=": (0, 1),
            "<=": (-1, 0),
        }
        possibilities = possibilities_dict[prefix]
        cmp_res = self._compare(SemVer.from_str(match_version))

        return cmp_res in possibilities

    def is_in_branch(self, branch_str: str) -> bool:
        """
        Check if current version is part of a branch version

        Comparison is done across MAJOR and MINOR

        Args:
            branch_str (str): a string for EOS branch. It supports following formats 4.23 or 4.23.0

        Returns:
            bool: True if current version is in provided branch, otherwise False
        """
        try:
            branch = SemVer.from_str(branch_str)
        except Exception as error:  # pylint: disable = broad-exception-caught
            logger.error(exc_to_str(error))
        else:
            return self.major == branch.major and self.minor == branch.minor
        return False


class EosVersion(SemVer):
    """EosVersion object to play with version management in code.

    Since EOS is not using strictly semver approach, this class mimics some functions from the semver library for Arista EOS versions.
    It is based on Pydantic and provides helpers for comparison.

    Example:
        >>> version = EosVersion(major=4, minor=21, patch=1, rtype="M")
        >>> print(version)
        EosVersion(major=4, minor=21, patch=1, rtype='M', other=None)
        >>> version = EosVersion.from_str('4.32.1F')
        >>> print(version)
        EosVersion(major=4, minor=32, patch=1, rtype='F', other=None)

    Attributes:
        major (int): Major version number, default is 4.
        minor (int): Minor version number, default is 0.
        patch (int): Patch version number, default is 0.
        rtype (Optional[str]): Release type, default is "F".
        other (Any): Any other version information.
        regex_version (ClassVar[Pattern[str]]): Regular expression to extract version information.
        regex_branch (ClassVar[Pattern[str]]): Regular expression to extract branch information.
        description (str): A basic description of this class, default is "A Generic SemVer implementation".
    """

    major: int = 4
    minor: int = 0
    patch: int = 0
    rtype: Optional[str] = "F"
    other: Any = None
    # Regular Expression to extract version information.
    regex_version: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>4)\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})(?P<other>\.\d*)*(?P<rtype>[M,F])*$"
    )
    regex_branch: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>4)\.(?P<minor>\d{1,2})(\.?P<patch>\d)*(\.\d)*(?P<rtype>[M,F])*$"
    )
    # A Basic description of this class
    description: str = "A SemVer implementation for EOS"


class CvpVersion(SemVer):
    """A CloudVision Portal Version class that inherits from SemVer.

    This class implements version management for CloudVision Portal (CVP) versions
    following a modified semantic versioning pattern where:
    - major version represents the year (e.g. 2024)
    - minor version represents feature releases
    - patch version represents bug fixes

    Attributes:
        major (int): The year component of the version (e.g. 2024)
        minor (int): The minor version number
        patch (int): The patch version number
        rtype (Optional[str]): Release type if any
        other (Any): Additional version information if any
        regex_version (Pattern[str]): Regular expression to parse version strings
        regex_branch (Pattern[str]): Regular expression to parse branch version strings
        description (str): Brief description of the class purpose

    Example:
        >>> version = CvpVersion(2024, 1, 0)
        >>> str(version)
        '2024.1.0'
    """

    major: int = 2024
    minor: int = 0
    patch: int = 0
    rtype: Optional[str] = None
    other: Any = None
    # Regular Expression to extract version information.
    regex_version: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>\d{4})\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})(?P<other>\.\d*)*$"
    )
    regex_branch: ClassVar[Pattern[str]] = re.compile(
        r"^.*(?P<major>\d{4})\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})(?P<other>\.\d*)*$"
    )
    # A Basic description of this class
    description: str = "A SemVer implementation for CloudVision"
