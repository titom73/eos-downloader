#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

"""Tests for the interactive download wizard (cli/get/interactive.py)."""

from __future__ import annotations

from contextlib import ExitStack
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
import typer
from rich.console import Console
from typer.testing import CliRunner

from eos_downloader.cli.cli import app
from eos_downloader.cli.get import interactive as interactive_module
from eos_downloader.cli.get.interactive import (
    InteractiveResult,
    _formats_for,
    require_interactive_context,
    run_interactive,
)
from eos_downloader.models.version import CvpVersion, EosVersion


def _ans(value: Any) -> Mock:
    """Build a fake questionary prompt whose ``.ask()`` returns ``value``."""
    prompt = Mock()
    prompt.ask.return_value = value
    return prompt


class TestFormats:
    """_formats_for returns package-specific formats without the fallback."""

    def test_eos_excludes_default(self) -> None:
        formats = _formats_for("eos")
        assert "default" not in formats
        assert "cEOS" in formats and "vEOS-lab" in formats

    def test_cvp_formats(self) -> None:
        assert set(_formats_for("cvp")) == {"ova", "rpm", "kvm", "atswi", "upgrade"}


class TestToCommand:
    """InteractiveResult.to_command renders the equivalent CLI command."""

    def test_plain(self) -> None:
        result = InteractiveResult(
            package="cvp", image_format="ova", version="2024.3.0", output="/tmp"
        )
        assert result.to_command() == (
            "ardl get cvp --format ova --version 2024.3.0 --output /tmp"
        )

    def test_ceos_with_docker(self) -> None:
        result = InteractiveResult(
            package="eos",
            image_format="cEOS",
            version="4.29.3M",
            output=".",
            force=True,
            import_docker=True,
            docker_name="arista/ceos",
            docker_tag="4.29.3M",
        )
        cmd = result.to_command()
        assert "--force" in cmd
        assert "--import-docker" in cmd
        assert "--docker-name arista/ceos" in cmd
        assert "--docker-tag 4.29.3M" in cmd

    def test_veos_with_eve_ng(self) -> None:
        result = InteractiveResult(
            package="eos",
            image_format="vEOS-lab",
            version="4.29.3M",
            output=".",
            eve_ng=True,
        )
        assert "--eve-ng" in result.to_command()


class TestRequireInteractiveContext:
    """The wizard only runs with a TTY and a token."""

    def test_non_terminal_exits(self) -> None:
        console = Console(force_terminal=False)
        with pytest.raises(typer.Exit):
            require_interactive_context(console, "token")

    def test_missing_token_exits(self) -> None:
        console = Console(force_terminal=True)
        with pytest.raises(typer.Exit):
            require_interactive_context(console, None)

    def test_valid_context_passes(self) -> None:
        console = Console(force_terminal=True)
        require_interactive_context(console, "token")  # no raise


def _patch_questionary(
    *,
    selects: List[Any],
    confirms: List[Any],
    texts: List[Any],
    paths: List[Any],
) -> ExitStack:
    """Patch questionary prompts with sequenced answers; return an ExitStack."""
    stack = ExitStack()
    stack.enter_context(
        patch.object(
            interactive_module.questionary,
            "select",
            side_effect=[_ans(v) for v in selects],
        )
    )
    stack.enter_context(
        patch.object(
            interactive_module.questionary,
            "confirm",
            side_effect=[_ans(v) for v in confirms],
        )
    )
    stack.enter_context(
        patch.object(
            interactive_module.questionary,
            "text",
            side_effect=[_ans(v) for v in texts],
        )
    )
    stack.enter_context(
        patch.object(
            interactive_module.questionary,
            "path",
            side_effect=[_ans(v) for v in paths],
        )
    )
    return stack


def _mock_querier(branches: List[str], versions: List[Any]) -> Mock:
    """Build a mock AristaXmlQuerier."""
    querier = Mock()
    querier.branches.return_value = branches
    querier.available_public_versions.return_value = versions
    return querier


