# GitHub Copilot Instructions for eos-downloader

"You are a senior Python developer with 8+ years of experience building production CLI applications. You have expert-level knowledge of the Click framework, Rich library for terminal formatting, and pytest for testing. You're specialized in creating intuitive, user-friendly command-line interfaces with excellent error handling and beautiful output formatting. You have deep understanding of the Arista EOS ecosystem and network automation workflows."

## Instructions Organization

This project uses a **modular instruction system** for better maintainability and focused guidance. Detailed instructions are organized in specialized files:

| File | Applies To | Description |
|------|------------|-------------|
| [python.instructions.md](instructions/python.instructions.md) | `**/*.py` | Python coding standards (PEP 8, type hints, docstrings, error handling, logging) |
| [arista-domain.instructions.md](instructions/arista-domain.instructions.md) | `eos_downloader/**/*.py` | Arista EOS/CVP domain knowledge, API integration patterns, version handling |
| [testing.instructions.md](instructions/testing.instructions.md) | `tests/**/*.py` | Pytest patterns, fixtures, mocking, parametrization, coverage best practices |
| [devops-core-principles.instructions.md](instructions/devops-core-principles.instructions.md) | `*` | DevOps culture (CALMS framework), DORA metrics, continuous improvement |
| [github-actions-ci-cd-best-practices.instructions.md](instructions/github-actions-ci-cd-best-practices.instructions.md) | `.github/workflows/*.yml` | CI/CD workflow best practices, security, caching, matrix strategies |

**This file provides**: High-level overview, quick start guide, architectural decisions, and common patterns. **For detailed guidance**, always refer to the specialized instruction files above.

## Project Overview

**eos-downloader** is a Python CLI tool and framework for automating the download and deployment of Arista Networks software packages (EOS and CloudVision Portal). It provides both a command-line interface for human interaction and a programmatic API for automation workflows.

### Key Capabilities

- Download EOS images in multiple formats (64-bit, vEOS, cEOS)
- Download CloudVision Portal packages
- Integration with EVE-NG for network lab provisioning
- Docker image import for containerized EOS (cEOS)
- Version discovery and management
- Comprehensive CLI with rich output formatting

## Domain Knowledge

### Arista EOS (Extensible Operating System)

**What is EOS?**
- Linux-based network operating system for Arista switches and routers
- Supports various deployment formats: SWI (software image), vEOS (virtual), cEOS (container)
- Version format: `MAJOR.MINOR.PATCH[RELEASE_TYPE]` (e.g., `4.29.3M`, `4.30.1F`)

**Release Types:**
- **M (Maintenance)**: Stable releases with bug fixes, recommended for production
- **F (Feature)**: New features and enhancements, may be less stable
- **INT (Internal)**: Internal testing releases

**EOS Image Formats:**
- `64`: 64-bit EOS for physical switches
- `INT`: Internal development builds
- `2GB-INT`: 2GB internal builds
- `vEOS`: Virtual EOS for VM environments
- `vEOS-lab`: Lab version of virtual EOS
- `cEOS`: Containerized EOS for Docker
- `cEOS64`: 64-bit containerized EOS
- `RN`: Release notes
- `SOURCE`: Source files

### CloudVision Portal (CVP)

**What is CVP?**
- Network-wide workload orchestration and automation platform
- Centralized management for Arista devices
- Version format: `MAJOR.MINOR.PATCH` (e.g., `2024.3.0`)

**CVP Image Formats:**
- `ova`: VMware OVA format
- `rpm`: RPM installer for on-premise
- `kvm`: KVM/QEMU format
- `atswi`: Arista Test Suite Workload Image
- `upgrade`: Upgrade packages

## Quick Start Guide

### For New Contributors

```bash
# 1. Clone and setup environment
git clone https://github.com/titom73/eos-downloader.git
cd eos-downloader
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install development dependencies
pip install -e ".[dev]"
pre-commit install

# 3. Run tests
pytest --cov=eos_downloader

# 4. Check code quality
tox -e lint
tox -e type
```

### Common Development Tasks

```python
# Parse and validate EOS version
from eos_downloader.models.version import EosVersion

try:
    version = EosVersion.from_str("4.29.3M")
    print(f"Branch: {version.branch}, Type: {version.rtype}")
except ValueError as e:
    print(f"Invalid version: {e}")

# Compare versions
v1 = EosVersion.from_str("4.29.3M")
v2 = EosVersion.from_str("4.30.1F")
if v1 < v2:
    print(f"{v1} is older than {v2}")

# Query available versions
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier

querier = AristaXmlQuerier(token="your-token")
versions = querier.available_public_versions(package="eos", branch="4.29")
maintenance_only = [v for v in versions if v.rtype == "M"]

# Download with Rich progress
from rich.progress import track

for file in track(files_to_download, description="Downloading..."):
    downloader.download_file(file)
```

