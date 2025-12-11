---
applyTo: 'tests/**/*.py'
description: 'Comprehensive testing guidelines using pytest, including fixtures, mocking, parametrization, and coverage best practices for eos-downloader.'
---

# Testing Guidelines for eos-downloader

## Your Mission

As GitHub Copilot working on tests for **eos-downloader**, you must create comprehensive, maintainable, and effective tests using pytest. Every piece of code must be thoroughly tested to ensure reliability and prevent regressions.

## Testing Philosophy

### Test-Driven Development (TDD) Principles

1. **Write tests first** (when possible) to clarify requirements
2. **Test behavior, not implementation** to allow refactoring
3. **Keep tests simple and readable** - they're documentation
4. **Aim for high coverage** (>80%) but focus on meaningful tests
5. **Test edge cases and error conditions** explicitly

### Testing Pyramid

```
       /\          E2E Tests (Few)
      /  \         - Full integration
     /____\        - Slow, expensive
    /      \
   /        \      Integration Tests (Some)
  /__________\     - Multiple components
 /            \    - Medium speed
/______________\   Unit Tests (Many)
                   - Single functions/classes
                   - Fast, cheap
```

## Project Test Structure

```
tests/
├── __init__.py                 # Test package init
├── conftest.py                 # Shared fixtures
├── data/                       # Test data files
│   └── arista_test.xml        # Sample XML responses
├── lib/                        # Test utilities
│   ├── fixtures.py            # Common fixtures
│   ├── helpers.py             # Test helper functions
│   └── dataset.py             # Test data generators
├── unit/                       # Unit tests
│   ├── cli/                   # CLI tests
│   │   ├── test_cli.py
│   │   └── test_commands.py
│   ├── logics/                # Logic tests
│   │   ├── test_arista_xml_server.py
│   │   └── test_download.py
│   └── models/                # Model tests
│       ├── test_version.py
│       └── test_data.py
└── integration/               # Integration tests
    └── test_full_download.py
```

## Pytest Configuration

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = [
    "-ra",                    # Show summary of all test outcomes
    "--strict-markers",       # Treat unregistered markers as errors
    "--strict-config",        # Treat config issues as errors
    "--showlocals",          # Show local variables in tracebacks
    "--tb=short",            # Short traceback format
    "--cov=eos_downloader",  # Coverage for main package
    "--cov-report=term-missing",  # Show missing lines
    "--cov-report=html",     # Generate HTML report
    "--cov-branch",          # Branch coverage
]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "requires_token: marks tests that require Arista API token",
]
```

## Writing Effective Tests

### Test Naming Convention

```python
# ✅ Good: Descriptive test names
def test_eos_version_parsing_with_valid_format():
    """Test that valid EOS version strings are parsed correctly."""
    pass

def test_eos_version_parsing_raises_error_with_invalid_format():
    """Test that invalid version strings raise ValueError."""
    pass

def test_download_file_creates_output_directory_if_missing():
    """Test that download creates parent directories automatically."""
    pass

# ❌ Bad: Non-descriptive names
def test_version():
    pass

def test_download():
    pass

def test_case1():
    pass
```

### Test Structure: Arrange-Act-Assert (AAA)

```python
import pytest
from pathlib import Path
from eos_downloader.models.version import EosVersion

def test_eos_version_comparison():
    """Test that EOS versions can be compared correctly."""
    # Arrange - Set up test data
    version_1 = EosVersion.from_str("4.29.3M")
    version_2 = EosVersion.from_str("4.30.1F")
    version_3 = EosVersion.from_str("4.29.3M")

    # Act - Perform the operations
    is_less_than = version_1 < version_2
    is_equal = version_1 == version_3
    is_greater_than = version_2 > version_1

    # Assert - Verify results
    assert is_less_than, "4.29.3M should be less than 4.30.1F"
    assert is_equal, "Same versions should be equal"
    assert is_greater_than, "4.30.1F should be greater than 4.29.3M"
```

## Fixtures

### Basic Fixtures

```python
# conftest.py or in test file
import pytest
from pathlib import Path
from typing import Generator

