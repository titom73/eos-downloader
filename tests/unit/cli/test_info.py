#!/usr/bin/env python
# coding: utf-8 -*-
"""Tests for cli/info/commands.py module.

This module provides comprehensive tests for all info commands:
- versions: List available versions with filtering
- latest: Get latest version for a package
- mapping: List available flavors
"""

import json
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from eos_downloader.cli.cli import ardl
from eos_downloader.models.version import EosVersion, CvpVersion


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_eos_versions():
    """Provide mock EOS versions for testing."""
    return [
        EosVersion.from_str("4.29.3M"),
        EosVersion.from_str("4.29.2M"),
        EosVersion.from_str("4.30.1F"),
        EosVersion.from_str("4.30.0F"),
    ]


@pytest.fixture
def mock_cvp_versions():
    """Provide mock CVP versions for testing."""
    return [
        CvpVersion.from_str("2024.3.0"),
        CvpVersion.from_str("2024.2.1"),
        CvpVersion.from_str("2024.1.0"),
    ]


# =============================================================================
# Test: info help command
# =============================================================================


def test_info_help(runner):
    """Test info command help output."""
    result = runner.invoke(ardl, ["info", "--help"])
    assert result.exit_code == 0
    assert "List information from Arista website" in result.output


# =============================================================================
# Test: versions command - basic functionality
# =============================================================================


class TestInfoVersionsCommand:
    """Test suite for info versions command."""

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_eos_default_fancy_output(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test versions command with EOS and default fancy output."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.available_public_versions.return_value = mock_eos_versions
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            ["--token", "test-token", "info", "versions", "--package", "eos"],
        )

        # Verify
        assert result.exit_code == 0
        assert "4.29.3M" in result.output
        assert "4.30.1F" in result.output
        assert "Available versions" in result.output
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos", branch=None, rtype=None
        )

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_cvp_json_output(
        self, mock_querier_class, runner, mock_cvp_versions
    ):
        """Test versions command with CVP and JSON output."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.available_public_versions.return_value = mock_cvp_versions
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "versions",
                "--package",
                "cvp",
                "--format",
                "json",
            ],
        )

        # Verify
        assert result.exit_code == 0
        output_data = json.loads(result.output.strip())
        assert len(output_data) == 3
        assert output_data[0]["version"] == "2024.3.0"
        assert output_data[0]["branch"] == "2024.3"

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_text_output(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test versions command with text output format."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.available_public_versions.return_value = mock_eos_versions
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "versions",
                "--format",
                "text",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Listing available versions" in result.output
        assert "4.29.3M" in result.output
        assert "4.30.1F" in result.output

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_with_branch_filter(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test versions command filtering by branch."""
        # Setup mock - only return versions for specific branch
        filtered_versions = [
            v for v in mock_eos_versions if v.branch == "4.29"
        ]
        mock_querier = Mock()
        mock_querier.available_public_versions.return_value = filtered_versions
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "versions",
                "--branch",
                "4.29",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "4.29.3M" in result.output
        assert "4.29.2M" in result.output
        assert "4.30" not in result.output
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos", branch="4.29", rtype=None
        )

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_with_release_type_filter(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test versions command filtering by release type (M/F)."""
        # Setup mock - only return maintenance releases
        filtered_versions = [v for v in mock_eos_versions if v.rtype == "M"]
        mock_querier = Mock()
        mock_querier.available_public_versions.return_value = filtered_versions
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "versions",
                "--release-type",
                "M",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "4.29.3M" in result.output
        assert "4.29.2M" in result.output
        mock_querier.available_public_versions.assert_called_once_with(
            package="eos", branch=None, rtype="M"
        )

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_no_results_found(self, mock_querier_class, runner):
        """Test versions command when no versions found."""
        # Setup mock to raise ValueError (no versions found)
        mock_querier = Mock()
        mock_querier.available_public_versions.side_effect = ValueError(
            "No versions found"
        )
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "versions",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "No versions found" in result.output

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_versions_with_debug_on_error(self, mock_querier_class, runner):
        """Test versions command with debug flag shows exception details."""
        # Setup mock to raise ValueError
        mock_querier = Mock()
        mock_querier.available_public_versions.side_effect = ValueError(
            "API Error"
        )
        mock_querier_class.return_value = mock_querier

        # Execute with debug
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "--debug",
                "info",
                "versions",
            ],
        )

        # Verify - debug mode shows traceback
        assert result.exit_code == 0
        # With debug, console.print_exception is called


# =============================================================================
# Test: latest command
# =============================================================================


class TestInfoLatestCommand:
    """Test suite for info latest command."""

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_eos_version_fancy(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test getting latest EOS version with fancy format."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_eos_versions[0]  # 4.29.3M
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--package",
                "eos",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Latest version" in result.output
        assert "eos" in result.output
        assert "4.29.3M" in result.output

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_cvp_version(
        self, mock_querier_class, runner, mock_cvp_versions
    ):
        """Test getting latest CVP version."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_cvp_versions[0]  # 2024.3.0
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--package",
                "cvp",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "cvp" in result.output
        assert "2024.3.0" in result.output

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_with_branch(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test latest version for specific branch."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_eos_versions[0]  # 4.29.3M
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--branch",
                "4.29",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "4.29" in result.output
        assert "4.29.3M" in result.output
        mock_querier.latest.assert_called_once_with(
            package="eos", branch="4.29", rtype=None
        )

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_with_release_type(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test latest maintenance vs feature release."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_eos_versions[0]  # 4.29.3M
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--release-type",
                "M",
            ],
        )

        # Verify
        assert result.exit_code == 0
        mock_querier.latest.assert_called_once_with(
            package="eos", branch=None, rtype="M"
        )

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_json_format(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test latest version with JSON output."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_eos_versions[0]  # 4.29.3M
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--format",
                "json",
            ],
        )

        # Verify
        assert result.exit_code == 0
        output_data = json.loads(result.output.strip())
        assert output_data["version"] == "4.29.3M"

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_text_format(
        self, mock_querier_class, runner, mock_eos_versions
    ):
        """Test latest version with text output."""
        # Setup mock
        mock_querier = Mock()
        mock_querier.latest.return_value = mock_eos_versions[0]  # 4.29.3M
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
                "--format",
                "text",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Latest version" in result.output
        assert "4.29.3M" in result.output

    @patch("eos_downloader.cli.info.commands.AristaXmlQuerier")
    def test_latest_no_versions_found(self, mock_querier_class, runner):
        """Test behavior when no versions match criteria."""
        # Setup mock to raise ValueError
        mock_querier = Mock()
        mock_querier.latest.side_effect = ValueError("No versions found")
        mock_querier_class.return_value = mock_querier

        # Execute
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "latest",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "No versions found" in result.output


