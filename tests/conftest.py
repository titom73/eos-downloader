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
    """Isolate loguru handlers and terminal width around every test."""
    # Stable, wide terminal so Rich-rendered Typer help never wraps/truncates.
    monkeypatch.setenv("COLUMNS", "200")

    # Drop any loguru handler left over from a previous test (it may be bound to
    # a captured stream that has since been closed).
    logger.remove()
    try:
        yield
    finally:
        # Drop handlers this test configured so they cannot leak, bound to a
        # now-closed captured stream, into the next test.
        logger.remove()
