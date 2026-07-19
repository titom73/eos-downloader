#!/usr/bin/env python
# coding: utf-8 -*-

"""Shared pytest fixtures and test-environment isolation.

The CLI tests drive the Typer application through ``typer.testing.CliRunner``,
which swaps ``sys.stdout``/``sys.stderr`` for captured streams during each
invocation and closes them afterwards. Two side effects of that need taming so
the suite behaves identically on every platform/CI:

1. ``eos_downloader.logging_config.configure_logging`` binds a loguru handler to
   ``sys.stderr`` *at call time*. When a command runs inside a CliRunner
   invocation, that handler points at the (soon to be closed) captured stream.
   A later test that logs before re-configuring would then write to a closed
   stream, raising ``ValueError: I/O operation on closed file`` — which on Linux
   cascades into a pytest ``INTERNALERROR`` and can corrupt captured output.

2. Typer renders help with Rich, whose width depends on the environment. Forcing
   a wide, stable width keeps help-text assertions robust across platforms (no
   wrapping or ``…`` truncation of option names).
"""

import pytest
from loguru import logger


@pytest.fixture(autouse=True)
def _isolate_test_environment(monkeypatch: pytest.MonkeyPatch) -> object:
    """Isolate loguru handlers, terminal width and color around every test."""
    # Stable, wide terminal so Rich-rendered Typer help never wraps/truncates.
    monkeypatch.setenv("COLUMNS", "200")

    # Force plain (non-terminal) help output. Typer sets its module-level
    # ``FORCE_TERMINAL`` to True whenever ``GITHUB_ACTIONS``/``FORCE_COLOR``/
    # ``PY_COLORS`` is set, which makes Rich emit bold/color escape codes in the
    # rendered help. Those codes split tokens like "Usage: ardl" and
    # "--log-level", so plain-substring assertions pass locally but fail on CI
    # (where GITHUB_ACTIONS is always set). ``_get_rich_console`` reads this
    # global at call time, so patching it to False yields plain text everywhere.
    monkeypatch.setattr("typer.rich_utils.FORCE_TERMINAL", False)

    # Drop any loguru handler left over from a previous test (it may be bound to
    # a captured stream that has since been closed).
    logger.remove()
    try:
        yield
    finally:
        # Drop handlers this test configured so they cannot leak, bound to a
        # now-closed captured stream, into the next test.
        logger.remove()
