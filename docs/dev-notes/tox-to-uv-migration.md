# Tox to UV Migration Guide

## Overview

This document provides the complete mapping from **tox** commands to **UV + Makefile** commands for the `eos-downloader` project.

The migration **maintains backward compatibility** with tox commands while leveraging UV's performance. You can use either:
- **Tox commands** (backward compatible): `tox -e lint`, `tox -e test`
- **Makefile commands** (direct UV, faster): `make lint`, `make test`

**Both work!** The tox.ini delegates to the Makefile, which uses UV directly.

---

## Quick Reference Table

| Old Tox Command | New Options (Both Work!) | Description |
|-----------------|--------------------------|-------------|
| `tox` | `tox -e all` or `make check` | Run all checks (lint, type, test) |
| `tox -e lint` | `tox -e lint` or `make lint` | Run linting (flake8 + pylint) |
| `tox -e type` | `tox -e type` or `make type` | Run type checking (mypy) |
| `tox -e py38` | `tox -e test` or `make test` | Run tests with pytest |
| `tox -e py39` | `tox -e test` or `make test` | Run tests with pytest |
| `tox -e py310` | `tox -e test` or `make test` | Run tests with pytest |
| `tox -e clean` | `tox -e clean` or `make clean` | Clean generated files |
| `tox -e report` | `tox -e coverage` or `make coverage` | Generate coverage report |

**Note:** Tox commands still work but delegate to UV + Makefile for maximum performance.

---

## Detailed Command Mapping

### 1. Linting (`tox -e lint`)

**Still works (backward compatible):**
```bash
tox -e lint
```

**Or use Makefile (slightly faster):**
```bash
make lint
```

**Or direct UV command:**
```bash
uv run flake8 --max-line-length=165 --config=/dev/null eos_downloader
uv run pylint --rcfile=pylintrc eos_downloader
```

**What it does:**
- Runs `flake8` for style checking
- Runs `pylint` for code quality analysis
- Both tools check the `eos_downloader` package

---

### 2. Type Checking (`tox -e type`)

**Old (tox):**
```bash
tox -e type
```

**New (UV):**
```bash
# Using Makefile (recommended)
make type

# Direct UV command
uv run mypy --config-file=pyproject.toml eos_downloader
```

**What it does:**
- Runs `mypy` type checker
- Uses configuration from `pyproject.toml`
- Validates type hints across the codebase

---

### 3. Testing (`tox -e py{38,39,310}`)

**Old (tox):**
```bash
tox -e py38      # Python 3.8
tox -e py39      # Python 3.9
tox -e py310     # Python 3.10
```

**New (UV):**
```bash
# Using Makefile (recommended)
make test

# Direct UV command
uv run pytest -rA -q --color yes --cov=eos_downloader tests/
```

**What it does:**
- Runs pytest test suite
- Includes basic coverage
- Uses pytest configuration from `pyproject.toml`

**Note:** UV automatically uses the Python version from `.python-version` file. For multi-version testing, use GitHub Actions matrix strategy (see CI/CD section).

---

### 4. Coverage Report (`tox -e report`)

**Old (tox):**
```bash
tox -e report
```

**New (UV):**
```bash
# Using Makefile (recommended)
make coverage

# Direct UV command
uv run pytest -rA -q \
    --cov=eos_downloader \
    --cov-report term-missing \
    --cov-report html \
    --cov-report xml \
    --color yes \
    tests/
```

**What it does:**
- Runs tests with comprehensive coverage
- Generates three report formats:
  - **Terminal:** Shows missing lines
  - **HTML:** `htmlcov/index.html` (interactive)
  - **XML:** `coverage.xml` (for CI/CD)

---

### 5. Clean (`tox -e clean`)

**Old (tox):**
```bash
tox -e clean
```

**New (UV):**
```bash
# Using Makefile (recommended)
make clean

# Manual cleanup
rm -rf .pytest_cache __pycache__ .mypy_cache htmlcov coverage.xml .coverage
```

**What it does:**
- Removes Python cache files (`__pycache__`)
- Removes test artifacts (`.pytest_cache`)
- Removes coverage reports (`htmlcov`, `coverage.xml`)
- Removes mypy cache (`.mypy_cache`)

---

### 6. Full Test Suite (`tox`)

**Old (tox):**
```bash
tox
```

**New (UV):**
```bash
# Using Makefile (recommended)
make check

# Or run each step individually
make lint
make type
make test
```

