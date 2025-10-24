---
applyTo: '**/*.py'
description: 'Python coding standards, best practices, and project-specific conventions for eos-downloader.'
---

# Python Coding Standards for eos-downloader

## Your Mission

As GitHub Copilot working on Python code in **eos-downloader**, you must follow strict Python coding standards, project conventions, and best practices. This ensures code quality, maintainability, and consistency across the codebase.

## Python Version Support

- **Minimum**: Python 3.9
- **Tested**: Python 3.9, 3.10, 3.11
- **Use modern Python features**: Type hints, f-strings, pathlib, dataclasses, async/await where appropriate

## Requirements

Code must be valid and pass without errors or warnings through the following tools:

- black
- mypy
- flake8
- pylint

Configuration to follow for these tools is located in the project root with pre-commit configuration file: `.pre-commit-config.yaml`.

## Code Style

### Docstring format

Code comments must follow docstrings based on the NumPy style.

Example:

```python
# -*- coding: utf-8 -*-
"""Example NumPy style docstrings.

This module demonstrates documentation as specified by the `NumPy
Documentation HOWTO`_. Docstrings may extend over multiple lines. Sections
are created with a section header followed by an underline of equal length.

Example
-------
Examples can be given using either the ``Example`` or ``Examples``
sections. Sections support any reStructuredText formatting, including
literal blocks::

    $ python example_numpy.py


Section breaks are created with two blank lines. Section breaks are also
implicitly created anytime a new section starts. Section bodies *may* be
indented:

Notes
-----
    This is an example of an indented section. It's like any other section,
    but the body is indented to help it stand out from surrounding text.

If a section is indented, then a section break is created by
resuming unindented text.

Attributes
----------
module_level_variable1 : int
    Module level variables may be documented in either the ``Attributes``
    section of the module docstring, or in an inline docstring immediately
    following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.


.. _NumPy Documentation HOWTO:
   https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

"""

def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.

    `PEP 484`_ type annotations are supported. If attribute, parameter, and
    return types are annotated according to `PEP 484`_, they do not need to be
    included in the docstring:

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter.

    Returns
    -------
    bool
        True if successful, False otherwise.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/

    """
```

Reference: https://numpy.org/doc/1.19/docs/howto_document.html


### PEP 8 Compliance

Always follow PEP 8 with these project-specific conventions:

```python
# ✅ Good: PEP 8 compliant
def download_eos_image(
    version: str,
    image_format: str,
    output_dir: Path,
    token: str,
) -> Path:
    """Download an EOS image from Arista server."""
    pass

# ❌ Bad: Non-compliant
def downloadEosImage(version,imageFormat,outputDir,token):  # camelCase, no spaces
    pass
```

### Line Length

- **Maximum**: 120 characters (configured in project)
- **Docstrings**: 100 characters for better readability
- **Comments**: 72 characters

### Import Organization

Always organize imports in this order:

```python
#!/usr/bin/env python
# coding: utf-8 -*-

"""Module docstring."""

# Standard library imports (alphabetically sorted within groups)
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Third-party imports (alphabetically sorted)
import click
import requests
from rich.console import Console
from rich.table import Table

# Local application imports (alphabetically sorted)
from eos_downloader.exceptions import DownloadError, TokenExpiredError
from eos_downloader.logics.download import SoftManager
from eos_downloader.models.version import EosVersion
```

## Type Hints

### Mandatory Type Hints

Always provide type hints for:
- Function parameters
- Function return types
- Class attributes
- Module-level variables

```python
# ✅ Good: Complete type hints
from typing import Optional, List, Dict, Any
from pathlib import Path

def process_versions(
    versions: List[EosVersion],
    filter_branch: Optional[str] = None,
    output_format: str = "json",
) -> Dict[str, Any]:
    """Process and format version information.

    Parameters
    ----------
    versions : List[EosVersion]
        List of EOS versions to process
    filter_branch : Optional[str], optional
        Branch to filter by, by default None
    output_format : str, optional
        Output format (json, text, fancy), by default "json"

    Returns
    -------
    Dict[str, Any]
        Processed version data
    """
    results: Dict[str, Any] = {}
    filtered: List[EosVersion] = [
        v for v in versions
        if filter_branch is None or v.branch == filter_branch
    ]
    return results

# ❌ Bad: Missing type hints
def process_versions(versions, filter_branch=None):
    results = {}
    return results
```

### Use Modern Type Hints

