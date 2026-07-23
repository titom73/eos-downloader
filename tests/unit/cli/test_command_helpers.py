#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Tests for shared helpers in ``eos_downloader.cli.get.command_helpers``."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from rich.console import Console

from eos_downloader.cli.get.command_helpers import (
    build_download_object,
    ensure_selection_mode_exclusive,
    maybe_run_interactive,
    print_exception_and_exit,
    progress_mode_from_flag,
    resolve_cvp_version,
)
from eos_downloader.exceptions import AuthenticationError


def test_progress_mode_from_flag() -> None:
    assert progress_mode_from_flag(True) == "none"
    assert progress_mode_from_flag(False) == "auto"


def test_ensure_selection_mode_exclusive_passes() -> None:
    ensure_selection_mode_exclusive(None, False, None, option_name="--interactive")


def test_ensure_selection_mode_exclusive_raises() -> None:
    with pytest.raises(typer.BadParameter):
        ensure_selection_mode_exclusive(
            "4.29.3M", False, None, option_name="--interactive"
        )


@patch("eos_downloader.cli.get.command_helpers.run_interactive")
def test_maybe_run_interactive_disabled(mock_run_interactive: Mock) -> None:
    result = maybe_run_interactive(
        "eos",
        Console(force_terminal=True),
        "token",
        ".",
        interactive=False,
        version=None,
        latest=False,
        branch=None,
    )
    assert result is None
    mock_run_interactive.assert_not_called()


@patch("eos_downloader.cli.get.command_helpers.run_interactive")
@patch("eos_downloader.cli.get.command_helpers.require_interactive_context")
def test_maybe_run_interactive_enabled(
    mock_require_context: Mock,
    mock_run_interactive: Mock,
) -> None:
    expected = MagicMock()
    mock_run_interactive.return_value = expected

    result = maybe_run_interactive(
        "cvp",
        Console(force_terminal=True),
        "token",
        ".",
        interactive=True,
        version=None,
        latest=False,
        branch=None,
    )

    assert result is expected
    mock_require_context.assert_called_once()
    mock_run_interactive.assert_called_once()


def test_print_exception_and_exit_normal_mode() -> None:
    console = MagicMock()
    with pytest.raises(typer.Exit):
        print_exception_and_exit(console, False, RuntimeError("boom"))
    console.print.assert_called()


def test_print_exception_and_exit_debug_mode() -> None:
    console = MagicMock()
    with pytest.raises(typer.Exit):
        print_exception_and_exit(console, True, RuntimeError("boom"))
    console.print_exception.assert_called_once_with(show_locals=True)


def test_build_download_object_success() -> None:
    class Factory:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    instance = build_download_object(
        Factory, MagicMock(), False, searched_version="4.29.3M"
    )
    assert instance.kwargs["searched_version"] == "4.29.3M"


def test_build_download_object_failure() -> None:
    class Factory:
        def __init__(self, **kwargs):
            raise ValueError("invalid")

    with pytest.raises(typer.Exit):
        build_download_object(Factory, MagicMock(), False, searched_version="4.29.3M")


def test_resolve_cvp_version_passthrough() -> None:
    console = MagicMock()
    result = resolve_cvp_version(
        console,
        "token",
        version="2024.3.0",
        latest=False,
        branch=None,
        file_format="ova",
        debug=False,
    )
    assert result == "2024.3.0"


@patch("eos_downloader.cli.get.command_helpers.AristaXmlQuerier")
def test_resolve_cvp_version_latest(mock_querier_class: Mock) -> None:
    mock_querier = MagicMock()
    mock_querier.latest.return_value = "2024.3.0"
    mock_querier_class.return_value = mock_querier

    result = resolve_cvp_version(
        MagicMock(),
        "token",
        version=None,
        latest=True,
        branch=None,
        file_format="ova",
        debug=False,
    )

    assert result == "2024.3.0"
    mock_querier.latest.assert_called_once_with(package="cvp", branch=None)


@patch("eos_downloader.cli.get.command_helpers.AristaXmlQuerier")
def test_resolve_cvp_version_authentication_error(mock_querier_class: Mock) -> None:
    mock_querier = MagicMock()
    mock_querier.latest.side_effect = AuthenticationError("nope")
    mock_querier_class.return_value = mock_querier

    with pytest.raises(typer.Exit):
        resolve_cvp_version(
            MagicMock(),
            "token",
            version=None,
            latest=True,
            branch=None,
            file_format="ova",
            debug=False,
        )
