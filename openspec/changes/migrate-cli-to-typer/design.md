## Context

The `ardl` CLI is a Click application: a root `@click.group(cls=AliasedGroup)`
plus four sub-groups and nine subcommands, each built from stacks of
`@click.option`. Shared state (`token`, `log_level`, `debug`) flows through
`ctx.obj`. Configuration comes from a TOML file transformed into Click's
`default_map` (`eos_downloader/config.py`), and environment variables resolve
through `auto_envvar_prefix="arista"` set at invocation time in `cli()`.

The decisive fact for this migration: **Typer is a thin layer over Click, but
since v0.26 it vendors its own copy of Click** (`typer._click`, "code adapted
from Click 8.3.1") rather than using the installed top-level `click`. The
project itself runs on top-level `click` 8.3.0, so at runtime two structurally
compatible — but not identical — Click runtimes coexist. A `typer.Typer()`
compiles to a (vendored) `TyperGroup`; decorated functions become vendored
commands; the runtime `Context` is a `typer._click` Context. Empirically
(validated during apply) this compatibility is high enough that the config
machinery (`ctx.default_map`, `ctx.get_parameter_source`), the env-var prefix,
`CliRunner`, `ctx.obj` passthrough, and attaching top-level `click.Group`s into
the compiled Typer tree all work. The migration is therefore a re-expression of
the surface, not a rewrite of the plumbing — **with one cross-runtime caveat**
(see D8).

Requirements are captured in `specs/cli-framework/spec.md`; motivation in
`proposal.md`.

## Goals / Non-Goals

**Goals:**
- Iso-functional migration: identical command tree, options, aliases, defaults,
  env-var resolution, config precedence, and exit codes.
- Incremental delivery: migrate group by group, keeping `uv run pytest`,
  `make lint`, and `make type` green at every commit.
- Reduce boilerplate and adopt Typer's native Rich help.

**Non-Goals:**
- No change to command names, option names, or exit codes.
- No change to business logic (`logics/`, `models/`, `config.py`).
- No new features. Help/error *presentation* may change; behavior may not.
- Not removing `click` as a dependency (Typer depends on it; some primitives —
  `click.Path`, `click.Context` type hints — may remain).

## Decisions

### D1: Migration cadence — BLOCKER discovered during apply (revised)
**Original plan (incremental cohabitation) is not viable with vendored Typer.**
Empirically, mounting a top-level `click` (8.3) group under a compiled
`typer.Typer` root — or the reverse — breaks control flow: `--help`, `ctx.exit`,
`UsageError`, and `Abort` are raised as one runtime's exception type and are not
caught by the other runtime's `main()` handler (Typer only catches
`typer._click.exceptions.*`; top-level Click only catches
`click.exceptions.*`). Cross-runtime subcommand parsing also fails
(`Got unexpected extra argument(s)`). Because any migrated piece forces the whole
invocation into one runtime, true group-by-group cohabitation is impossible once
Typer vendors its own Click (≥ 0.26).

Two viable cadences remain, and the choice is exclusive:
- **Big-bang on vendored Typer (≥0.27):** migrate the entire CLI in one change so
  a single (vendored) runtime is ever active. Clean modern end state; larger
  diff, no intermediate green rollback points.
- **Incremental on pre-vendoring Typer (<0.26) + pin `click<8.2`:** Typer and the
  project share one Click runtime, so cohabitation works and groups migrate one
  at a time. Requires downgrading `click` project-wide and pinning an older,
  less-maintained Typer line.

**DECISION: big-bang on vendored Typer 0.27.** It delivers the modern stack that
motivated the change and avoids downgrading `click` project-wide. The CLI is
small (9 commands); the single-change risk is acceptable on a feature branch. The
whole CLI is converted to Typer sub-applications mounted on the root via
`app.add_typer`; no top-level Click command groups survive, so no cross-runtime
mixing ever occurs. The project's direct `click` usage (all classic APIs) is
replaced by Typer equivalents or the vendored primitives Typer re-exports.

*Superseded alternative — `Typer.add_click_command()` / structural `add_command`
cohabitation:* the method does not exist in Typer 0.27 and cross-runtime mounting
fails at runtime per the above.

### D2: Preserve `auto_envvar_prefix` via the compiled command — CRITICAL
Typer's `app()` does not expose `auto_envvar_prefix`. The `cli()` entry point
must obtain the compiled Click command and invoke it with the prefix:
```python
def cli() -> None:
    command = typer.main.get_command(app)
    command(obj={}, auto_envvar_prefix="arista")
```
Losing this silently breaks every `ARISTA_*` variable. A regression test asserts
`ARISTA_TOKEN` still resolves the root `--token` (spec: *Environment variable
resolution*).
*Alternative — per-option `envvar=`:* rejected; it would require re-declaring
prefixed names on dozens of options and diverges from current behavior.

### D3: Port `AliasedGroup` onto `TyperGroup`
Typer groups instantiate `TyperGroup`, not `click.Group`. Re-base the alias
class as `class AliasedGroup(TyperGroup)` (keeping the `get_command` /
`resolve_command` prefix logic verbatim) and pass it via
`typer.Typer(cls=AliasedGroup)` on the root and each sub-group.
*Alternative — drop prefix aliasing:* rejected; it is existing behavior covered
by the spec.

### D4: Keep `config.py` and the `default_map` flow unchanged
The root callback continues to call `get_default_map()` and set
`ctx.default_map`, then reconcile root options against
`ctx.get_parameter_source(...)`. Because the Typer context *is* a Click context,
this code is reused as-is. This isolates the migration to the CLI surface and
avoids reworking config precedence.