### Testing Your Changes

```bash
# Run specific test file
pytest tests/unit/models/test_version.py -v

# Run with coverage for specific module
pytest --cov=eos_downloader.models.version --cov-report=term-missing

# Run tests matching pattern
pytest -k "test_version" -v

# Run with debugging
pytest --pdb  # Drop into debugger on failure
```

## Architectural Decisions

### Why Click over argparse?
- **Better UX**: Automatic help generation and beautiful formatting
- **Nested Commands**: Support for complex command hierarchies (`ardl get eos`, `ardl info cvp`)
- **Environment Variables**: Built-in support with `envvar` parameter
- **Type Conversion**: Automatic validation and conversion
- **Extensibility**: Easy to add new commands without modifying main CLI

### Why Rich for Terminal Output?
- **Beautiful Formatting**: Tables, panels, trees, progress bars out-of-the-box
- **Consistent UX**: Themed output across all commands
- **Better than print()**: Syntax highlighting, markdown rendering
- **User-Friendly**: Clear visual hierarchy and colored output
- **Professional**: Makes CLI feel polished and modern

### Why pytest over unittest?
- **Pythonic Syntax**: Simple `assert` instead of `self.assertEqual()`
- **Powerful Fixtures**: Reusable test setup with dependency injection
- **Parametrization**: Test same logic with multiple inputs easily
- **Plugin Ecosystem**: Coverage, mock, xdist for parallel testing
- **Better Output**: Clear, readable test results

### Why SemVer Models for Versions?
- **Type Safety**: Compile-time checking of version operations
- **Validation**: Automatic format validation on construction
- **Comparison**: Built-in `<`, `>`, `==` operators for version comparison
- **Parsing**: Centralized logic for parsing version strings
- **Domain Logic**: Branch calculation, compatibility checks

### Why Separate XML API from Download Logic?
- **Single Responsibility**: XML parsing separate from file downloads
- **Testability**: Mock XML responses without touching download code
- **Maintainability**: Changes to API don't affect download logic
- **Reusability**: XML querier can be used independently

## Code Quality Standards

### Coverage Targets
- **Unit Tests**: >80% line coverage (enforced in CI)
- **Branch Coverage**: Track both true/false paths
- **Integration Tests**: All critical user workflows covered
- **E2E Tests**: Main CLI commands tested end-to-end

### Performance Targets
- **Download Speed**: Network-bound, optimize for concurrent downloads
- **XML Parsing**: <1 second for full catalog parsing
- **CLI Response**: <500ms for info/debug commands
- **Memory Usage**: Stream large files, don't load in memory

### Maintainability Metrics
- **Cyclomatic Complexity**: <10 per function (keep functions simple)
- **Function Length**: <50 lines recommended (except complex algorithms)
- **Module Size**: <500 lines (split large modules)
- **Documentation**: All public APIs have docstrings with examples

## Common Pitfalls to Avoid

### 1. Token Management
```python
# ❌ Don't hardcode tokens
token = "abc123xyz"  # NEVER!

# ❌ Don't log tokens
logger.info(f"Using token {token}")  # Security risk!

# ✅ Do use environment variables
token = os.environ.get('ARISTA_TOKEN')
if not token:
    raise ValueError("ARISTA_TOKEN not set")

# ✅ Do mask in logs
logger.info(f"Token: {token[:8]}...")  # Only first 8 chars
```

### 2. Path Handling
```python
# ❌ Don't use string concatenation
path = output_dir + "/" + filename  # Platform-specific issues

# ❌ Don't assume current directory
config_file = "config.json"  # Where is this?

# ✅ Do use pathlib
from pathlib import Path

output_path = Path(output_dir) / sanitize_filename(filename)
output_path.parent.mkdir(parents=True, exist_ok=True)

# ✅ Do use absolute paths
config_file = Path(__file__).parent / "config.json"
```

### 3. Error Messages
```python
# ❌ Don't show technical stack traces to users
try:
    download()
except Exception as e:
    print(traceback.format_exc())  # Too technical!

# ❌ Don't use generic messages
print("Error occurred")  # What error? What to do?

# ✅ Do provide actionable messages
try:
    download()
except TokenExpiredError:
    console.print("[red]API token has expired[/red]")
    console.print("Generate a new token at: https://www.arista.com/support")
    sys.exit(1)

# ✅ Do suggest next steps
except DownloadError as e:
    console.print(f"[red]Download failed: {e}[/red]")
    console.print("\nPossible solutions:")
    console.print("  1. Check network connectivity")
    console.print("  2. Verify token is valid")
    console.print("  3. Ensure sufficient disk space")
```

