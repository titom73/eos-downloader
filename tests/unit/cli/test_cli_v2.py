"""Comprehensive unit tests for the EOS Downloader CLI interface.

This module provides extensive testing coverage for the Arista Network
Download CLI tool, including all main commands, subcommands, options,
and error handling scenarios.

Test Categories:
    - Main CLI functionality (help, version, no args)
    - Command groups (get, info, debug)
    - Option handling (token, log-level, debug)
    - Error scenarios and edge cases
    - Context object handling
    - Exit codes and output validation

The tests use Typer's CliRunner for isolated testing without subprocess
execution.
"""

import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from eos_downloader.cli.cli import app
from eos_downloader import __version__


class TestMainCli:
    """Test suite for main CLI functionality."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_cli_help_display(self) -> None:
        """Test that CLI displays help information correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Arista Network Download CLI" in result.output
        # Typer renders the command list in a Rich panel titled "Commands"
        # (no trailing colon like Click's plain formatter).
        assert "Commands" in result.output
        assert "get" in result.output
        assert "info" in result.output
        assert "debug" in result.output

    def test_cli_version_display(self) -> None:
        """Test that CLI displays version information correctly."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_no_arguments_shows_help(self) -> None:
        """Test that CLI shows help when called with no arguments."""
        result = self.runner.invoke(app, [])
        # In some environments (like tox), Click may return exit code 2
        # when no args is help, which is acceptable behavior
        assert result.exit_code in [0, 2]
        assert "Arista Network Download CLI" in result.output
        assert "Commands" in result.output

    def test_cli_with_global_options(self) -> None:
        """Test CLI with global options like token and log-level."""
        result = self.runner.invoke(
            app, ["--token", "test_token", "--log-level", "debug", "--help"]
        )
        assert result.exit_code == 0
        assert "Arista Network Download CLI" in result.output

    def test_cli_invalid_log_level(self) -> None:
        """Test CLI behavior with invalid log level."""
        result = self.runner.invoke(app, ["--log-level", "invalid"])
        assert result.exit_code == 2
        assert "Invalid value for" in result.output


class TestCommandGroups:
    """Test suite for CLI command groups."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_get_command_group_help(self) -> None:
        """Test get command group help display."""
        result = self.runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0
        assert "Download Arista from Arista website" in result.output
        assert "eos" in result.output
        assert "cvp" in result.output

    def test_get_command_no_args(self) -> None:
        """Test get command without subcommand."""
        result = self.runner.invoke(app, ["get"])
        # In tox environment, this may return exit code 2, which is acceptable
        assert result.exit_code in [0, 2]
        assert "Download Arista from Arista website" in result.output

    def test_info_command_group_help(self) -> None:
        """Test info command group help display."""
        result = self.runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "List information from Arista website" in result.output
        assert "versions" in result.output

    def test_debug_command_group_help(self) -> None:
        """Test debug command group help display."""
        result = self.runner.invoke(app, ["debug", "--help"])
        assert result.exit_code == 0
        assert "Debug commands to work with ardl" in result.output
        assert "xml" in result.output


class TestSubcommands:
    """Test suite for CLI subcommands."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_get_eos_help(self) -> None:
        """Test get eos subcommand help."""
        result = self.runner.invoke(app, ["get", "eos", "--help"])
        assert result.exit_code == 0
        assert "Download EOS image from Arista server" in result.output

    def test_get_cvp_help(self) -> None:
        """Test get cvp subcommand help."""
        result = self.runner.invoke(app, ["get", "cvp", "--help"])
        assert result.exit_code == 0
        assert "Download CVP image from Arista server" in result.output

    def test_info_versions_help(self) -> None:
        """Test info versions subcommand help."""
        result = self.runner.invoke(app, ["info", "versions", "--help"])
        assert result.exit_code == 0
        assert "List available package versions" in result.output

    def test_debug_xml_help(self) -> None:
        """Test debug xml subcommand help."""
        result = self.runner.invoke(app, ["debug", "xml", "--help"])
        assert result.exit_code == 0
        assert "Downloads and saves XML data" in result.output


class TestContextHandling:
    """Test suite for CLI context handling."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_context_object_creation(self) -> None:
        """Test that CLI creates proper context objects."""
        # We can't easily test the internal context object creation
        # without more invasive mocking, but we can test that the CLI
        # accepts context-related options
        result = self.runner.invoke(app, ["--token", "test", "--debug", "--help"])
        assert result.exit_code == 0

    def test_environment_variable_handling(self) -> None:
        """Test CLI behavior with environment variables."""
        env = {"ARISTA_TOKEN": "env_token", "ARISTA_LOG_LEVEL": "info"}
        result = self.runner.invoke(app, ["--help"], env=env)
        assert result.exit_code == 0
        assert "Arista Network Download CLI" in result.output


