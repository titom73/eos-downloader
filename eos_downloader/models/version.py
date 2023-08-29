#!/usr/bin/python
# coding: utf-8 -*-

"""Module for EOS version management"""

from __future__ import annotations

import re
import typing
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel

from eos_downloader.tools import exc_to_str

# logger = logging.getLogger(__name__)

BASE_VERSION_STR = "4.0.0F"
BASE_BRANCH_STR = "4.0"

RTYPE_FEATURE = "F"
RTYPE_MAINTENANCE = "M"
RTYPES = [RTYPE_FEATURE, RTYPE_MAINTENANCE]

# Regular Expression to capture multiple EOS version format
# 4.24
# 4.23.0
# 4.21.1M
# 4.28.10.F
# 4.28.6.1M
REGEX_EOS_VERSION = re.compile(
    r"^.*(?P<major>4)\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})(?P<other>\.\d*)*(?P<rtype>[M,F])*$"
)
REGEX_EOS_BRANCH = re.compile(
    r"^.*(?P<major>4)\.(?P<minor>\d{1,2})(\.?P<patch>\d)*(\.\d)*(?P<rtype>[M,F])*$"
)


class EosVersion(BaseModel):
    """
    EosVersion object to play with version management in code

    Since EOS is not using strictly semver approach, this class mimic some functions from semver lib for Arista EOS versions
    It is based on Pydantic and provides helpers for comparison:

    Examples:
    >>> eos_version_str = '4.23.2F'
    >>> eos_version = EosVersion.from_str(eos_version_str)
    >>> print(f'str representation is: {str(eos_version)}')
    str representation is: 4.23.2F

    >>> other_version = EosVersion.from_str(other_version_str)
    >>> print(f'eos_version < other_version: {eos_version < other_version}')
    eos_version < other_version: True

    >>> print(f'Is eos_version match("<=4.23.3M"): {eos_version.match("<=4.23.3M")}')
    Is eos_version match("<=4.23.3M"): True

    >>> print(f'Is eos_version in branch 4.23: {eos_version.is_in_branch("4.23.0")}')
    Is eos_version in branch 4.23: True

    Args:
        BaseModel (Pydantic): Pydantic Base Model
    """

    major: int = 4
    minor: int = 0
    patch: int = 0
    rtype: Optional[str] = "F"
    other: Any = None

    @classmethod
    def from_str(cls, eos_version: str) -> EosVersion:
        """
        Class constructor from a string representing EOS version

        Use regular expresion to extract fields from string.
        It supports following formats:
        - 4.24
        - 4.23.0
        - 4.21.1M
        - 4.28.10.F
        - 4.28.6.1M

        Args:
            eos_version (str): EOS version in str format

        Returns:
            EosVersion object
        """
        logger.debug(f"receiving version: {eos_version}")
        if REGEX_EOS_VERSION.match(eos_version):
            matches = REGEX_EOS_VERSION.match(eos_version)
            # assert matches is not None
            assert matches is not None
            return cls(**matches.groupdict())
        if REGEX_EOS_BRANCH.match(eos_version):
            matches = REGEX_EOS_BRANCH.match(eos_version)
            # assert matches is not None
            assert matches is not None
            return cls(**matches.groupdict())
        logger.error(f"Error occured with {eos_version}")
        return EosVersion()

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
        if self.other is None:
            return f"{self.major}.{self.minor}.{self.patch}{self.rtype}"
        return f"{self.major}.{self.minor}.{self.patch}{self.other}{self.rtype}"

    def _compare(self, other: EosVersion) -> float:
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
        if not isinstance(other, EosVersion):
            raise ValueError(
                f"could not compare {other} as it is not an EosVersion object"
            )
        comparison_flag: float = 0
        logger.warning(
            f"current version {self.__str__()} - other {str(other)}"  # pylint: disable = unnecessary-dunder-call
        )
        for key, _ in self.dict().items():
            if (
                comparison_flag == 0
                and self.dict()[key] is None
                or other.dict()[key] is None
            ):
                logger.debug(f"{key}: local None - remote None")
                logger.debug(f"{key}: local {self.dict()} - remote {other.dict()}")
                return comparison_flag
            logger.debug(
                f"{key}: local {self.dict()[key]} - remote {other.dict()[key]}"
            )
            if comparison_flag == 0 and self.dict()[key] < other.dict()[key]:
                comparison_flag = -1
            if comparison_flag == 0 and self.dict()[key] > other.dict()[key]:
                comparison_flag = 1
            if comparison_flag != 0:
                logger.info(f"comparison result is {comparison_flag}")
                return comparison_flag
        logger.info(f"comparison result is {comparison_flag}")
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
        logger.debug(f"work on comparison {prefix} with base release {match_version}")
        possibilities_dict = {
            ">": (1,),
            "<": (-1,),
            "==": (0,),
            "!=": (-1, 1),
            ">=": (0, 1),
            "<=": (-1, 0),
        }
        possibilities = possibilities_dict[prefix]
        cmp_res = self._compare(EosVersion.from_str(match_version))

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
            logger.debug(f"reading branch str:{branch_str}")
            branch = EosVersion.from_str(branch_str)
        except Exception as error:  # pylint: disable = broad-exception-caught
            logger.error(exc_to_str(error))
        else:
            return self.major == branch.major and self.minor == branch.minor
        return False
