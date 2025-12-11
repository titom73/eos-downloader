#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Tests for eos_downloader.helpers.security module.

Tests the security utility functions including token masking
and validation.
"""

import pytest
from eos_downloader.helpers.security import mask_token, validate_arista_token


class TestMaskToken:
    """Test suite for mask_token function."""

    def test_mask_token_standard(self) -> None:
        """Test masking a standard-length token."""
        token = "abcdefghijklmnopqrstuvwxyz"
        result = mask_token(token)
        assert result == "abcd...wxyz"
        assert len(result) == 11  # 4 + 3 + 4

    def test_mask_token_custom_visible_chars(self) -> None:
        """Test masking with custom visible character count."""
        token = "abcdefghijklmnopqrstuvwxyz"
        result = mask_token(token, visible_chars=6)
        assert result == "abcdef...uvwxyz"

    def test_mask_token_short(self) -> None:
        """Test that short tokens are not masked."""
        token = "short"
        result = mask_token(token)
        assert result == "short"

    def test_mask_token_none(self) -> None:
        """Test masking None returns placeholder."""
        result = mask_token(None)
        assert result == "<no-token>"

    def test_mask_token_empty(self) -> None:
        """Test masking empty string returns placeholder."""
        result = mask_token("")
        assert result == "<no-token>"

    def test_mask_token_exactly_double_visible(self) -> None:
        """Test token exactly 2x visible_chars long."""
        token = "12345678"  # 8 chars with visible_chars=4
        result = mask_token(token, visible_chars=4)
        assert result == "12345678"  # Not masked

    def test_mask_token_real_world_example(self) -> None:
        """Test with a realistic token format."""
        token = "sk_test_1234567890abcdefghijklmnop"
        result = mask_token(token)
        assert result.startswith("sk_t")
        assert result.endswith("mnop")
        assert "..." in result


class TestValidateAristaToken:
    """Test suite for validate_arista_token function."""

    def test_validate_valid_token(self) -> None:
        """Test validation of a valid token format."""
        token = "abc123def456ghi789jkl012"
        assert validate_arista_token(token) is True

    def test_validate_token_with_hyphens(self) -> None:
        """Test validation of token with hyphens."""
        token = "abc123-def456-ghi789-jkl012"
        assert validate_arista_token(token) is True

    def test_validate_token_with_underscores(self) -> None:
        """Test validation of token with underscores."""
        token = "abc123_def456_ghi789_jkl012"
        assert validate_arista_token(token) is True

    def test_validate_token_too_short(self) -> None:
        """Test that short tokens are invalid."""
        token = "short"
        assert validate_arista_token(token) is False

    def test_validate_token_minimum_length(self) -> None:
        """Test token at minimum valid length."""
        token = "a" * 20  # Exactly 20 chars
        assert validate_arista_token(token) is True

    def test_validate_token_below_minimum(self) -> None:
        """Test token below minimum length."""
        token = "a" * 19  # Just under 20 chars
        assert validate_arista_token(token) is False

    def test_validate_token_none(self) -> None:
        """Test that None is invalid."""
        assert validate_arista_token(None) is False

    def test_validate_token_empty(self) -> None:
        """Test that empty string is invalid."""
        assert validate_arista_token("") is False

    def test_validate_token_with_spaces(self) -> None:
        """Test that tokens with spaces are invalid."""
        token = "abc 123 def 456 ghi 789 jkl 012"
        assert validate_arista_token(token) is False

    def test_validate_token_with_special_chars(self) -> None:
        """Test that tokens with special characters are invalid."""
        token = "abc123@def456#ghi789$jkl012"
        assert validate_arista_token(token) is False

    def test_validate_token_real_world_format(self) -> None:
        """Test with realistic Arista token format."""
        token = "sk_test_1234567890abcdefghijklmnopqrstuvwxyz"
        assert validate_arista_token(token) is True


class TestSecurityIntegration:
    """Integration tests for security module."""

    def test_mask_and_validate_workflow(self) -> None:
        """Test typical workflow: validate then mask."""
        token = "abc123def456ghi789jkl012mno345"

        # Validate token
        is_valid = validate_arista_token(token)
        assert is_valid is True

        # Mask for logging
        masked = mask_token(token)
        assert masked.startswith("abc1")
        assert masked.endswith("o345")
        assert "..." in masked

        # Ensure masked version is different from original
        assert masked != token

    def test_mask_invalid_token(self) -> None:
        """Test masking an invalid token format."""
        token = "short"

        # Token is invalid
        is_valid = validate_arista_token(token)
        assert is_valid is False

        # But can still be masked (doesn't check validity)
        masked = mask_token(token)
        assert masked == "short"  # Too short to mask
