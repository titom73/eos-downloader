#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Tests for ardl config CLI commands."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from eos_downloader.cli.cli import ardl


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click test runner."""
    return CliRunner()


class TestConfigInit:
    """Tests for 'ardl config init' command."""

    def test_creates_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """Creates a config file at the specified path."""
        output = tmp_path / "config.toml"
        result = runner.invoke(ardl, ["config", "init", "--output", str(output)])

        assert result.exit_code == 0
        assert output.exists()
        assert "[ardl]" in output.read_text()

    def test_sets_permissions(self, runner: CliRunner, tmp_path: Path) -> None:
        """Config file is created with restricted permissions."""
        output = tmp_path / "config.toml"
        result = runner.invoke(ardl, ["config", "init", "--output", str(output)])

        assert result.exit_code == 0
        mode = oct(output.stat().st_mode & 0o777)
        assert mode == "0o600"

    def test_no_overwrite_without_force(self, runner: CliRunner, tmp_path: Path) -> None:
        """Refuses to overwrite existing file without --force."""
        output = tmp_path / "config.toml"
        output.write_text("existing content")

        result = runner.invoke(ardl, ["config", "init", "--output", str(output)])

        assert result.exit_code != 0
        assert "already exists" in result.output or "already exists" in (result.stderr or "")
        assert output.read_text() == "existing content"

    def test_force_overwrites(self, runner: CliRunner, tmp_path: Path) -> None:
        """Overwrites existing file with --force."""
        output = tmp_path / "config.toml"
        output.write_text("old content")

        result = runner.invoke(
            ardl, ["config", "init", "--output", str(output), "--force"]
        )

        assert result.exit_code == 0
        assert "[ardl]" in output.read_text()

    def test_custom_output(self, runner: CliRunner, tmp_path: Path) -> None:
        """Creates file at custom output path."""
        custom_dir = tmp_path / "custom" / "nested"
        output = custom_dir / "my-config.toml"

        result = runner.invoke(ardl, ["config", "init", "-o", str(output)])

        assert result.exit_code == 0
        assert output.exists()
        assert "Configuration file created" in result.output


class TestConfigShow:
    """Tests for 'ardl config show' command."""

    def test_no_config_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """Shows helpful message when no config file exists."""
        search_paths = [
            (str(tmp_path / "nonexistent.toml"), "home"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            # Also patch the import in commands module
            with patch(
                "eos_downloader.cli.config.commands.find_config_file", return_value=None
            ):
                result = runner.invoke(ardl, ["config", "show"])

        assert result.exit_code == 0
        assert "No configuration file found" in result.output

    def test_show_with_config(self, runner: CliRunner, tmp_path: Path) -> None:
        """Displays config file content with masked token."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[ardl]\ntoken = "abcdefghijklmnopqrstuvwxyz"\nlog_level = "info"\n'
        )

        with patch(
            "eos_downloader.cli.config.commands.find_config_file",
            return_value=config_file,
        ):
            result = runner.invoke(ardl, ["config", "show"])

        assert result.exit_code == 0
        assert str(config_file) in result.output
        # Token should be masked
        assert "abcdefghijklmnopqrstuvwxyz" not in result.output
        assert "abcd...wxyz" in result.output
        # Other options visible
        assert 'log_level = "info"' in result.output

    def test_show_without_token(self, runner: CliRunner, tmp_path: Path) -> None:
        """Displays config without token masking when no token present."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('[ardl]\nlog_level = "debug"\n')

        with patch(
            "eos_downloader.cli.config.commands.find_config_file",
            return_value=config_file,
        ):
            result = runner.invoke(ardl, ["config", "show"])

        assert result.exit_code == 0
        assert 'log_level = "debug"' in result.output