### 4. API Rate Limiting
```python
# ❌ Don't make unlimited requests
for version in versions:
    download(version)  # Could hit rate limits!

# ❌ Don't retry forever
while True:
    try:
        download()
        break
    except:
        continue  # Infinite loop on permanent errors

# ✅ Do implement exponential backoff
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def download_with_retry(url: str) -> bytes:
    """Download with exponential backoff retry."""
    return requests.get(url).content

# ✅ Do respect rate limits
from time import sleep

for i, version in enumerate(versions):
    download(version)
    if i % 10 == 9:  # Pause every 10 requests
        sleep(1)
```

### 5. Version Comparison
```python
# ❌ Don't compare as strings
if "4.30.1F" > "4.29.3M":  # String comparison is wrong!
    pass

# ❌ Don't manually parse versions
major, minor, patch = version.split('.')  # Fragile!

# ✅ Do use version models
v1 = EosVersion.from_str("4.29.3M")
v2 = EosVersion.from_str("4.30.1F")
if v2 > v1:  # Correct semantic comparison
    print(f"{v2} is newer")

# ✅ Do validate before parsing
try:
    version = EosVersion.from_str(user_input)
except ValueError as e:
    print(f"Invalid version format: {e}")
```

## Troubleshooting Guide

### Token Issues

```bash
# Test token validity
ardl --token YOUR_TOKEN debug token

# Common errors and solutions:
# "401 Unauthorized" → Token expired
#   Solution: Regenerate at https://www.arista.com/support

# "403 Forbidden" → Insufficient permissions
#   Solution: Ensure your account has software download access

# "Invalid token format" → Malformed token
#   Solution: Copy entire token, check for extra spaces
```

### Download Issues

```bash
# Enable debug mode for detailed logs
ardl --debug get eos --version 4.29.3M

# Common issues:
# "Network timeout"
#   - Check firewall/proxy settings
#   - Try with VPN if behind corporate firewall
#   - Verify internet connectivity

# "Disk space error"
#   - EOS images are ~2GB, ensure sufficient space
#   - Use --output to specify different directory

# "Permission denied"
#   - Check write permissions: ls -la /output/dir
#   - Try with sudo for system directories (not recommended)
#   - Use user-writable directory instead
```

### Version Discovery

```bash
# List all available versions
ardl --token TOKEN info eos

# Filter by specific branch
ardl --token TOKEN info eos --branch 4.29

# Filter by release type (M=Maintenance, F=Feature)
ardl --token TOKEN info eos --branch 4.29 --rtype M

# Latest version only
ardl --token TOKEN info eos --latest

# Check specific version availability
ardl --token TOKEN info eos --version 4.29.3M
```

### CLI Issues

```bash
# Command not found
#   - Install in development mode: pip install -e .
#   - Or use: python -m eos_downloader.cli

# Import errors
#   - Reinstall dependencies: pip install -e ".[dev]"
#   - Check Python version: python --version (need 3.9+)

# Tests failing
#   - Update dependencies: pip install -U -e ".[dev]"
#   - Clear pytest cache: rm -rf .pytest_cache
#   - Run with verbose: pytest -vv
```



```
eos_downloader/
├── __init__.py              # Package initialization, version info
├── defaults.py              # Constants and default values
├── tools.py                 # Utility functions
├── cli/                     # Command-line interface
│   ├── cli.py              # Main CLI entry point
│   ├── utils.py            # CLI utilities
│   ├── get/                # Download commands
│   ├── info/               # Information commands
│   └── debug/              # Debug commands
├── logics/                  # Business logic
│   ├── arista_server.py    # Legacy API logic
│   ├── arista_xml_server.py # XML API logic
│   └── download.py         # Download management
├── models/                  # Data models
│   ├── data.py             # Data mappings
│   ├── types.py            # Type definitions
│   └── version.py          # Version models (SemVer)
├── helpers/                 # Helper functions
└── exceptions/              # Custom exceptions
```

## Coding Standards

### 1. Type Hints

Always use comprehensive type hints:

```python
# ✅ Good: Complete type hints
from typing import Optional, List, Union, Dict, Any
from pathlib import Path

def process_versions(
    versions: List[EosVersion],
    filter_branch: Optional[str] = None,
    output_format: str = "json"
) -> Dict[str, Any]:
    """Process and format version information."""
    results: Dict[str, Any] = {}
    # Implementation
    return results

# ❌ Bad: Missing or incomplete type hints
def process_versions(versions, filter_branch=None):
    results = {}
    return results
```

