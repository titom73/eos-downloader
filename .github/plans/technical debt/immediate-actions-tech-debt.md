# Immediate Actions - Technical Debt eos-downloader
**Date**: December 11, 2025
**Priority**: CRITICAL
**Parent Document**: [technical-debt-analysis-dec-2025.md](technical-debt-analysis-dec-2025.md)

---

## 🚀 Quick Start - Actions to Do Now

This document lists **concrete and immediate actions** to start technical debt remediation. All these tasks can be completed **this week**.

---

## ✅ Task 1: Python 3.12 Support (⏱️ 2 hours)

### Objective
Add official support for Python 3.12 to the project.

### Actions
```bash
# 1. Edit configuration file
nano .github/python-versions.json

# Modify to include Python 3.12:
{
  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],
  "uv_version": "latest"
}

# 2. Sync with pyproject.toml
uv run python .github/scripts/sync-python-versions.py

# 3. Verify correctness
git diff pyproject.toml

# 4. Commit and push
git add .github/python-versions.json pyproject.toml
git commit -m "feat: Add Python 3.12 support"
git push
```

### Validation
- [ ] GitHub Actions CI tests Python 3.12
- [ ] All tests pass for Python 3.12
- [ ] pyproject.toml includes Python 3.12 in classifiers

### GitHub Issue to Create
```markdown
**Title**: Add Python 3.12 support
**Labels**: enhancement, python
**Description**:
The project currently supports Python 3.9, 3.10, 3.11, and 3.13 but is missing Python 3.12.

**Tasks**:
- [ ] Update `.github/python-versions.json`
- [ ] Run sync script
- [ ] Verify CI tests pass
- [ ] Update documentation if needed
```

---

## ✅ Task 2: Token Masking in Logs (⏱️ 3 hours)

### Objective
Prevent accidental exposure of Arista tokens in logs.

### Actions

#### Step 1: Create Security Module
```bash
# Create file
touch eos_downloader/helpers/security.py
```

**Content of `eos_downloader/helpers/security.py`**:
```python
#!/usr/bin/env python
# coding: utf-8 -*-
"""Security utilities for handling sensitive data."""

from typing import Optional


def mask_token(token: Optional[str], show_chars: int = 4) -> str:
    """
    Mask a token for safe logging.

    Parameters
    ----------
    token : Optional[str]
        The token to mask
    show_chars : int, optional
        Number of characters to show at start and end, by default 4

    Returns
    -------
    str
        Masked token in format: "abcd...wxyz"

    Examples
    --------
    >>> mask_token("abcdefghijklmnopqrstuvwxyz")
    'abcd...wxyz'
    >>> mask_token("")
    '***'
    >>> mask_token(None)
    '***'
    """
    if not token or len(token) < show_chars * 2:
        return "***"

    return f"{token[:show_chars]}...{token[-show_chars:]}"


def validate_arista_token(token: Optional[str]) -> bool:
    """
    Validate Arista token format.

    Parameters
    ----------
    token : Optional[str]
        Token to validate

    Returns
    -------
    bool
        True if token is valid

    Raises
    ------
    ValueError
        If token is invalid
    """
    if not token:
        raise ValueError("Token cannot be empty")

    if len(token) < 20:
        raise ValueError(
            "Token too short. Arista tokens are typically longer than 20 characters."
        )

    return True
```

#### Step 2: Create Tests
```bash
touch tests/unit/helpers/test_security.py
```

**Content of `tests/unit/helpers/test_security.py`**:
```python
"""Tests for security utilities."""

import pytest
from eos_downloader.helpers.security import mask_token, validate_arista_token


class TestTokenMasking:
    """Test token masking functionality."""

    def test_mask_long_token(self):
        """Test masking a long token."""
        token = "abcdefghijklmnopqrstuvwxyz0123456789"
        masked = mask_token(token)

        assert "abcd" in masked
        assert "6789" in masked
        assert "..." in masked
        assert len(masked) < len(token)

    def test_mask_empty_token(self):
        """Test masking an empty token."""
        assert mask_token("") == "***"
        assert mask_token(None) == "***"

    def test_mask_short_token(self):
        """Test masking a very short token."""
        assert mask_token("abc") == "***"

    def test_custom_show_chars(self):
        """Test masking with custom number of visible chars."""
        token = "abcdefghijklmnop"
        masked = mask_token(token, show_chars=2)

        assert "ab" in masked
        assert "op" in masked


class TestTokenValidation:
    """Test token validation."""

    def test_valid_token(self):
        """Test validation of a valid token."""
        token = "a" * 25  # Token long enough
        assert validate_arista_token(token) is True

    def test_empty_token(self):
        """Test validation of empty token."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_arista_token("")

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_arista_token(None)

    def test_short_token(self):
        """Test validation of too short token."""
        with pytest.raises(ValueError, match="too short"):
            validate_arista_token("short")
```

