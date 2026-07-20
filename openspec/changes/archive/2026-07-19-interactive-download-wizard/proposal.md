## Why

Downloading an image with `ardl get eos` / `ardl get cvp` requires the user to
already know the exact flag values — the image format string, the release type,
and a valid version — and to type them correctly. New or occasional users don't
know which formats exist or which versions are available, so they resort to
trial-and-error or a separate `ardl info` lookup first. A guided, arrow-key
wizard removes that friction: the tool shows the available choices and the user
picks, without memorising any flag.

## What Changes

- Add an `--interactive` / `-i` flag to `get eos` and `get cvp`. When set, the
  command opens a step-by-step wizard instead of reading the other options:
  1. **Format** — pick from the formats available for the package
     (`software_mapping.EOS` / `CloudVision`).
  2. **Release type** — pick `F` or `M`. **Skipped for CVP.**
  3. **Branch** — pick one branch from the available branches (sorted, newest
     first).
  4. **Version** — pick one version from the versions of that branch (sorted,
     newest first).
  5. **Format-dependent options**:
     - `cEOS*` → offer Docker import (then Docker image name + tag).
     - `vEOS*` → offer EVE-NG provisioning.
     - all formats → ask the output directory and a "force re-download" toggle.
  6. **Recap** — show the equivalent non-interactive command and ask for
     confirmation before starting the download.
- Selections use arrow-key navigation via a new `questionary` dependency.
- The wizard reuses the existing download path (`EosXmlObject` / `CvpXmlObject`,
  `download_files`, docker/EVE-NG handling) — no business logic is duplicated.
- Guardrails:
  - `--interactive` requires an interactive terminal (TTY); otherwise it exits
    with a clear error.
  - A token must be available before the wizard starts (branch/version steps
    query the Arista API); otherwise it exits with a clear error.
  - `--interactive` combined with `--version`, `--latest`, or `--branch` is
    rejected with a `BadParameter` error (they are mutually exclusive).
  - `--dry-run` is intentionally not offered in the wizard.

## Capabilities

### New Capabilities
- `interactive-download`: The `--interactive` wizard for `get eos` / `get cvp` —
  its steps, per-package differences (CVP skips release type), format-dependent
  option prompts, the confirmation recap, and the TTY/token/mutual-exclusion
  guardrails.

### Modified Capabilities
<!-- None: the non-interactive get commands keep their current behaviour; the
     wizard is purely additive. -->

## Impact

- **Code**
  - New `eos_downloader/cli/get/interactive.py` — the wizard
    (`run_interactive(...)` returning the collected parameters).
  - `eos_downloader/cli/get/commands.py` — add `--interactive` to `eos()` and
    `cvp()`; when set, run the wizard, then continue the existing flow.
  - `eos_downloader/models/data.py` — reuse `software_mapping` keys for the
    format list (read-only).
- **Dependencies**: add `questionary` (arrow-key prompts; pulls in
  `prompt_toolkit`).
- **Behavior**: non-interactive usage is unchanged; `--interactive` is an
  additive, opt-in entry point.