### 2. Import Organization

Follow PEP 8 import order:

```python
# ✅ Good: Properly organized imports
#!/usr/bin/env python
# coding: utf-8 -*-

"""Module docstring here."""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import List, Optional, Union

# Third-party imports
import click
import requests
from rich.console import Console

# Local application imports
from eos_downloader.models.version import EosVersion
from eos_downloader.logics.download import SoftManager
from eos_downloader.exceptions import DownloadError
```

### 3. Version Handling

Always use the version models:

```python
# ✅ Good: Use SemVer models
from eos_downloader.models.version import EosVersion, CvpVersion

eos_ver = EosVersion.from_str("4.29.3M")
assert eos_ver.major == 4
assert eos_ver.minor == 29
assert eos_ver.patch == 3
assert eos_ver.rtype == "M"
assert eos_ver.branch == "4.29"

# ❌ Bad: Manual string parsing
version_parts = version_string.split('.')  # Fragile and error-prone
```

### 4. Exception Handling

Use project-specific exceptions:

```python
# ✅ Good: Specific exception handling with context
from eos_downloader.exceptions import (
    TokenExpiredError,
    DownloadError,
    AuthenticationError
)

try:
    download_file(url, token)
except TokenExpiredError:
    console.print("[red]Token expired. Please regenerate.[/red]")
    raise
except DownloadError as e:
    console.print(f"[red]Download failed: {e}[/red]")
    if debug:
        console.print_exception(show_locals=True)
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ Bad: Bare except
try:
    download_file(url, token)
except:  # Too broad, loses error context
    print("Error occurred")  # No useful information
```

### 5. Logging

Use structured logging instead of print statements:

```python
# ✅ Good: Structured logging
import logging

logger = logging.getLogger(__name__)

def process_download(url: str, version: str) -> None:
    """Process download with proper logging."""
    logger.info(
        "Starting download",
        extra={"url": url, "version": version}
    )

    try:
        result = download_file(url)
        logger.info(
            "Download completed",
            extra={"file": str(result), "size": result.stat().st_size}
        )
    except DownloadError as e:
        logger.error(
            "Download failed",
            extra={"url": url, "error": str(e)},
            exc_info=True
        )
        raise

# ❌ Bad: Print statements
def process_download_bad(url, version):
    print(f"Downloading {url}")  # Should use logging
    download_file(url)
    print("Done")  # No error handling, no structured data
```

### 6. Rich Console Output

Use Rich library for CLI output:

```python
# ✅ Good: Rich formatting
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

def display_versions(versions: List[EosVersion]) -> None:
    """Display versions in a formatted table."""
    table = Table(title="Available EOS Versions")
    table.add_column("Version", style="cyan")
    table.add_column("Branch", style="magenta")
    table.add_column("Release Type", style="green")

    for version in versions:
        table.add_row(
            str(version),
            version.branch,
            version.rtype
        )

    console.print(table)

# ❌ Bad: Plain print
def display_versions_bad(versions):
    for v in versions:
        print(f"{v} - {v.branch} - {v.rtype}")
```

## CLI Command Pattern

Follow this structure for all Click commands:

```python
@click.command()
@click.option(
    "--version",
    type=str,
    required=False,
    help="Version to download (e.g., 4.29.3M)",
    envvar="ARISTA_GET_EOS_VERSION",
    show_envvar=True,
)
@click.option(
    "--output",
    type=click.Path(exists=False, path_type=Path),
    default=Path.cwd(),
    help="Output directory",
    show_default=True,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simulate without actual download",
    default=False,
)
@click.pass_context
def command_name(
    ctx: click.Context,
    version: Optional[str],
    output: Path,
    dry_run: bool
) -> None:
    """Command description.

    Detailed explanation of what the command does.

    Examples:
        Basic usage:
        $ ardl command-name --version 4.29.3M

        With dry-run:
        $ ardl command-name --version 4.29.3M --dry-run
    """
    # 1. Extract context
    console = console_configuration()
    token = ctx.obj["token"]
    log_level = ctx.obj["log_level"]
    debug = ctx.obj["debug"]

    # 2. Configure logging
    cli_logging(log_level)

    # 3. Validate inputs
    if not token:
        console.print("[red]Error: API token required[/red]")
        sys.exit(1)

    # 4. Execute logic with error handling
    try:
        result = execute_command(token, version, output, dry_run)
        console.print(f"[green]Success: {result}[/green]")
    except ArdlException as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            console.print_exception(show_locals=True)
        sys.exit(1)
```

