## Why

The codebase currently passes linting and type-checking, but several critical modules concentrate too many responsibilities and the unit-test suite covers only 94% of the production code. This makes routine changes riskier than they need to be and leaves the repository below the expected 95% unit-coverage bar.

## What Changes

- Introduce an explicit engineering quality gate covering unit-test coverage, hotspot refactoring, and regression-focused tests.
- Refactor the largest orchestration modules so that CLI flows, download orchestration, and progress/reporting logic are split into smaller, focused units.
- Reduce duplicated command-path logic between EOS and CVP flows where the current structure creates parallel branches that are hard to evolve safely.
- Add targeted unit tests for currently uncovered or weakly covered branches so the repository reaches and maintains at least 95% unit-test coverage.
- Preserve the current public CLI and library behavior while improving internal maintainability.

## Capabilities

### New Capabilities
- `engineering-quality-gate`: Defines the repository's quality and maintainability requirements for hotspot modules, refactoring boundaries, and the minimum 95% unit-test coverage expectation.

### Modified Capabilities
- None.

## Impact

- Affected code: `eos_downloader/cli/get/commands.py`, `eos_downloader/cli/get/utils.py`, `eos_downloader/logics/download.py`, `eos_downloader/helpers/__init__.py`, `eos_downloader/config.py`, and related tests.
- Affected systems: local quality workflow (`pytest`, coverage, lint, mypy) and the internal structure of the CLI/download stack.
- API impact: no intended breaking change for CLI flags, command behavior, or public library entry points.
