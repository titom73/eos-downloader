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
import typer
from typer.testing import CliRunner

from eos_downloader.cli.cli import app

# Fixtures


@pytest.fixture
def runner() -> CliRunner:
    """Provide a Typer CLI runner for testing."""
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
            app,
            ["get", "eos", "--version", "4.29.3M"],
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
                app,
                ["get", "eos", "--latest"],
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
                app,
                ["get", "eos", "--latest", "--branch", "4.29"],
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
            app,
            ["get", "eos", "--version", "4.29.3M", "--eve-ng"],
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
                app,
                [
                    "get",
                    "eos",
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
                app,
                ["get", "eos", "--version", "4.29.3M", "--skip-download"],
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
                    app,
                    ["get", "eos", "--version", "4.29.3M", "--dry-run"],
                    obj=mock_context,
                )

        # Assert
        assert result.exit_code == 0
        mock_sm.assert_called_once_with(
            dry_run=True, force_download=False, console=mock_console
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.search_version")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.handle_docker_import")
    def test_eos_command_dry_run_skips_docker_import(
        self,
        mock_docker_import: Mock,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_search: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test --dry-run with --import-docker skips docker import."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_search.return_value = "4.29.3M"

        with patch("eos_downloader.cli.get.commands.download_files"):
            result = runner.invoke(
                app,
                [
                    "get",
                    "eos",
                    "--version",
                    "4.29.3M",
                    "--import-docker",
                    "--docker-name",
                    "arista/ceos",
                    "--docker-tag",
                    "4.29.3M",
                    "--dry-run",
                ],
                obj=mock_context,
            )

        assert result.exit_code == 0
        mock_docker_import.assert_not_called()
        dry_run_printed = any(
            "DRY-RUN" in str(call) for call in mock_console.print.call_args_list
        )
        assert dry_run_printed

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
            app,
            ["get", "eos", "--latest"],
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
            app,
            ["get", "eos", "--version", "4.29.3M"],
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
            app,
            ["get", "eos", "--version", "4.29.3M", "--eve-ng"],
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
            app,
            ["get", "eos", "--version", "4.29.3M", "--eve-ng"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 1
        mock_console.print_exception.assert_called()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.maybe_run_interactive")
    @patch("eos_downloader.cli.get.commands.EosXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_eos_command_interactive_result_is_applied(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_eos_xml: Mock,
        mock_maybe_run_interactive: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Interactive EOS flow applies the returned selections."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_maybe_run_interactive.return_value = MagicMock(
            image_format="cEOS",
            version="4.29.3M",
            output="/downloads",
            force=True,
            import_docker=False,
            docker_name="arista/ceos",
            docker_tag="4.29.3M",
            eve_ng=False,
        )

        result = runner.invoke(app, ["get", "eos", "--interactive"], obj=mock_context)

        assert result.exit_code == 0
        mock_eos_xml.assert_called_once_with(
            searched_version="4.29.3M", token="test-token", image_type="cEOS"
        )
        mock_soft_manager.assert_called_once_with(
            dry_run=False, force_download=True, console=mock_console
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.download_from_containerlab_topology")
    def test_eos_command_containerlab_auto_defaults_ceos_and_no_progress(
        self,
        mock_download_from_containerlab: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """Containerlab flow auto-defaults to cEOS and disables progress when asked."""
        topology = tmp_path / "lab.yml"
        topology.write_text("name: test\n")
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_download_from_containerlab.return_value = 0

        result = runner.invoke(
            app,
            [
                "get",
                "eos",
                "--containerlab-topology",
                str(topology),
                "--format",
                "64",
                "--no-progress",
            ],
            obj=mock_context,
        )

        assert result.exit_code == 0
        kwargs = mock_download_from_containerlab.call_args.kwargs
        assert kwargs["image_format"] == "cEOS"
        assert kwargs["progress"] == "none"


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
            app,
            ["get", "cvp", "--version", "2024.3.0"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_cvp_xml.assert_called_once()
        mock_download_files.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.resolve_cvp_version")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_latest(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_resolve_cvp_version: Mock,
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
        mock_resolve_cvp_version.return_value = "2024.3.0"

        # Execute
        result = runner.invoke(
            app,
            ["get", "cvp", "--latest"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_resolve_cvp_version.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.resolve_cvp_version")
    @patch("eos_downloader.cli.get.commands.CvpXmlObject")
    @patch("eos_downloader.cli.get.commands.SoftManager")
    @patch("eos_downloader.cli.get.commands.download_files")
    def test_cvp_command_with_branch(
        self,
        mock_download_files: Mock,
        mock_soft_manager: Mock,
        mock_cvp_xml: Mock,
        mock_resolve_cvp_version: Mock,
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
        mock_resolve_cvp_version.return_value = "2024.2.0"

        # Execute
        result = runner.invoke(
            app,
            ["get", "cvp", "--latest", "--branch", "2024.2"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_resolve_cvp_version.assert_called_once()

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
            app,
            ["get", "cvp", "--version", "2024.3.0", "--format", "rpm"],
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
            app,
            ["get", "cvp", "--version", "2024.3.0", "--dry-run"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        mock_soft_manager.assert_called_once_with(
            dry_run=True, force_download=False, console=mock_console
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.resolve_cvp_version")
    def test_cvp_command_querier_error(
        self,
        mock_resolve_cvp_version: Mock,
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
        mock_resolve_cvp_version.side_effect = typer.Exit(1)

        # Execute
        result = runner.invoke(
            app,
            ["get", "cvp", "--latest"],
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
            app,
            ["get", "cvp", "--version", "2024.3.0"],
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
            app,
            ["get", "cvp", "--version", "2024.3.0"],
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
            app,
            [
                "get",
                "path",
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
            app,
            ["get", "path", "--output", "/tmp"],
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
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
            app,
            [
                "get",
                "path",
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
            app,
            [
                "get",
                "path",
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
            app,
            [
                "get",
                "path",
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
            app,
            ["get", "path", "--source", "/path/to/file.swi"],
            obj=mock_context,
        )

        # Assert
        assert result.exit_code == 0
        # In debug mode, should print URL
        assert any(
            "URL to download" in str(call) for call in mock_console.print.call_args_list
        )


class TestEosContainerlabCommand:
    """Test suite for eos --containerlab-topology option."""

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.download_from_containerlab_topology")
    def test_containerlab_basic(
        self,
        mock_clab_download: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """Test containerlab topology triggers batch download flow."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_clab_download.return_value = 0

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            ["get", "eos", "--containerlab-topology", str(topo_file)],
            obj=mock_context,
        )

        assert result.exit_code == 0
        mock_clab_download.assert_called_once()

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_containerlab_mutual_exclusivity_with_version(
        self,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """--containerlab-topology fails with --version."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            [
                "get",
                "eos",
                "--containerlab-topology",
                str(topo_file),
                "--version",
                "4.29.3M",
            ],
            obj=mock_context,
        )

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output or isinstance(
            result.exception, typer.BadParameter
        )

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_containerlab_mutual_exclusivity_with_latest(
        self,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """--containerlab-topology fails with --latest."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            ["get", "eos", "--containerlab-topology", str(topo_file), "--latest"],
            obj=mock_context,
        )

        assert result.exit_code != 0

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_containerlab_mutual_exclusivity_with_branch(
        self,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """--containerlab-topology fails with --branch."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            [
                "get",
                "eos",
                "--containerlab-topology",
                str(topo_file),
                "--branch",
                "4.29",
            ],
            obj=mock_context,
        )

        assert result.exit_code != 0

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.download_from_containerlab_topology")
    def test_containerlab_no_versions_found(
        self,
        mock_clab_download: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """Empty version list from parser exits 0."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_clab_download.return_value = 0

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            ["get", "eos", "--containerlab-topology", str(topo_file)],
            obj=mock_context,
        )

        assert result.exit_code == 0

    @patch("eos_downloader.cli.get.commands.initialize")
    @patch("eos_downloader.cli.get.commands.download_from_containerlab_topology")
    def test_containerlab_with_clab_alias(
        self,
        mock_clab_download: Mock,
        mock_init: Mock,
        runner: CliRunner,
        mock_context: dict,
        tmp_path: Path,
    ) -> None:
        """Test --clab alias works the same as --containerlab-topology."""
        mock_console = MagicMock()
        mock_init.return_value = (mock_console, "test-token", False, "info")
        mock_clab_download.return_value = 0

        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text("topology: {}")

        result = runner.invoke(
            app,
            ["get", "eos", "--clab", str(topo_file)],
            obj=mock_context,
        )

        assert result.exit_code == 0
        mock_clab_download.assert_called_once()