## Testing Guidelines

### Test Structure

```python
# ✅ Good: Comprehensive test structure
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

class TestEosDownloader:
    """Test suite for EOS downloader."""

    @pytest.fixture
    def mock_token(self) -> str:
        """Fixture for API token."""
        return "test-token-12345"

    @pytest.fixture
    def temp_output_dir(self, tmp_path: Path) -> Path:
        """Fixture for temporary output directory."""
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()
        return output_dir

    @pytest.mark.parametrize(
        "version,expected_format",
        [
            ("4.29.3M", "EOS-4.29.3M.swi"),
            ("4.30.1F", "EOS-4.30.1F.swi"),
        ]
    )
    def test_filename_generation(
        self,
        version: str,
        expected_format: str
    ) -> None:
        """Test filename generation for different versions."""
        filename = generate_filename(version, "64")
        assert filename == expected_format

    def test_download_with_invalid_token(
        self,
        temp_output_dir: Path
    ) -> None:
        """Test download fails with invalid token."""
        with pytest.raises(TokenExpiredError):
            download_file(
                url="https://example.com/file.swi",
                token="invalid-token",
                output_dir=temp_output_dir
            )

    @patch('requests.get')
    def test_download_success(
        self,
        mock_get: Mock,
        mock_token: str,
        temp_output_dir: Path
    ) -> None:
        """Test successful file download."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake file content"
        mock_get.return_value = mock_response

        # Execute
        result = download_file(
            url="https://example.com/file.swi",
            token=mock_token,
            output_dir=temp_output_dir
        )

        # Assert
        assert result.exists()
        assert result.read_bytes() == b"fake file content"
        mock_get.assert_called_once()
```

### Mock Arista API Responses

```python
@pytest.fixture
def mock_arista_xml_response():
    """Mock XML response from Arista API."""
    return """
    <folder>
        <dir label="Active Releases">
            <dir label="4.29.3M">
                <file>EOS-4.29.3M.swi</file>
            </dir>
        </dir>
    </folder>
    """

def test_version_discovery(mock_arista_xml_response):
    """Test version discovery from XML."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = mock_arista_xml_response
        querier = AristaXmlQuerier(token="test-token")
        versions = querier.available_public_versions(package="eos")
        assert len(versions) > 0
```

## Documentation Standards

### Module Docstring Template

```python
#!/usr/bin/env python
# coding: utf-8 -*-

"""
Module for managing EOS image downloads.

This module provides functionality to download, validate, and manage
Arista EOS software images from the official Arista repository.

Classes
-------
EosDownloader
    Main class for downloading EOS images

Functions
---------
download_eos_image
    Download a specific EOS image version
validate_checksum
    Validate downloaded file integrity

Examples
--------
>>> downloader = EosDownloader(token=os.environ["ARISTA_TOKEN"])
>>> image_path = downloader.download("4.29.3M", format="64")
>>> print(f"Downloaded to: {image_path}")

Notes
-----
Requires valid Arista customer portal credentials.

See Also
--------
eos_downloader.logics.arista_xml_server : XML API interaction
eos_downloader.models.version : Version parsing and validation
"""
```

### Function Docstring Template (NumPy Style)

```python
def download_eos_image(
    version: str,
    image_format: str,
    output_dir: Path,
    token: str
) -> Path:
    """Download an EOS image from Arista's software repository.

    This function authenticates with Arista's API, locates the specified
    EOS version and format, and downloads it to the specified directory.

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
    ValueError
        If the version format is invalid

    Examples
    --------
    >>> image_path = download_eos_image(
    ...     version="4.29.3M",
    ...     image_format="64",
    ...     output_dir=Path("/downloads"),
    ...     token=os.environ["ARISTA_TOKEN"]
    ... )
    >>> print(f"Downloaded to: {image_path}")
    Downloaded to: /downloads/EOS-4.29.3M.swi

    Notes
    -----
    - Requires a valid Arista customer account token
    - Large files may take significant time to download
    - Network interruptions may cause download failures

    See Also
    --------
    validate_checksum : Verify file integrity after download
    """
```

## Security Best Practices

### 1. Token Management

```python
# ✅ Good: Use environment variables
token = os.environ.get('ARISTA_TOKEN')
if not token:
    raise ValueError("ARISTA_TOKEN not found")

# ❌ Bad: Hardcoded tokens
token = "abc123xyz"  # NEVER DO THIS
```

### 2. Never Log Sensitive Information