```python
# ✅ Good: Modern Python 3.9+ type hints
from typing import Optional

def get_version(version_str: str) -> Optional[EosVersion]:
    """Get version or None if not found."""
    pass

# For Python 3.10+ you can use the | operator
def get_version(version_str: str) -> EosVersion | None:
    """Get version or None if not found."""
    pass

# ✅ Good: Generic types
from typing import Dict, List, Tuple

def get_mapping() -> Dict[str, List[str]]:
    """Return mapping of formats to extensions."""
    return {"64": [".swi"], "cEOS": [".tar", ".tar.gz"]}

# ❌ Bad: Using dict, list without type parameters
def get_mapping() -> dict:
    return {"64": [".swi"]}
```

## Documentation Standards

### Module Docstrings

Every module must have a comprehensive docstring:

```python
#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Module for managing EOS image downloads.

This module provides functionality to download, validate, and manage
Arista EOS software images from the official Arista repository.

Classes
-------
EosDownloader
    Main class for downloading EOS images
SoftManager
    Manages software download operations

Functions
---------
download_eos_image
    Download a specific EOS image version
validate_checksum
    Validate downloaded file integrity
generate_filename
    Generate standard filename for EOS images

Examples
--------
Basic usage:

>>> from eos_downloader.logics.download import SoftManager
>>> downloader = SoftManager()
>>> downloader.download_file(url, output_dir, filename)

With authentication:

>>> token = os.environ["ARISTA_TOKEN"]
>>> downloader = EosDownloader(token=token)
>>> image_path = downloader.download("4.29.3M", format="64")

Notes
-----
Requires valid Arista customer portal credentials.

See Also
--------
eos_downloader.logics.arista_xml_server : XML API interaction
eos_downloader.models.version : Version parsing and validation
"""
```

### Function/Method Docstrings

Use NumPy style docstrings:

```python
def download_eos_image(
    version: str,
    image_format: str,
    output_dir: Path,
    token: str,
    verify_checksum: bool = True,
) -> Path:
    """Download an EOS image from Arista's software repository.

    This function authenticates with Arista's API, locates the specified
    EOS version and format, downloads it to the specified directory, and
    optionally verifies the file integrity using checksums.

    Parameters
    ----------
    version : str
        EOS version in format MAJOR.MINOR.PATCH[TYPE] (e.g., "4.29.3M")
    image_format : str
        Image format. One of: "64", "vEOS", "cEOS", "INT"
    output_dir : Path
        Directory where the image will be saved
    token : str
        Arista API authentication token from arista.com
    verify_checksum : bool, optional
        Whether to verify file integrity after download, by default True

    Returns
    -------
    Path
        Path to the downloaded image file

    Raises
    ------
    TokenExpiredError
        If the authentication token has expired or is invalid
    DownloadError
        If the download fails due to network or server errors
    ValueError
        If the version format is invalid or image_format is not supported
    FileNotFoundError
        If the output directory does not exist and cannot be created

    Examples
    --------
    Download a specific version:

    >>> image_path = download_eos_image(
    ...     version="4.29.3M",
    ...     image_format="64",
    ...     output_dir=Path("/downloads"),
    ...     token=os.environ["ARISTA_TOKEN"]
    ... )
    >>> print(f"Downloaded to: {image_path}")
    Downloaded to: /downloads/EOS-4.29.3M.swi

    Download without checksum verification:

    >>> image_path = download_eos_image(
    ...     version="4.30.1F",
    ...     image_format="cEOS",
    ...     output_dir=Path("/tmp"),
    ...     token=token,
    ...     verify_checksum=False
    ... )

    Notes
    -----
    - Requires a valid Arista customer account token
    - Large files may take significant time to download
    - Network interruptions may cause download failures
    - The function will create the output directory if it doesn't exist

    See Also
    --------
    validate_checksum : Verify file integrity after download
    generate_filename : Generate standard filename for the image
    """
    # Implementation
    pass
```

### Class Docstrings

