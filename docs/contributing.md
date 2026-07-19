# Contributing to eos-downloader

Thank you for your interest in contributing to the eos-downloader project! This guide will help you get started with contributing to this Python CLI tool for downloading Arista EOS and CloudVision Portal software packages.

## Overview

eos-downloader is a Python CLI application built with Typer, Rich, and pytest. It provides both a command-line interface and a programmatic API for downloading Arista software packages. The project follows modern Python development practices with comprehensive testing, type hints, and automated CI/CD.

Changes are planned and tracked with [OpenSpec](https://github.com/Fission-AI/OpenSpec): every change is proposed, designed, specified, implemented, and archived on a **single dedicated branch**, then merged as one Pull Request. See [Contribution Workflow (OpenSpec)](#contribution-workflow-openspec) below for the full flow and the branch rules.

## Getting Started

### 1. Fork the Repository

1. Navigate to the [eos-downloader repository](https://github.com/titom73/eos-downloader)
2. Click the "Fork" button in the top-right corner
3. Select your GitHub account to create a fork

### 2. Clone Your Fork

```bash
# Clone your forked repository
git clone https://github.com/YOUR_USERNAME/eos-downloader.git
cd eos-downloader

# Add the original repository as upstream
git remote add upstream https://github.com/titom73/eos-downloader.git
```

### 3. Set Up Development Environment

#### Prerequisites

- Python 3.9 or higher
- Git
- [UV package manager](https://github.com/astral-sh/uv) (replaces pip, pip-tools, virtualenv)

#### Install UV (One-Time Setup)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS with Homebrew
brew install uv

# Verify installation
uv --version  # Should show 0.4.0 or higher
```

#### Environment Setup with UV

UV automatically creates and manages virtual environments - no need for manual venv creation!

```bash
# Install all development dependencies (creates .venv automatically)
uv sync --all-extras

# This installs:
# - Core dependencies
# - Development tools (pytest, ruff, mypy, etc.)
# - Documentation tools (mkdocs, etc.)

# Install pre-commit hooks for code quality
uv run pre-commit install
```

> **Important:** `uv run pre-commit install` also activates the OpenSpec branch
> guard (`.github/scripts/opsx-branch-guard`), which blocks OpenSpec artifacts from
> being committed on `main`. Install it before you start working — see
> [Contribution Workflow (OpenSpec)](#contribution-workflow-openspec).

**What `uv sync` does:**
- Creates `.venv/` directory if it doesn't exist
- Installs dependencies from `uv.lock` (deterministic)
- Installs the package in editable mode
- Validates dependency resolution

#### Verify Installation

```bash
# Run tests to ensure everything is working
uv run pytest

# Check code style
make lint
# or directly: uv run ruff check .

# Run type checking
make type
# or directly: uv run mypy eos_downloader

# Test CLI
uv run ardl --help
```

#### UV Command Reference

| Task | pip/tox Command | UV Command |
|------|----------------|------------|
| Install dev dependencies | `pip install -e ".[dev]"` | `uv sync --all-extras` |
| Install docs only | `pip install -e ".[doc]"` | `uv sync --extra doc` |
| Run command in venv | `python -m pytest` | `uv run pytest` |
| Add dependency | Edit pyproject.toml + `pip install -e .` | `uv add <package>` |
| Add dev dependency | Edit pyproject.toml + `pip install -e ".[dev]"` | `uv add --dev <package>` |
| Remove dependency | Edit pyproject.toml + `pip uninstall` | `uv remove <package>` |
| Update lockfile | `pip-compile` | `uv lock` |
| Update all dependencies | `pip install --upgrade -e ".[dev]"` | `uv lock --upgrade` |
| Build package | `python -m build` | `uv build` |
| Show dependencies | `pip list` | `uv pip list` |

## Contribution Workflow (OpenSpec)

This project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) to plan and
track changes. The workflow has four stages, driven by the `opsx:*` commands (or
the `openspec` CLI directly):

```
  explore  ─▶  propose  ─▶  apply  ─▶  archive
  (think)     (plan)       (build)    (finalize)
```

- **explore** — think through the problem. Read-only, produces nothing to commit.
- **propose** — create the change and its artifacts (`proposal.md`, `design.md`,
  delta specs, `tasks.md`).
- **apply** — implement the tasks.
- **archive** — move the change to `openspec/changes/archive/` and update the
  main specs in `openspec/specs/`.

### The golden rule: one change = one typed branch

The **entire lifecycle of a change lives on a single dedicated branch**, with no
dependency on `main` or on other change branches, and is merged into `main` as
**one Pull Request**. The proposal, the design, the specs, the implementation,
*and* the archive commit all belong to that branch.

Branches are named after the change, with a Conventional-Commit-style type:

| Branch pattern            | Use when the change…                              |
|---------------------------|---------------------------------------------------|
| `feat/<change-name>`      | adds or extends a capability (docs optional)      |
| `fix/<change-name>`       | corrects a defect or problem                      |
| `doc/<change-name>`       | updates documentation only                        |
| `refactor/` `chore/` `ci/`| other conventional types, as needed              |

If a change is a feature that also updates documentation, it is a `feat/…`. Only
when the change is *documentation only* is it a `doc/…`.

### Auto-switch from `main`

When you start the first change of a session from `main`, the `opsx` workflow
**creates the branch for you** at the first artifact write: it derives the type
from your intent and runs `git checkout -b <type>/<change-name>`. Pure
exploration never branches (nothing is committed).

If you work by hand (or with an assistant that did not switch), create the branch
yourself before writing artifacts:

```bash
git checkout main
git pull                       # (fork: git fetch upstream && git merge upstream/main)
git checkout -b feat/my-change # or fix/… or doc/…
```

### The deterministic guard

A local `pre-commit` hook, `.github/scripts/opsx-branch-guard`, enforces the golden
rule independently of any AI assistant or editor. On every commit it checks:

```
staged files under openspec/changes/** or openspec/specs/**
        AND  current branch ∈ { main, master }
        ─▶  commit REJECTED (with guidance)
```

It blocks nothing else on `main`, and never blocks OpenSpec commits on a working
branch. Activate it with `uv run pre-commit install`. If you are certain you need
to bypass it, `git commit --no-verify` is the explicit escape hatch.

AI assistants other than Claude Code read the same rules from
[`AGENTS.md`](https://github.com/titom73/eos-downloader/blob/main/AGENTS.md).

## Development Workflow

### 1. Start (or continue) a change on its branch

Use `/opsx:propose` to create a change (it will auto-switch you to a
`<type>/<change-name>` branch from `main`), then `/opsx:apply` to implement it.
Prefer using the `opsx` workflow; if you branch manually, follow the typed-branch
convention above so the guard stays happy.

### 2. Python Development Guidelines

#### Code Style

The project follows strict Python coding standards:

- **PEP 8 compliance** with 120 character line limit
- **Type hints** for all function signatures and class attributes
- **NumPy-style docstrings** for all public functions and classes
- **Black** for code formatting
- **isort** for import organization

#### Key Principles

```python
# Always use type hints
from typing import Optional, List, Dict, Any
from pathlib import Path

def download_eos_image(
    version: str,
    image_format: str,
    output_dir: Path,
    token: str,
) -> Path:
    """Download an EOS image from Arista server.

    Parameters
    ----------
    version : str
        EOS version in format MAJOR.MINOR.PATCH[TYPE] (e.g., "4.29.3M")
    image_format : str
        Image format (e.g., "64", "vEOS", "cEOS")
    output_dir : Path
        Directory where the image will be saved
    token : str
        Arista API authentication token

    Returns
    -------
    Path
        Path to the downloaded image file

    Raises
    ------
    TokenExpiredError
        If the authentication token has expired
    DownloadError
        If the download fails
    """
    # Implementation here
```

#### Project Structure

- `eos_downloader/` - Main package
  - `cli/` - Typer-based command line interface
  - `logics/` - Business logic and core functionality
  - `models/` - Data models with Pydantic validation
  - `exceptions/` - Custom exception classes
  - `helpers/` - Utility functions
- `tests/` - Test suite organized by package structure
- `docs/` - Documentation files

#### Domain Knowledge

Understanding Arista's ecosystem is crucial:

- **EOS versions**: Format is `MAJOR.MINOR.PATCH[TYPE]` (e.g., "4.29.3M")
- **Release types**: M (Maintenance), F (Feature), INT (Internal)
- **Image formats**: 64-bit, vEOS (virtual), cEOS (container)
- **CVP versions**: CloudVision Portal with different format

### 3. Writing and Running Tests

#### Test Organization

```
tests/
├── unit/           # Unit tests (isolated, fast)
│   ├── cli/       # CLI command tests
│   ├── logics/    # Business logic tests
│   └── models/    # Data model tests
├── integration/    # Integration tests (with external dependencies)
└── lib/           # Test utilities and fixtures
```

#### Writing Unit Tests

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from eos_downloader.models.version import EosVersion

class TestEosVersion:
    """Test suite for EOS version parsing and validation."""

    def test_valid_version_parsing(self):
        """Test parsing of valid EOS version strings."""
        version = EosVersion.from_str("4.29.3M")

        assert version.major == 4
        assert version.minor == 29
        assert version.patch == 3
        assert version.rtype == "M"
        assert version.branch == "4.29"

    def test_invalid_version_raises_error(self):
        """Test that invalid version strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version format"):
            EosVersion.from_str("invalid-version")

    @pytest.mark.parametrize(
        "version_str,expected_branch",
        [
            ("4.29.3M", "4.29"),
            ("4.30.1F", "4.30"),
            ("4.28.10M", "4.28"),
        ]
    )
    def test_branch_calculation(self, version_str: str, expected_branch: str):
        """Test branch calculation for different versions."""
        version = EosVersion.from_str(version_str)
        assert version.branch == expected_branch
```

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=eos_downloader --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/models/test_version.py

# Run tests matching a pattern
uv run pytest -k "test_version"

# Run with verbose output
uv run pytest -v

# Run tests in parallel (if you have pytest-xdist installed)
uv run pytest -n auto

# Using Makefile shortcuts
make test            # Run all tests
make test-coverage   # Run with coverage report
```

#### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies** (API calls, file system operations)
4. **Use fixtures** for common setup and teardown
5. **Test both success and failure scenarios**
6. **Parametrize tests** to cover multiple cases efficiently

### 4. Code Quality Checks

Before submitting your changes, ensure they pass all quality checks:

```bash
# Run all checks using Makefile
make lint        # Linting with ruff
make type        # Type checking with mypy
make test        # Run tests
make check       # Run all checks (lint + type + test)

# Individual UV commands
uv run ruff check .              # Linting
uv run mypy eos_downloader       # Type checking
uv run pytest                    # Tests

# Format code
uv run ruff format eos_downloader/ tests/
# or use Makefile: make format

# Pre-commit checks (runs automatically on commit)
uv run pre-commit run --all-files
```

**Note:** The project uses UV for dependency management. All commands above use `uv run` to execute tools in the project's virtual environment. The Makefile provides convenient shortcuts for common tasks.

### 5. UV Lockfile Management

The `uv.lock` file ensures deterministic, reproducible builds across all environments. It contains exact versions and hashes of all dependencies.

#### When to Update the Lockfile

**You MUST update `uv.lock` when:**
- Adding a new dependency
- Removing a dependency
- Changing dependency version constraints in `pyproject.toml`
- Updating dependencies to newer versions

**DO NOT manually edit `uv.lock`** - always use UV commands to update it.

#### Adding Dependencies

```bash
# Add a runtime dependency (automatically updates uv.lock)
uv add requests

# Add a development dependency
uv add --dev pytest-mock

# Add with version constraint
uv add "rich>=13.0.0"

# Add optional dependency to specific group
# Edit pyproject.toml [project.optional-dependencies] manually, then:
uv lock
```

#### Removing Dependencies

```bash
# Remove a dependency (automatically updates uv.lock)
uv remove requests

# Remove from specific group
# Edit pyproject.toml manually, then:
uv lock
```

#### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
uv lock --upgrade

# Update specific package
uv lock --upgrade-package requests

# Verify lockfile is in sync with pyproject.toml
uv sync --frozen  # Fails if lockfile is out of sync
```

#### Lockfile in Pull Requests

- **Always commit `uv.lock` changes** with your code changes
- CI will verify lockfile is in sync (`uv sync --frozen`)
- If CI fails with "lockfile out of sync":
  ```bash
  uv lock
  git add uv.lock
  git commit --amend --no-edit
  git push --force-with-lease
  ```

#### Troubleshooting UV

```bash
# Clear UV cache if resolution fails
uv cache clean

# Verify environment is correct
uv run python --version
uv pip list

# Recreate virtual environment from scratch
rm -rf .venv
uv sync --all-extras

# Check for dependency conflicts
uv lock --verbose
```

## Submitting Your Contribution

Your change branch already holds the whole story — proposal, design, specs,
implementation, and (once done) the archive commit. It is merged into `main` as
**a single Pull Request**.

### 1. Archive the change (on the branch)

When implementation is complete, finalize the change with `/opsx:archive`. This
moves it to `openspec/changes/archive/` and updates the main specs in
`openspec/specs/`. **These commits happen on your change branch**, not on `main` —
the guard will reject them on `main`.

### 2. Commit Your Changes

Follow conventional commit messages, aligned with your branch type:

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat(cli): add support for EOS 4.31 versions

- Added parsing for new version format
- Updated XML querier to handle new structure
- Added comprehensive tests for version parsing

Closes #123"
```

If the commit is rejected because OpenSpec artifacts are staged on `main`, you
are on the wrong branch — create `<type>/<change-name>` and commit again.

### 3. Push Your Branch

```bash
git push origin feat/<change-name>   # (fork: git push origin feat/<change-name>)
```

### 4. Create a Pull Request

1. Navigate to the repository (or your fork) on GitHub
2. Click "Compare & pull request" for your `<type>/<change-name>` branch
3. Open **one** PR covering the whole change, and fill out the PR template with:
   - Clear description of changes
   - Reference to related issues
   - Testing performed
   - Breaking changes (if any)

### 5. PR Review Process

- Automated checks will run (tests, linting, type checking)
- Code coverage must not decrease significantly
- Maintainers will review your code
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Development Tips

### Working with Arista API

```python
# Always use environment variables for tokens
token = os.environ.get('ARISTA_TOKEN')
if not token:
    raise ValueError("ARISTA_TOKEN not found")

# Use the project's exception hierarchy
from eos_downloader.exceptions import TokenExpiredError, DownloadError

try:
    download_file(url, token)
except requests.HTTPError as e:
    if e.response.status_code == 401:
        raise TokenExpiredError("Token expired") from e
    raise DownloadError(f"HTTP error: {e}") from e
```

### Debugging

```bash
# Enable debug logging
export ARDL_LOG_LEVEL=debug

# Run with Python debugger
python -m pdb -m eos_downloader.cli get eos --version 4.29.3M

# Use pytest debugger
pytest --pdb tests/unit/models/test_version.py::test_specific_function
```

### Performance Considerations

- Use lazy evaluation and generators for large datasets
- Implement caching for expensive operations
- Consider concurrent downloads for multiple files
- Profile code with `cProfile` for performance bottlenecks

## Getting Help

- Check existing [issues](https://github.com/titom73/eos-downloader/issues)
- Read the [documentation](https://titom73.github.io/eos-downloader/)
- Ask questions in discussions or create a new issue
- Join our community discussions

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). Please read and follow it in all your interactions with the project.

## License

By contributing to eos-downloader, you agree that your contributions will be licensed under the same [Apache License 2.0](LICENSE) that covers the project.