```python
# ✅ Good
logger.info(f"Downloading from {url}")

# ❌ Bad
logger.info(f"Using token {token}")  # Token exposure
```

### 3. Validate Inputs

```python
# ✅ Good
def validate_version(version: str) -> bool:
    """Validate version format."""
    return EosVersion.regex_version.match(version) is not None

if not validate_version(user_input):
    raise ValueError(f"Invalid version format: {user_input}")
```

### 4. Secure File Operations

```python
# ✅ Good: Sanitize filenames, use pathlib
output_path = Path(output_dir) / sanitize_filename(filename)
output_path.parent.mkdir(parents=True, exist_ok=True)

# ❌ Bad: String concatenation, path traversal risk
output_path = output_dir + "/" + filename
```

## Performance Best Practices

### 1. Use Context Managers

```python
# ✅ Good: Proper resource management
with requests.Session() as session:
    response = session.get(url)
    process_response(response)

with open(file_path, 'wb') as f:
    f.write(content)
```

### 2. Concurrent Downloads

```python
# ✅ Good: ThreadPoolExecutor for parallel downloads
from concurrent.futures import ThreadPoolExecutor

def download_multiple_files(urls: List[str], dest_dir: str) -> None:
    """Download multiple files concurrently."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(download_file, url, dest_dir)
            for url in urls
        ]
        for future in futures:
            future.result()
```

### 3. Lazy Evaluation

```python
# ✅ Good: Generator for memory efficiency
def iter_versions(xml_root: ET.Element) -> Generator[EosVersion, None, None]:
    """Iterate over versions without loading all into memory."""
    for node in xml_root.findall('.//dir[@label]'):
        if label := node.get("label"):
            if version := parse_version(label):
                yield version
```

### 4. Caching

```python
# ✅ Good: Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=32)
def get_software_catalog(token: str) -> ET.Element:
    """Get and cache software catalog XML."""
    response = requests.get(API_URL, headers={"Authorization": token})
    return ET.fromstring(response.content)
```

## Common Anti-Patterns to Avoid

1. ❌ **Hardcoded URLs**: Use constants from `defaults.py`
2. ❌ **String concatenation for paths**: Use `pathlib.Path`
3. ❌ **Ignoring type hints**: Always use proper typing
4. ❌ **Print statements**: Use `rich.console` or logging
5. ❌ **Bare exceptions**: Catch specific exceptions
6. ❌ **Missing tests**: Every new function needs tests
7. ❌ **Poor error messages**: Provide actionable feedback
8. ❌ **Mutable default arguments**: Use `None` and initialize inside function
9. ❌ **Global state**: Use function parameters and return values
10. ❌ **Mixed concerns**: Separate UI, business logic, and data access

## Tooling Integration

### Tox

Run tests across Python versions:

```bash
# Run all tests
tox

# Run specific environment
tox -e py310

# Run linting
tox -e lint

# Run type checking
tox -e type
```

### Pytest

Run tests with coverage:

```bash
# Run all tests with coverage
pytest --cov=eos_downloader --cov-report=term-missing

# Run specific test file
pytest tests/unit/models/test_version.py

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Mypy

Type checking:

```bash
# Check entire project
mypy eos_downloader

# Check specific file
mypy eos_downloader/models/version.py

# Strict mode
mypy --strict eos_downloader
```

### Pre-commit

Automated code quality checks:

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run flake8 --all-files
```

## DevOps & CI/CD

This project follows DevOps best practices with focus on:

### DORA Metrics

- **Deployment Frequency**: Automated releases on main branch
- **Lead Time for Changes**: Fast CI/CD pipeline (<30 min)
- **Change Failure Rate**: Comprehensive test coverage (>80%)
- **Mean Time to Recovery**: Automated rollback capabilities

### GitHub Actions Workflows

- **pr-management.yml**: Run tests, linting, type checking on PRs
- Coverage badge automation
- Automated releases to PyPI
- Docker image publishing to GHCR

### Dedicated Repository Content

- All custom script for repository management shall be stored in the `.github/scripts/` folder
- All documentation related to repository management shall be stored in the `.github/docs/` folder

### Repository language

All documentation and code comments shall be written in English to ensure accessibility to the global developer community.

## Contributing Guidelines

### Before Submitting a PR

- [ ] Type hints on all function signatures
- [ ] Docstrings with examples for public functions
- [ ] Unit tests with >80% coverage
- [ ] All tests passing (`tox`)
- [ ] No linting errors (`tox -e lint`)
- [ ] No type errors (`tox -e type`)
- [ ] Updated documentation if needed
- [ ] Changelog entry added

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(cli): add support for EOS 4.30 versions

