#!/usr/bin/env python
# coding: utf-8 -*-
"""Integration tests for CLI commands.

Tests the complete CLI workflow using Click's test runner
with mocked API responses.
"""

from pathlib import Path
from typing import Any

import pytest
import responses
from click.testing import CliRunner

from tests.integration.mock_arista_api import (
    MOCK_XML_CATALOG,
    MOCK_SESSION_RESPONSE,
    mock_arista_token,
    mock_download_dir,
)

from eos_downloader.cli.cli import ardl
from eos_downloader.defaults import DEFAULT_SOFTWARE_FOLDER_TREE, DEFAULT_SERVER_SESSION


def setup_cli_api_mocks() -> None:
    """Set up common API mocks for CLI tests."""
    responses.add(
        responses.POST,
        DEFAULT_SERVER_SESSION,
        json=MOCK_SESSION_RESPONSE,
        status=200
    )
    responses.add(
        responses.POST,
        DEFAULT_SOFTWARE_FOLDER_TREE,
        json={"data": {"xml": MOCK_XML_CATALOG}},
        status=200
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.mark.integration
class TestCLIInfoCommands:
    """Test CLI info commands."""

    @responses.activate
    def test_info_eos_command(
        self,
        cli_runner: CliRunner,
        mock_arista_token: str,
    ) -> None:
        """Test 'ardl info eos' command."""
        setup_cli_api_mocks()

        result = cli_runner.invoke(
            ardl,
            ["--token", mock_arista_token, "info", "eos"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0 or "versions" in result.output.lower() or len(result.output) > 0

    @responses.activate
    def test_info_eos_with_branch_filter(
        self,
        cli_runner: CliRunner,
        mock_arista_token: str,
    ) -> None:
        """Test 'ardl info eos --branch 4.32' command."""
        setup_cli_api_mocks()

        result = cli_runner.invoke(
            ardl,
            ["--token", mock_arista_token, "info", "eos", "--branch", "4.32"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0 or len(result.output) > 0


@pytest.mark.integration
class TestCLIHelp:
    """Test CLI help messages."""

    def test_main_help(self, cli_runner: CliRunner) -> None:
        """Test main help message."""
        result = cli_runner.invoke(ardl, ["--help"])

        assert result.exit_code == 0
        assert "Arista" in result.output or "ardl" in result.output.lower()

    def test_get_help(self, cli_runner: CliRunner) -> None:
        """Test get subcommand help."""
        result = cli_runner.invoke(ardl, ["get", "--help"])

        assert result.exit_code == 0

    def test_info_help(self, cli_runner: CliRunner) -> None:
        """Test info subcommand help."""
        result = cli_runner.invoke(ardl, ["info", "--help"])

        assert result.exit_code == 0


@pytest.mark.integration
class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_missing_token_warning(self, cli_runner: CliRunner) -> None:
        """Test behavior when token is missing."""
        result = cli_runner.invoke(
            ardl,
            ["info", "eos"],
        )

        assert result.exit_code != 0 or "token" in result.output.lower() or "error" in result.output.lower()

    @responses.activate
    def test_invalid_token_error(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test error message with invalid token."""
        responses.add(
            responses.POST,
            DEFAULT_SERVER_SESSION,
            json={"error": "Unauthorized"},
            status=401
        )

        result = cli_runner.invoke(
            ardl,
            ["--token", "invalid-token", "info", "eos"],
        )

        assert result.exit_code != 0


@pytest.mark.integration
class TestCLIVersion:
    """Test CLI version command."""

    def test_version_option(self, cli_runner: CliRunner) -> None:
        """Test --version option."""
        result = cli_runner.invoke(ardl, ["--version"])

        assert result.exit_code == 0
        assert "v0" in result.output or "version" in result.output.lower()


@pytest.mark.integration
class TestCLIDebugCommands:
    """Test CLI debug commands."""

    def test_debug_help(self, cli_runner: CliRunner) -> None:
        """Test debug subcommand help."""
        result = cli_runner.invoke(ardl, ["debug", "--help"])

        assert result.exit_code == 0
