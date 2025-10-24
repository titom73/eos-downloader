#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
"""
Tests for eos_downloader.cli.get.utils module.

This module contains comprehensive tests for all utility functions used
by the get commands, including version search, download, and Docker import.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from eos_downloader.cli.get.utils import (
    download_files,
    handle_docker_import,
    initialize,
    search_version,
)
from eos_downloader.models.version import EosVersion


# Fixtures


@pytest.fixture
def mock_context():
    """Provide a mock Click context."""
    ctx = Mock()
    ctx.obj = {
        "token": "test-token-abc123",
        "log_level": "info",
        "debug": False,
    }
    return ctx


@pytest.fixture
def mock_console():
    """Provide a mock Rich Console."""
    console = MagicMock()
    return console


@pytest.fixture
def mock_arista_dl_obj():
    """Provide a mock AristaDownloadManager object."""
    dl_obj = MagicMock()
    dl_obj.download_file = MagicMock(return_value=Path("/tmp/test.swi"))
    dl_obj.verify_checksum = MagicMock(return_value=True)
    return dl_obj


# Test Classes


class TestInitialize:
    """Test suite for initialize function."""

    def test_initialize_extracts_context(self, mock_context):
        """Test that initialize correctly extracts context values."""
        console, token, debug, log_level = initialize(mock_context)

        assert token == "test-token-abc123"
        assert log_level == "info"
        assert debug is False

    def test_initialize_with_debug_mode(self):
        """Test initialize with debug mode enabled."""
        ctx = Mock()
        ctx.obj = {
            "token": "debug-token",
            "log_level": "debug",
            "debug": True,
        }

        console, token, debug, log_level = initialize(ctx)

        assert token == "debug-token"
        assert log_level == "debug"
        assert debug is True


class TestSearchVersion:
    """Test suite for search_version function."""

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_specific_version(self, mock_querier_class):
        """Test searching for a specific version."""
        # Setup
        mock_console = MagicMock()
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier

        # Execute
        result = search_version(
            console=mock_console,
            token="test-token",
            version="4.29.3M",
            latest=False,
            branch=None,
            file_format="64",
            release_type="M",
        )

        # Assert
        assert result == "4.29.3M"
        # Should not call AristaXmlQuerier for specific version
        mock_querier_class.assert_not_called()

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_latest_version(self, mock_querier_class):
        """Test searching for the latest version."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_version = EosVersion.from_str("4.30.1F")
        mock_querier.latest.return_value = mock_version

        # Execute
        result = search_version(
            console=MagicMock(),
            token="test-token",
            version=None,
            latest=True,
            branch=None,
            file_format="64",
            release_type="",  # Empty string instead of None
        )

        # Assert
        assert result == "4.30.1F"  # Latest version as string
        mock_querier.latest.assert_called_once_with(
            package="eos",
            branch=None,
            rtype="F",  # Default to Feature
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_by_branch(self, mock_querier_class):
        """Test searching by branch."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_version = EosVersion.from_str("4.29.3M")
        mock_querier.latest.return_value = mock_version

        # Execute
        result = search_version(
            console=MagicMock(),
            token="test-token",
            version=None,
            latest=True,
            branch="4.29",
            file_format="64",
            release_type=None,
        )

        # Assert
        assert result == "4.29.3M"
        mock_querier.latest.assert_called_once_with(
            package="eos",
            branch="4.29",
            rtype="F",
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_with_invalid_release_type_defaults(
        self, mock_querier_class
    ):
        """Test that invalid release type defaults to feature."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_version = EosVersion.from_str("4.29.3M")
        mock_querier.latest.return_value = mock_version

        # Execute
        search_version(
            console=MagicMock(),
            token="test-token",
            version=None,
            latest=True,
            branch=None,
            file_format="64",
            release_type="invalid",  # Invalid type
        )

        # Assert - should call latest with feature type
        mock_querier.latest.assert_called_once_with(
            package="eos",
            branch=None,
            rtype="F",  # Should default to feature
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_latest_with_branch_and_release_type(
        self, mock_querier_class
    ):
        """Test searching latest with both branch and release type."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_version = EosVersion.from_str("4.29.3M")
        mock_querier.latest.return_value = mock_version

        # Execute
        result = search_version(
            console=MagicMock(),
            token="test-token",
            version=None,
            latest=True,
            branch="4.29",
            file_format="64",
            release_type="M",
        )

        # Assert
        assert result == "4.29.3M"
        mock_querier.latest.assert_called_once_with(
            package="eos",
            branch="4.29",
            rtype="M",
        )


class TestDownloadFiles:
    """Test suite for download_files function."""

    def test_download_files_success(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test successful file download."""
        # Setup
        output_path = tmp_path
        mock_cli = MagicMock()
        # Mock downloads to return tuple (path, was_cached)
        mock_cli.downloads.return_value = (str(output_path), False)

        # Execute
        download_files(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(output_path),
            rich_interface=True,
            debug=False,
            checksum_format="sha512sum",
        )

        # Assert - Function should execute without error
        # Check that cli.downloads() was called
        mock_cli.downloads.assert_called_once_with(
            mock_arista_dl_obj, file_path=str(output_path), rich_interface=True
        )
        mock_cli.checksum.assert_called_once_with("sha512sum")

    def test_download_files_with_custom_checksum(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download with custom checksum format."""
        # Setup
        output_path = tmp_path
        checksum = "sha256sum"
        mock_cli = MagicMock()
        # Mock downloads to return tuple (path, was_cached)
        mock_cli.downloads.return_value = (str(output_path), False)

        # Execute
        download_files(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(output_path),
            rich_interface=True,
            debug=False,
            checksum_format=checksum,
        )

        # Assert
        mock_cli.checksum.assert_called_once_with(checksum)

    def test_download_files_checksum_error(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download with checksum verification failure."""
        # Setup
        mock_cli = MagicMock()
        # Mock downloads to return tuple (path, was_cached)
        mock_cli.downloads.return_value = (str(tmp_path), False)
        mock_cli.checksum.side_effect = subprocess.CalledProcessError(
            1, "checksum"
        )

        # Execute - should not raise exception
        download_files(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            rich_interface=True,
            debug=False,
            checksum_format="sha512sum",
        )

        # Assert that checksum was called despite error
        mock_cli.checksum.assert_called_once_with("sha512sum")

    def test_download_files_checksum_error_debug_mode(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test checksum failure in debug mode prints exception details."""
        # Setup
        mock_cli = MagicMock()
        # Mock downloads to return tuple (path, was_cached)
        mock_cli.downloads.return_value = (str(tmp_path), False)
        mock_cli.checksum.side_effect = subprocess.CalledProcessError(
            1, "checksum"
        )

        # Execute
        download_files(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            rich_interface=True,
            debug=True,  # Enable debug mode
            checksum_format="sha512sum",
        )

        # Assert that print_exception was called in debug mode
        mock_console.print_exception.assert_called_once_with(show_locals=True)

    def test_download_files_no_rich_interface(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download without Rich interface."""
        # Setup
        mock_cli = MagicMock()
        # Mock downloads to return tuple (path, was_cached)
        mock_cli.downloads.return_value = (str(tmp_path), False)

        # Execute
        download_files(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            rich_interface=False,  # Disable Rich interface
            debug=False,
            checksum_format="sha512sum",
        )

        # Assert - cli.downloads should be called with rich_interface=False
        mock_cli.downloads.assert_called_once_with(
            mock_arista_dl_obj, file_path=str(tmp_path), rich_interface=False
        )


class TestHandleDockerImport:
    """Test suite for handle_docker_import function."""

    def test_docker_import_success(
        self, mock_console, tmp_path
    ):
        """Test successful Docker image import."""
        # Setup
        test_file = tmp_path / "cEOS-lab-4.29.3M.tar.xz"
        test_file.touch()
        docker_name = "arista/ceos"
        docker_tag = "4.29.3M"

        mock_cli = MagicMock()
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = "cEOS-lab-4.29.3M.tar.xz"
        mock_arista_dl_obj.version = "4.29.3M"

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            docker_name=docker_name,
            docker_tag=docker_tag,
            debug=False,
        )

        # Assert
        assert result == 0
        mock_cli.import_docker.assert_called_once_with(
            local_file_path=str(tmp_path / "cEOS-lab-4.29.3M.tar.xz"),
            docker_name=docker_name,
            docker_tag=docker_tag,
            force=False,
        )

    def test_docker_import_with_default_tag(
        self, mock_console, tmp_path
    ):
        """Test Docker import with default tag from version when None specified."""
        # Setup
        test_file = tmp_path / "cEOS-lab-4.29.3M.tar.xz"
        test_file.touch()
        docker_name = "arista/ceos"

        mock_cli = MagicMock()
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = "cEOS-lab-4.29.3M.tar.xz"
        mock_arista_dl_obj.version = "4.29.3M"

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            docker_name=docker_name,
            docker_tag=None,  # No tag specified, should use version
            debug=False,
        )

        # Assert - should use arista_dl_obj.version as default tag
        assert result == 0
        mock_cli.import_docker.assert_called_once_with(
            local_file_path=str(tmp_path / "cEOS-lab-4.29.3M.tar.xz"),
            docker_name=docker_name,
            docker_tag="4.29.3M",  # Should use version as default tag
            force=False,
        )

    def test_docker_import_file_not_found(self, mock_console, tmp_path):
        """Test Docker import with non-existent file returns error code."""
        # Setup
        mock_cli = MagicMock()
        mock_cli.import_docker.side_effect = FileNotFoundError("File not found")
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = "nonexistent.tar.xz"

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            docker_name="arista/ceos",
            docker_tag="latest",
            debug=False,
        )

        # Assert - should return 1 on FileNotFoundError
        assert result == 1

    def test_docker_import_file_not_found_debug_mode(
        self, mock_console, tmp_path
    ):
        """Test file not found in debug mode prints exception details."""
        # Setup
        mock_cli = MagicMock()
        mock_cli.import_docker.side_effect = FileNotFoundError("File not found")
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = "nonexistent.tar.xz"

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            docker_name="arista/ceos",
            docker_tag="latest",
            debug=True,  # Debug mode
        )

        # Assert - should return 1 and print exception details
        assert result == 1
        mock_console.print_exception.assert_called_once_with(show_locals=True)

    def test_docker_import_invalid_filename(
        self, mock_console, tmp_path
    ):
        """Test Docker import with None filename returns error."""
        # Setup
        mock_cli = MagicMock()
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = None  # Invalid filename

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(tmp_path),
            docker_name="arista/ceos",
            docker_tag="latest",
            debug=False,
        )

        # Assert - should return 1 for invalid filename
        assert result == 1
        # Should not call import_docker when filename is None
        mock_cli.import_docker.assert_not_called()

    def test_docker_import_with_custom_output_path(
        self, mock_console, tmp_path
    ):
        """Test Docker import with custom output path."""
        # Setup
        test_file = tmp_path / "custom" / "cEOS-lab-4.29.3M.tar.xz"
        test_file.parent.mkdir(parents=True)
        test_file.touch()
        custom_output = tmp_path / "custom"

        mock_cli = MagicMock()
        mock_arista_dl_obj = MagicMock()
        mock_arista_dl_obj.filename = "cEOS-lab-4.29.3M.tar.xz"
        mock_arista_dl_obj.version = "4.29.3M"

        # Execute
        result = handle_docker_import(
            console=mock_console,
            cli=mock_cli,
            arista_dl_obj=mock_arista_dl_obj,
            output=str(custom_output),
            docker_name="arista/ceos",
            docker_tag="4.29.3M",
            debug=False,
        )

        # Assert - should use custom output path
        assert result == 0
        expected_path = str(custom_output / "cEOS-lab-4.29.3M.tar.xz")
        mock_cli.import_docker.assert_called_once_with(
            local_file_path=expected_path,
            docker_name="arista/ceos",
            docker_tag="4.29.3M",
            force=False,
        )