- Added parsing for new version format
- Updated XML querier to handle new structure
- Added tests for version parsing

Closes #123
```

## API Integration Details

### Arista API Endpoints

```python
# Defined in defaults.py
DEFAULT_SOFTWARE_FOLDER_TREE = "https://www.arista.com/custom_data/api/cvp/getFolderTree/"
DEFAULT_DOWNLOAD_URL = "https://www.arista.com/custom_data/api/cvp/getDownloadLink/"
DEFAULT_SERVER_SESSION = "https://www.arista.com/custom_data/api/cvp/getSessionCode/"
```

### Authentication Flow

1. User provides API token from arista.com
2. Token passed in request headers
3. API returns session code
4. Session code used for subsequent requests
5. Handle 401 for expired tokens

### XPath Patterns for Version Discovery

```python
# EOS versions
xpath_eos = './/dir[@label="Active Releases"]//dir[@label]'

# CVP versions
xpath_cvp = './/dir[@label="Active Releases"]//dir[@label]'
```

## Integration Points

### EVE-NG

- Default path: `/opt/unetlab/addons/qemu/`
- Requires specific file naming: `veos-lab-{version}/`
- Must set proper permissions: `chmod +x`
- Support for both vEOS and vEOS-lab formats

### Docker

- Import cEOS images to local Docker daemon
- Custom image names and tags supported
- Verify image integrity after import
- Support for both `docker import` and `docker load`

---

## External Resources

### Official Documentation
- **Project Documentation**: [eos-downloader docs](../docs/)
- **Click Framework**: [https://click.palletsprojects.com/](https://click.palletsprojects.com/)
- **Rich Library**: [https://rich.readthedocs.io/](https://rich.readthedocs.io/)
- **Pytest**: [https://docs.pytest.org/](https://docs.pytest.org/)
- **Arista Software Download**: [https://www.arista.com/en/support/software-download](https://www.arista.com/en/support/software-download)

### Arista Resources
- **EOS Documentation**: [https://www.arista.com/en/support/product-documentation](https://www.arista.com/en/support/product-documentation)
- **CVP Documentation**: [https://www.arista.com/en/cg-cv/cv-cloudvision-platform](https://www.arista.com/en/cg-cv/cv-cloudvision-platform)
- **Arista Community**: [https://community.arista.com/](https://community.arista.com/)

### Python Best Practices
- **PEP 8**: [Style Guide for Python Code](https://peps.python.org/pep-0008/)
- **PEP 257**: [Docstring Conventions](https://peps.python.org/pep-0257/)
- **Type Hints**: [PEP 484](https://peps.python.org/pep-0484/)
- **The Hitchhiker's Guide to Python**: [https://docs.python-guide.org/](https://docs.python-guide.org/)

### Testing Resources
- **Pytest Best Practices**: [https://docs.pytest.org/en/latest/goodpractices.html](https://docs.pytest.org/en/latest/goodpractices.html)
- **Test-Driven Development**: [https://testdriven.io/](https://testdriven.io/)
- **Coverage.py**: [https://coverage.readthedocs.io/](https://coverage.readthedocs.io/)

## Quick Reference

### Common Code Patterns

#### Version Operations
```python
from eos_downloader.models.version import EosVersion, CvpVersion

# Parse and validate
version = EosVersion.from_str("4.29.3M")

# Access components
print(version.major)     # 4
print(version.minor)     # 29
print(version.patch)     # 3
print(version.rtype)     # "M"
print(version.branch)    # "4.29"

# Compare versions
v1 = EosVersion.from_str("4.29.3M")
v2 = EosVersion.from_str("4.30.1F")
print(v1 < v2)  # True
print(v1 == EosVersion.from_str("4.29.3M"))  # True

# Sort versions
versions = [
    EosVersion.from_str("4.30.1F"),
    EosVersion.from_str("4.29.3M"),
    EosVersion.from_str("4.29.5M"),
]
sorted_versions = sorted(versions)  # Oldest to newest
```

#### Query API for Versions
```python
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier

# Initialize querier
querier = AristaXmlQuerier(token="your-token-here")

# Get all EOS versions
all_versions = querier.available_public_versions(package="eos")

# Filter by branch
branch_versions = querier.available_public_versions(
    package="eos",
    branch="4.29"
)

# Filter by release type
maintenance_only = querier.available_public_versions(
    package="eos",
    branch="4.29",
    rtype="M"
)

# Get CVP versions
cvp_versions = querier.available_public_versions(package="cvp")

# Get latest version for branch
branches = querier.available_branches(package="eos", latest=True)
```

#### Download Files
```python
from eos_downloader.logics.download import SoftManager
from pathlib import Path