```python
class EosDownloader:
    """Download and manage Arista EOS software images.

    This class provides a high-level interface for downloading EOS images
    from Arista's software repository. It handles authentication, version
    discovery, and download management.

    Parameters
    ----------
    token : str
        Arista API authentication token
    timeout : int, optional
        Request timeout in seconds, by default 30
    verify_ssl : bool, optional
        Whether to verify SSL certificates, by default True

    Attributes
    ----------
    token : str
        The authentication token
    session : requests.Session
        Persistent HTTP session for API calls
    timeout : int
        Request timeout value

    Examples
    --------
    Basic usage:

    >>> downloader = EosDownloader(token=os.environ["ARISTA_TOKEN"])
    >>> versions = downloader.get_available_versions(branch="4.29")
    >>> image = downloader.download(version="4.29.3M", format="64")

    With custom timeout:

    >>> downloader = EosDownloader(
    ...     token=token,
    ...     timeout=60,
    ...     verify_ssl=True
    ... )

    Notes
    -----
    Always use context managers or explicitly close the session when done.

    See Also
    --------
    SoftManager : Lower-level download management
    AristaXmlQuerier : Version discovery and querying
    """

    def __init__(
        self,
        token: str,
        timeout: int = 30,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the EOS downloader."""
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
```

## Error Handling

### Use Project-Specific Exceptions

```python
# ✅ Good: Specific exception handling
from eos_downloader.exceptions import (
    TokenExpiredError,
    DownloadError,
    AuthenticationError,
)

def download_file(url: str, token: str) -> bytes:
    """Download file with proper error handling."""
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        response.raise_for_status()
        return response.content

    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise TokenExpiredError(
                "API token expired. Please regenerate at arista.com"
            ) from e
        elif e.response.status_code == 404:
            raise DownloadError(
                f"Resource not found: {url}"
            ) from e
        else:
            raise DownloadError(
                f"HTTP error {e.response.status_code}: {e}"
            ) from e

    except requests.Timeout as e:
        raise DownloadError(
            f"Download timeout after 30s: {url}"
        ) from e

    except requests.RequestException as e:
        raise DownloadError(
            f"Network error during download: {e}"
        ) from e

# ❌ Bad: Generic exception handling
def download_file_bad(url, token):
    try:
        response = requests.get(url)
        return response.content
    except Exception as e:  # Too broad
        print(f"Error: {e}")  # Poor error handling
        return None  # Silent failure
```

### Exception Chaining

Always use `from e` to preserve exception context:

```python
# ✅ Good: Exception chaining
try:
    data = parse_xml(content)
except ET.ParseError as e:
    raise ValueError(f"Invalid XML format: {e}") from e

# ❌ Bad: Lost exception context
try:
    data = parse_xml(content)
except ET.ParseError as e:
    raise ValueError(f"Invalid XML format")  # Lost original error
```

## Logging

### Use Structured Logging

```python
# ✅ Good: Structured logging with context
import logging

logger = logging.getLogger(__name__)

def download_file(url: str, output_path: Path) -> None:
    """Download file with proper logging."""
    logger.info(
        "Starting file download",
        extra={
            "url": url,
            "output_path": str(output_path),
            "operation": "download_start"
        }
    )

    try:
        # Download logic
        size = download_logic(url, output_path)

        logger.info(
            "Download completed successfully",
            extra={
                "url": url,
                "output_path": str(output_path),
                "size_bytes": size,
                "operation": "download_complete"
            }
        )

    except DownloadError as e:
        logger.error(
            "Download failed",
            extra={
                "url": url,
                "error": str(e),
                "operation": "download_failed"
            },
            exc_info=True
        )
        raise

# ❌ Bad: Print statements and poor logging
def download_file_bad(url, output_path):
    print(f"Downloading {url}")  # Should use logging
    try:
        download_logic(url, output_path)
        print("Done")  # No context
    except Exception as e:
        print(f"Error: {e}")  # No structured data
```

### Log Levels

Use appropriate log levels:

```python
# DEBUG: Detailed diagnostic information
logger.debug("XML response: %s", xml_content[:100])

# INFO: Normal operations and confirmations
logger.info("Version 4.29.3M found in catalog")

# WARNING: Something unexpected but handled
logger.warning("Token expires in 1 hour")

# ERROR: Error that prevents operation
logger.error("Failed to download file", exc_info=True)

# CRITICAL: System-level failure
logger.critical("Unable to connect to Arista API")
```

## Path Handling

### Always Use pathlib

```python
from pathlib import Path

# ✅ Good: Using pathlib
def save_file(content: bytes, output_dir: Path, filename: str) -> Path:
    """Save file using pathlib."""
    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Build path safely
    output_path = output_dir / safe_filename

    # Write file
    output_path.write_bytes(content)

    return output_path

# ❌ Bad: String concatenation
def save_file_bad(content, output_dir, filename):
    # Path traversal risk
    output_path = output_dir + "/" + filename

    # No directory creation
    with open(output_path, 'wb') as f:
        f.write(content)

    return output_path
```

### File Operations

