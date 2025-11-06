#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

"""
Comprehensive tests for cli/debug/commands.py module.

Tests the XML debug command for downloading and saving Arista
server XML data.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, MagicMock, patch, mock_open

import pytest
from click.testing import CliRunner

from eos_downloader.cli.cli import ardl


@pytest.fixture
def runner() -> CliRunner:
    """Provide Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_xml_tree() -> ET.ElementTree:
    """Provide mock XML ElementTree."""
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
    <folder>
        <dir label="EOS">
            <dir label="Active Releases">
                <dir label="4.29">
                    <dir label="4.29.3M">
                        <file>EOS-4.29.3M.swi</file>
                    </dir>
                </dir>
            </dir>
        </dir>
    </folder>
    """
    return ET.ElementTree(ET.fromstring(xml_string))


@pytest.fixture
def mock_arista_server(
    mock_xml_tree: ET.ElementTree,
) -> Generator[Mock, None, None]:
    """Provide mock AristaServer instance."""
    with patch("eos_downloader.logics.arista_server.AristaServer") as mock_class:
        mock_instance = MagicMock()
        mock_instance.authenticate.return_value = None
        mock_instance.get_xml_data.return_value = mock_xml_tree
        mock_class.return_value = mock_instance
        yield mock_instance


class TestXmlCommand:
    """Test suite for debug xml command."""

    def test_xml_command_help(self, runner: CliRunner) -> None:
        """Test xml command help display."""
        result = runner.invoke(ardl, ["debug", "xml", "--help"])

        assert result.exit_code == 0
        assert "Downloads and saves XML data" in result.output
        assert "--output" in result.output
        assert "--log-level" in result.output

    def test_xml_command_basic_success(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful XML download and save."""
        output_file = tmp_path / "test_output.xml"

        with patch("builtins.open", mock_open()) as mock_file:
            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                    "--log-level",
                    "info",
                ],
            )

            assert result.exit_code == 0
            mock_arista_server.authenticate.assert_called_once()
            mock_arista_server.get_xml_data.assert_called_once()
            mock_file.assert_called_once_with(str(output_file), "w", encoding="utf-8")

    def test_xml_command_with_default_output(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
    ) -> None:
        """Test XML command uses default output filename."""
        with patch("builtins.open", mock_open()) as mock_file:
            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                ],
            )

            assert result.exit_code == 0
            mock_file.assert_called_once_with("arista.xml", "w", encoding="utf-8")

    def test_xml_command_with_debug_log_level(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
        tmp_path: Path,
    ) -> None:
        """Test XML command with debug log level."""
        output_file = tmp_path / "debug_output.xml"

        with patch("builtins.open", mock_open()):
            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                    "--log-level",
                    "debug",
                ],
            )

            assert result.exit_code == 0
            mock_arista_server.authenticate.assert_called_once()

    def test_xml_command_authentication_failure(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test XML command handles authentication failure."""
        output_file = tmp_path / "output.xml"

        with patch("eos_downloader.logics.arista_server.AristaServer") as mock_class:
            mock_instance = MagicMock()
            mock_instance.authenticate.side_effect = Exception("Authentication failed")
            mock_instance.get_xml_data.return_value = None
            mock_class.return_value = mock_instance

            with patch("builtins.open", mock_open()):
                result = runner.invoke(
                    ardl,
                    [
                        "--token",
                        "invalid-token",
                        "debug",
                        "xml",
                        "--output",
                        str(output_file),
                        "--log-level",
                        "error",
                    ],
                )

                # Command handles error and continues
                mock_instance.authenticate.assert_called_once()

    def test_xml_command_no_xml_data_received(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test XML command handles None XML data gracefully."""
        output_file = tmp_path / "output.xml"

        with patch("eos_downloader.logics.arista_server.AristaServer") as mock_class:
            mock_instance = MagicMock()
            mock_instance.authenticate.return_value = None
            mock_instance.get_xml_data.return_value = None
            mock_class.return_value = mock_instance

            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                    "--log-level",
                    "error",
                ],
            )

            assert result.exit_code == 0
            mock_instance.get_xml_data.assert_called_once()

    def test_xml_command_xml_root_is_none(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test XML command handles XML with None root element."""
        output_file = tmp_path / "output.xml"

        with patch("eos_downloader.logics.arista_server.AristaServer") as mock_class:
            mock_instance = MagicMock()
            mock_instance.authenticate.return_value = None

            mock_tree = MagicMock(spec=ET.ElementTree)
            mock_tree.getroot.return_value = None
            mock_instance.get_xml_data.return_value = mock_tree

            mock_class.return_value = mock_instance

            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                    "--log-level",
                    "error",
                ],
            )

            assert result.exit_code == 0
            mock_tree.getroot.assert_called_once()

    def test_xml_command_prettified_output(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that XML output is prettified with indentation."""
        output_file = tmp_path / "pretty_output.xml"
        written_content: list = []

        def capture_write(content: str) -> None:
            """Capture written content."""
            written_content.append(content)

        mock_file = mock_open()
        mock_file.return_value.write.side_effect = capture_write

        with patch("builtins.open", mock_file):
            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            assert len(written_content) > 0
            xml_content = written_content[0]
            # Verify it's prettified (contains indentation)
            assert "    " in xml_content  # 4-space indentation
            assert "<?xml" in xml_content  # XML declaration

    def test_xml_command_file_write_error(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
        tmp_path: Path,
    ) -> None:
        """Test XML command handles file write errors."""
        output_file = tmp_path / "readonly" / "output.xml"

        # Mock open to raise exception
        with patch(
            "builtins.open",
            side_effect=PermissionError("Permission denied"),
        ):
            result = runner.invoke(
                ardl,
                [
                    "--token",
                    "test-token",
                    "debug",
                    "xml",
                    "--output",
                    str(output_file),
                    "--log-level",
                    "error",
                ],
            )

            # Click will catch the exception
            assert result.exit_code != 0 or (
                "Permission denied" in result.output or "Error" in result.output
            )

    def test_xml_command_with_all_log_levels(
        self,
        runner: CliRunner,
        mock_arista_server: Mock,
        tmp_path: Path,
    ) -> None:
        """Test XML command works with all log levels."""
        log_levels = ["debug", "info", "warning", "error", "critical"]
        output_file = tmp_path / "output.xml"

        with patch("builtins.open", mock_open()):
            for log_level in log_levels:
                result = runner.invoke(
                    ardl,
                    [
                        "--token",
                        "test-token",
                        "debug",
                        "xml",
                        "--output",
                        str(output_file),
                        "--log-level",
                        log_level,
                    ],
                )

                assert result.exit_code == 0, f"Failed with log level: {log_level}"
