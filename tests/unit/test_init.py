#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods

"""Tests for eos_downloader package init module."""

import dataclasses
import json
from typing import Any

import pytest

from eos_downloader import (
    MSG_INVALID_DATA,
    MSG_TOKEN_EXPIRED,
    MSG_TOKEN_INVALID,
    EnhancedJSONEncoder,
    __author__,
    __email__,
    __version__,
)


class TestModuleMetadata:
    """Test suite for module metadata."""

    def test_version_exists(self) -> None:
        """Test that __version__ is defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_author_exists(self) -> None:
        """Test that __author__ is defined."""
        assert __author__ == "@titom73"

    def test_email_exists(self) -> None:
        """Test that __email__ is defined."""
        assert __email__ == "tom@inetsix.net"


class TestErrorMessages:
    """Test suite for error message constants."""

    def test_msg_token_expired_content(self) -> None:
        """Test MSG_TOKEN_EXPIRED contains expected content."""
        assert "API token has expired" in MSG_TOKEN_EXPIRED
        assert "arista.com" in MSG_TOKEN_EXPIRED
        assert "Regenerate Token" in MSG_TOKEN_EXPIRED

    def test_msg_token_invalid_content(self) -> None:
        """Test MSG_TOKEN_INVALID contains expected content."""
        assert "API token is incorrect" in MSG_TOKEN_INVALID
        assert "arista.com" in MSG_TOKEN_INVALID
        assert "Access Token" in MSG_TOKEN_INVALID

    def test_msg_invalid_data_content(self) -> None:
        """Test MSG_INVALID_DATA contains expected content."""
        assert "Invalid data" in MSG_INVALID_DATA


class TestEnhancedJSONEncoder:
    """Test suite for EnhancedJSONEncoder class."""

    def test_encode_simple_dict(self) -> None:
        """Test encoding a simple dictionary."""
        data = {"key": "value", "number": 42}
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        assert result == '{"key": "value", "number": 42}'

    def test_encode_nested_dict(self) -> None:
        """Test encoding a nested dictionary."""
        data = {"outer": {"inner": "value"}}
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        assert '"outer"' in result
        assert '"inner"' in result

    def test_encode_list(self) -> None:
        """Test encoding a list."""
        data = [1, 2, 3, "four"]
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        assert result == '[1, 2, 3, "four"]'

    def test_encode_dataclass(self) -> None:
        """Test encoding a dataclass object."""

        @dataclasses.dataclass
        class SampleDataclass:
            """Sample dataclass for testing."""

            name: str
            value: int
            active: bool

        obj = SampleDataclass(name="test", value=123, active=True)
        result = json.dumps(obj, cls=EnhancedJSONEncoder)
        parsed = json.loads(result)

        assert parsed["name"] == "test"
        assert parsed["value"] == 123
        assert parsed["active"] is True

    def test_encode_nested_dataclass(self) -> None:
        """Test encoding nested dataclasses."""

        @dataclasses.dataclass
        class InnerDataclass:
            """Inner dataclass for testing."""

            field: str

        @dataclasses.dataclass
        class OuterDataclass:
            """Outer dataclass for testing."""

            inner: InnerDataclass
            count: int

        obj = OuterDataclass(inner=InnerDataclass(field="nested"), count=5)
        result = json.dumps(obj, cls=EnhancedJSONEncoder)
        parsed = json.loads(result)

        assert parsed["inner"]["field"] == "nested"
        assert parsed["count"] == 5

    def test_encode_dataclass_with_list(self) -> None:
        """Test encoding a dataclass containing a list."""

        @dataclasses.dataclass
        class DataclassWithList:
            """Dataclass with list field."""

            items: list[str]
            count: int

        obj = DataclassWithList(items=["a", "b", "c"], count=3)
        result = json.dumps(obj, cls=EnhancedJSONEncoder)
        parsed = json.loads(result)

        assert parsed["items"] == ["a", "b", "c"]
        assert parsed["count"] == 3

    def test_encode_unsupported_type_raises_error(self) -> None:
        """Test that encoding unsupported types raises TypeError."""

        class CustomClass:
            """Custom class that is not JSON serializable."""

            def __init__(self, value: Any) -> None:
                self.value = value

        obj = CustomClass(value="test")

        with pytest.raises(TypeError):
            json.dumps(obj, cls=EnhancedJSONEncoder)

    def test_encode_dataclass_with_optional_none(self) -> None:
        """Test encoding a dataclass with Optional field set to None."""
        from typing import Optional

        @dataclasses.dataclass
        class DataclassWithOptional:
            """Dataclass with optional field."""

            required: str
            optional: Optional[str] = None

        obj = DataclassWithOptional(required="value", optional=None)
        result = json.dumps(obj, cls=EnhancedJSONEncoder)
        parsed = json.loads(result)

        assert parsed["required"] == "value"
        assert parsed["optional"] is None

    def test_encode_mixed_content(self) -> None:
        """Test encoding mixed content with dataclass in dict."""

        @dataclasses.dataclass
        class SimpleDataclass:
            """Simple dataclass."""

            id: int
            name: str

        data = {
            "string": "value",
            "number": 42,
            "dataclass": SimpleDataclass(id=1, name="item"),
        }
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        parsed = json.loads(result)

        assert parsed["string"] == "value"
        assert parsed["number"] == 42
        assert parsed["dataclass"]["id"] == 1
        assert parsed["dataclass"]["name"] == "item"