#### Step 3: Use in Existing Code

**Modify `eos_downloader/cli/cli.py`**:
```python
# Add import
from eos_downloader.helpers.security import mask_token, validate_arista_token

# In ardl() function
@click.option("--token", ...)
def ardl(ctx: click.Context, token: str, log_level: str, debug_enabled: bool) -> None:
    """Arista Network Download CLI"""

    # Validate and mask token
    if token:
        try:
            validate_arista_token(token)
            logger.info(f"Using token: {mask_token(token)}")

            # Warning if token passed via CLI instead of env var
            if not os.environ.get('ARISTA_TOKEN'):
                logger.warning(
                    "⚠️  Token passed via CLI is less secure. "
                    "Consider using ARISTA_TOKEN environment variable."
                )
        except ValueError as e:
            logger.error(f"Invalid token: {e}")
            sys.exit(1)
```

### Validation
```bash
# Run tests
pytest tests/unit/helpers/test_security.py -v

# Verify token is masked in logs
ardl --token "test_token_1234567890" info eos --debug 2>&1 | grep -i token
# Should display: "test...7890" and not the full token
```

### GitHub Issue to Create
```markdown
**Title**: Implement token masking for secure logging
**Labels**: security, enhancement
**Description**:
Prevent accidental exposure of Arista API tokens in logs and terminal output.

**Security Impact**: Medium - prevents credential leakage

**Tasks**:
- [ ] Create `helpers/security.py` with masking utilities
- [ ] Add comprehensive tests
- [ ] Update CLI to use token masking
- [ ] Add warning for CLI token usage
- [ ] Document best practices in security guide
```

---

## ✅ Task 3: detect-secrets Pre-commit Hook (⏱️ 1 hour)

### Objective
Prevent accidental commits of secrets.

### Actions

#### Step 1: Install detect-secrets
```bash
uv pip install detect-secrets
```

#### Step 2: Create Baseline
```bash
# Scan project and create baseline
detect-secrets scan > .secrets.baseline

# Audit detected secrets
detect-secrets audit .secrets.baseline
```

#### Step 3: Configure Pre-commit
**Modify `.pre-commit-config.yaml`**:
```yaml
# Add to end of file
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: package.lock.json
```

#### Step 4: Install Hook
```bash
pre-commit install
```

### Validation
```bash
# Test the hook
echo "api_key = 'sk-test123456789'" > test_secret.py
git add test_secret.py
git commit -m "test"  # Should fail

# Cleanup
rm test_secret.py
```

### GitHub Issue to Create
```markdown
**Title**: Add detect-secrets pre-commit hook
**Labels**: security, devops
**Description**:
Prevent accidental commits of secrets and credentials.

**Tasks**:
- [ ] Install detect-secrets
- [ ] Create secrets baseline
- [ ] Configure pre-commit hook
- [ ] Update contributing guide
- [ ] Add to CI pipeline
```

---

## ✅ Task 4: Clean __pycache__ (⏱️ 30 minutes)

### Objective
Ensure no `__pycache__` files are tracked in git.

### Actions

#### Step 1: Verify
```bash
# Check if any __pycache__ are tracked
git ls-files | grep __pycache__
```

#### Step 2: Clean (if needed)
```bash
# If files found, remove them
find . -type d -name __pycache__ -exec git rm -r --cached {} + 2>/dev/null

# Commit change
git commit -m "chore: Remove __pycache__ directories from git tracking"
```

#### Step 3: Add Makefile Command
**Modify `Makefile`**:
```makefile
.PHONY: clean-pycache
clean-pycache: ## Clean all __pycache__ directories and .pyc files
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Python cache cleaned"

.PHONY: clean-all
clean-all: clean clean-pycache ## Clean everything (build artifacts + cache)
	@echo "✓ All cleaned"
```

#### Step 4: Verify .gitignore
**Verify `.gitignore` contains**:
```gitignore
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.pyc
*.pyo
```

