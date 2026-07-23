---
name: run-checks
description: Run the full quality gate (black format, flake8+pylint lint, mypy type-check, pytest) via make check
disable-model-invocation: true
---

Run the full quality gate for eos-downloader.

Steps:
1. Run `make check` from the repo root (`uv run` is used internally by the Makefile)
2. If the command fails, identify whether it's a lint, type, or test failure
3. Report failures concisely with file:line references
4. If it's a formatting issue, offer to run `make format` (which runs black) then recheck

The `make check` target runs: lint (flake8 + pylint) → type (mypy) → test (pytest with coverage).
To run individual stages: `make lint`, `make type`, `uv run pytest`.
