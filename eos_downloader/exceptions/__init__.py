# coding: utf-8 -*-
"""Exceptions module for eos_downloader package."""


class AuthenticationError(Exception):
    """Erxception when authentication fails."""


class AristaServerError(Exception):
    """Exception returned when an error occured on server side."""
