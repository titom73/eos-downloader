# download-progress Specification

## Purpose
Define how download progress is reported to the user: the automatic selection between a rich (interactive terminal) and a plain (non-TTY / CI) reporter, the grouped single-display contract for a download's files, concurrent fetching of those files, and the `progress` parameter (with the deprecated `rich_interface` alias).
## Requirements
### Requirement: Automatic reporter selection by terminal capability

The system SHALL report download progress through a `DownloadReporter`
abstraction with two implementations, and SHALL select one automatically based
on whether the shared `Console` is attached to an interactive terminal.

#### Scenario: Interactive terminal selects the rich reporter
- **WHEN** a download starts and the shared `Console.is_terminal` is `True`
- **THEN** the system uses the `RichReporter` (animated grouped display)

#### Scenario: Non-interactive output selects the plain reporter
- **WHEN** a download starts and the shared `Console.is_terminal` is `False`
  (piped output, CI, redirected file)
- **THEN** the system uses the `PlainReporter`
- **AND** no ANSI escape sequences are emitted to the output stream

### Requirement: Grouped single-progress display for a download

The system SHALL render all files of a single download (image plus its hash
files) within one shared Rich `Progress` instance, so the display does not
create and tear down a separate progress block per file.

#### Scenario: Multi-file download renders as one grouped block
- **WHEN** a download of an image and its `sha512` file is rendered in a terminal
- **THEN** both files appear as bars within a single titled `Panel`
- **AND** an aggregated **Total** bar reflects combined progress across the files
- **AND** the display is not torn down and recreated between files

#### Scenario: Per-file completion state
- **WHEN** an individual file within the grouped display finishes
- **THEN** its row shows a completed state while the other rows keep updating

### Requirement: Concurrent download of a download's files

The system SHALL download the files that make up a single download (image and
hash files) concurrently using a thread pool, updating their respective bars in
the shared display.

#### Scenario: Image and hash download concurrently
- **WHEN** a download contains an image file and one or more hash files
- **THEN** the files are fetched concurrently rather than strictly sequentially
- **AND** each file's progress updates its own row in the shared display
- **AND** the call returns only after all files have completed

### Requirement: Non-TTY progress is reported as log lines

In non-interactive mode the system SHALL report progress as `loguru` log lines
rather than an animated bar, covering start, intermediate progress, and
completion.

#### Scenario: Plain reporter emits lifecycle log lines
- **WHEN** a file is downloaded under the `PlainReporter`
- **THEN** a start line records the filename and total size
- **AND** a progress line is emitted at each 10% milestone (10%, 20%, … 90%)
- **AND** a completion line records the transferred size and duration

### Requirement: Progress mode parameter

`SoftManager.download_file()` and `SoftManager.downloads()` SHALL accept a
`progress` parameter with values `"auto"`, `"rich"`, `"plain"`, or `"none"`
controlling reporter selection, defaulting to `"auto"`.

#### Scenario: Auto defers to terminal detection
- **WHEN** `progress="auto"` (the default)
- **THEN** the reporter is chosen from `Console.is_terminal`

#### Scenario: Explicit rich or plain overrides detection
- **WHEN** `progress="rich"` or `progress="plain"` is passed
- **THEN** the corresponding reporter is used regardless of terminal detection

#### Scenario: None disables progress rendering
- **WHEN** `progress="none"` is passed
- **THEN** no progress display is rendered while the download still proceeds

#### Scenario: CLI `--no-progress` flag disables the display
- **WHEN** a download command is invoked with `--no-progress`
- **THEN** the download runs with `progress="none"` and renders no progress display

### Requirement: Deprecated `rich_interface` alias

The system SHALL keep the `rich_interface` boolean parameter as a deprecated
alias for `progress` so existing library callers are not broken, and SHALL emit
a `DeprecationWarning` when it is used.

#### Scenario: rich_interface=False maps to plain
- **WHEN** a caller passes `rich_interface=False`
- **THEN** the effective mode is `progress="plain"`
- **AND** a `DeprecationWarning` is emitted

#### Scenario: rich_interface=True maps to auto
- **WHEN** a caller passes `rich_interface=True`
- **THEN** the effective mode is `progress="auto"`
- **AND** a `DeprecationWarning` is emitted

### Requirement: Single shared console

The downloader SHALL render through the same `Console` instance used by the rest
of the CLI rather than constructing its own.

#### Scenario: Downloader uses the CLI console
- **WHEN** a download renders progress from within the CLI
- **THEN** it uses the `Console` provided by the CLI layer

### Requirement: No import-time signal side effect

Importing the download helpers module SHALL NOT install a process-wide signal
handler; interrupt handling SHALL be scoped to an active download.

#### Scenario: Import does not alter SIGINT handling
- **WHEN** the download helpers module is imported
- **THEN** the process `SIGINT` handler is not replaced as a side effect of import

#### Scenario: Interrupt during an active download is handled
- **WHEN** the user interrupts (Ctrl+C) while a download is in progress
- **THEN** the download terminates gracefully

### Requirement: Removal of the tqdm progress path

The system SHALL NOT depend on `tqdm`; the legacy `tqdm`-based raw download path
is removed.

#### Scenario: tqdm is not a dependency
- **WHEN** the project dependencies are inspected
- **THEN** `tqdm` is not listed as a runtime dependency
- **AND** no code path renders progress via `tqdm`
