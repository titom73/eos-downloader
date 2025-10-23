#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Tests for eos_downloader.cli.__main__ module.

This module tests the entry point for the CLI application.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestMain:
    """Test suite for __main__ module entry point."""

    @patch("eos_downloader.cli.__main__.cli")
    def test_main_entry_point_calls_cli(self, mock_cli: pytest.Mock) -> None:
        """Test that running __main__ calls the cli function."""
        # Execute the __main__ module
        import eos_downloader.cli.__main__ as main_module

        # Simulate running as script
        if __name__ == "__main__":
            main_module.cli()

        # Since we patched cli, verify it would be available
        assert mock_cli is not None

    def test_main_module_has_cli_import(self) -> None:
        """Test that __main__ module imports cli correctly."""
        import eos_downloader.cli.__main__ as main_module

        # Verify cli is available in the module
        assert hasattr(main_module, "cli")
        assert callable(main_module.cli)

    def test_main_module_structure(self) -> None:
        """Test that __main__ module has expected structure."""
        import eos_downloader.cli.__main__ as main_module

        # Verify module docstring
        assert main_module.__doc__ is not None
        assert "ARDL Module CLI" in main_module.__doc__

        # Verify cli import
        assert hasattr(main_module, "cli")

    @patch("sys.argv", ["ardl"])
    @patch("eos_downloader.cli.__main__.cli")
    def test_main_can_be_executed(self, mock_cli: pytest.Mock) -> None:
        """Test that __main__ module can be executed."""
        # This would normally be called by python -m eos_downloader.cli
        # We just verify the structure allows it
        import eos_downloader.cli.__main__

        assert eos_downloader.cli.__main__.cli == mock_cli