@pytest.fixture
def mock_token() -> str:
    """Provide a mock API token for testing.

    Returns
    -------
    str
        Mock token string
    """
    return "test-token-abc123xyz789"

@pytest.fixture
def temp_download_dir(tmp_path: Path) -> Path:
    """Provide a temporary download directory.

    Uses pytest's built-in tmp_path fixture.

    Returns
    -------
    Path
        Temporary directory path
    """
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    return download_dir

@pytest.fixture
def sample_eos_version() -> str:
    """Provide a sample EOS version string.

    Returns
    -------
    str
        Sample version string
    """
    return "4.29.3M"
```

### Fixture Scope

```python
# Function scope (default) - created/destroyed for each test
@pytest.fixture(scope="function")
def temp_file(tmp_path: Path) -> Path:
    """Create temporary file for single test."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path

# Class scope - shared across test class
@pytest.fixture(scope="class")
def database_connection():
    """Shared database connection for test class."""
    conn = create_connection()
    yield conn
    conn.close()

# Module scope - shared across test module
@pytest.fixture(scope="module")
def expensive_resource():
    """Expensive resource shared across module."""
    resource = setup_expensive_resource()
    yield resource
    teardown_expensive_resource(resource)

# Session scope - shared across entire test session
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Test data directory shared across session."""
    return Path(__file__).parent / "data"
```

### Parametrized Fixtures

```python
@pytest.fixture(params=["4.29.3M", "4.30.1F", "4.28.10M"])
def eos_version_string(request) -> str:
    """Provide multiple EOS version strings.

    Test will run once for each parameter.
    """
    return request.param

def test_version_parsing_multiple(eos_version_string: str):
    """Test version parsing with multiple version strings."""
    version = EosVersion.from_str(eos_version_string)
    assert version is not None
    assert isinstance(version, EosVersion)
```

### Fixture Factories

```python
from typing import Callable

@pytest.fixture
def make_eos_version() -> Callable[[int, int, int, str], EosVersion]:
    """Factory fixture to create EOS versions on demand.

    Returns
    -------
    Callable
        Function to create EosVersion instances

    Examples
    --------
    >>> def test_versions(make_eos_version):
    ...     v1 = make_eos_version(4, 29, 3, "M")
    ...     v2 = make_eos_version(4, 30, 1, "F")
    ...     assert v1 < v2
    """
    def _make_version(
        major: int,
        minor: int,
        patch: int,
        rtype: str
    ) -> EosVersion:
        return EosVersion(
            major=major,
            minor=minor,
            patch=patch,
            rtype=rtype
        )
    return _make_version

def test_version_factory(make_eos_version):
    """Test using version factory fixture."""
    version = make_eos_version(4, 29, 3, "M")
    assert version.branch == "4.29"
```

### Complex Fixtures with Setup/Teardown

```python
@pytest.fixture
def mock_arista_api(tmp_path: Path) -> Generator[dict, None, None]:
    """Mock Arista API with setup and teardown.

    Yields
    ------
    dict
        Mock API configuration

    Examples
    --------
    >>> def test_api(mock_arista_api):
    ...     token = mock_arista_api["token"]
    ...     base_url = mock_arista_api["base_url"]
    """
    # Setup
    cache_dir = tmp_path / "api_cache"
    cache_dir.mkdir()

    config = {
        "token": "test-token",
        "base_url": "https://test.arista.com",
        "cache_dir": cache_dir,
    }

    # Provide fixture
    yield config

    # Teardown
    # Clean up cache
    for file in cache_dir.glob("*"):
        file.unlink()
    cache_dir.rmdir()
```

## Mocking & Patching

### Basic Mocking with unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock, call
import requests

def test_download_with_mock():
    """Test download function with mocked requests."""
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake file content"
    mock_response.headers = {"Content-Length": "17"}

    # Mock the get method
    with patch('requests.get', return_value=mock_response) as mock_get:
        # Test the function
        result = download_file("https://example.com/file.swi")

        # Verify mock was called correctly
        mock_get.assert_called_once_with("https://example.com/file.swi")
        assert result == b"fake file content"
```

