#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods

"""Tests for eos_downloader.tools module."""

import pytest

from eos_downloader.tools import exc_to_str


class TestExcToStr:
    """Test suite for exc_to_str function."""

    def test_exception_with_message(self) -> None:
        """Test exc_to_str with an exception that has a message."""
        exception = ValueError("This is an error message")
        result = exc_to_str(exception)
        assert result == "ValueError (This is an error message)"

    def test_exception_without_message(self) -> None:
        """Test exc_to_str with an exception without a message."""
        exception = ValueError()
        result = exc_to_str(exception)
        assert result == "ValueError"

    def test_exception_with_empty_message(self) -> None:
        """Test exc_to_str with an exception with empty string message."""
        exception = ValueError("")
        result = exc_to_str(exception)
        assert result == "ValueError"

    def test_runtime_error(self) -> None:
        """Test exc_to_str with RuntimeError."""
        exception = RuntimeError("Runtime issue")
        result = exc_to_str(exception)
        assert result == "RuntimeError (Runtime issue)"

    def test_type_error(self) -> None:
        """Test exc_to_str with TypeError."""
        exception = TypeError("Type mismatch")
        result = exc_to_str(exception)
        assert result == "TypeError (Type mismatch)"

    def test_key_error(self) -> None:
        """Test exc_to_str with KeyError."""
        exception = KeyError("missing_key")
        result = exc_to_str(exception)
        assert result == "KeyError ('missing_key')"

    def test_custom_exception(self) -> None:
        """Test exc_to_str with a custom exception class."""

        class CustomError(Exception):
            """Custom exception for testing."""

        exception = CustomError("Custom error occurred")
        result = exc_to_str(exception)
        assert result == "CustomError (Custom error occurred)"

    def test_os_error(self) -> None:
        """Test exc_to_str with OSError."""
        exception = OSError("File not found")
        result = exc_to_str(exception)
        assert result == "OSError (File not found)"

    def test_attribute_error(self) -> None:
        """Test exc_to_str with AttributeError."""
        exception = AttributeError("object has no attribute 'foo'")
        result = exc_to_str(exception)
        assert result == "AttributeError (object has no attribute 'foo')"

    def test_exception_with_multiline_message(self) -> None:
        """Test exc_to_str with multiline error message."""
        exception = ValueError("Line 1\nLine 2\nLine 3")
        result = exc_to_str(exception)
        assert result == "ValueError (Line 1\nLine 2\nLine 3)"
