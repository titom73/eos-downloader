## Why

The `ardl` CLI is built on Click with a growing stack of `@click.option`
decorators, a custom `AliasedGroup`, and manual `ctx.obj` wiring. Typer offers
the same Click foundation with typed function signatures, native Rich help
rendering, and less boilerplate. Because Typer compiles down to Click, we can
adopt it without breaking the existing command contract — only the help/output
presentation evolves.

## What Changes

- Migrate the CLI framework from **Click to Typer**, group by group, keeping the
  tree green at every step (config → debug → info → get), with temporary
  Click/Typer cohabitation via `add_click_command` during the transition.
- Convert the root `ardl` group and all subcommands (`get eos|cvp|path`,
  `info versions|latest|mapping`, `debug xml`, `config init|show`) to Typer,
  preserving every option, alias, default, and env var.
- Preserve `auto_envvar_prefix="arista"` by invoking the compiled Click command
  from `typer.main.get_command(app)` — **critical**, or all `ARISTA_*` env vars
  break.
- Port `AliasedGroup` (command-prefix matching) from `click.Group` onto
  `TyperGroup`.
- Keep TOML config injection (`config.py`, `ctx.default_map`,
  `get_parameter_source`) unchanged — it operates on the underlying Click
  context, which Typer preserves.
- Replace `ctx.exit(code)` with `typer.Exit(code)` and `click.UsageError` with
  the Typer equivalent, keeping exit codes identical.
- Rewrite tests that invoke command callables directly (e.g.
  `test_get_commands.py` importing `eos/cvp/path`) to invoke through the root
  app (`ardl get eos …`).
- Remove the unused `click-help-colors` dependency; add `typer` to
  dependencies. Direct `click` usage remains as a transitive/explicit dep.
- **Display change (accepted):** help and error output adopt Typer's native Rich
  formatting. No behavioral change to commands, options, or exit codes.

## Capabilities

### New Capabilities
- `cli-framework`: The framework-agnostic contract the `ardl` CLI must satisfy —
  command/subcommand tree, option names and aliases, defaults, environment
  variable resolution (`auto_envvar_prefix`), command-prefix aliasing, TOML
  config injection precedence, shared context (`token`/`log_level`/`debug`), and
  exit codes. Encodes the iso-functional guarantees the Typer migration must not
  regress.

### Modified Capabilities
<!-- None: no existing CLI spec; behavior is preserved, not changed. -->

## Impact

- **Code:** `eos_downloader/cli/**` (root `cli.py`, `utils.py`, and the `get`,
  `info`, `debug`, `config` command modules). `config.py` unchanged.
- **Dependencies:** add `typer`; remove `click-help-colors`; `rich` retained.
- **Tests:** `tests/unit/cli/**` and `tests/integration/test_cli_workflow.py`
  invocation call-sites rewritten to go through the root app.
- **Users:** no change to command syntax, options, env vars, or exit codes;
  help/error output looks different (Rich-rendered).
- **Entry point:** `ardl = "eos_downloader.cli.cli:cli"` preserved.
