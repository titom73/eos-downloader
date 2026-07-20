# interactive-download Specification

## Purpose
Define the `--interactive` wizard for `ardl get eos` / `ardl get cvp`: its step sequence, the per-package differences (CVP has no release type), the format-dependent option prompts, the confirmation recap showing the equivalent command, and the terminal/token/mutual-exclusion guardrails.
## Requirements
### Requirement: Interactive flag on the get commands

`get eos` and `get cvp` SHALL accept an `--interactive` / `-i` flag that opens a
guided wizard to collect the download parameters instead of reading the other
selection options.

#### Scenario: Interactive flag opens the wizard
- **WHEN** `ardl get eos --interactive` is run in an interactive terminal with a
  valid token
- **THEN** a step-by-step wizard is presented instead of downloading directly
  from CLI-provided options

#### Scenario: Non-interactive usage is unchanged
- **WHEN** `get eos` / `get cvp` is run without `--interactive`
- **THEN** the command behaves exactly as before, reading its options from the
  CLI

### Requirement: Wizard step sequence

The wizard SHALL guide the user through, in order: format, release type (EOS
only), branch, version, and format-dependent options, each selected with
arrow-key navigation.

#### Scenario: EOS wizard steps
- **WHEN** the wizard runs for `get eos`
- **THEN** the user selects, in order, a format, a release type (`F`/`M`), a
  branch, a version, and any format-dependent options

#### Scenario: CVP wizard skips release type
- **WHEN** the wizard runs for `get cvp`
- **THEN** the release-type step is not presented
- **AND** the remaining steps (format, branch, version, options) are presented

#### Scenario: Format list comes from the package mapping
- **WHEN** the format step is presented
- **THEN** the choices are the formats available for the package (EOS or CVP)
  from the software mapping

### Requirement: Branch-narrowed version selection

The wizard SHALL present branches sorted newest-first, require the user to pick
exactly one branch, then present the versions of that branch sorted newest-first
for selection.

#### Scenario: Branch then version
- **WHEN** the user reaches the branch step
- **THEN** the available branches are listed newest-first and the user picks one
- **AND** the version step then lists only that branch's versions, newest-first

#### Scenario: Release type filters the versions
- **WHEN** an EOS release type has been chosen
- **THEN** the version list is limited to versions of that release type

### Requirement: Format-dependent option prompts

After the version is chosen, the wizard SHALL offer additional prompts based on
the selected format, and SHALL always ask for the output directory and a
force-re-download toggle.

#### Scenario: cEOS offers Docker import
- **WHEN** the selected format is a `cEOS` variant (`cEOS`, `cEOS64`, `cEOSarm`)
- **THEN** the wizard offers to import the image into Docker
- **AND** when accepted, prompts for the Docker image name and tag

#### Scenario: vEOS offers EVE-NG provisioning
- **WHEN** the selected format is a `vEOS` variant
- **THEN** the wizard offers EVE-NG provisioning

#### Scenario: Common options always asked
- **WHEN** any format is selected
- **THEN** the wizard asks for the output directory (default: current directory)
- **AND** asks whether to force a re-download

#### Scenario: Dry-run is not offered
- **WHEN** the wizard runs
- **THEN** no dry-run option is presented

### Requirement: Confirmation recap

Before starting the download the wizard SHALL display the equivalent
non-interactive command built from the selections and ask the user to confirm.

#### Scenario: Confirm before download
- **WHEN** all selections are made
- **THEN** the wizard shows the equivalent `ardl get ...` command
- **AND** starts the download only after the user confirms

#### Scenario: Declining aborts without downloading
- **WHEN** the user declines the confirmation
- **THEN** no download is performed and the command exits

### Requirement: Interactive guardrails

The wizard SHALL be usable only in a valid context: an interactive terminal, an
available token, and no conflicting selection options.

#### Scenario: Requires an interactive terminal
- **WHEN** `--interactive` is used but output is not an interactive terminal
  (piped, redirected, CI)
- **THEN** the command exits with a clear error explaining a TTY is required

#### Scenario: Requires a token
- **WHEN** `--interactive` is used without an available token
- **THEN** the command exits with a clear error before opening the wizard

#### Scenario: Mutually exclusive with explicit selection options
- **WHEN** `--interactive` is combined with `--version`, `--latest`, or
  `--branch`
- **THEN** the command fails with a `BadParameter` error
