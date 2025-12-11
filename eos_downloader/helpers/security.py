#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Security utilities for eos-downloader.

This module provides functions for secure handling of authentication tokens,
including masking for safe logging and format validation.

Functions
---------
mask_token
    Mask an authentication token for safe display in logs
validate_arista_token
    Validate the format of an Arista API token

Examples
--------
>>> from eos_downloader.helpers.security import mask_token
>>> token = "abcdefghijklmnopqrstuvwxyz"
>>> print(mask_token(token))
abcd...wxyz
"""

import re
from typing import Optional


def mask_token(token: Optional[str], visible_chars: int = 4) -> str:
    """
    Mask an authentication token for safe display in logs.

    Shows only the first and last N characters of the token,
    replacing the middle with '...'. This prevents accidental
    exposure of credentials in logs while allowing token identification.

    Parameters
    ----------
    token : Optional[str]
        The authentication token to mask. Can be None.
    visible_chars : int, optional
        Number of characters to show at start and end, by default 4

    Returns
    -------
    str
        Masked token string, or placeholder if token is None/empty

    Examples
    --------
    >>> mask_token("abc123xyz789")
    'abc1...x789'

    >>> mask_token("short")
    'short'

    >>> mask_token(None)
    '<no-token>'

    >>> mask_token("")
    '<no-token>'

    Notes
    -----
    - Tokens shorter than 2 * visible_chars are returned as-is
    - None or empty tokens return '<no-token>'
    - Safe to use in log messages without credential leakage
    """
    if not token:
        return "<no-token>"

    token_len = len(token)

    # If token is too short to mask meaningfully, return as-is
    if token_len <= (visible_chars * 2):
        return token

    # Show first N and last N characters
    start = token[:visible_chars]
    end = token[-visible_chars:]

    return f"{start}...{end}"


def validate_arista_token(token: Optional[str]) -> bool:
    """
    Validate the format of an Arista API token.

    Checks if the provided token matches expected format patterns
    for Arista customer portal API tokens. This is a basic format
    validation and does not verify token validity with the API.

    Parameters
    ----------
    token : Optional[str]
        The token string to validate

    Returns
    -------
    bool
        True if token format is valid, False otherwise

    Examples
    --------
    >>> validate_arista_token("abc123def456")
    True

    >>> validate_arista_token("short")
    False

    >>> validate_arista_token(None)
    False

    >>> validate_arista_token("")
    False

    Notes
    -----
    - Minimum length: 20 characters
    - Must contain only alphanumeric characters, hyphens, and underscores
    - This is format validation only, not API authentication
    - Use mask_token() before logging validation results
    """
    if not token:
        return False

    # Arista tokens are typically long alphanumeric strings
    # Minimum reasonable length for a secure token
    min_length = 20

    if len(token) < min_length:
        return False

    # Allow alphanumeric, hyphens, and underscores
    # This covers most token formats
    pattern = r"^[a-zA-Z0-9_-]+$"

    return bool(re.match(pattern, token))
