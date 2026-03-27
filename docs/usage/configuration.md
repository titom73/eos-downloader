# Configuration File

`ardl` supports an optional TOML configuration file to set default values for CLI options. This is useful for a **dotfiles** / **chezmoi** workflow where you want persistent defaults without passing options every time.

## Priority Order

When resolving option values, `ardl` follows this priority (highest to lowest):

1. **CLI options** — explicitly passed on the command line
2. **Environment variables** — `ARISTA_*` prefixed variables
3. **Configuration file** — values from the TOML config
4. **Click defaults** — built-in default values

For example, if your config file sets `format = "cEOS"`, but you run `ardl get eos --format 64`, the CLI option wins.

## File Locations

`ardl` searches for the configuration file in two locations, using the first one found:

1. `~/.eos-downloader.toml`
2. `$XDG_CONFIG_HOME/eos-downloader/config.toml` (defaults to `~/.config/eos-downloader/config.toml`)

## Creating a Configuration File

Use `ardl config init` to generate a template:

```bash
# Create config at default location (~/.eos-downloader.toml)
ardl config init

# Create config at a custom path
ardl config init --output ~/dotfiles/eos-downloader.toml

# Overwrite an existing config
ardl config init --force
```

The generated file contains all available options, commented out, with documentation. The file is created with `0600` permissions since it may contain your API token.

## Viewing Active Configuration

```bash
ardl config show
```

This displays the path of the active configuration file and its content. The API token is automatically masked in the output.

## Configuration Format

The configuration file uses [TOML](https://toml.io/) format. Sections map to the CLI command hierarchy:

```toml
[ardl]
token = "your-arista-api-token"
log_level = "info"

[ardl.get.eos]
format = "cEOS"
output = "/home/user/downloads"
import_docker = true
docker_name = "arista/ceos"

[ardl.get.cvp]
format = "ova"

[ardl.info]
# Group-level defaults apply to all info subcommands
format = "json"
package = "eos"

[ardl.info.latest]
# Subcommand-specific values override group defaults
branch = "4.29"

[ardl.debug.xml]
output = "arista.xml"
```

### Group-Level Defaults

Options defined at a group level (e.g., `[ardl.info]`) are shared across all subcommands in that group. Subcommand-specific values override the group defaults:

```toml
[ardl.info]
format = "json"        # Applies to versions, latest, and mapping

[ardl.info.mapping]
format = "fancy"       # Overrides the group default for mapping only
```

## Complete Option Reference

### `[ardl]` — Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `token` | string | — | Arista API token |
| `log_level` | string | `"error"` | Logging level (`debug`, `info`, `warning`, `error`, `critical`) |
| `debug_enabled` | boolean | `false` | Enable debug mode |

### `[ardl.get.eos]` — EOS Download

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | `"vmdk"` | Image format (`64`, `vEOS`, `vEOS-lab`, `cEOS`, `cEOS64`, etc.) |
| `output` | string | `"."` | Download directory |
| `latest` | boolean | `false` | Download latest version |
| `eve_ng` | boolean | `false` | EVE-NG provisioning mode |
| `import_docker` | boolean | `false` | Import as Docker image |
| `skip_download` | boolean | `false` | Skip download (debug) |
| `docker_name` | string | `"arista/ceos"` | Docker image name |
| `docker_tag` | string | — | Docker image tag |
| `version` | string | — | Specific EOS version |
| `release_type` | string | `"F"` | Release type (`M` or `F`) |
| `branch` | string | — | Version branch (e.g., `"4.29"`) |
| `dry_run` | boolean | `false` | Dry-run mode |
| `force` | boolean | `false` | Force re-download |
| `containerlab_topology` | string | — | Path to containerlab topology file |

### `[ardl.get.cvp]` — CVP Download

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | `"ova"` | Image format |
| `output` | string | `"."` | Download directory |
| `latest` | boolean | `false` | Download latest version |
| `version` | string | — | Specific CVP version |
| `branch` | string | — | Version branch |
| `dry_run` | boolean | `false` | Dry-run mode |
| `force` | boolean | `false` | Force re-download |

### `[ardl.get.path]` — Direct Path Download

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `source` | string | — | Download path on Arista website |
| `output` | string | `"."` | Download directory |
| `import_docker` | boolean | `false` | Import as Docker image |
| `docker_name` | string | `"arista/ceos:raw"` | Docker image name |
| `docker_tag` | string | `"dev"` | Docker image tag |
| `force` | boolean | `false` | Force re-download |

### `[ardl.info.versions]` — List Versions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | `"fancy"` | Output format (`json`, `text`, `fancy`) |
| `package` | string | `"eos"` | Package type (`eos` or `cvp`) |
| `branch` | string | — | Branch filter |
| `release_type` | string | — | Release type filter |

### `[ardl.info.latest]` — Latest Version

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | `"fancy"` | Output format (`json`, `text`, `fancy`) |
| `package` | string | `"eos"` | Package type (`eos` or `cvp`) |
| `branch` | string | — | Branch filter |
| `release_type` | string | — | Release type filter |

### `[ardl.info.mapping]` — Software Mapping

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `package` | string | `"eos"` | Package type (`eos` or `cvp`) |
| `format` | string | `"fancy"` | Output format (`json`, `text`, `fancy`) |
| `details` | boolean | `false` | Show detailed information |

### `[ardl.debug.xml]` — XML Debug

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output` | string | `"arista.xml"` | Output file path |
| `log_level` | string | `"INFO"` | Logging level |

## Security

The configuration file may contain your Arista API token. To keep it secure:

- `ardl config init` creates the file with `0600` permissions (owner read/write only)
- `ardl config show` automatically masks the token in its output
- If using version control for dotfiles, consider using a secrets manager or `.gitignore` the config file
