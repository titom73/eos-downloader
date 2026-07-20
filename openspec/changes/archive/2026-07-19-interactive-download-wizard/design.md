## Context

`get eos` / `get cvp` are Typer commands whose selection options (`--format`,
`--release-type`, `--branch`, `--version`, `--latest`) drive
`search_version()` → `EosXmlObject`/`CvpXmlObject` → `download_files()` and, for
EOS, optional `--import-docker` / `--eve-ng` handling. Discovering valid values
today requires prior knowledge or a separate `ardl info` call.

The building blocks the wizard needs already exist:
- Format lists: `software_mapping.EOS.keys()` and
  `software_mapping.CloudVision.keys()` (`eos_downloader/models/data.py`).
- Release types: `RTYPES = ["F", "M"]`.
- Branches: `AristaXmlQuerier.branches(package=...)` → sorted-desc list.
- Versions: `AristaXmlQuerier.available_public_versions(branch, rtype, package)`.
  The querier fetches the XML once at construction, so listing branches then
  versions parses the in-memory tree — no second network round-trip.

Rich/Typer provide only text prompts, not arrow-key menus, so a dedicated
prompt library is required.

## Goals / Non-Goals

**Goals:**
- An opt-in `--interactive` wizard on `get eos` / `get cvp` that collects the
  same parameters a normal invocation would and then reuses the existing
  download path.
- Arrow-key selection for format, release type, branch and version.
- Format-aware follow-up prompts (Docker for cEOS, EVE-NG for vEOS) plus output
  directory and a force toggle.
- A confirmation recap showing the equivalent command.

**Non-Goals:**
- Changing any non-interactive behaviour.
- Adding the wizard to `get path` (no version listing there) or to `info`/`debug`.
- A `--dry-run` prompt inside the wizard.
- Segmented download or progress changes (separate work).

## Decisions

### 1. `questionary` for arrow-key prompts

Add `questionary` (built on `prompt_toolkit`) as a runtime dependency. It gives
`select`, `checkbox`, `confirm`, `text` and `path` prompts with arrow-key
navigation and incremental search, and is cross-platform. Alternatives:
`InquirerPy` (similar, less maintained), `simple-term-menu` (Unix-only, no
Windows), `prompt_toolkit` directly (more code). `questionary` is the cleanest
fit and the "no dependency limitation" constraint is accepted.

### 2. Wizard isolated in `cli/get/interactive.py`

A new module exposes `run_interactive(package, console, token, output_default)`
returning a small result object / dict of collected parameters
(`format`, `version`, `import_docker`, `docker_name`, `docker_tag`, `eve_ng`,
`output`, `force`). `eos()` / `cvp()` call it when `--interactive` is set, apply
the result, and fall through to the existing flow. This keeps all business
logic (XML objects, `download_files`, docker/EVE-NG) untouched and unduplicated.

### 3. Package known from the command

`--interactive` lives on each command, so the package (`eos`/`cvp`) is known and
the wizard starts at the format step. The CVP path skips the release-type step
and the Docker/EVE-NG prompts (they don't apply). Chosen over a unified
`get interactive` command because it matches the requested "flag" ergonomics and
avoids an extra package-selection step.

### 4. Format-driven follow-ups

A mapping classifies the chosen format:
- `cEOS`, `cEOS64`, `cEOSarm` → offer Docker import; if accepted, prompt image
  name (default `arista/ceos`) and tag (default = chosen version).
- `vEOS`, `vEOS-lab`, `vEOS64*` → offer EVE-NG provisioning.
- everything → output directory (default cwd) + "force re-download?" toggle.

### 5. Branch then version (both newest-first)

The version list is filtered by the chosen branch and release type and sorted
descending. Requiring a branch first keeps the version list short and readable
(explicitly no "all branches" escape hatch).

### 6. Guardrails before the wizard opens

`eos()`/`cvp()` validate up front:
- `--interactive` with `--version`/`--latest`/`--branch` → `typer.BadParameter`.
- `console.is_terminal` is false → exit with a TTY-required message (reuses the
  shared console from the progress work).
- No token → exit before opening the wizard, since branch/version steps hit the
  API.

### 7. Recap uses the same option names

The confirmation renders the equivalent `ardl get <pkg> --format ... --version
... [--import-docker ...]` string from the collected parameters, both to confirm
intent and to teach the flag form. Download proceeds only on confirmation.

## Risks / Trade-offs

- **New dependency (`questionary` + `prompt_toolkit`)** → Accepted per the "no
  limitation" decision; isolated to the wizard module so the rest of the CLI is
  unaffected if it is ever swapped.
- **Version lists can still be long within a branch** → questionary's
  incremental search mitigates; the branch step already narrows substantially.
- **Wizard requires network + token mid-flow** → validated up front so failures
  are clear rather than mid-wizard.
- **Non-TTY misuse (CI)** → explicit `is_terminal` guard; consistent with the
  plain/rich reporter selection already in the codebase.
- **`--format` has a default, so it can't be reliably detected as "explicitly
  set"** → only `--version`/`--latest`/`--branch` (which default to
  None/False) are treated as conflicting; `--format` is simply overridden by the
  wizard.

## Migration Plan

1. Add `questionary` to dependencies.
2. Add `cli/get/interactive.py` with `run_interactive()` and the format→options
   mapping.
3. Add `--interactive` to `eos()` / `cvp()` with the guardrails; wire the result
   into the existing flow.
4. Tests (mock `questionary` prompts and the querier) + docs.

Rollback: remove the flag, the module, and the dependency; nothing else depends
on them.

## Open Questions

- None outstanding — format/branch/version ordering, CVP skipping release type,
  the force-toggle/no-dry-run choice, and the recap were settled during
  exploration.
