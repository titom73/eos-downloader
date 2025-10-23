#!/usr/bin/env python
# coding: utf-8 -*-
"""Tests for cli/get commands (basic integration tests).

This module provides basic integration tests for get commands.
For detailed tests of utility functions, see test_get_utils.py
"""

import pytest
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


def test_get_help(runner):
    """Test get command help output."""
    result = runner.invoke(ardl, ["get", "--help"])
    assert result.exit_code == 0
    assert "Download Arista from Arista website" in result.output


def test_get_eos_help(runner):
    """Test get eos command help output."""
    result = runner.invoke(ardl, ["get", "eos", "--help"])
    assert result.exit_code == 0


def test_get_cvp_help(runner):
    """Test get cvp command help output."""
    result = runner.invoke(ardl, ["get", "cvp", "--help"])
    assert result.exit_code == 0