```python
# ✅ Good: Safe file operations with context managers
from pathlib import Path

def read_config(config_path: Path) -> Dict[str, Any]:
    """Read configuration file safely."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if not config_path.is_file():
        raise ValueError(f"Path is not a file: {config_path}")

    try:
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config: {e}") from e

# ✅ Good: Writing files safely
def write_data(data: Dict[str, Any], output_path: Path) -> None:
    """Write data to file safely."""
    # Create parent directories
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write atomically (temp file + rename)
    temp_path = output_path.with_suffix('.tmp')
    try:
        with temp_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        temp_path.replace(output_path)
    except Exception:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise
```

## Resource Management

### Always Use Context Managers

```python
# ✅ Good: Context managers for resource cleanup
def download_with_session(urls: List[str]) -> List[bytes]:
    """Download multiple files using session."""
    results = []

    with requests.Session() as session:
        session.headers.update(DEFAULT_REQUEST_HEADERS)

        for url in urls:
            response = session.get(url)
            response.raise_for_status()
            results.append(response.content)

    return results

# ✅ Good: File handling
def process_large_file(file_path: Path) -> int:
    """Process large file line by line."""
    line_count = 0

    with file_path.open('r', encoding='utf-8') as f:
        for line in f:
            process_line(line)
            line_count += 1

    return line_count

# ❌ Bad: Manual resource management
def download_with_session_bad(urls):
    session = requests.Session()
    results = []
    for url in urls:
        response = session.get(url)
        results.append(response.content)
    session.close()  # Might not be called if exception occurs
    return results
```

## Performance Best Practices

### Use Lazy Evaluation

```python
from typing import Generator

# ✅ Good: Generator for memory efficiency
def iter_versions(
    xml_root: ET.Element
) -> Generator[EosVersion, None, None]:
    """Iterate over versions without loading all into memory."""
    for node in xml_root.findall('.//dir[@label]'):
        if label := node.get("label"):
            try:
                version = EosVersion.from_str(label)
                yield version
            except ValueError:
                # Skip invalid versions
                continue

# ❌ Bad: Load everything into memory
def get_all_versions(xml_root):
    versions = []
    for node in xml_root.findall('.//dir[@label]'):
        label = node.get("label")
        if label:
            try:
                versions.append(EosVersion.from_str(label))
            except ValueError:
                pass
    return versions  # High memory usage for large datasets
```

### Use Caching Appropriately

```python
from functools import lru_cache

# ✅ Good: Cache expensive operations
@lru_cache(maxsize=128)
def get_software_catalog(token: str) -> ET.Element:
    """Get and cache software catalog XML.

    Cached per token to avoid redundant API calls.
    """
    response = requests.get(
        CATALOG_URL,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return ET.fromstring(response.content)

# ✅ Good: Cache validation results
@lru_cache(maxsize=1024)
def validate_version_format(version: str) -> bool:
    """Validate version format (cached for performance)."""
    return bool(EosVersion.regex_version.match(version))
```

### Concurrent Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable

# ✅ Good: Parallel downloads
def download_multiple_files(
    urls: List[str],
    dest_dir: Path,
    max_workers: int = 4
) -> List[Path]:
    """Download multiple files concurrently.

    Parameters
    ----------
    urls : List[str]
        URLs to download
    dest_dir : Path
        Destination directory
    max_workers : int, optional
        Maximum number of concurrent downloads, by default 4

    Returns
    -------
    List[Path]
        Paths to downloaded files
    """
    results: List[Path] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_url = {
            executor.submit(download_file, url, dest_dir): url
            for url in urls
        }

        # Process completed downloads
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Downloaded: {url}")
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")

    return results