### Patching Objects and Methods

```python
from unittest.mock import patch
from pathlib import Path

@patch('eos_downloader.logics.download.requests.Session')
def test_download_with_session(mock_session_class):
    """Test download using session with patched Session class."""
    # Setup mock session
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"test content"
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Test function
    downloader = SoftManager()
    result = downloader.download_with_session("https://example.com/file")

    # Verify
    mock_session.get.assert_called_once()
    assert result == b"test content"

@patch('pathlib.Path.mkdir')
@patch('pathlib.Path.write_bytes')
def test_save_file(mock_write, mock_mkdir, tmp_path):
    """Test file saving with patched Path methods."""
    output_path = tmp_path / "test.swi"
    content = b"test content"

    save_file(content, output_path)

    # Verify mkdir was called
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Verify write_bytes was called
    mock_write.assert_called_once_with(content)
```

### Mocking External APIs

```python
@pytest.fixture
def mock_arista_xml_response() -> str:
    """Provide mock XML response from Arista API.

    Returns
    -------
    str
        Mock XML content
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
    <folder>
        <dir label="EOS">
            <dir label="Active Releases">
                <dir label="4.29">
                    <dir label="4.29.3M">
                        <dir label="EOS-4.29.3M">
                            <file>EOS-4.29.3M.swi</file>
                        </dir>
                    </dir>
                </dir>
            </dir>
        </dir>
    </folder>
    """

@patch('requests.get')
def test_version_discovery(mock_get, mock_arista_xml_response, mock_token):
    """Test version discovery from Arista API."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = mock_arista_xml_response
    mock_get.return_value = mock_response

    # Test
    from eos_downloader.logics.arista_xml_server import AristaXmlQuerier
    querier = AristaXmlQuerier(token=mock_token)
    versions = querier.available_public_versions(package="eos")

    # Verify
    assert len(versions) > 0
    assert any(str(v) == "4.29.3M" for v in versions)
    mock_get.assert_called_once()
```

### Mock Side Effects

```python
from unittest.mock import Mock

def test_retry_on_network_error():
    """Test that download retries on network errors."""
    # Mock that fails twice then succeeds
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"success"

    mock_get = Mock()
    mock_get.side_effect = [
        requests.RequestException("Network error"),
        requests.RequestException("Network error"),
        mock_response,
    ]

    with patch('requests.get', mock_get):
        result = download_with_retry("https://example.com/file")

        # Verify it tried 3 times
        assert mock_get.call_count == 3
        assert result == b"success"
```

### Mocking File System

```python
from unittest.mock import mock_open, patch

def test_read_config_file():
    """Test reading configuration file."""
    mock_content = '{"token": "test-token", "output": "/tmp"}'

    with patch('builtins.open', mock_open(read_data=mock_content)):
        config = read_config("config.json")

        assert config["token"] == "test-token"
        assert config["output"] == "/tmp"

def test_write_log_file():
    """Test writing to log file."""
    mock_file = mock_open()

    with patch('builtins.open', mock_file):
        write_log("test.log", "log message")

        # Verify file was opened for writing
        mock_file.assert_called_once_with("test.log", "a")

        # Verify content was written
        handle = mock_file()
        handle.write.assert_called_once_with("log message\n")
```

## Parametrization

### Basic Parametrization

```python
import pytest
from eos_downloader.models.version import EosVersion

@pytest.mark.parametrize(
    "version_str,expected_major,expected_minor,expected_patch,expected_rtype",
    [
        ("4.29.3M", 4, 29, 3, "M"),
        ("4.30.1F", 4, 30, 1, "F"),
        ("4.28.10M", 4, 28, 10, "M"),
        ("4.31.0F", 4, 31, 0, "F"),
    ]
)
def test_version_parsing(
    version_str: str,
    expected_major: int,
    expected_minor: int,
    expected_patch: int,
    expected_rtype: str
):
    """Test EOS version parsing with multiple inputs."""
    version = EosVersion.from_str(version_str)

    assert version.major == expected_major
    assert version.minor == expected_minor
    assert version.patch == expected_patch
    assert version.rtype == expected_rtype
```

