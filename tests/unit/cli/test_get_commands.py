#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
"""
Tests for eos_downloader.cli.get.commands module.

This module contains comprehensive tests for all get commands including
eos, cvp, and path download commands.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from eos_downloader.cli.get.commands import cvp, eos, path


# Fixtures


@pytest.fixture
def runner() -> CliRunner:
    """Provide a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_context() -> dict:
    """Provide a mock context dictionary."""
    return {
        "token": "test-token-abc123",
        "log_level": "info",
        "debug": False,
    }


@pytest.fixture
def mock_eos_xml_object() -> MagicMock:
    """Provide a mock EosXmlObject."""
    mock_obj = MagicMock()
    mock_obj.searched_version = "4.29.3M"
    mock_obj.image_type = "64"
    mock_obj.filename = "EOS-4.29.3M.swi"
    return mock_obj


@pytest.fixture
def mock_cvp_xml_object() -> MagicMock:
    """Provide a mock CvpXmlObject."""
    mock_obj = MagicMock()
    mock_obj.searched_version = "2024.3.0"
    mock_obj.image_type = "ova"
    mock_obj.filename = "cvp-2024.3.0.ova"
    return mock_obj


# Test Classes


class TestEosCommand:
    """Test suite for eos download command."""

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_eos_command_basic_download(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test basic EOS download command."""
        # Setup mocks
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"
        mock_eos_instance = MagicMock()
        mock_eos_xml.return_value = mock_eos_instance

        # Execute
        result = runner.invoke(
            eos,
            ["--version", "4.29.3M"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_search.assert_called_once()
        mock_eos_xml.assert_called_once()
        mock_download_files.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_eos_command_with_latest_flag(
        self,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS download with --latest flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.30.1F"

        # Execute
        with patch("eos_downloader.cli.get.commands.download_files"):
            result = runner.invoke(
                eos,
                ["--latest"],
                obj=mock_context,
            )

        # Assert
        assert result.exit_code == 0
        mock_search.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_eos_command_with_branch(
        self,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS download with --branch option."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.5M"

        # Execute
        with patch("eos_downloader.cli.get.commands.download_files"):
            result = runner.invoke(
                eos,
                ["--latest", "--branch", "4.29"],
                obj=mock_context,
            )

        # Assert
        assert result.exit_code == 0

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_eos_command_with_eve_ng(
        self,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS download with --eve-ng flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"
        mock_cli = MagicMock()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            eos,
            ["--version", "4.29.3M", "--eve-ng"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_cli.provision_eve.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.handle_docker_import")
    def test_eos_command_with_docker_import(
        self,
        mock_docker_import: Mock,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS download with --import-docker flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"
        mock_docker_import.return_value = 0

        # Execute
        with patch("eos_downloader.cli.get.commands.download_files"):
            result = runner.invoke(
                eos,
                [
                    "--version",
                    "4.29.3M",
                    "--import-docker",
                    "--docker-name",
                    "arista/ceos",
                    "--docker-tag",
                    "4.29.3M",
                ],
                obj=mock_context,
            )

        # Assert
        assert result.exit_code == 0
        mock_docker_import.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    def test_eos_command_with_skip_download(
        self,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS command with --skip-download flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"

        # Execute
        with patch("eos_downloader.cli.get.commands.SoftManager"):
            result = runner.invoke(
                eos,
                ["--version", "4.29.3M", "--skip-download"],
                obj=mock_context,
            )

        # Assert
        assert result.exit_code == 0

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    def test_eos_command_with_dry_run(
        self,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS command with --dry-run flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"

        # Execute
        with patch("eos_downloader.cli.get.commands.SoftManager") as mock_sm:
            with patch("eos_downloader.cli.get.commands.download_files"):
                result = runner.invoke(
                    eos,
                    ["--version", "4.29.3M", "--dry-run"],
                    obj=mock_context,
                )

        # Assert
        assert result.exit_code == 0
        mock_sm.assert_called_once_with(dry_run=True)

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    def test_eos_command_version_not_found(
        self,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS command when version is None."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = None

        # Execute
        result = runner.invoke(
            eos,
            ["--latest"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code != 0
        assert isinstance(result.exception, ValueError)

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    def test_eos_command_xml_object_creation_error(
        self,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS command when EosXmlObject creation fails."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"
        mock_eos_xml.side_effect = Exception("XML creation failed")

        # Execute
        result = runner.invoke(
            eos,
            ["--version", "4.29.3M"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_eos_command_eve_ng_provision_error(
        self,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EOS command when EVE-NG provisioning fails."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_search.return_value = "4.29.3M"
        mock_cli = MagicMock()
        mock_cli.provision_eve.side_effect = Exception("EVE-NG error")
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            eos,
            ["--version", "4.29.3M", "--eve-ng"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_eos_command_eve_ng_provision_error_debug_mode(
        self,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test EVE-NG provisioning error in debug mode."""
        # Setup
        mock_console = MagicMock()
        mock_context["debug"] = True
        mock_init.return_value = (
            mock_console,
            "test-token",
            True,
            "debug",
        )
        mock_search.return_value = "4.29.3M"
        mock_cli = MagicMock()
        mock_cli.provision_eve.side_effect = Exception("EVE-NG error")
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            eos,
            ["--version", "4.29.3M", "--eve-ng"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()


class TestCvpCommand:
    """Test suite for cvp download command."""

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_version(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP download with specific version."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )

        # Execute
        result = runner.invoke(
            cvp,
            ["--version", "2024.3.0"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_cvp_xml.assert_called_once()
        mock_download_files.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaXmlQuerier")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_latest(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_querier_class: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP download with --latest flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_querier = MagicMock()
        mock_version = MagicMock()
        mock_version.__str__ = lambda self: "2024.3.0"
        mock_querier.latest.return_value = mock_version
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            cvp,
            ["--latest"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_querier.latest.assert_called_once_with(
            package="cvp", branch=None
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaXmlQuerier")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_branch(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_querier_class: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP download with --branch option."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_querier = MagicMock()
        mock_version = MagicMock()
        mock_version.__str__ = lambda self: "2024.2.0"
        mock_querier.latest.return_value = mock_version
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            cvp,
            ["--latest", "--branch", "2024.2"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_querier.latest.assert_called_once_with(
            package="cvp", branch="2024.2"
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_format(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP download with custom format."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )

        # Execute
        result = runner.invoke(
            cvp,
            ["--version", "2024.3.0", "--format", "rpm"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        call_args = mock_cvp_xml.call_args
        assert call_args.kwargs["image_type"] == "rpm"

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_dry_run(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP command with --dry-run flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )

        # Execute
        result = runner.invoke(
            cvp,
            ["--version", "2024.3.0", "--dry-run"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_soft_manager.assert_called_once_with(dry_run=True)

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaXmlQuerier")
    def test_cvp_command_querier_error(
        self,
        mock_querier_class: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP command when querier raises exception."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_querier_class.side_effect = Exception("API error")

        # Execute
        result = runner.invoke(
            cvp,
            ["--latest"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    def test_cvp_command_xml_object_creation_error(
        self,
        mock_cvp_xml: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP command when CvpXmlObject creation fails."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_cvp_xml.side_effect = Exception("XML creation failed")

        # Execute
        result = runner.invoke(
            cvp,
            ["--version", "2024.3.0"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    def test_cvp_command_xml_object_creation_error_debug_mode(
        self,
        mock_cvp_xml: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test CVP XML error in debug mode."""
        # Setup
        mock_console = MagicMock()
        mock_context["debug"] = True
        mock_init.return_value = (
            mock_console,
            "test-token",
            True,
            "debug",
        )
        mock_cvp_xml.side_effect = Exception("XML error")

        # Execute
        result = runner.invoke(
            cvp,
            ["--version", "2024.3.0"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()


class TestPathCommand:
    """Test suite for path download command."""

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_basic_download(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test basic path download command."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.swi"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            [
                "--source",
                "/path/to/EOS-4.29.3M.swi",
                "--output",
                "/tmp",
            ],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_server.get_url.assert_called_once()
        mock_cli.download_file.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_path_command_missing_source(
        self,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command without --source option."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )

        # Execute
        result = runner.invoke(
            path,
            ["--output", "/tmp"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    def test_path_command_get_url_error(
        self,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command when get_url raises exception."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.side_effect = Exception("URL error")
        mock_arista_server.return_value = mock_server

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    def test_path_command_get_url_error_debug_mode(
        self,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test get_url error in debug mode."""
        # Setup
        mock_console = MagicMock()
        mock_context["debug"] = True
        mock_init.return_value = (
            mock_console,
            "test-token",
            True,
            "debug",
        )
        mock_server = MagicMock()
        mock_server.get_url.side_effect = Exception("URL error")
        mock_arista_server.return_value = mock_server

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    def test_path_command_url_is_none(
        self,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command when get_url returns None."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = None
        mock_arista_server.return_value = mock_server

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_download_error(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command when download fails."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.swi"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_cli.download_file.side_effect = Exception("Download failed")
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_download_error_debug_mode(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test download error in debug mode."""
        # Setup
        mock_console = MagicMock()
        mock_context["debug"] = True
        mock_init.return_value = (
            mock_console,
            "test-token",
            True,
            "debug",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.swi"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_cli.download_file.side_effect = Exception("Download error")
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_with_docker_import(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command with --import-docker flag."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.tar"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            [
                "--source",
                "/path/to/cEOS.tar",
                "--import-docker",
                "--docker-name",
                "arista/ceos",
                "--docker-tag",
                "latest",
            ],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_cli.import_docker.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_docker_import_file_not_found(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test Docker import with missing file."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "info",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.tar"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_cli.import_docker.side_effect = FileNotFoundError()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            [
                "--source",
                "/path/to/cEOS.tar",
                "--import-docker",
            ],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_docker_import_error_debug_mode(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test Docker import error in debug mode."""
        # Setup
        mock_console = MagicMock()
        mock_context["debug"] = True
        mock_init.return_value = (
            mock_console,
            "test-token",
            True,
            "debug",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.tar"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_cli.import_docker.side_effect = FileNotFoundError()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            [
                "--source",
                "/path/to/cEOS.tar",
                "--import-docker",
            ],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.AristaServer")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    def test_path_command_with_log_level_debug(
        self,
        mock_soft_manager: Mock,
        mock_arista_server: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test path command with debug log level."""
        # Setup
        mock_console = MagicMock()
        mock_init.return_value = (
            mock_console,
            "test-token",
            False,
            "debug",
        )
        mock_server = MagicMock()
        mock_server.get_url.return_value = "https://example.com/file.swi"
        mock_arista_server.return_value = mock_server
        mock_cli = MagicMock()
        mock_soft_manager.return_value = mock_cli

        # Execute
        result = runner.invoke(
            path,
            ["--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        # In debug mode, should print URL
        assert any(
            "URL to download" in str(call)
            for call in mock_console.print.call_args_list
        )