class TestRunInteractive:
    """End-to-end wizard flow with mocked prompts and querier."""

    @pytest.fixture
    def console(self) -> Console:
        return Console(force_terminal=True)

    def test_eos_ceos_flow_with_docker(self, console: Console) -> None:
        versions = [EosVersion.from_str("4.29.3M"), EosVersion.from_str("4.29.1M")]
        querier = _mock_querier(["4.29", "4.28"], versions)
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=["cEOS", "M", "4.29", "4.29.3M"],
                confirms=[True, False, True],  # docker?, force?, start?
                texts=["arista/ceos", "4.29.3M"],  # docker name, tag
                paths=["/downloads"],
            ):
                result = run_interactive("eos", console, "token", ".")

        assert result is not None
        assert result.image_format == "cEOS"
        assert result.version == "4.29.3M"
        assert result.output == "/downloads"
        assert result.import_docker is True
        assert result.docker_tag == "4.29.3M"
        assert result.eve_ng is False
        querier.available_public_versions.assert_called_once_with(
            branch="4.29", rtype="M", package="eos"
        )

    def test_cvp_skips_release_type(self, console: Console) -> None:
        versions = [CvpVersion.from_str("2024.3.0")]
        querier = _mock_querier(["2024.3"], versions)
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=["ova", "2024.3", "2024.3.0"],  # NO release-type select
                confirms=[False, True],  # force?, start?
                texts=[],
                paths=["."],
            ) as stack:
                select_mock = interactive_module.questionary.select
                result = run_interactive("cvp", console, "token", ".")
                prompts = [call.args[0] for call in select_mock.call_args_list]

        assert result is not None
        assert "Select release type:" not in prompts
        assert prompts == [
            "Select image format:",
            "Select branch:",
            "Select version:",
        ]
        # CVP never queries with a release type.
        querier.available_public_versions.assert_called_once_with(
            branch="2024.3", rtype=None, package="cvp"
        )

    def test_decline_confirmation_aborts(self, console: Console) -> None:
        versions = [EosVersion.from_str("4.29.3M")]
        querier = _mock_querier(["4.29"], versions)
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=["64", "F", "4.29", "4.29.3M"],
                confirms=[False, False],  # force?, start? -> declined
                texts=[],
                paths=["."],
            ):
                result = run_interactive("eos", console, "token", ".")

        assert result is None

    def test_abort_on_format_step(self, console: Console) -> None:
        querier = _mock_querier(["4.29"], [])
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=[None],  # user hit Ctrl+C at the format step
                confirms=[],
                texts=[],
                paths=[],
            ):
                result = run_interactive("eos", console, "token", ".")

        assert result is None

    def test_cancel_output_prompt_aborts(self, console: Console) -> None:
        querier = _mock_querier(["4.29"], [EosVersion.from_str("4.29.3M")])
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=["64", "F", "4.29", "4.29.3M"],
                confirms=[],
                texts=[],
                paths=[None],  # Ctrl+C at the output-directory prompt
            ):
                result = run_interactive("eos", console, "token", ".")

        assert result is None

    def test_cancel_docker_confirm_aborts(self, console: Console) -> None:
        querier = _mock_querier(["4.29"], [EosVersion.from_str("4.29.3M")])
        with patch.object(interactive_module, "AristaXmlQuerier", return_value=querier):
            with _patch_questionary(
                selects=["cEOS", "M", "4.29", "4.29.3M"],
                confirms=[None],  # Ctrl+C at the "Import into Docker?" prompt
                texts=[],
                paths=[],
            ):
                result = run_interactive("eos", console, "token", ".")

        assert result is None


class TestInteractiveGuardrails:
    """Command-level guardrails for --interactive."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> Dict[str, Any]:
        return {"token": "test-token", "log_level": "info", "debug": False}

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_mutually_exclusive_with_version(
        self, mock_init: Mock, runner: CliRunner, mock_context: Dict[str, Any]
    ) -> None:
        mock_init.return_value = (Console(force_terminal=True), "token", False, "info")
        result = runner.invoke(
            app,
            ["get", "eos", "--interactive", "--version", "4.29.3M"],
            obj=mock_context,
        )
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output

    @patch("eos_downloader.cli.get.commands.initialize")
    def test_non_tty_exits(
        self, mock_init: Mock, runner: CliRunner, mock_context: Dict[str, Any]
    ) -> None:
        mock_init.return_value = (Console(force_terminal=False), "token", False, "info")
        result = runner.invoke(app, ["get", "eos", "--interactive"], obj=mock_context)
        assert result.exit_code == 1
        assert "terminal" in result.output.lower()
