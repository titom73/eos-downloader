# UV Installation Modes

This document describes the different installation modes available with UV for the eos-downloader project.

## Overview

UV supports flexible installation modes equivalent to pip's `-e .` and `-e ".[extra]"` patterns, allowing you to install only the dependencies you need for your specific use case.

## Installation Modes

### 1. Base Installation (Core Dependencies Only)

**Pip equivalent**: `pip install -e .`

**UV command**:
```bash
uv sync
```

**Packages installed**: 31 packages (core dependencies only)

**Includes**:
- Core application dependencies (click, requests, rich, loguru, tqdm, pydantic, etc.)
- Runtime requirements for CLI commands (ardl, lard)
- Essential libraries (cryptography, paramiko, cvprac)

**Use case**:
- Production deployments
- Docker containers
- Minimal installations
- Users who only need the CLI tools

**Makefile target**:
```bash
make install-base
```

### 2. Documentation Extra

**Pip equivalent**: `pip install -e ".[doc]"`

**UV command**:
```bash
uv sync --extra doc
```

**Packages installed**: 75 packages (core + documentation dependencies)

**Additional packages include**:
- mkdocs and mkdocs-material (documentation site generator)
- mkdocstrings (API documentation from docstrings)
- mkdocs plugins (git-revision-date, glightbox, etc.)
- Markdown extensions (pymdown-extensions)

**Use case**:
- Building project documentation locally
- Contributing to documentation
- Previewing documentation changes

**Makefile target**:
```bash
make install-doc
```

### 3. Development Extra

**Pip equivalent**: `pip install -e ".[dev]"`

**UV command**:
```bash
uv sync --extra dev
```

**Packages installed**: 78 packages (core + development dependencies)

**Additional packages include**:
- Testing tools (pytest, pytest-cov, pytest-html, pytest-dependency)
- Linting tools (flake8, pylint, pylint-pydantic)
- Type checking (mypy, types-*)
- Code formatting (black, isort)
- Build tools (tox, bumpver)
- Pre-commit hooks

**Use case**:
- Active development
- Running tests
- Code quality checks
- Contributing code changes

**Makefile target**:
```bash
make install-dev
```

### 4. Full Installation (All Extras)

**Pip equivalent**: `pip install -e ".[dev,doc]"` or `pip install -e ".[dev]"` (if dev includes all)

**UV command**:
```bash
uv sync --all-extras
```

**Packages installed**: 115 packages (core + dev + doc)

**Includes**: Everything from all extras combined

**Use case**:
- Full-featured development environment
- Contributing to both code and documentation
- Running all project tasks (test, lint, type check, build docs)
- Recommended for core maintainers

**Makefile target**:
```bash
make install
```

## Multiple Extras

You can also install multiple specific extras:

```bash
uv sync --extra dev --extra doc
```

This gives you fine-grained control over which dependency groups to install.

## Comparison Table

| Installation Mode | Packages | Pip Equivalent | UV Command | Makefile |
|-------------------|----------|----------------|------------|----------|
| **Base** | 31 | `pip install -e .` | `uv sync` | `make install-base` |
| **+ Doc** | 75 | `pip install -e ".[doc]"` | `uv sync --extra doc` | `make install-doc` |
| **+ Dev** | 78 | `pip install -e ".[dev]"` | `uv sync --extra dev` | `make install-dev` |
| **All** | 115 | `pip install -e ".[dev,doc]"` | `uv sync --all-extras` | `make install` |

## Benefits of Partial Installation

1. **Faster installation**: Only install what you need
2. **Smaller environment**: Reduces disk space and memory usage
3. **Clearer dependencies**: Explicit about what's required for each use case
4. **CI/CD optimization**: Different jobs can use different extras (e.g., test job uses `--extra dev`, docs job uses `--extra doc`)
5. **Docker optimization**: Production images can use base install only

## Verification

After installation, you can verify what's installed:

```bash
# List all installed packages
uv pip list

# Count installed packages
uv pip list | wc -l

# Check if a specific package is installed
uv pip show pytest  # Will show info if installed, error if not
```

## Environment Variables

UV respects the following environment variables from `.envrc` (loaded by direnv):

```bash
# API token for Arista downloads
export ARISTA_TOKEN="your-token-here"

# Prevent pyenv/UV VIRTUAL_ENV conflicts
unset VIRTUAL_ENV
```

## Troubleshooting

### Warning: VIRTUAL_ENV mismatch

If you see:
```
warning: `VIRTUAL_ENV=...` does not match the project environment path `.venv`
```

**Solution**: Add `unset VIRTUAL_ENV` to your `.envrc` file (see [`.envrc.example`](../.envrc.example))

### Warning: Unsupported Python request in .python-version

If you see:
```
warning: Ignoring unsupported Python request `eos-downloader` in version file
```

**Solution**: Update `.python-version` to contain actual Python version (e.g., `3.13`) instead of project name (see [`.python-version.example`](../.python-version.example))

## See Also

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- [Migration Guide](migration-guide-uv.md)
- [UV Commands Cheatsheet](uv-commands-cheatsheet.md)
