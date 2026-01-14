# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**eos-downloader** is a Python CLI tool and library for downloading Arista Networks software packages (EOS and CloudVision Portal). It provides both a command-line interface (`ardl`) and a programmatic API for automation workflows.

## Development Commands

```bash
# Install all dependencies (creates .venv automatically)
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest                                    # All tests
uv run pytest tests/unit/models/test_version.py # Single file
uv run pytest -k "test_version"                  # Pattern match

# Run with coverage
uv run pytest --cov=eos_downloader --cov-report=term-missing

# Linting and type checking
make lint      # flake8 + pylint
make type      # mypy
make check     # lint + type + test

# Format code
make format    # black

# Serve documentation locally
make docs-serve

# Run CLI
uv run ardl --help
```

## Architecture

### Core Components

- **`eos_downloader/cli/`** - Click-based CLI with command groups:
  - `get` - Download commands (eos, cvp, path)
  - `info` - Version information commands (versions, latest, mapping)
  - `debug` - Debug commands (xml)

- **`eos_downloader/logics/`** - Business logic:
  - `arista_xml_server.py` - Query Arista's XML API for available versions (`AristaXmlQuerier`)
  - `arista_server.py` - Authentication and server communication
  - `download.py` - File download management (`SoftManager`)

- **`eos_downloader/models/`** - Pydantic data models:
  - `version.py` - Version parsing/comparison (`SemVer`, `EosVersion`, `CvpVersion`)
  - `types.py` - Type definitions (`AristaPackage`, `AristaVersions`)
  - `data.py` - Data mappings for EOS/CVP formats

### Key Patterns

**Version Handling** - Always use version models, never parse manually:
```python
from eos_downloader.models.version import EosVersion
version = EosVersion.from_str("4.29.3M")
print(version.branch)  # "4.29"
print(version.rtype)   # "M"
```

**CLI Commands** - Commands pass context containing token and config:
```python
@click.pass_context
def command(ctx: click.Context) -> None:
    token = ctx.obj["token"]
    log_level = ctx.obj["log_level"]
```

**API Queries** - Use `AristaXmlQuerier` for version discovery:
```python
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier
querier = AristaXmlQuerier(token="your-token")
versions = querier.available_public_versions(package="eos", branch="4.29")
```

## Domain Knowledge

### EOS Versions
- Format: `MAJOR.MINOR.PATCH[TYPE]` (e.g., `4.29.3M`, `4.30.1F`)
- Release types: **M** (Maintenance/stable), **F** (Feature), **INT** (Internal)
- Image formats: `64` (physical), `vEOS`/`vEOS-lab` (virtual), `cEOS`/`cEOS64` (container)

### CVP Versions
- Format: `YEAR.MINOR.PATCH` (e.g., `2024.3.0`)
- Formats: `ova`, `rpm`, `kvm`, `upgrade`

### Environment Variables
- `ARISTA_TOKEN` - API authentication token
- `ARDL_LOG_LEVEL` - Logging level (debug, info, warning, error, critical)

## Testing

Tests are organized in `tests/unit/` (fast, isolated) and `tests/integration/`. Use fixtures from `tests/lib/fixtures.py`. Mock external API calls - never make real requests to Arista servers in tests.

## Code Style

- Type hints on all function signatures
- NumPy-style docstrings for public functions
- Use `loguru` for logging, `rich` for CLI output
- Paths via `pathlib.Path`, not string concatenation
- Never log or hardcode API tokens
