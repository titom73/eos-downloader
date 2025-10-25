# Contributing to eos-downloader

Thank you for your interest in contributing to the eos-downloader project! This guide will help you get started with contributing to this Python CLI tool for downloading Arista EOS and CloudVision Portal software packages.

## Overview

eos-downloader is a Python CLI application built with Click, Rich, and pytest. It provides both a command-line interface and a programmatic API for downloading Arista software packages. The project follows modern Python development practices with comprehensive testing, type hints, and automated CI/CD.

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
- A virtual environment tool (venv, conda, etc.)

#### Environment Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks for code quality
pre-commit install
```

#### Verify Installation

```bash
# Run tests to ensure everything is working
pytest

# Check code style
tox -e lint

# Run type checking
tox -e type
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Sync your fork with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create a new feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

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
  - `cli/` - Click-based command line interface
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
pytest

# Run with coverage
pytest --cov=eos_downloader --cov-report=term-missing

# Run specific test file
pytest tests/unit/models/test_version.py

# Run tests matching a pattern
pytest -k "test_version"

# Run with verbose output
pytest -v

# Run tests in parallel (if you have pytest-xdist installed)
pytest -n auto
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
# Run all checks with tox
tox

# Individual checks
tox -e lint      # Linting with flake8 and pylint
tox -e type      # Type checking with mypy
tox -e py310     # Tests on Python 3.10

# Format code
black eos_downloader/ tests/
isort eos_downloader/ tests/

# Pre-commit checks (runs automatically on commit)
pre-commit run --all-files
```

## Submitting Your Contribution

### 1. Commit Your Changes

Follow conventional commit messages:

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

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Navigate to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template with:
   - Clear description of changes
   - Reference to related issues
   - Testing performed
   - Breaking changes (if any)

### 4. PR Review Process

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

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read and follow it in all your interactions with the project.

## License

By contributing to eos-downloader, you agree that your contributions will be licensed under the same [Apache License 2.0](LICENSE) that covers the project.