# Initialize download manager
downloader = SoftManager(token="your-token")

# Download EOS image
output_path = downloader.download_eos(
    version="4.29.3M",
    format="64",
    output_dir=Path("/downloads"),
    dry_run=False
)

# Import cEOS to Docker
downloader.import_docker(
    image_path=output_path,
    docker_name="arista/ceos",
    docker_tag="4.29.3M"
)

# Install to EVE-NG
downloader.install_eve_ng(
    image_path=output_path,
    version="4.29.3M"
)
```

#### CLI with Rich
```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Display table
table = Table(title="EOS Versions")
table.add_column("Version", style="cyan")
table.add_column("Type", style="green")
for v in versions:
    table.add_row(str(v), v.rtype)
console.print(table)

# Show progress
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    task = progress.add_task("Downloading...", total=None)
    download_file(url)
    progress.update(task, completed=True)

# Status messages
console.print("[green]✓ Success[/green]")
console.print("[red]✗ Error[/red]")
console.print("[yellow]⚠ Warning[/yellow]")
console.print("[cyan]ℹ Info[/cyan]")
```

### Environment Variables

```bash
# Authentication
export ARISTA_TOKEN="your-api-token-from-arista.com"

# CLI default options (optional)
export ARISTA_GET_EOS_VERSION="4.29.3M"
export ARISTA_GET_EOS_FORMAT="64"
export ARISTA_GET_EOS_OUTPUT="/path/to/downloads"

# Logging level
export ARDL_LOG_LEVEL="debug"  # debug, info, warning, error, critical

# Python environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Common CLI Commands

```bash
# Download EOS image
ardl --token TOKEN get eos --version 4.29.3M --format 64

# Download cEOS and import to Docker
ardl --token TOKEN get eos \
  --version 4.29.3M \
  --format cEOS \
  --docker-name arista/ceos \
  --docker-tag 4.29.3M

# Download vEOS for EVE-NG
ardl --token TOKEN get eos \
  --version 4.29.3M \
  --format vEOS-lab \
  --eve-ng

# Dry-run (simulate without downloading)
ardl --token TOKEN get eos \
  --version 4.29.3M \
  --dry-run

# Get version information
ardl --token TOKEN info eos --branch 4.29
ardl --token TOKEN info eos --branch 4.29 --rtype M
ardl --token TOKEN info cvp

# Debug token validity
ardl --token TOKEN debug token

# Using environment variables
export ARISTA_TOKEN="your-token"
export ARISTA_GET_EOS_VERSION="4.29.3M"
ardl get eos  # Uses env vars
```

### Development Commands

```bash
# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# Run tests
pytest                                    # All tests
pytest tests/unit/                       # Unit tests only
pytest tests/unit/models/test_version.py # Specific file
pytest -k "test_version"                 # Pattern matching
pytest -v                                # Verbose output
pytest -x                                # Stop at first failure
pytest --pdb                             # Debug on failure

# Coverage
pytest --cov=eos_downloader --cov-report=term-missing
pytest --cov=eos_downloader --cov-report=html
open htmlcov/index.html  # View HTML coverage report

# Code quality
tox                     # Run all tox environments
tox -e lint            # Linting only (flake8, pylint)
tox -e type            # Type checking (mypy)
tox -e py310           # Tests on Python 3.10
pre-commit run --all-files  # Run all pre-commit hooks

# Type checking
mypy eos_downloader
mypy --strict eos_downloader

# Formatting
black eos_downloader tests
isort eos_downloader tests

# Build documentation
cd docs
mkdocs serve  # View at http://localhost:8000
mkdocs build  # Build static site
```

### pytest Fixtures Reference

```python
# Built-in pytest fixtures
def test_example(tmp_path, monkeypatch, capsys):
    # tmp_path: Temporary directory (pathlib.Path)
    test_file = tmp_path / "test.txt"

    # monkeypatch: Modify environment, attributes
    monkeypatch.setenv("ARISTA_TOKEN", "test-token")

    # capsys: Capture stdout/stderr
    print("test output")
    captured = capsys.readouterr()
    assert "test output" in captured.out

# Project-specific fixtures (in conftest.py)
def test_download(mock_token, temp_download_dir, mock_arista_xml_response):
    # mock_token: Pre-configured test token
    # temp_download_dir: Temporary download directory
    # mock_arista_xml_response: Mock XML from Arista API
    pass
```

---

**Remember**: This tool is critical for network automation workflows. Prioritize reliability, clear error messages, and comprehensive logging in all contributions.