```

## Testing Guidelines

### Use Pytest

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# ✅ Good: Well-structured test class
class TestEosDownloader:
    """Test suite for EOS downloader functionality."""

    @pytest.fixture
    def mock_token(self) -> str:
        """Provide a mock API token for testing."""
        return "test-token-abc123xyz"

    @pytest.fixture
    def temp_output_dir(self, tmp_path: Path) -> Path:
        """Provide a temporary output directory."""
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()
        return output_dir

    @pytest.fixture
    def mock_arista_response(self) -> str:
        """Provide mock XML response from Arista API."""
        return """
        <folder>
            <dir label="Active Releases">
                <dir label="4.29.3M">
                    <file>EOS-4.29.3M.swi</file>
                </dir>
            </dir>
        </folder>
        """

    def test_version_parsing_valid(self) -> None:
        """Test parsing of valid EOS version strings."""
        version = EosVersion.from_str("4.29.3M")

        assert version.major == 4
        assert version.minor == 29
        assert version.patch == 3
        assert version.rtype == "M"
        assert version.branch == "4.29"

    def test_version_parsing_invalid(self) -> None:
        """Test that invalid version strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version format"):
            EosVersion.from_str("invalid-version")

    @pytest.mark.parametrize(
        "version_str,expected_major,expected_minor,expected_patch,expected_rtype",
        [
            ("4.29.3M", 4, 29, 3, "M"),
            ("4.30.1F", 4, 30, 1, "F"),
            ("4.28.10M", 4, 28, 10, "M"),
            ("4.31.0F", 4, 31, 0, "F"),
        ]
    )
    def test_version_parsing_parametrized(
        self,
        version_str: str,
        expected_major: int,
        expected_minor: int,
        expected_patch: int,
        expected_rtype: str
    ) -> None:
        """Test version parsing with multiple inputs."""
        version = EosVersion.from_str(version_str)

        assert version.major == expected_major
        assert version.minor == expected_minor
        assert version.patch == expected_patch
        assert version.rtype == expected_rtype

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
        mock_response.content = b"fake EOS image content"
        mock_response.headers = {"Content-Length": "23"}
        mock_get.return_value = mock_response

        # Execute
        downloader = SoftManager()
        result = downloader.download_file(
            url="https://example.com/EOS-4.29.3M.swi",
            output_dir=temp_output_dir,
            filename="EOS-4.29.3M.swi"
        )

        # Assert
        assert result.exists()
        assert result.name == "EOS-4.29.3M.swi"
        assert result.read_bytes() == b"fake EOS image content"
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_download_with_expired_token(
        self,
        mock_get: Mock,
        mock_token: str,
        temp_output_dir: Path
    ) -> None:
        """Test download fails gracefully with expired token."""
        # Setup mock to return 401
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        # Execute and assert
        downloader = SoftManager()
        with pytest.raises(TokenExpiredError):
            downloader.download_file(
                url="https://example.com/file.swi",
                output_dir=temp_output_dir,
                filename="test.swi"
            )
```

## Code Quality Tools

### Configuration

The project uses these tools (configured in `pyproject.toml`):

- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pylint**: Additional linting
- **isort**: Import sorting

### Run Before Committing

```bash
# Format code
black eos_downloader/

# Sort imports
isort eos_downloader/

# Type check
mypy eos_downloader/

# Lint
flake8 eos_downloader/
pylint eos_downloader/

# Run all tests
pytest --cov=eos_downloader

# Or use tox to run everything
tox
```

## Common Anti-Patterns to Avoid

1. ❌ **Mutable default arguments**
```python
# ❌ Bad
def add_item(item, items=[]):  # Shared between calls!
    items.append(item)
    return items

# ✅ Good
def add_item(item: str, items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

2. ❌ **Catching Exception without context**
```python
# ❌ Bad
try:
    risky_operation()
except Exception:
    pass  # Silent failure

# ✅ Good
try:
    risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

3. ❌ **Not using context managers**
```python
# ❌ Bad
f = open("file.txt")
data = f.read()
f.close()

# ✅ Good
with open("file.txt") as f:
    data = f.read()
```

4. ❌ **String formatting with %**
```python
# ❌ Bad
message = "Version %s downloaded" % version

# ✅ Good
message = f"Version {version} downloaded"
```

5. ❌ **Not using enumerate**
```python
# ❌ Bad
for i in range(len(items)):
    print(i, items[i])

# ✅ Good
for i, item in enumerate(items):
    print(i, item)
```

## Project-Specific Conventions

### Version Handling

Always use the version models:
```python
from eos_downloader.models.version import EosVersion, CvpVersion

# Parse version
version = EosVersion.from_str("4.29.3M")

# Access properties
print(version.major)   # 4
print(version.branch)  # "4.29"
print(version.rtype)   # "M"
```

### Constants

Use constants from `defaults.py`:
```python
from eos_downloader.defaults import (
    DEFAULT_SOFTWARE_FOLDER_TREE,
    DEFAULT_DOWNLOAD_URL,
    DEFAULT_REQUEST_HEADERS,
    EVE_QEMU_FOLDER_PATH,
)
```

### CLI Commands

Follow the standard pattern for Click commands (see `.github/copilot-instructions.md`).

---

**Remember**: Code quality, type safety, and comprehensive testing are priorities in this project. Every piece of code should be production-ready, well-documented, and thoroughly tested.
