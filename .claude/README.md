# Claude Code Configuration

This directory contains Claude Code automations for the eos-downloader project.
All files here (except `settings.local.json`) are checked into version control and shared across the team.

---

## Directory Structure

```
.claude/
├── settings.json          # Shared hooks (auto-format, security guards)
├── settings.local.json    # Personal permissions — NOT committed
├── agents/
│   ├── python-reviewer.md # Code review subagent
│   └── test-writer.md     # Test generation subagent
└── skills/
    ├── run-checks/        # /run-checks — full quality gate
    └── bump-release/      # /bump-release — version bump workflow
```

Also at the repo root:

```
.mcp.json                  # Project-level MCP server definitions
```

---

## MCP Servers

Defined in `.mcp.json`. Claude Code picks them up automatically when you open this project.

### context7
Live documentation lookup for the libraries used in this project (Click, Pydantic v2, requests, paramiko, rich, loguru…).

**Usage** — ask Claude to use context7 when you want up-to-date API references:
> "Using context7, show me how to use `@field_validator` in Pydantic v2."

**Requires**: `npx` available in PATH (`npm` / Node.js installed).

### GitHub MCP
Rich GitHub integration: issues, PRs, Actions runs, without shelling out to `gh`.

**Requires**: set `GITHUB_PERSONAL_ACCESS_TOKEN` in your environment (add to `.envrc`):
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
```

---

## Hooks

Defined in `.claude/settings.json`. They run automatically — no user action needed.

### PostToolUse: Auto-format Python on edit
After every `Edit` or `Write` on a `.py` file, `black` runs automatically.
This catches formatting issues before pre-commit does, reducing round-trips.

### PreToolUse: Block edits to sensitive files
Any attempt to write to `.envrc` or `.env` files is blocked with an error.
This prevents accidental token exposure via edited config files.

---

## Skills

Invoked by typing `/skill-name` in the Claude Code prompt.
These are **user-only** skills (`disable-model-invocation: true`) — Claude will not call them autonomously.

### `/run-checks` — Full quality gate

Runs `make check`, which executes lint → type-check → tests in sequence.

```
/run-checks
```

What it does:
1. Runs `make check` (flake8 + pylint → mypy → pytest with coverage)
2. Reports failures with `file:line` references
3. Offers to run `make format` if only formatting is the issue

Use this before opening a PR to catch everything in one shot.

### `/bump-release` — Version bump

Bumps the project version using `bumpver` and prepares the release.

```
/bump-release [patch|minor|major]
```

Default level: `patch`

What it does:
1. Shows the current version
2. Dry-runs the bump and displays the diff for review
3. Waits for confirmation
4. Applies the bump (updates `pyproject.toml`, creates a commit)
5. Reminds you to push — GitHub Actions then handles PyPI publishing via OIDC

Version pattern: `MAJOR.MINOR.PATCH` (e.g. `0.15.0 → 0.15.1`).

---

## Subagents

Subagents are specialized Claude instances with project-specific instructions.
Claude can invoke them automatically, or you can ask explicitly.

### `python-reviewer`

Reviews Python code against eos-downloader conventions:
- Full type hints (mypy strict)
- NumPy docstrings on public APIs
- `loguru` for logging, `rich` for CLI output
- `pathlib.Path` for file paths
- `EosVersion`/`CvpVersion` for version handling (no manual string parsing)
- No tokens logged or hardcoded

**How to trigger**:
> "Review `eos_downloader/logics/arista_xml_server.py` with the python-reviewer agent."

Or Claude will invoke it automatically after significant code changes.

### `test-writer`

Generates pytest unit tests following project conventions:
- Files in `tests/unit/<module>/test_<module>.py`
- Uses `responses` library to mock HTTP — never hits real Arista servers
- Imports fixtures from `tests/lib/fixtures.py`
- Applies `@pytest.mark.parametrize` for data-driven cases
- Covers CLI commands via `click.testing.CliRunner`

**How to trigger**:
> "Use test-writer to generate tests for `eos_downloader/models/version.py`."

---

## Personal Settings (`settings.local.json`)

This file is gitignored. It holds your personal tool permissions (the `allow` list that controls which Bash commands Claude can run without prompting you).

To add a permission, either edit the file directly or use:
```
/update-config
```
