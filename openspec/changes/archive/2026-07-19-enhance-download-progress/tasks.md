## 1. Reporter layer

- [x] 1.1 Add a `DownloadReporter` interface (ABC or `Protocol`) with `add_file(name, total) -> id`, `advance(id, n)`, `complete(id)`, and context-manager start/stop, in `eos_downloader/helpers/`
- [x] 1.2 Implement `RichReporter`: one shared `rich.progress.Progress` with spinner, filename, bar, percentage, transfer speed, download size, and time-remaining columns, rendered in a titled `Panel`, plus an aggregated **Total** task
- [x] 1.3 Implement `PlainReporter`: `loguru` lifecycle lines (start with size, a progress line at each 10% milestone, completion with size/duration/speed), no ANSI, no `Live`
- [x] 1.4 Implement a no-op reporter for `progress="none"`
- [x] 1.5 Add a factory that resolves `progress` mode + shared `Console` into the concrete reporter (`"auto"` → `console.is_terminal`)
- [x] 1.6 Handle missing `Content-Length` gracefully (indeterminate bar / start line without total)

## 2. Signal handling

- [x] 2.1 Remove the module-level `signal.signal(SIGINT, ...)` side effect from `helpers/__init__.py`
- [x] 2.2 Install/restore the SIGINT handler inside the reporter's start/stop using `signal.getsignal`; keep a threading `Event` to stop worker threads

## 3. Shared console

- [x] 3.1 Make `cli/utils.py` own the single `Console` and expose it to the download layer
- [x] 3.2 Remove the module-global `Console` in `helpers/__init__.py`; thread the shared console down into `SoftManager`

## 4. SoftManager integration

- [x] 4.1 Add `progress: Literal["auto","rich","plain","none"] = "auto"` to `SoftManager.download_file()` and `downloads()`
- [x] 4.2 Add `rich_interface` deprecated alias (sentinel default `None`; `False`→`"plain"`, `True`→`"auto"`) emitting `DeprecationWarning`
- [x] 4.3 Rework `downloads()` to create one reporter, enter it once, and download the image + hash files concurrently via the existing `ThreadPoolExecutor`, each updating its own bar
- [x] 4.4 Make `download_file()` register a file on a supplied reporter, or create a one-file reporter when called standalone
- [x] 4.5 Remove `SoftManager._download_file_raw` and the old `DownloadProgressBar` internals

## 5. Dependency & call sites

- [x] 5.1 Remove `tqdm` from `pyproject.toml` and delete its imports
- [x] 5.2 Update all CLI call sites (`cli/get/commands.py`, `cli/get/utils.py`) to pass the shared console and `progress=` instead of `rich_interface=True`
- [x] 5.3 Add a CLI `--no-progress` flag that maps to `progress="none"` (available on the download commands)

## 6. Tests & docs

- [x] 6.1 Unit test reporter selection: `auto` with `is_terminal` True/False, explicit `rich`/`plain`/`none`
- [x] 6.2 Unit test `rich_interface` alias mapping emits `DeprecationWarning` and resolves to the right mode
- [x] 6.3 Test that `PlainReporter` output contains no ANSI escape sequences
- [x] 6.4 Test that importing the helpers module does not replace the process SIGINT handler
- [x] 6.5 Test concurrent multi-file download completes and updates one shared display
- [x] 6.6 Update docs/docstrings for the new `progress` parameter and the `rich_interface` deprecation
- [x] 6.7 Run `make check` (lint + type + test) and fix findings
