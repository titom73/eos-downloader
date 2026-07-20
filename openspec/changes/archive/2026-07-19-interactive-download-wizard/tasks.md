## 1. Dependency

- [x] 1.1 Add `questionary` to `pyproject.toml` runtime dependencies and update `uv.lock`

## 2. Wizard module

- [x] 2.1 Create `eos_downloader/cli/get/interactive.py` with a `run_interactive(package, console, token, output_default)` entry point returning the collected parameters
- [x] 2.2 Format step: arrow-key select from `software_mapping.EOS.keys()` / `CloudVision.keys()` for the package
- [x] 2.3 Release-type step: select `F`/`M` for EOS; skip entirely for CVP
- [x] 2.4 Branch step: select one branch from `AristaXmlQuerier.branches(package)` (newest-first)
- [x] 2.5 Version step: select one version from `available_public_versions(branch, rtype, package)` (newest-first)
- [x] 2.6 Format-dependent options: `cEOS*` → Docker import (+ name default `arista/ceos`, tag default = version); `vEOS*` → EVE-NG toggle
- [x] 2.7 Common options: output directory (default cwd) and a force-re-download toggle; no dry-run prompt
- [x] 2.8 Build and display the equivalent `ardl get <pkg> ...` command, then a confirmation prompt; abort cleanly if declined

## 3. Command integration

- [x] 3.1 Add `--interactive` / `-i` flag to `get eos` and `get cvp`
- [x] 3.2 On `--interactive`, validate guardrails: reject combination with `--version`/`--latest`/`--branch` (`typer.BadParameter`); require `console.is_terminal`; require a token — each with a clear message
- [x] 3.3 Run `run_interactive()`, apply the returned parameters, and continue the existing download flow (`EosXmlObject`/`CvpXmlObject` → `download_files`, plus Docker/EVE-NG for EOS)

## 4. Tests & docs

- [x] 4.1 Test the format→options mapping (cEOS→docker, vEOS→eve-ng, others→none)
- [x] 4.2 Test CVP skips the release-type step
- [x] 4.3 Test guardrails: non-TTY error, missing-token error, mutual-exclusion `BadParameter`
- [x] 4.4 Test the wizard end-to-end with mocked `questionary` prompts and a mocked querier, asserting the resulting parameters and that decline aborts
- [x] 4.5 Test that the recap renders the correct equivalent command
- [x] 4.6 Update docs/CLI help for `--interactive`
- [x] 4.7 Run `make check` (lint + type + test) and fix findings