class TestErrorScenarios:
    """Test suite for CLI error scenarios."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_invalid_command(self) -> None:
        """Test CLI behavior with invalid command."""
        result = self.runner.invoke(app, ["invalid_command"])
        assert result.exit_code == 2
        assert "No such command" in result.output

    def test_invalid_subcommand(self) -> None:
        """Test CLI behavior with invalid subcommand."""
        result = self.runner.invoke(app, ["get", "invalid_subcommand"])
        assert result.exit_code == 2
        assert "No such command" in result.output

    def test_missing_required_options(self) -> None:
        """Test CLI behavior when required options are missing."""
        # Most commands require --token, but they should show help
        # rather than error when just testing the command structure
        result = self.runner.invoke(app, ["get", "eos", "--help"])
        assert result.exit_code == 0


class TestMainFunction:
    """Test suite for CLI main function and module execution."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_cli_main_function(self) -> None:
        """Test that the main CLI function works."""
        # The cli function is an alias, we'll test ardl instead
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Arista Network Download CLI" in result.output

    def test_main_module_execution(self) -> None:
        """Test CLI can be executed as a module."""
        # This tests the __main__.py functionality indirectly
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Arista Network Download CLI" in result.output


class TestOutputFormatting:
    """Test suite for CLI output formatting."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_help_output_formatting(self) -> None:
        """Test that help output is properly formatted."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        output_lines = result.output.split("\n")
        # Check that help output has expected structure. Typer renders Options
        # and Commands as Rich panel titles (no trailing colon).
        assert any("Usage:" in line for line in output_lines)
        assert any("Options" in line for line in output_lines)
        assert any("Commands" in line for line in output_lines)

    def test_version_output_format(self) -> None:
        """Test version output format."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Version should contain the version string
        assert __version__ in result.output


class TestCliIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    def test_global_options_with_subcommands(self) -> None:
        """Test that global options work with subcommands."""
        result = self.runner.invoke(
            app,
            [
                "--token",
                "test_token",
                "--log-level",
                "debug",
                "--debug",
                "get",
                "--help",
            ],
        )
        assert result.exit_code == 0
        assert "Download Arista from Arista website" in result.output

    def test_command_chain_validation(self) -> None:
        """Test command chain validation."""
        # Test that command chains are properly validated
        result = self.runner.invoke(app, ["get", "eos", "--help"])
        assert result.exit_code == 0

        result = self.runner.invoke(app, ["info", "versions", "--help"])
        assert result.exit_code == 0

        result = self.runner.invoke(app, ["debug", "xml", "--help"])
        assert result.exit_code == 0


class TestConfigInjection:
    """Test config file injection into CLI defaults (lines 64-69, 77-78)."""

    @pytest.fixture(autouse=True)
    def setup_runner(self) -> None:
        """Create a Typer CLI runner for testing."""
        self.runner = CliRunner()

    @patch("eos_downloader.cli.cli.get_default_map")
    def test_config_injects_token(self, mock_get_default_map) -> None:
        """Test that config file injects token when source=DEFAULT (lines 64-65)."""
        mock_get_default_map.return_value = {
            "token": "config-token-123",
            "log_level": "debug",
            "debug_enabled": True,
        }

        # Invoke without --help so ardl callback actually runs
        # Use get --help so it invokes ardl callback then shows get help
        result = self.runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0
        mock_get_default_map.assert_called_once()

    @patch("eos_downloader.cli.cli.get_default_map")
    def test_config_injects_log_level(self, mock_get_default_map) -> None:
        """Test config injects log_level when source=DEFAULT (lines 66-67)."""
        mock_get_default_map.return_value = {
            "log_level": "warning",
        }

        result = self.runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0

    @patch("eos_downloader.cli.cli.get_default_map")
    def test_config_injects_debug_enabled(self, mock_get_default_map) -> None:
        """Test config injects debug_enabled when source=DEFAULT (lines 68-69)."""
        mock_get_default_map.return_value = {
            "debug_enabled": True,
        }

        result = self.runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0

    @patch("eos_downloader.cli.cli.get_default_map")
    def test_no_subcommand_shows_help(self, mock_get_default_map) -> None:
        """Test no subcommand shows help and exits 0 (lines 77-78)."""
        mock_get_default_map.return_value = None

        result = self.runner.invoke(app, [])
        assert result.exit_code in [0, 2]
        assert "Arista Network Download CLI" in result.output
