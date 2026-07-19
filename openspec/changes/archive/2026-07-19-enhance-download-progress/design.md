## Context

Download progress today is produced two different ways:

- `SoftManager.download_file(rich_interface=True)` (always true from the CLI)
  creates a new `eos_downloader.helpers.DownloadProgressBar` per file. Each
  instance owns its own Rich `Progress` and enters/exits its own `with` block,
  so a multi-file download (image + `sha512`, sometimes `md5`) shows several
  progress blocks appearing and disappearing in sequence.
- `SoftManager._download_file_raw` renders via `tqdm`. This path is only reached
  when `rich_interface=False`, which never happens from the CLI — it is dead
  code, and `tqdm` remains a declared dependency.

Additional friction: `helpers/__init__.py` builds its own `Console`, separate
from the CLI's `console_configuration()`; `DownloadProgressBar.download()` was
written for a `ThreadPoolExecutor` with 4 workers but is always called with a
single-URL list, so the concurrency is inert; and the module installs a global
`signal.signal(SIGINT, ...)` at import time.

Constraints:
- **CI / non-TTY must keep working** and must not emit ANSI control sequences.
- The library API (`SoftManager`) is public — breaking callers outright is not
  acceptable without a migration path.

## Goals / Non-Goals

**Goals:**
- A single, polished grouped display per download (one Panel, one bar per file,
  ETA, per-file state, aggregated Total bar) in a terminal.
- Clean, ANSI-free `loguru` output in non-TTY / CI.
- One shared `Console` between CLI and downloader.
- Real inter-file concurrency using the existing thread pool.
- Remove `tqdm` and the dead raw path; remove the import-time signal side effect.
- Replace `rich_interface` with a `progress` mode while preserving the old
  parameter as a deprecated alias.

**Non-Goals:**
- Intra-file segmented / multi-connection (HTTP Range) download — the actual
  single-file speed-up. Separate follow-up change.
- Cross-download concurrency (downloading several versions at once).
- Changing checksum, caching, docker-import, or EVE-NG provisioning logic beyond
  the call-site parameter rename.

## Decisions

### 1. A `DownloadReporter` interface with two implementations

Introduce a small interface (e.g. an abstract base or `Protocol`) exposing the
lifecycle the download loop needs, roughly:

```
class DownloadReporter:
    def __enter__/__exit__            # start/stop the live display
    def add_file(name, total) -> id   # register a file
    def advance(id, n_bytes)          # progress
    def complete(id)                  # mark a file done
```

- `RichReporter` wraps one shared `rich.progress.Progress` (with `TextColumn`,
  `BarColumn`, `TaskProgressColumn`/percentage, `TransferSpeedColumn`,
  `DownloadColumn`, `TimeRemainingColumn`, and a `SpinnerColumn`) plus a separate
  "Total" task, rendered inside a titled `Panel` via `Live`.
- `PlainReporter` implements the same methods but emits `loguru` lines: one at
  `add_file` (name + total size), milestone lines from `advance` (e.g. every
  25%), and one at `complete` (size + duration + average speed). No `Live`, no
  ANSI.

Rationale: one seam lets the download loop stay identical across TTY and CI, and
keeps Rich objects out of `SoftManager`'s core logic. Alternative — branching on
`is_terminal` inside `download_file` with two inline code paths — was rejected as
the exact duplication that made the current code inconsistent.

### 2. One shared `Progress` per `downloads()` call, opened around the loop

`SoftManager.downloads()` creates one reporter, enters it once, and passes it
into each `download_file()` invocation (which registers a file and streams into
it) instead of each `download_file()` creating its own display. `download_file()`
called standalone (library use) still works by creating a one-file reporter
internally when none is supplied.

Rationale: removes the flicker (the visible core defect) and is the natural home
for the Total bar. Alternative — keeping per-file `Progress` but stacking them in
a `Group` — still tears down/recreates and complicates the Total aggregation.

### 3. Reporter selection via `progress` mode + shared console

`progress: Literal["auto","rich","plain","none"] = "auto"`. `"auto"` picks by
`console.is_terminal`; `"rich"`/`"plain"` force; `"none"` uses a no-op reporter.
The `Console` is created once (in `cli/utils.py`) and threaded down into
`SoftManager`, replacing the module-global console in `helpers`.

### 4. `rich_interface` kept as a deprecated alias

Signatures accept both. Resolution:

```
if rich_interface is not None:
    warnings.warn(..., DeprecationWarning, stacklevel=2)
    progress = "plain" if rich_interface is False else "auto"
```

`rich_interface` defaults to `None` (sentinel) so we can distinguish "not passed"
from an explicit bool. Rationale: zero breakage for existing library callers,
clean new surface, removable at the next major.

### 5. Signal handling scoped to a download

Move `signal.signal(SIGINT, handler)` out of module scope. The `RichReporter`
(and the plain path) install/restore the handler within their `__enter__` /
`__exit__` using `signal.getsignal` to save and restore the previous handler, so
importing the module has no global effect. A threading `Event` still signals the
worker threads to stop.

Rationale: import side effects are surprising and hostile to library embedding
and tests. Trade-off: signal handlers only work in the main thread — acceptable
since the reporter is entered from the main thread.

### 6. Remove `tqdm`

Delete `_download_file_raw` and the `tqdm` import; drop `tqdm` from
`pyproject.toml`. The former `rich_interface=False` behavior is superseded by
`progress="plain"`.

## Risks / Trade-offs

- **Public API change on `SoftManager`** → Mitigated by the deprecated
  `rich_interface` alias with a `DeprecationWarning`; documented in the proposal
  as a soft-breaking change.
- **Rich `Progress`/`Live` may still emit control chars if `is_terminal`
  detection is wrong (e.g. odd CI TERM)** → `"auto"` relies on Rich's own
  detection, and CI can force `progress="plain"` (or `--no-progress`); the plain
  path is guaranteed ANSI-free.
- **Thread-safety of shared `Progress` updates** → Rich `Progress.update` is
  thread-safe; each worker owns a distinct task id, so concurrent `advance`
  calls do not contend on the same task.
- **Concurrency changes log/interleave ordering** → Per-file rows isolate output
  in TTY; in plain mode, log lines carry the filename so interleaving stays
  readable.
- **Content-Length missing** → current code assumes the header exists; keep a
  guard so an unknown total renders an indeterminate bar / a start line without a
  total rather than crashing.

## Migration Plan

1. Add the reporter layer in `helpers/` without removing the old class yet.
2. Thread the shared `Console` and `progress` param through `SoftManager` and CLI
   call sites; add the `rich_interface` alias shim.
3. Switch `downloads()` to the single-reporter loop with concurrency.
4. Remove `_download_file_raw`, the old `DownloadProgressBar` internals, the
   module-level signal call, and the `tqdm` dependency.
5. Update tests/docs.

Rollback: revert the branch; no persisted state or data migration is involved.

## Resolved Decisions

- **CLI `--no-progress` flag**: added on the download commands, mapping to
  `progress="none"`. Auto-detection stays the default; the flag gives CI an
  explicit, discoverable override.
- **`PlainReporter` milestones**: one progress line at each 10% step
  (10%, 20%, … 90%), plus the start and completion lines.