### D5: Context and errors — Typer idioms mapped 1:1
- `@click.pass_context` → `ctx: typer.Context` parameter; `ctx.obj` dict
  unchanged; the `initialize()` helper keeps its `tuple[Console, str, bool, str]`
  contract.
- `ctx.exit(1)` → `raise typer.Exit(1)`; `raise click.UsageError(...)` →
  `raise typer.BadParameter(...)` (or keep `click.UsageError`, which Typer
  propagates). Exit codes are asserted by spec.
- Options become typed parameters with explicit names to preserve aliases and
  avoid builtin shadowing, e.g.
  `format: str = typer.Option("vmdk", "--format")`,
  `log_level: str = typer.Option("error", "--log-level", "--log")`,
  `clab: Optional[str] = typer.Option(None, "--containerlab-topology", "--clab")`.

### D6: Rewrite tests to invoke through the root app
Tests that import command callables directly (notably
`tests/unit/cli/test_get_commands.py` importing `eos/cvp/path`) are rewritten to
invoke the root app with full argument paths (`runner.invoke(app_or_cmd,
["get", "eos", …])`) using `typer.testing.CliRunner` (or Click's on the compiled
command). This matches real usage and survives future internal restructuring.
*Alternative — expose a `typer.Typer` per module for isolated invocation:*
rejected in favor of root-app invocation per the exploration decision.

### D7: Dependencies — top-level Click removed entirely
Add `typer`; remove the unused `click-help-colors`; keep `rich`. **Top-level
`click` is removed from the project's declared dependencies altogether** (neither
`[project.dependencies]` nor the `dev` extras): Typer vendors its own Click, so
nothing in the repo imports top-level `click` — not the application, not the
tests. Verified two ways: no `import click` remains anywhere under
`eos_downloader/` or `tests/`, and the app imports, runs `--help`, resolves
subcommand aliases, and exposes `.commands` even when `click` is made
unimportable (blocked in `sys.modules`). The `_build_command` return type is
annotated with `AliasedTyperGroup` (a `typer.core.TyperGroup`) instead of
`click.Command`.

To make the tests click-free, the root `Typer` is given `name="ardl"` (so the
compiled prog name and `Usage: ardl` are preserved) and every test invokes the
`Typer` **app** object through `typer.testing.CliRunner` — which forwards
`obj=`/`auto_envvar_prefix=`/`prog_name=` via its `**extra` to `cli.main`. The
compiled command is still exported as `ardl` for the one diagnostic test that
inspects `.commands`. `click` remains installed only transitively (via dev tools
like black/mkdocs), which is irrelevant to this package's dependency contract.

### D8: Enum comparisons must be cross-runtime safe — CRITICAL (discovered during apply)
Because Typer vendors Click, a `typer.Context` inside a Typer callback returns a
`typer._click.core.ParameterSource`, which is a **different enum object** from
the top-level `click.core.ParameterSource`. The current root config
reconciliation in `cli.py` compares `ctx.get_parameter_source(name) ==
click.core.ParameterSource.DEFAULT`; under Typer this comparison is **always
False**, silently disabling config injection for root options. Fix: compare by
member name — `ctx.get_parameter_source(name).name == "DEFAULT"` — which is
runtime-agnostic. Verified empirically: by-identity comparison returns False for
both DEFAULT and COMMANDLINE sources; by-name returns the correct result.
*Alternative — import the vendored enum:* rejected; `typer._click` is a private
module and unstable API.

## Risks / Trade-offs

- **Losing `auto_envvar_prefix` (D2)** → dedicated regression test for
  `ARISTA_TOKEN`; called out as the first migration checkpoint.
- **`TyperGroup` vs `click.Group` base for `AliasedGroup` (D3)** → verify prefix
  resolution with existing `test_cli.py` alias tests (`ge`, `d`) before
  migrating subcommands.
- **Help/error text changes break assertions** → audit tests that assert on help
  strings; relax to behavior/exit-code assertions where presentation changed
  (display change is explicitly accepted in the proposal).
- **`default_map` reconciliation subtleties (D4)** → keep `config.py` untouched
  and re-run `test_config_commands.py` / config-precedence tests after the root
  conversion.
- **Option name auto-derivation (`format`, `release_type`)** → pin explicit
  `--option-name` strings so Typer does not rename or shadow builtins.
- **Return values vs exit codes** → commands currently `return 0/int`; both Click
  and Typer ignore return values for exit status, so error paths must use
  `typer.Exit`; verified by exit-code scenarios.

## Migration Plan

1. Add `typer` dep; introduce `app = typer.Typer(cls=AliasedGroup)` root and the
   `cli()` entry using `typer.main.get_command`; port `AliasedGroup` onto
   `TyperGroup`; keep all four sub-groups as Click commands mounted via
   `add_click_command`. Green.
2. Migrate `config` (`init`, `show`) — simplest, no `ctx.obj`. Green.
3. Migrate `debug` (`xml`). Green.
4. Migrate `info` (`versions`, `latest`, `mapping`). Green.
5. Migrate `get` (`eos`, `cvp`, `path`) — largest surface. Green.
6. Rewrite direct-invocation tests to root-app invocation; audit help-string
   assertions.
7. Remove `click-help-colors`; final lint/type/test sweep.

**Rollback:** each step is an independent green commit; revert the last step
without touching earlier ones. Cohabitation guarantees a working CLI throughout.

## Open Questions

- Should `click.UsageError` be swapped for `typer.BadParameter` everywhere, or
  left as-is where already raised? (Both preserve exit behavior — cosmetic.)
- Do any downstream automation scripts assert on exact help/error text? If so,
  coordinate the accepted display change.
