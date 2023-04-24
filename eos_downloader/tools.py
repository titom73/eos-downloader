#!/usr/bin/python
# coding: utf-8 -*-

"""Module for tools related to ardl"""


def exc_to_str(exception: Exception) -> str:
    """
    Helper function to parse Exceptions
    """
    return (
        f"{type(exception).__name__}{f' ({str(exception)})' if str(exception) else ''}"
    )
