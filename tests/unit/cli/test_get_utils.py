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
        token, log_level, debug = initialize(mock_context)

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

        token, log_level, debug = initialize(ctx)

        assert token == "debug-token"
        assert log_level == "debug"
        assert debug is True


class TestSearchVersion:
    """Test suite for search_version function."""

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_specific_version(self, mock_querier_class):
        """Test searching for a specific version."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        expected_version = EosVersion.from_str("4.29.3M")

        # Execute
        result = search_version(
            token="test-token",
            package="eos",
            version="4.29.3M",
            latest=None,
            branch=None,
            release_type="M",
        )

        # Assert
        assert result == expected_version
        mock_querier_class.assert_called_once_with(token="test-token")
        # Should not call available_public_versions for specific version
        mock_querier.available_public_versions.assert_not_called()

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_latest_version(self, mock_querier_class):
        """Test searching for the latest version."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_versions = [
            EosVersion.from_str("4.29.3M"),
            EosVersion.from_str("4.30.1F"),
        ]
        mock_querier.available_public_versions.return_value = mock_versions

        # Execute
        result = search_version(
            token="test-token",
            package="eos",
            version=None,
            latest=True,
            branch=None,
            release_type=None,
        )

        # Assert
        assert result == EosVersion.from_str("4.30.1F")  # Latest version
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos",
            branch=None,
            rtype=None,
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_by_branch(self, mock_querier_class):
        """Test searching by branch."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_versions = [
            EosVersion.from_str("4.29.2M"),
            EosVersion.from_str("4.29.3M"),
        ]
        mock_querier.available_public_versions.return_value = mock_versions

        # Execute
        result = search_version(
            token="test-token",
            package="eos",
            version=None,
            latest=True,
            branch="4.29",
            release_type=None,
        )

        # Assert
        assert result == EosVersion.from_str("4.29.3M")
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos",
            branch="4.29",
            rtype=None,
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_with_invalid_release_type_defaults(
        self, mock_querier_class
    ):
        """Test that invalid release type defaults to None."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_versions = [EosVersion.from_str("4.29.3M")]
        mock_querier.available_public_versions.return_value = mock_versions

        # Execute
        result = search_version(
            token="test-token",
            package="eos",
            version=None,
            latest=True,
            branch=None,
            release_type="invalid",  # Invalid type
        )

        # Assert
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos",
            branch=None,
            rtype=None,  # Should default to None
        )

    @patch("eos_downloader.cli.get.utils.AristaXmlQuerier")
    def test_search_latest_with_branch_and_release_type(
        self, mock_querier_class
    ):
        """Test searching latest with both branch and release type."""
        # Setup
        mock_querier = MagicMock()
        mock_querier_class.return_value = mock_querier
        mock_versions = [
            EosVersion.from_str("4.29.1M"),
            EosVersion.from_str("4.29.3M"),
        ]
        mock_querier.available_public_versions.return_value = mock_versions

        # Execute
        result = search_version(
            token="test-token",
            package="eos",
            version=None,
            latest=True,
            branch="4.29",
            release_type="M",
        )

        # Assert
        assert result == EosVersion.from_str("4.29.3M")
        mock_querier.available_public_versions.assert_called_once_with(
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
        version = EosVersion.from_str("4.29.3M")
        image = "64"
        output_path = tmp_path

        # Execute
        result = download_files(
            downloader=mock_arista_dl_obj,
            console=mock_console,
            version=version,
            image=image,
            output_path=output_path,
            rich_interface=True,
            checksum=None,
            debug=False,
        )

        # Assert
        assert result is not None
        mock_arista_dl_obj.download_file.assert_called_once()
        mock_arista_dl_obj.verify_checksum.assert_called_once()

    def test_download_files_with_custom_checksum(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download with custom checksum format."""
        # Setup
        version = EosVersion.from_str("4.29.3M")
        image = "64"
        output_path = tmp_path
        checksum = "sha512sum"

        # Execute
        result = download_files(
            downloader=mock_arista_dl_obj,
            console=mock_console,
            version=version,
            image=image,
            output_path=output_path,
            rich_interface=True,
            checksum=checksum,
            debug=False,
        )

        # Assert
        mock_arista_dl_obj.verify_checksum.assert_called_once()
        call_args = mock_arista_dl_obj.verify_checksum.call_args
        assert checksum in str(call_args)

    def test_download_files_checksum_error(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download with checksum verification failure."""
        # Setup
        mock_arista_dl_obj.verify_checksum.return_value = False
        version = EosVersion.from_str("4.29.3M")

        # Execute & Assert
        with pytest.raises(SystemExit):
            download_files(
                downloader=mock_arista_dl_obj,
                console=mock_console,
                version=version,
                image="64",
                output_path=tmp_path,
                rich_interface=True,
                checksum=None,
                debug=False,
            )

    def test_download_files_checksum_error_debug_mode(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test checksum failure in debug mode raises exception."""
        # Setup
        mock_arista_dl_obj.verify_checksum.return_value = False
        version = EosVersion.from_str("4.29.3M")

        # Execute & Assert
        with pytest.raises(ValueError):
            download_files(
                downloader=mock_arista_dl_obj,
                console=mock_console,
                version=version,
                image="64",
                output_path=tmp_path,
                rich_interface=True,
                checksum=None,
                debug=True,  # Debug mode
            )

    def test_download_files_no_rich_interface(
        self, mock_arista_dl_obj, mock_console, tmp_path
    ):
        """Test download without Rich interface."""
        # Setup
        version = EosVersion.from_str("4.29.3M")

        # Execute
        result = download_files(
            downloader=mock_arista_dl_obj,
            console=mock_console,
            version=version,
            image="64",
            output_path=tmp_path,
            rich_interface=False,  # No Rich interface
            checksum=None,
            debug=False,
        )

        # Assert
        assert result is not None
        mock_arista_dl_obj.download_file.assert_called_once()


class TestHandleDockerImport:
    """Test suite for handle_docker_import function."""

    @patch("subprocess.run")
    def test_docker_import_success(
        self, mock_subprocess, mock_console, tmp_path
    ):
        """Test successful Docker image import."""
        # Setup
        test_file = tmp_path / "cEOS-lab-4.29.3M.tar.xz"
        test_file.touch()
        docker_name = "arista/ceos"
        docker_tag = "4.29.3M"

        # Execute
        handle_docker_import(
            console=mock_console,
            filename=test_file,
            docker_name=docker_name,
            docker_tag=docker_tag,
            output_path=tmp_path,
            debug=False,
        )

        # Assert
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "docker" in call_args
        assert "import" in call_args
        assert docker_name in call_args[3]
        assert docker_tag in call_args[3]

    @patch("subprocess.run")
    def test_docker_import_with_default_tag(
        self, mock_subprocess, mock_console, tmp_path
    ):
        """Test Docker import with default tag."""
        # Setup
        test_file = tmp_path / "cEOS-lab-4.29.3M.tar.xz"
        test_file.touch()
        docker_name = "arista/ceos"

        # Execute
        handle_docker_import(
            console=mock_console,
            filename=test_file,
            docker_name=docker_name,
            docker_tag=None,  # No tag specified
            output_path=tmp_path,
            debug=False,
        )

        # Assert
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "latest" in call_args[3]  # Should use "latest" as default

    def test_docker_import_file_not_found(self, mock_console, tmp_path):
        """Test Docker import with non-existent file."""
        # Setup
        nonexistent_file = tmp_path / "nonexistent.tar.xz"

        # Execute & Assert
        with pytest.raises(SystemExit):
            handle_docker_import(
                console=mock_console,
                filename=nonexistent_file,
                docker_name="arista/ceos",
                docker_tag="latest",
                output_path=tmp_path,
                debug=False,
            )

    def test_docker_import_file_not_found_debug_mode(
        self, mock_console, tmp_path
    ):
        """Test file not found in debug mode raises exception."""
        # Setup
        nonexistent_file = tmp_path / "nonexistent.tar.xz"

        # Execute & Assert
        with pytest.raises(FileNotFoundError):
            handle_docker_import(
                console=mock_console,
                filename=nonexistent_file,
                docker_name="arista/ceos",
                docker_tag="latest",
                output_path=tmp_path,
                debug=True,  # Debug mode
            )

    @patch("subprocess.run")
    def test_docker_import_invalid_filename(
        self, mock_subprocess, mock_console, tmp_path
    ):
        """Test Docker import with invalid filename."""
        # Setup
        test_file = tmp_path / "invalid-file.txt"
        test_file.touch()

        # Execute
        handle_docker_import(
            console=mock_console,
            filename=test_file,
            docker_name="arista/ceos",
            docker_tag="latest",
            output_path=tmp_path,
            debug=False,
        )

        # Assert - should still call docker import
        mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_docker_import_with_custom_output_path(
        self, mock_subprocess, mock_console, tmp_path
    ):
        """Test Docker import with custom output path."""
        # Setup
        test_file = tmp_path / "cEOS-lab-4.29.3M.tar.xz"
        test_file.touch()
        custom_output = tmp_path / "custom"
        custom_output.mkdir()

        # Execute
        handle_docker_import(
            console=mock_console,
            filename=test_file,
            docker_name="arista/ceos",
            docker_tag="4.29.3M",
            output_path=custom_output,
            debug=False,
        )

        # Assert
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert str(test_file) in call_args