### Parametrize with IDs

```python
@pytest.mark.parametrize(
    "version_str,is_valid",
    [
        ("4.29.3M", True),
        ("4.30.1F", True),
        ("invalid", False),
        ("4.29", False),
        ("4.29.3.4M", False),
    ],
    ids=[
        "valid_maintenance",
        "valid_feature",
        "invalid_format",
        "missing_patch",
        "too_many_parts",
    ]
)
def test_version_validation(version_str: str, is_valid: bool):
    """Test version validation with various inputs."""
    if is_valid:
        version = EosVersion.from_str(version_str)
        assert version is not None
    else:
        with pytest.raises(ValueError):
            EosVersion.from_str(version_str)
```

### Multiple Parametrize Decorators

```python
@pytest.mark.parametrize("version", ["4.29.3M", "4.30.1F"])
@pytest.mark.parametrize("format", ["64", "vEOS", "cEOS"])
def test_filename_generation(version: str, format: str):
    """Test filename generation for all version/format combinations.

    Creates 6 test cases (2 versions × 3 formats).
    """
    filename = generate_filename(version, format)

    assert version in filename
    assert filename.endswith(get_extension(format))
```

### Parametrize from External Data

```python
import json
from pathlib import Path

def load_test_cases():
    """Load test cases from JSON file."""
    test_data_file = Path(__file__).parent / "data" / "test_cases.json"
    with test_data_file.open() as f:
        return json.load(f)

@pytest.mark.parametrize(
    "test_case",
    load_test_cases(),
    ids=lambda tc: tc["name"]
)
def test_from_file(test_case):
    """Test cases loaded from external file."""
    version_str = test_case["input"]
    expected = test_case["expected"]

    version = EosVersion.from_str(version_str)
    assert str(version) == expected
```

## Testing Exceptions

### Basic Exception Testing

```python
import pytest
from eos_downloader.exceptions import TokenExpiredError, DownloadError

def test_invalid_version_raises_error():
    """Test that invalid version raises ValueError."""
    with pytest.raises(ValueError):
        EosVersion.from_str("invalid-version")

def test_expired_token_raises_error():
    """Test that expired token raises TokenExpiredError."""
    with pytest.raises(TokenExpiredError):
        download_file("https://example.com/file", token="expired")
```

### Testing Exception Messages

```python
def test_invalid_version_error_message():
    """Test that error message is informative."""
    with pytest.raises(ValueError, match="Invalid version format"):
        EosVersion.from_str("invalid")

def test_missing_file_error_message():
    """Test that file not found error is clear."""
    with pytest.raises(
        FileNotFoundError,
        match=r"File not found: /nonexistent/path"
    ):
        open_config_file("/nonexistent/path")
```

### Testing Exception Chaining

```python
def test_download_error_chain():
    """Test that exceptions are properly chained."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(DownloadError) as exc_info:
            download_file("https://example.com/file")

        # Verify exception chain
        assert isinstance(exc_info.value.__cause__, requests.RequestException)
        assert "Network error" in str(exc_info.value.__cause__)
```

## Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_download():
    """Test asynchronous download function."""
    result = await async_download("https://example.com/file")
    assert result is not None

