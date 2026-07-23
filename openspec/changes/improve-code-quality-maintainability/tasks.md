## 1. Coverage Baseline And Regression Safety

- [x] 1.1 Add targeted unit tests for the currently uncovered branches in `cli/config/commands.py`, `cli/get/interactive.py`, `cli/utils.py`, `logging_config.py`, and other low-effort gaps blocking the 95% threshold
- [x] 1.2 Add regression tests around the public `ardl get eos` / `ardl get cvp` flows so the current command behavior is pinned before refactoring shared orchestration
- [x] 1.3 Re-run unit coverage and record the remaining uncovered hotspots that still need structural work

## 2. CLI Orchestration Refactor

- [x] 2.1 Extract shared EOS/CVP validation, version resolution, and error-rendering helpers from `eos_downloader/cli/get/commands.py`
- [x] 2.2 Keep package-specific branches explicit while removing duplicated command-path logic between EOS and CVP flows
- [x] 2.3 Update or add focused unit tests for the extracted CLI orchestration helpers

## 3. Download And Helper Decomposition

- [x] 3.1 Split `eos_downloader/logics/download.py` into clearer responsibility boundaries while preserving the current public downloader entry points
- [x] 3.2 Reorganize `eos_downloader/helpers/__init__.py` so progress reporting, signal handling, and transfer orchestration no longer live in one monolithic helper module
- [x] 3.3 Update imports and compatibility exports as needed so internal refactors do not break supported callers

## 4. Quality Gate Closure

- [x] 4.1 Add or adjust unit tests for any branches introduced or moved during the refactor until total unit coverage for `eos_downloader` is at least 95%
- [x] 4.2 Run `make check` and fix any regressions from linting, typing, or tests
- [x] 4.3 Review the resulting public behavior against the regression tests and confirm that no intended CLI or library contract has changed
