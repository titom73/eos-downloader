## Why

The CLI download progress display is built by instantiating a fresh
`DownloadProgressBar` (Rich `Progress`) for every single file of a download.
Because an EOS/CVP download is made of several files (the image plus its
`sha512`/`md5` hashes), the user sees a separate progress block appear and
disappear for each file instead of one coherent, grouped display — it flickers
and looks unpolished. On top of that, a second, dead progress path built on
`tqdm` still ships as a dependency, the downloader owns its own `Console`
separate from the rest of the CLI, and the concurrency machinery that already
exists (`ThreadPoolExecutor`) is never actually used because each call downloads
a single URL. There is also an import-time side effect installing a global
`SIGINT` handler.

## What Changes

- Introduce a `DownloadReporter` abstraction with two implementations selected
  automatically from `console.is_terminal`:
  - `RichReporter` (TTY): a single grouped, "dressed-up" display — one Rich
    `Progress` inside a titled `Panel`, one bar per file with ETA and a
    per-file spinner/done state, plus an aggregated **Total** bar.
  - `PlainReporter` (non-TTY / CI): clean `loguru` log lines (start, periodic
    percentage milestones, done with size/duration/speed) and **no ANSI codes**.
    CI / non-TTY compatibility is a hard requirement.
- Use **one** shared `Progress` instance for all files of a single download
  instead of one instance per file (removes the flicker).
- Share **one** `Console` between the downloader and `cli/utils.py`.
- Reactivate **inter-file parallelism** using the already-present
  `ThreadPoolExecutor` so the image and its hash files download concurrently
  under the same grouped display.
- **BREAKING (soft)** Replace the `rich_interface: bool` parameter of
  `SoftManager.download_file()` / `SoftManager.downloads()` with
  `progress: "auto" | "rich" | "plain" | "none"`. `rich_interface` is kept as a
  **deprecated alias** (`False` → `"plain"`, `True` → `"auto"`) that emits a
  `DeprecationWarning`, so existing library callers are not broken.
- Remove the dead `tqdm` code path (`SoftManager._download_file_raw`) and drop
  the `tqdm` dependency from `pyproject.toml`.
- Move the module-level `signal.signal(SIGINT, ...)` call out of import time to
  remove the import side effect; interruption handling is scoped to an active
  download.

Explicitly **out of scope**: intra-file segmented / multi-connection download
(HTTP Range) — the change that would actually speed up a single large file. It
depends on server support and needs its own error-recovery design, and will be
proposed as a separate follow-up change.

## Capabilities

### New Capabilities
- `download-progress`: How download progress is reported to the user — the
  TTY vs non-TTY reporter selection, the grouped multi-file display contract,
  parallelism of a download's files, and the `progress` parameter (with the
  deprecated `rich_interface` alias).

### Modified Capabilities
<!-- None: there is no existing spec describing download progress today. -->

## Impact

- **Code**
  - `eos_downloader/helpers/__init__.py` — `DownloadProgressBar` reworked into
    the reporter layer; module-level `SIGINT` side effect removed.
  - `eos_downloader/logics/download.py` — `SoftManager.download_file()` /
    `downloads()` signatures (`progress=` + `rich_interface` alias); one shared
    reporter per `downloads()` call; `_download_file_raw` removed.
  - `eos_downloader/cli/utils.py` and `eos_downloader/cli/get/` — pass the shared
    `Console` into the downloader; call sites updated for the new `progress=`
    parameter.
- **Public API**: `SoftManager.download_file` / `downloads` signature change,
  softened by the deprecated `rich_interface` alias.
- **Dependencies**: `tqdm` removed from `pyproject.toml`.
- **Behavior**: download output is now a single grouped display (TTY) or clean
  log lines (CI); files of one download are fetched concurrently.