@pytest.fixture
def event_loop():
    """Provide event loop for async tests."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
```

## Coverage Best Practices

### Measuring Coverage

```bash
# Run with coverage
pytest --cov=eos_downloader --cov-report=term-missing

# Generate HTML report
pytest --cov=eos_downloader --cov-report=html

# Check specific module
pytest --cov=eos_downloader.models.version --cov-report=term

# Fail if coverage below threshold
pytest --cov=eos_downloader --cov-fail-under=80
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["eos_downloader"]
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

### Ignoring Code from Coverage

```python
def debug_function():  # pragma: no cover
    """Debug function not tested."""
    print("Debug information")

def production_function():
    """Production function with coverage."""
    if DEBUG:  # pragma: no cover
        debug_function()

    return process_data()
```

## Test Organization

### Test Class Organization

```python
class TestEosVersion:
    """Test suite for EosVersion class."""

    class TestParsing:
        """Tests for version parsing."""

        def test_valid_maintenance_release(self):
            """Test parsing valid maintenance release."""
            version = EosVersion.from_str("4.29.3M")
            assert version.rtype == "M"

        def test_valid_feature_release(self):
            """Test parsing valid feature release."""
            version = EosVersion.from_str("4.30.1F")
            assert version.rtype == "F"

        def test_invalid_format_raises_error(self):
            """Test invalid format raises ValueError."""
            with pytest.raises(ValueError):
                EosVersion.from_str("invalid")

    class TestComparison:
        """Tests for version comparison."""

        def test_less_than(self):
            """Test version less than comparison."""
            v1 = EosVersion.from_str("4.29.3M")
            v2 = EosVersion.from_str("4.30.1F")
            assert v1 < v2

        def test_equality(self):
            """Test version equality."""
            v1 = EosVersion.from_str("4.29.3M")
            v2 = EosVersion.from_str("4.29.3M")
            assert v1 == v2

    class TestSerialization:
        """Tests for version serialization."""

        def test_to_string(self):
            """Test converting version to string."""
            version = EosVersion(major=4, minor=29, patch=3, rtype="M")
            assert str(version) == "4.29.3M"

        def test_to_dict(self):
            """Test converting version to dictionary."""
            version = EosVersion.from_str("4.29.3M")
            data = version.to_dict()
            assert data["major"] == 4
```

## Markers for Test Organization

```python
import pytest

@pytest.mark.unit
def test_version_parsing():
    """Unit test for version parsing."""
    pass

@pytest.mark.integration
def test_full_download_workflow():
    """Integration test for complete download."""
    pass

@pytest.mark.slow
def test_large_file_download():
    """Slow test for large file download."""
    pass

@pytest.mark.requires_token
def test_api_authentication():
    """Test that requires real API token."""
    pass

# Run specific markers
# pytest -m unit
# pytest -m "not slow"
# pytest -m "integration and not requires_token"
```

## Testing CLI Commands

```python
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl

def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(ardl, ["--help"])

    assert result.exit_code == 0
    assert "Arista Network Download CLI" in result.output

def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(ardl, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output.lower()

def test_cli_get_eos_command(tmp_path):
    """Test get eos command with mocked download."""
    runner = CliRunner()

    with patch('eos_downloader.logics.download.SoftManager.download_file'):
        result = runner.invoke(
            ardl,
            [
                "--token", "test-token",
                "get", "eos",
                "--version", "4.29.3M",
                "--format", "64",
                "--output", str(tmp_path),
                "--dry-run"
            ]
        )

        assert result.exit_code == 0
```

## Best Practices Summary

### ✅ DO

1. **Write descriptive test names** that explain what is being tested
2. **Use fixtures** for common setup and teardown
3. **Parametrize** tests to cover multiple cases efficiently
4. **Mock external dependencies** (API calls, file system, network)
5. **Test error conditions** explicitly
6. **Aim for >80% coverage** but focus on meaningful tests
7. **Keep tests independent** - each test should run in isolation
8. **Use AAA pattern** (Arrange-Act-Assert) for clarity
9. **Test behavior, not implementation**
10. **Document complex test scenarios** with docstrings

### ❌ DON'T

1. **Don't test implementation details** - test behavior
2. **Don't create test dependencies** - tests should run in any order
3. **Don't ignore failing tests** - fix or mark as xfail
4. **Don't test third-party code** - mock it instead
5. **Don't write tests that depend on external services** - use mocks
6. **Don't duplicate test code** - use fixtures and parametrization
7. **Don't write overly complex tests** - keep them simple
8. **Don't skip error testing** - error paths are critical
9. **Don't commit commented-out tests** - remove or fix them
10. **Don't aim for 100% coverage** - focus on critical paths

---

**Remember**: Good tests are an investment in code quality and maintainability. They serve as documentation, enable refactoring, and catch regressions early. Write tests that you'd want to maintain yourself!