### Validation
```bash
# No __pycache__ should be listed
git ls-files | grep __pycache__ || echo "✓ Clean"

# Test make command
make clean-pycache
```

---

## ✅ Task 5: Create Centralized Logging Config Module (⏱️ 2 hours)

### Objective
Centralize logging configuration to facilitate migration to loguru.

### Actions

#### Step 1: Create Module
```bash
touch eos_downloader/logging_config.py
```

**Content of `eos_downloader/logging_config.py`**:
```python
#!/usr/bin/env python
# coding: utf-8 -*-
"""
Centralized logging configuration for eos-downloader.

This module provides a unified logging interface using loguru.
All modules should import and use the logger from this module.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
) -> None:
    """
    Configure global logging settings.

    Parameters
    ----------
    level : str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), by default "INFO"
    log_file : Optional[Path], optional
        Path to log file, by default None (console only)
    rotation : str, optional
        Log file rotation size, by default "10 MB"

    Examples
    --------
    >>> configure_logging(level="DEBUG")
    >>> configure_logging(level="INFO", log_file=Path("app.log"))
    """
    # Remove default handler
    logger.remove()

    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention="1 week",
            compression="zip",
        )

    logger.info(f"Logging configured at level: {level}")


# Export logger for use in other modules
__all__ = ["logger", "configure_logging"]
```

#### Step 2: Create Tests
```bash
touch tests/unit/test_logging_config.py
```

**Content of `tests/unit/test_logging_config.py`**:
```python
"""Tests for logging configuration."""

import pytest
from pathlib import Path
from eos_downloader.logging_config import logger, configure_logging


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_logger_available(self):
        """Test that logger is available."""
        assert logger is not None

    def test_configure_basic(self):
        """Test basic logging configuration."""
        configure_logging(level="INFO")
        # Should not raise

    def test_configure_with_file(self, tmp_path):
        """Test logging configuration with file output."""
        log_file = tmp_path / "test.log"
        configure_logging(level="DEBUG", log_file=log_file)

        logger.info("Test message")

        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_different_levels(self):
        """Test different logging levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            configure_logging(level=level)
            # Should not raise
```

#### Step 3: Migration Plan for Existing Modules
**Create `.github/plans/logging-migration-checklist.md`**:
```markdown
# Logging Migration to Centralized Configuration

## Modules to Migrate

- [ ] eos_downloader/models/version.py
- [ ] eos_downloader/logics/arista_server.py
- [ ] eos_downloader/logics/arista_xml_server.py
- [ ] eos_downloader/logics/download.py
- [ ] eos_downloader/cli/utils.py

## Migration Pattern

### Before
```python
import logging
logging.debug("message")
```

### After
```python
from eos_downloader.logging_config import logger
logger.debug("message")
```

## Validation
- [ ] All tests pass
- [ ] Logs are consistent
- [ ] No standard `logging` imports remaining
```

### Validation
```bash
# Run tests
pytest tests/unit/test_logging_config.py -v

# Test import
python -c "from eos_downloader.logging_config import logger; logger.info('Test')"
```

---

## 📋 Complete Checklist

Mark each task once completed:

### This Week
- [ ] Task 1: Python 3.12 Support (2h)
- [ ] Task 2: Token Masking (3h)
- [ ] Task 3: detect-secrets (1h)
- [ ] Task 4: Clean __pycache__ (30min)
- [ ] Task 5: Centralized Logging Module (2h)

### Global Validation
- [ ] All tests pass: `pytest`
- [ ] Linting OK: `make lint`
- [ ] Type checking OK: `make type`
- [ ] GitHub Actions CI passes
- [ ] Documentation updated

---

## 🎯 After These Actions

Once these 5 tasks are completed, you will have:

✅ **+5% coverage** (new features tested)
✅ **Enhanced security** (masked tokens, detect-secrets)
✅ **Extended support** (Python 3.12)
✅ **Clean base** (no git cache)
✅ **Improved architecture** (centralized logging)

**Estimated Total Time**: ~9 hours (1-2 days)
**Impact**: 🔴 High - Solid foundation for future work

---

## 📞 Support

**Questions?** Open a GitHub discussion
**Bugs?** Create an issue with label `technical-debt`
**Parent Document**: [technical-debt-analysis-dec-2025.md](technical-debt-analysis-dec-2025.md)

---

**Created**: December 11, 2025
**Status**: 🔄 Actions Pending