**What it does:**
- Runs all quality checks in sequence:
  1. Linting (flake8 + pylint)
  2. Type checking (mypy)
  3. Tests (pytest)

---

## Installation & Setup

### Installing Dependencies

**Old (tox):**
```bash
pip install tox
tox --notest  # Install dependencies without running tests
```

**New (UV):**
```bash
# Install all dependencies (dev + doc)
make install
# or
uv sync --all-extras

# Install only what you need
make install-dev      # Development dependencies
make install-doc      # Documentation dependencies
make install-base     # Production dependencies only
```

---

## CI/CD Integration

### GitHub Actions Migration

**Old (tox in GitHub Actions):**
```yaml
- name: Run tox
  run: tox -e lint,type,py310
```

**New (UV + Makefile in GitHub Actions):**
```yaml
- name: Install UV
  uses: astral-sh/setup-uv@v3
  with:
    version: "0.5.0"
    enable-cache: true

- name: Install dependencies
  run: make ci-install

- name: Run checks
  run: make ci-all
```

**Available CI targets:**
- `make ci-install` - Install dependencies (frozen, dev extras)
- `make ci-lint` - Run linting
- `make ci-type` - Run type checking
- `make ci-test` - Run tests
- `make ci-coverage` - Run tests with coverage
- `make ci-all` - Run all checks (lint + type + test)

---

## Benefits of UV Over Tox

### 1. **Speed**
- **Tox:** Creates separate virtual environments for each test environment (slow)
- **UV:** Single virtual environment, instant command execution
- **Result:** 5-10x faster for typical workflows

### 2. **Simplicity**
- **Tox:** Requires `tox.ini` configuration + understanding tox environments
- **UV:** Direct command execution + simple Makefile
- **Result:** Easier onboarding for new contributors

### 3. **Dependency Resolution**
- **Tox:** Uses pip for each environment (slow, non-deterministic)
- **UV:** Single `uv.lock` file, deterministic builds
- **Result:** Consistent environments across machines and CI

### 4. **Modern Features**
- **UV:** Built-in caching, workspace support, Python version management
- **Tox:** Requires additional tools (pyenv, pip-tools)

---

## Troubleshooting

### "Command not found: make"

Install `make`:
- **Ubuntu/Debian:** `sudo apt install build-essential`
- **macOS:** `xcode-select --install`
- **Windows:** Use WSL or install GNU Make

### "UV not found"

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Virtual environment not found"

Recreate the environment:
```bash
make reset      # Remove .venv
make install    # Reinstall dependencies
```

### "Tests failing with import errors"

Ensure dependencies are installed:
```bash
make install-dev  # Install dev dependencies
```

---

## Migration Checklist

If you're migrating from tox to UV:

- [ ] Install UV (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] Remove old virtual environment (`rm -rf .venv`)
- [ ] Install dependencies (`make install`)
- [ ] Test local commands:
  - [ ] `make lint` - Should pass
  - [ ] `make type` - Should pass
  - [ ] `make test` - Should pass
  - [ ] `make coverage` - Should generate reports
  - [ ] `make check` - Should run all checks
- [ ] Update CI/CD workflows (see Phase 5 plan)
- [ ] Update documentation references
- [ ] Remove `tox` from dependencies (if present)

---

## Additional Resources

- **UV Documentation:** https://docs.astral.sh/uv/
- **UV Installation Modes:** [`docs/uv-installation-modes.md`](./uv-installation-modes.md)
- **Migration Plan:** [`.github/plans/upgrade-package-manager-uv-v1.md`](../.github/plans/upgrade-package-manager-uv-v1.md)
- **Makefile:** [`Makefile`](../Makefile) (see all available targets with `make help`)

---

## Quick Start Examples

### Developer Workflow

```bash
# First time setup
make dev-setup

# Daily workflow
make format        # Format code
make check         # Run all checks before commit
make coverage      # Check test coverage

# Specific checks
make lint          # Only linting
make type          # Only type checking
make test          # Only tests
```

### CI/CD Workflow

```bash
# In GitHub Actions
make ci-install    # Install dependencies
make ci-all        # Run all checks
```

### Maintenance

```bash
make clean         # Clean generated files
make clean-venv    # Remove virtual environment
make reset         # Full reset
```

---

## Questions?

If you have questions about the migration:

1. Check the [UV documentation](https://docs.astral.sh/uv/)
2. Review the [migration plan](.github/plans/upgrade-package-manager-uv-v1.md)
3. Open an issue on GitHub

**Happy migrating!** 🚀
