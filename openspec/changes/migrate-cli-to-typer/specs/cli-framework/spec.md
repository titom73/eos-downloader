## ADDED Requirements

### Requirement: Command tree structure

The `ardl` CLI SHALL expose a root command with four groups — `get`, `info`,
`debug`, `config` — and the subcommands `get eos`, `get cvp`, `get path`,
`info versions`, `info latest`, `info mapping`, `debug xml`, `config init`, and
`config show`, regardless of the underlying CLI framework.

#### Scenario: Root help lists all groups
- **WHEN** the user runs `ardl --help`
- **THEN** the output lists the `get`, `info`, `debug`, and `config` groups
- **AND** the process exits with code 0

#### Scenario: Every documented subcommand is invocable
- **WHEN** the user runs `--help` on any of `get eos`, `get cvp`, `get path`,
  `info versions`, `info latest`, `info mapping`, `debug xml`, `config init`,
  `config show`
- **THEN** the command is found and its help is displayed with exit code 0

#### Scenario: No arguments shows help
- **WHEN** the user runs `ardl` with no subcommand
- **THEN** the root help is printed and the process exits with code 0

### Requirement: Command-prefix aliasing

The CLI SHALL resolve any unambiguous prefix of a group or command name to that
name (e.g. `ge` → `get`, `d` → `debug`), and SHALL fail with an error listing
the matches when a prefix is ambiguous.

#### Scenario: Unique prefix resolves
- **WHEN** the user runs `ardl ge --help`
- **THEN** the CLI resolves it to `get` and shows the `get` group help

#### Scenario: Ambiguous prefix reports matches
- **WHEN** a typed prefix matches more than one command
- **THEN** the CLI fails and reports the matching command names

### Requirement: Shared invocation context

The root command SHALL accept `--token`, `--log-level` (alias `--log`), and
`--debug-enabled` (alias `--debug`), and SHALL make the resolved `token`,
`log_level`, and `debug` values available to every subcommand through the shared
context object.

#### Scenario: Subcommand reads the token from context
- **WHEN** the user runs `ardl --token XYZ get eos …`
- **THEN** the `eos` subcommand receives `token == "XYZ"` from the context

#### Scenario: Log-level alias is accepted
- **WHEN** the user passes `--log debug` at the root
- **THEN** the resolved `log_level` is `debug`, identical to passing `--log-level debug`

#### Scenario: Debug alias is accepted
- **WHEN** the user passes `--debug` at the root
- **THEN** the resolved `debug` flag is `True`, identical to `--debug-enabled`

### Requirement: Environment variable resolution

The CLI SHALL resolve options from environment variables using the `arista`
auto-prefix, such that `ARISTA_TOKEN` supplies the root `--token` when it is not
given on the command line.

#### Scenario: Token from environment
- **WHEN** `ARISTA_TOKEN` is set and `--token` is not passed
- **THEN** the resolved token equals the value of `ARISTA_TOKEN`

#### Scenario: Command line overrides environment
- **WHEN** both `ARISTA_TOKEN` and `--token` are provided
- **THEN** the `--token` value takes precedence

### Requirement: TOML config injection and precedence

The CLI SHALL load a TOML configuration file into the option defaults so that
config values apply when a matching option is not supplied on the command line
or via environment variable, preserving the precedence CLI > env var > config >
built-in default.

#### Scenario: Config supplies an unset option
- **WHEN** a config file defines `[ardl] token` and no `--token`/`ARISTA_TOKEN`
  is provided
- **THEN** the resolved token equals the config value

#### Scenario: CLI and env var win over config
- **WHEN** an option is provided on the command line or via its environment
  variable
- **THEN** the config value is ignored for that option

#### Scenario: Group and subcommand config defaults merge
- **WHEN** the config defines both group-level (e.g. `[ardl.info]`) and
  subcommand-level (e.g. `[ardl.info.latest]`) defaults
- **THEN** the subcommand receives the merged defaults with subcommand-specific
  values taking precedence

### Requirement: Option names, aliases, and defaults preserved

Every existing option name, short flag, secondary alias, default value, and
choice constraint SHALL remain available after the migration, including
`get eos --containerlab-topology` (alias `--clab`), `--format`, `--output`
(`-o`), `--source` (`-s`), and the `versions`/`latest`/`mapping` `--format`
choices (`json`, `text`, `fancy`).

#### Scenario: Containerlab alias preserved
- **WHEN** the user passes `ardl get eos --clab <file>`
- **THEN** it behaves identically to `--containerlab-topology <file>`

#### Scenario: Mutually exclusive options still rejected
- **WHEN** `--containerlab-topology` is combined with `--version`, `--latest`,
  or `--branch`
- **THEN** the CLI reports a usage error and exits non-zero

#### Scenario: Invalid choice rejected
- **WHEN** the user passes an unsupported value to an option constrained to a
  fixed set (e.g. `info versions --format bogus`)
- **THEN** the CLI reports a usage error and exits non-zero

### Requirement: Exit codes preserved

Command outcomes SHALL map to the same process exit codes as before the
migration: success exits 0, and error paths that previously used `ctx.exit(1)`
or raised a usage error continue to exit non-zero.

#### Scenario: Success exits zero
- **WHEN** a command completes successfully
- **THEN** the process exits with code 0

#### Scenario: Handled error exits non-zero
- **WHEN** a command hits a handled error path (authentication failure, missing
  required source, mutually exclusive options)
- **THEN** the process exits with a non-zero code

### Requirement: Version reporting

The CLI SHALL report the package version via a root `--version` option and exit
0.

#### Scenario: Version flag
- **WHEN** the user runs `ardl --version`
- **THEN** the installed package version is printed and the process exits 0