# =============================================================================
# Test: mapping command
# =============================================================================


class TestInfoMappingCommand:
    """Test suite for info mapping command."""

    def test_mapping_eos_default(self, runner):
        """Test mapping command for EOS with default fancy format."""
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "mapping",
                "--package",
                "eos",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Flavors" in result.output
        # EOS should have flavors like 64, vEOS, cEOS
        assert "64" in result.output or "vEOS" in result.output

    def test_mapping_cvp(self, runner):
        """Test mapping command for CVP."""
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "mapping",
                "--package",
                "cvp",
            ],
        )

        # Verify
        assert result.exit_code == 0
        # CVP should have flavors like ova, rpm, kvm

    def test_mapping_with_details(self, runner):
        """Test mapping command with details flag."""
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "mapping",
                "--package",
                "eos",
                "--details",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Information" in result.output or "Flavor" in result.output

    def test_mapping_json_format(self, runner):
        """Test mapping command with JSON output."""
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "mapping",
                "--package",
                "eos",
                "--format",
                "json",
            ],
        )

        # Verify
        assert result.exit_code == 0
        # Should be valid JSON
        output_data = json.loads(result.output.strip())
        assert isinstance(output_data, dict)

    def test_mapping_text_format(self, runner):
        """Test mapping command with text output."""
        result = runner.invoke(
            ardl,
            [
                "--token",
                "test-token",
                "info",
                "mapping",
                "--package",
                "eos",
                "--format",
                "text",
            ],
        )

        # Verify
        assert result.exit_code == 0
        assert "Following flavors" in result.output
        assert "Flavor" in result.output
