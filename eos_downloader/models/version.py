#!/usr/bin/python
# coding: utf-8 -*-

import re
from typing import Any, Dict, Iterator, List, Optional, Type, Union
from pydantic import BaseModel, validator
from loguru import logger
from rich import console


BASE_VERSION_STR = '4.0.0F'
BASE_BRANCH_STR = '4.0'

# Regular Expression to capture multiple EOS version format
# 4.24
# 4.23.0
# 4.21.1M
# 4.28.10.F
# 4.28.6.1M
eos_version_reg = re.compile(r"^.*(?P<major>4)\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})(\.\d)*(?P<rtype>[M,F])*$")
eos_branch_reg = re.compile(r"^.*(?P<major>4)\.(?P<minor>\d{1,2})(\.?P<patch>\d)*(\.\d)*(?P<rtype>[M,F])*$")


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
    major: Optional[int] = 0
    minor: Optional[int] = 0
    patch: Optional[int] = 0
    rtype: Optional[str]

    @classmethod
    def from_str(cls, eos_version: str):
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
        logger.debug(f'receiving version: {eos_version}')
        if eos_version_reg.match(eos_version):
            matches = eos_version_reg.match(eos_version)
            return cls(**matches.groupdict())
        elif eos_branch_reg.match(eos_version):
            matches = eos_branch_reg.match(eos_version)
            return cls(**matches.groupdict())
        else:
            logger.error(f'Error occured with {eos_version}')

    def __str__(self) -> str:
        """
        Standard str representation

        Return string for EOS version like 4.23.3M

        Returns:
            str: A standard EOS version string representing <MAJOR>.<MINOR>.<PATCH><RTYPE>
        """
        return f'{self.major}.{self.minor}.{self.patch}{self.rtype}'

    def _compare(self, other) -> float:
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
            raise ValueError(f'could not compare {other} as it is not an EosVersion object')
        comparison_flag: float = 0
        for key,value in self.dict().items():
            if comparison_flag == 0 and self.dict()[key] < other.dict()[key]:
                comparison_flag = -1
            if comparison_flag == 0 and self.dict()[key] > other.dict()[key]:
                comparison_flag = 1
            if comparison_flag != 0:
                return comparison_flag
        return comparison_flag

    def __eq__(self, other):
        """ Implement __eq__ function (==) """
        return self._compare(other) == 0

    def __ne__(self, other):
        """ Implement __nw__ function (!=) """
        return self._compare(other) != 0

    def __lt__(self, other):
        """ Implement __lt__ function (<) """
        return self._compare(other) < 0

    def __le__(self, other):
        """ Implement __le__ function (<=) """
        return self._compare(other) <= 0

    def __gt__(self, other):
        """ Implement __gt__ function (>) """
        return self._compare(other) > 0

    def __ge__(self, other):
        """ Implement __ge__ function (>=) """
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
                "You provided: %r" % match_expr
            )
        logger.debug(f'work on comparison {prefix} with base release {match_version}')
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
            branch = EosVersion.from_str(branch_str)
        except Exception as error:
            logger.error(error)
        return self.major == branch.major and self.minor == branch.minor

    def branch(self) -> str:
        """
        Extract branch of version

        Returns:
            str: branch from version
        """
        return f'{self.major}.{self.minor}'
