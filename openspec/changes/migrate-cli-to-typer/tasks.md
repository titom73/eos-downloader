> **Cadence: big-bang** (see design D1). Incremental cohabitation is impossible
> with vendored Typer, so the whole CLI is converted in one change. "Green" is
> only asserted at the end of the migration, not per group.

## 1. Foundation: Typer root

- [x] 1.1 Add `typer` to `[project.dependencies]` in `pyproject.toml`; run `uv sync --all-extras`
- [x] 1.2 Add `AliasedTyperGroup(typer.core.TyperGroup)` in `cli/utils.py` with the command-prefix aliasing logic (kept for the Typer root and every sub-app)
- [x] 1.3 Convert root `ardl` in `cli.py` to `typer.Typer(cls=AliasedTyperGroup)` with a root callback holding `--token`, `--log-level`/`--log`, `--debug-enabled`/`--debug`, `--version` (eager callback); fill `ctx.obj{token,log_level,debug}`; keep `get_default_map()` / `ctx.default_map` reconciliation; no-subcommand → print help, exit 0
- [x] 1.4 Make the config-source reconciliation cross-runtime safe (D8): compare `ctx.get_parameter_source(name).name == "DEFAULT"`
- [x] 1.5 Rewrite `cli()` entry to `command = _build_command(); command(obj={}, auto_envvar_prefix="arista")`, where `_build_command` compiles the Typer app and names it `ardl`; expose module-level `ardl` for tests

## 2. Migrate command groups to Typer sub-apps

- [x] 2.1 `config`: convert `init`, `show` (`cli/config/commands.py`) to a `typer.Typer` sub-app (options `--output`/`-o`, `--force`/`-f`); `click.echo` → `typer.echo`; `SystemExit(1)` → `typer.Exit(1)`; mount via `app.add_typer(config_app, name="config", help="Manage ardl configuration.")`
- [x] 2.2 `debug`: convert `xml` (`cli/debug/commands.py`) to a Typer sub-app (`--output`, `--log-level`/`--log`), reading `token` from `ctx.obj`; mount via `add_typer` with help "Debug commands to work with ardl"
- [x] 2.3 `info`: convert `versions`, `latest`, `mapping` (`cli/info/commands.py`) preserving `--format` choices (`json`/`text`/`fancy`), `--package`, `--branch`/`-b`, `--release-type`, `--details`, JSON-clean output; mount with help "List information from Arista website"
- [x] 2.4 `get`: convert `eos`, `cvp`, `path` (`cli/get/commands.py`) preserving every option incl. `--containerlab-topology`/`--clab`, `--source`/`-s`, `--output`/`-o`, docker options, `--dry-run`, `--force`; keep mutual-exclusion check; `ctx.exit(1)` → `typer.Exit(1)`; mount with help "Download Arista from Arista website"
- [x] 2.5 Adapt `cli/get/utils.py::initialize(ctx)` to accept a `typer.Context` while keeping its `tuple[Console, str, bool, str]` return contract
- [x] 2.6 Represent fixed-choice options with `Enum`s (log level, format, package) so Typer enforces them iso-functionally

## 3. Tests

- [x] 3.1 Update `tests/unit/cli/test_cli.py` (root help/version/no-args/alias) to the Typer-compiled `ardl`
- [x] 3.2 Rewrite `tests/unit/cli/test_get_commands.py` (imports `eos/cvp/path`) to invoke through the root app (`ardl get eos …`); update mock patch targets if module paths change
- [x] 3.3 Update `test_config_commands.py`, `test_debug_commands.py`/`test_debug.py`, `test_info.py`, `test_get.py`/`test_get_utils.py` to root-app invocation
- [x] 3.4 Update `tests/integration/test_cli_workflow.py` invocations
- [x] 3.5 Add a regression test asserting `ARISTA_TOKEN` resolves the root `--token` (critical env-var guard)
- [x] 3.6 Add a regression test asserting a TOML config injects a root option under Typer (D8 guard)
- [x] 3.7 Audit help-string assertions; relax presentation-coupled ones to behavior/exit-code checks (display change is accepted)

## 4. Cleanup and verification

- [x] 4.1 Remove `click-help-colors` from `pyproject.toml`
- [x] 4.2 Remove the now-unused legacy `AliasedGroup(click.Group)` from `cli/utils.py`; drop direct top-level `click` imports where a Typer equivalent exists
- [x] 4.3 Full sweep: `make check` (lint + type + test) green; `uv run pytest --cov=eos_downloader` with no coverage regression
- [x] 4.4 Manual smoke test: env-var (`ARISTA_TOKEN`), config-file precedence, prefix aliasing, each subcommand `--help`, exit codes
- [x] 4.5 Update docs / CLAUDE.md references describing the CLI as "Click-based"

## 5. Remove top-level Click entirely (app + tests)

- [x] 5.1 Remove `import click` from source; annotate `_build_command` with `AliasedTyperGroup`; remove `click` from `[project.dependencies]`
- [x] 5.2 Give the root Typer `name="ardl"` so `typer.testing` preserves the `ardl` prog name / `Usage: ardl`
- [x] 5.3 Migrate all CLI/integration tests from `click.testing.CliRunner` (invoking compiled `ardl`) to `typer.testing.CliRunner` (invoking the `app` object); forward `obj=`/`env=`/`auto_envvar_prefix=` via `extra`
- [x] 5.4 Replace `click.UsageError` assertion in `test_get_commands.py` with `typer.BadParameter`; keep compiled `ardl` import only for the `.commands` diagnostic
- [x] 5.5 Remove `click` from the `dev` extras; refresh docstrings mentioning Click's runner
- [x] 5.6 Verify zero `import click` under `eos_downloader/` and `tests/`; prove the CLI runs with `click` blocked in `sys.modules`; `make check` green (445 tests)
