---
goal: Increase Unit Test Coverage to >80%
version: 1.0
date_created: 2025-10-17
last_updated: 2025-10-17
owner: Development Team
status: Planned
tags: ['testing', 'quality', 'coverage', 'pytest', 'unit-tests']
---

# Implementation Plan: Increase Unit Test Coverage to >80%

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Current Status

**Overall Coverage: 60%** (1048 statements, 423 missed)

**Target: >80% coverage**

### Coverage by Module (Current State)

| Module | Coverage | Priority |
|--------|----------|----------|
| **CLI Commands (Low Coverage - 22-34%)** |
| `cli/info/commands.py` | 22% | 🔴 HIGH |
| `cli/get/utils.py` | 23% | 🔴 HIGH |
| `cli/get/commands.py` | 30% | 🔴 HIGH |
| `cli/debug/commands.py` | 34% | 🟡 MEDIUM |
| **Helpers & Utils (Low-Medium Coverage)** |
| `helpers/__init__.py` | 44% | 🟡 MEDIUM |
| `tools.py` | 50% | 🟡 MEDIUM |
| `cli/utils.py` | 66% | 🟢 LOW |
| **Core Logic (Good Coverage - needs completion)** |
| `logics/download.py` | 64% | 🟡 MEDIUM |
| `logics/arista_xml_server.py` | 78% | 🟢 LOW |
| `logics/arista_server.py` | 85% | 🟢 LOW |
| **Models (Excellent Coverage)** |
| `models/version.py` | 93% | ✅ |
| `models/data.py` | 96% | ✅ |
| **Entry Points (Untested)** |
| `cli/__main__.py` | 0% | 🔴 HIGH |
| `__init__.py` | 80% | 🟢 LOW |

---

## Implementation Plan

### Phase 1: Critical CLI Commands (Highest Impact) 🔴

**Goal: Increase coverage of CLI commands from 22-34% to >75%**

#### Task 1.1: Test `cli/info/commands.py` (22% → 80%)
**Priority:** 🔴 HIGH
**Estimated Effort:** 4-6 hours
**Current Issues:**
- Only 29 out of 131 statements covered
- Missing tests for `versions` command with all options
- Missing tests for `latest` command
- No tests for error handling

**Required Tests:**
```python
# tests/unit/cli/test_info_commands.py (NEW FILE)

class TestInfoVersionsCommand:
    """Test suite for info versions command."""

    def test_versions_eos_default_output(self):
        """Test versions command with EOS and default fancy output."""
        # Mock AristaXmlQuerier.available_public_versions
        # Verify console output formatting

    def test_versions_cvp_json_output(self):
        """Test versions command with CVP and JSON output."""
        # Test JSON output format

    def test_versions_with_branch_filter(self):
        """Test versions command filtering by branch."""

    def test_versions_with_release_type_filter(self):
        """Test versions command filtering by release type (M/F)."""

    def test_versions_with_latest_only(self):
        """Test versions command with --latest flag."""

    def test_versions_invalid_package(self):
        """Test error handling for invalid package name."""

    def test_versions_authentication_failure(self):
        """Test handling of authentication errors."""

    def test_versions_network_timeout(self):
        """Test handling of network timeouts."""

class TestInfoLatestCommand:
    """Test suite for info latest command."""

    def test_latest_eos_version(self):
        """Test getting latest EOS version."""

    def test_latest_cvp_version(self):
        """Test getting latest CVP version."""

    def test_latest_with_branch(self):
        """Test latest version for specific branch."""

    def test_latest_with_release_type(self):
        """Test latest maintenance vs feature release."""

    def test_latest_no_versions_found(self):
        """Test behavior when no versions match criteria."""
```

**Key Testing Patterns:**
- Use `CliRunner` from `click.testing`
- Mock `AristaXmlQuerier` to avoid network calls
- Mock `console_configuration` and `cli_logging`
- Test all output formats: fancy, text, JSON
- Test all package types: EOS, CVP
- Test error paths: authentication, network, invalid input

---

#### Task 1.2: Test `cli/get/utils.py` (23% → 80%)
**Priority:** 🔴 HIGH
**Estimated Effort:** 3-4 hours
**Current Issues:**
- Only 13 out of 56 statements covered
- Missing tests for `search_version` function
- Missing tests for `download_files` function
- No tests for Docker import handling

**Required Tests:**
```python
# tests/unit/cli/test_get_utils.py (NEW FILE)

class TestInitialize:
    """Test suite for initialize helper function."""

    def test_initialize_extracts_context(self):
        """Test that initialize correctly extracts all context values."""

    def test_initialize_configures_logging(self):
        """Test that logging is configured with correct level."""

class TestSearchVersion:
    """Test suite for search_version function."""

    @pytest.mark.parametrize("version,expected", [
        ("4.29.3M", "4.29.3M"),
        ("4.30.1F", "4.30.1F"),
    ])
    def test_search_specific_version(self, version, expected):
        """Test searching for specific EOS version."""

    def test_search_latest_version(self):
        """Test searching for latest version with --latest flag."""

    def test_search_by_branch(self):
        """Test searching by branch without version."""

    def test_search_with_release_type_filter(self):
        """Test filtering by release type (M/F)."""

    def test_search_version_not_found(self):
        """Test handling when version not found."""

    def test_search_with_authentication_error(self):
        """Test error handling for authentication failures."""

class TestDownloadFiles:
    """Test suite for download_files function."""

    def test_download_files_success(self):
        """Test successful file download."""

    def test_download_files_with_dry_run(self):
        """Test dry-run mode doesn't actually download."""

    def test_download_files_with_checksum_verification(self):
        """Test checksum verification after download."""

    def test_download_files_network_error(self):
        """Test handling of network errors during download."""

class TestHandleDockerImport:
    """Test suite for handle_docker_import function."""

    def test_docker_import_success(self):
        """Test successful Docker image import."""

    def test_docker_import_docker_not_installed(self):
        """Test error when Docker is not available."""

    def test_docker_import_with_custom_tag(self):
        """Test Docker import with custom tag."""
```

**Key Testing Patterns:**
- Mock `AristaXmlQuerier` for version queries
- Mock `SoftManager` for download operations
- Mock `subprocess` for Docker commands
- Mock `Console` for output verification
- Test all code paths: success, errors, dry-run

---

#### Task 1.3: Test `cli/get/commands.py` (30% → 75%)
**Priority:** 🔴 HIGH
**Estimated Effort:** 6-8 hours
**Current Issues:**
- Only 40 out of 132 statements covered
- Missing tests for `eos` command with all options
- Missing tests for `cvp` command
- No tests for EVE-NG provisioning
- No tests for Docker import integration

**Required Tests:**
```python
# tests/unit/cli/test_get_commands.py (NEW FILE)

class TestGetEosCommand:
    """Test suite for get eos command."""

    def test_eos_download_specific_version(self):
        """Test downloading specific EOS version."""
        # Mock all dependencies: AristaXmlQuerier, SoftManager
        # Verify correct parameters passed

    def test_eos_download_latest_version(self):
        """Test downloading latest EOS version with --latest."""

    def test_eos_download_with_branch_filter(self):
        """Test downloading from specific branch."""

    def test_eos_download_with_format_option(self):
        """Test downloading different formats (64, vEOS, cEOS)."""

    def test_eos_download_with_docker_import(self):
        """Test download + Docker import workflow."""

    def test_eos_download_with_eve_ng_provision(self):
        """Test download + EVE-NG provisioning."""

    def test_eos_download_with_custom_output_path(self):
        """Test download to custom directory."""

    def test_eos_skip_download_flag(self):
        """Test --skip-download flag for debugging."""

    def test_eos_dry_run_mode(self):
        """Test dry-run mode doesn't perform actual download."""

    def test_eos_download_authentication_error(self):
        """Test error handling for authentication failures."""

    def test_eos_download_version_not_found(self):
        """Test error when requested version doesn't exist."""

    def test_eos_download_network_timeout(self):
        """Test handling of network timeouts."""

class TestGetCvpCommand:
    """Test suite for get cvp command."""

    def test_cvp_download_specific_version(self):
        """Test downloading specific CVP version."""

    def test_cvp_download_latest_version(self):
        """Test downloading latest CVP version."""

    def test_cvp_download_with_format_option(self):
        """Test downloading different CVP formats (ova, rpm, kvm)."""

    def test_cvp_download_with_custom_output_path(self):
        """Test download to custom directory."""

    def test_cvp_dry_run_mode(self):
        """Test dry-run mode for CVP downloads."""

    def test_cvp_authentication_error(self):
        """Test error handling for authentication failures."""
```

**Key Testing Patterns:**
- Use `CliRunner` for CLI invocation
- Mock `AristaXmlQuerier.available_public_versions`
- Mock `EosXmlObject` and `CvpXmlObject` creation
- Mock `SoftManager.download_file` and related methods
- Mock `subprocess` for Docker/EVE-NG operations
- Test all CLI options in isolation and combination
- Test error scenarios comprehensively

---

#### Task 1.4: Test `cli/debug/commands.py` (34% → 75%)
**Priority:** 🟡 MEDIUM
**Estimated Effort:** 2-3 hours
**Current Issues:**
- Only 11 out of 32 statements covered
- Missing comprehensive tests for `xml` command
- No tests for XML formatting/prettification
- No tests for error handling

**Required Tests:**
```python
# tests/unit/cli/test_debug_commands.py (NEW FILE)

class TestDebugXmlCommand:
    """Test suite for debug xml command."""

    def test_xml_command_saves_file(self):
        """Test that XML is saved to specified output file."""

    def test_xml_command_prettifies_xml(self):
        """Test that XML is prettified before saving."""

    def test_xml_command_with_custom_output_path(self):
        """Test specifying custom output path."""

    def test_xml_command_authentication_error(self):
        """Test handling authentication failures."""

    def test_xml_command_no_xml_data_received(self):
        """Test handling when server returns no data."""

    def test_xml_command_with_debug_log_level(self):
        """Test command with debug logging enabled."""
```

**Key Testing Patterns:**
- Mock `AristaServer.authenticate` and `get_xml_data`
- Use `tmp_path` fixture for output file testing
- Verify XML content and formatting
- Test file I/O operations

---

#### Task 1.5: Test `cli/__main__.py` (0% → 100%)
**Priority:** 🔴 HIGH
**Estimated Effort:** 1 hour
**Current Issues:**
- Completely untested (0% coverage)
- Entry point for `python -m eos_downloader`

**Required Tests:**
```python
# tests/unit/cli/test_main.py (NEW FILE)

def test_main_module_entry_point():
    """Test that __main__.py correctly invokes CLI."""
    with patch('eos_downloader.cli.cli.ardl') as mock_ardl:
        # Import and run __main__
        exec(open('eos_downloader/cli/__main__.py').read())
        mock_ardl.assert_called_once()

def test_main_module_with_args():
    """Test module execution with command-line arguments."""
    # Test via subprocess to ensure real execution path
```

---

### Phase 2: Helpers and Utilities (Medium Impact) 🟡

**Goal: Increase coverage of helper functions from 44-66% to >80%**

#### Task 2.1: Test `helpers/__init__.py` (44% → 85%)
**Priority:** 🟡 MEDIUM
**Estimated Effort:** 4-5 hours
**Current Issues:**
- Only 17 out of 39 statements covered
- Missing tests for `DownloadProgressBar` class
- Missing tests for concurrent download functionality
- No tests for signal handling

**Required Tests:**
```python
# tests/unit/test_helpers.py (NEW FILE)

class TestSignalHandling:
    """Test suite for signal handlers."""

    def test_handle_sigint_sets_done_event(self):
        """Test that SIGINT handler sets the done event."""

    def test_handle_sigint_graceful_shutdown(self):
        """Test graceful shutdown on interrupt."""

class TestDownloadProgressBar:
    """Test suite for DownloadProgressBar class."""

    def test_progress_bar_initialization(self):
        """Test DownloadProgressBar initializes correctly."""

    def test_copy_url_single_file(self):
        """Test downloading single file with progress."""

    def test_copy_url_multiple_files_concurrent(self):
        """Test concurrent download of multiple files."""

    def test_copy_url_with_retry_on_failure(self):
        """Test retry mechanism on download failure."""

    def test_copy_url_respects_done_event(self):
        """Test that downloads stop when done_event is set."""

    def test_progress_bar_display_updates(self):
        """Test that progress bar updates correctly during download."""

    def test_download_with_network_error(self):
        """Test handling of network errors during download."""

    def test_download_with_timeout(self):
        """Test handling of timeout during download."""
```

**Key Testing Patterns:**
- Mock `requests.get` for download simulation
- Mock `Progress` from Rich for progress tracking
- Use `tmp_path` for file I/O
- Mock `ThreadPoolExecutor` for concurrency testing
- Test signal handling with `signal` module

---

#### Task 2.2: Test `tools.py` (50% → 90%)
**Priority:** 🟡 MEDIUM
**Estimated Effort:** 1 hour
**Current Issues:**
- Only 1 out of 2 statements covered
- Minimal code but needs full coverage

**Required Tests:**
```python
# tests/unit/test_tools.py (NEW FILE)

def test_sanitize_filename():
    """Test filename sanitization for various inputs."""
    # Test removing special characters
    # Test handling Unicode
    # Test path traversal prevention
```

---

#### Task 2.3: Test `cli/utils.py` (66% → 90%)
**Priority:** 🟢 LOW
**Estimated Effort:** 2 hours
**Current Issues:**
- Already at 66% coverage
- Missing tests for some edge cases

**Required Tests:**
```python
# tests/unit/cli/test_cli_utils.py (EXPAND EXISTING)

class TestCliLogging:
    """Expand tests for cli_logging function."""

    def test_logging_with_all_levels(self):
        """Test logging configuration for all levels."""

    def test_logging_with_invalid_level(self):
        """Test error handling for invalid log level."""

class TestConsoleConfiguration:
    """Test console_configuration function."""

    def test_console_creation(self):
        """Test that console is created with correct settings."""

    def test_console_theme_configuration(self):
        """Test console theme settings."""
```

---

### Phase 3: Core Logic Completion (Medium Priority) 🟡

**Goal: Increase logic coverage from 64-85% to >90%**

#### Task 3.1: Test `logics/download.py` (64% → 90%)
**Priority:** 🟡 MEDIUM
**Estimated Effort:** 5-6 hours
**Current Issues:**
- 66 out of 183 statements missed
- Missing tests for checksum verification
- Missing tests for EVE-NG provisioning edge cases
- No tests for error recovery mechanisms

**Required Tests:**
```python
# tests/unit/logics/test_download_extended.py (NEW FILE - extend existing)

class TestSoftManagerChecksumVerification:
    """Extended tests for checksum verification."""

    def test_compute_hash_md5sum(self):
        """Test MD5 hash computation."""

    def test_compute_hash_sha512sum(self):
        """Test SHA512 hash computation."""

    def test_checksum_verification_success(self):
        """Test successful checksum verification."""

    def test_checksum_verification_failure(self):
        """Test handling of checksum mismatch."""

    def test_checksum_file_missing(self):
        """Test handling when checksum file is missing."""

class TestEveNgProvisioning:
    """Extended tests for EVE-NG provisioning."""

    def test_provision_eve_creates_directory(self):
        """Test that EVE-NG directory is created."""

    def test_provision_eve_converts_image(self):
        """Test qemu-img conversion."""

    def test_provision_eve_sets_permissions(self):
        """Test file permission setting."""

    def test_provision_eve_with_noztp(self):
        """Test provisioning with noztp option."""

    def test_provision_eve_directory_exists(self):
        """Test behavior when directory already exists."""

    def test_provision_eve_qemu_img_failure(self):
        """Test handling of qemu-img conversion failure."""

class TestDockerOperations:
    """Extended tests for Docker operations."""

    def test_import_docker_with_load(self):
        """Test docker load for .tar images."""

    def test_import_docker_with_import(self):
        """Test docker import for other formats."""

    def test_import_docker_not_installed(self):
        """Test error when docker is not installed."""

    def test_import_docker_command_failure(self):
        """Test handling of docker command failures."""

class TestErrorRecovery:
    """Test error recovery mechanisms."""

    def test_download_retry_on_network_error(self):
        """Test retry mechanism on network errors."""

    def test_download_cleanup_on_failure(self):
        """Test cleanup of partial downloads on failure."""

    def test_download_timeout_handling(self):
        """Test handling of download timeouts."""
```

**Key Testing Patterns:**
- Mock file I/O operations extensively
- Mock `os.system` for external command execution
- Mock `subprocess` for Docker/qemu-img
- Test all error paths and recovery mechanisms
- Use `tmp_path` for file operations

---

#### Task 3.2: Test `logics/arista_xml_server.py` (78% → 90%)
**Priority:** 🟢 LOW
**Estimated Effort:** 3-4 hours
**Current Issues:**
- 34 out of 154 statements missed
- Missing tests for some edge cases in XML parsing
- Missing tests for error handling in version querying

**Required Tests:**
```python
# tests/unit/logics/test_arista_xml_server_extended.py (EXPAND EXISTING)

class TestAristaXmlQuerierEdgeCases:
    """Extended edge case tests for AristaXmlQuerier."""

    def test_query_with_malformed_xml(self):
        """Test handling of malformed XML responses."""

    def test_query_with_empty_results(self):
        """Test behavior when no versions found."""

    def test_query_with_network_timeout(self):
        """Test handling of network timeouts."""

    def test_query_with_rate_limiting(self):
        """Test handling of API rate limiting."""

class TestVersionFiltering:
    """Extended tests for version filtering."""

    def test_filter_by_multiple_criteria(self):
        """Test filtering by branch AND release type."""

    def test_filter_with_regex_pattern(self):
        """Test version matching with regex patterns."""

    def test_latest_version_with_multiple_branches(self):
        """Test finding latest across multiple branches."""
```

---

#### Task 3.3: Test `logics/arista_server.py` (85% → 95%)
**Priority:** 🟢 LOW
**Estimated Effort:** 2 hours
**Current Issues:**
- Already high coverage (85%)
- Only 11 statements missed

**Required Tests:**
```python
# tests/unit/logics/test_arista_server_extended.py (EXPAND EXISTING)

class TestAristaServerEdgeCases:
    """Extended edge case tests for AristaServer."""

    def test_authenticate_with_network_error(self):
        """Test handling of network errors during auth."""

    def test_get_xml_data_with_timeout(self):
        """Test XML data retrieval with timeout."""

    def test_get_url_with_special_characters(self):
        """Test URL generation with special characters."""
```

---

### Phase 4: Model and Package Improvements (Low Priority) 🟢

#### Task 4.1: Test `models/version.py` (93% → 98%)
**Priority:** 🟢 LOW
**Estimated Effort:** 1-2 hours
**Current Issues:**
- Already excellent coverage
- Only 8 statements missed (likely edge cases)

**Required Tests:**
```python
# tests/unit/models/test_version_extended.py (EXPAND EXISTING)

class TestEosVersionEdgeCases:
    """Extended edge case tests for EosVersion."""

    def test_version_with_unusual_format(self):
        """Test handling of unusual but valid version formats."""

    def test_version_comparison_with_same_values(self):
        """Test comparison operators with identical versions."""

    def test_version_string_representation(self):
        """Test __str__ and __repr__ methods."""

class TestCvpVersionEdgeCases:
    """Extended edge case tests for CvpVersion."""

    def test_cvp_version_edge_cases(self):
        """Test CVP version parsing edge cases."""
```

---

#### Task 4.2: Test `__init__.py` (80% → 95%)
**Priority:** 🟢 LOW
**Estimated Effort:** 1 hour

**Required Tests:**
```python
# tests/unit/test_package_init.py (NEW FILE)

def test_package_version_defined():
    """Test that package version is defined."""
    from eos_downloader import __version__
    assert __version__ is not None

def test_package_exports():
    """Test that expected symbols are exported."""
    import eos_downloader
    # Verify key classes/functions are accessible
```

---

## Testing Strategy & Best Practices

### General Testing Guidelines

1. **Use Fixtures Extensively**
   - Create reusable fixtures in `tests/conftest.py`
   - Use `@pytest.fixture(scope="module")` for expensive setups
   - Leverage `tmp_path` for file operations

2. **Mock External Dependencies**
   - Mock all network calls (`requests.get`, `requests.post`)
   - Mock all file I/O where appropriate
   - Mock external commands (`subprocess`, `os.system`)
   - Mock Arista API responses with realistic XML data

3. **Parametrize Tests**
   - Use `@pytest.mark.parametrize` for multiple input scenarios
   - Test all enum values (release types, package types, formats)
   - Test boundary conditions

4. **Test Error Paths**
   - Test all exception types defined in `exceptions/`
   - Test network timeouts, authentication failures
   - Test invalid inputs and edge cases

5. **Use AAA Pattern**
   - **Arrange**: Set up test data and mocks
   - **Act**: Execute the function/command
   - **Assert**: Verify expected behavior

6. **CLI Testing Patterns**
   ```python
   from click.testing import CliRunner

   def test_cli_command():
       runner = CliRunner()
       result = runner.invoke(command, ['--option', 'value'])
       assert result.exit_code == 0
       assert "expected output" in result.output
   ```

7. **Rich Mocking for Console Output**
   ```python
   @patch('eos_downloader.cli.utils.Console')
   def test_console_output(mock_console):
       mock_console.return_value.print.assert_called_with(...)
   ```

---

## Priority Matrix

### Critical Path to 80% Coverage (Weeks 1-3)

| Week | Tasks | Expected Coverage Increase |
|------|-------|---------------------------|
| **Week 1** | Task 1.1 (info commands) + 1.2 (get utils) | +8% |
| **Week 2** | Task 1.3 (get commands) + 1.5 (__main__) | +10% |
| **Week 3** | Task 1.4 (debug) + 2.1 (helpers) | +6% |

**Total Expected: ~84% coverage after 3 weeks**

### Stretch Goals to 90% Coverage (Week 4)

| Week | Tasks | Expected Coverage |
|------|-------|-------------------|
| **Week 4** | Phase 3 (logic completion) | +6% → 90% total |

---

## Risk Assessment

### High Risk Areas

1. **CLI Integration Tests**
   - **Risk**: Complex Click context handling
   - **Mitigation**: Use `CliRunner` extensively, test context isolation

2. **Mocking External Services**
   - **Risk**: Over-mocking may miss real integration issues
   - **Mitigation**: Balance unit tests with integration tests in `tests/system/`

3. **Concurrent Download Testing**
   - **Risk**: Race conditions in tests
   - **Mitigation**: Use proper synchronization, test with mock objects

### Medium Risk Areas

1. **File I/O Operations**
   - **Risk**: Test pollution, permission issues
   - **Mitigation**: Always use `tmp_path`, clean up in teardown

2. **Signal Handling**
   - **Risk**: Signal tests may interfere with test runner
   - **Mitigation**: Test in isolation, use proper cleanup

---

## Success Criteria

### Phase 1 Complete (Critical)
- ✅ All CLI commands have >75% coverage
- ✅ `cli/__main__.py` has 100% coverage
- ✅ Overall coverage >70%

### Phase 2 Complete (Medium)
- ✅ Helpers have >80% coverage
- ✅ Overall coverage >75%

### Phase 3 Complete (Final Goal)
- ✅ Core logic modules >90% coverage
- ✅ **Overall coverage >80%** ✨
- ✅ All critical paths tested
- ✅ All error scenarios covered

---

## Implementation Order (Recommended)

```
Week 1:
Day 1-2: Task 1.1 - cli/info/commands.py tests
Day 3-4: Task 1.2 - cli/get/utils.py tests
Day 5: Review and integration

Week 2:
Day 1-3: Task 1.3 - cli/get/commands.py tests (large)
Day 4: Task 1.5 - cli/__main__.py tests
Day 5: Review and coverage check

Week 3:
Day 1-2: Task 1.4 - cli/debug/commands.py tests
Day 3-4: Task 2.1 - helpers/__init__.py tests
Day 5: Phase 1-2 completion review

Week 4 (Stretch):
Day 1-2: Task 3.1 - logics/download.py extended tests
Day 3: Task 3.2 - logics/arista_xml_server.py extended tests
Day 4-5: Final coverage push and documentation
```

---

## Measurement & Tracking

### Coverage Tracking Commands

```bash
# Get current coverage
pytest --cov=eos_downloader --cov-report=term-missing

# Generate HTML report
pytest --cov=eos_downloader --cov-report=html
open htmlcov/index.html

# Coverage for specific module
pytest --cov=eos_downloader.cli.get --cov-report=term-missing

# Run only new tests
pytest tests/unit/cli/test_info_commands.py -v
```

### Weekly Check-ins

1. Run full coverage report
2. Identify remaining gaps
3. Adjust priorities if needed
4. Update this document with progress

---

## Notes

- All test files should follow naming convention: `test_<module>.py`
- Use descriptive test names that explain what is being tested
- Keep tests independent - no shared state between tests
- Each test should have a clear docstring
- Follow the testing guidelines in `.github/instructions/testing.instructions.md`
- Use the Arista domain knowledge from `.github/instructions/arista-domain.instructions.md`
- Follow Python standards from `.github/instructions/python.instructions.md`

---

## Appendix: Quick Reference

### Common Fixtures Needed

```python
# tests/conftest.py additions

@pytest.fixture
def mock_arista_xml_querier():
    """Mock AristaXmlQuerier for testing."""
    with patch('eos_downloader.logics.arista_xml_server.AristaXmlQuerier') as mock:
        yield mock

@pytest.fixture
def mock_soft_manager():
    """Mock SoftManager for testing."""
    with patch('eos_downloader.logics.download.SoftManager') as mock:
        yield mock

@pytest.fixture
def mock_console():
    """Mock Rich Console for testing."""
    with patch('eos_downloader.cli.utils.Console') as mock:
        yield mock

@pytest.fixture
def sample_xml_response():
    """Sample XML response from Arista API."""
    return open('tests/data/arista_test.xml').read()
```

### Common Mock Patterns

```python
# Mock Click context
@pytest.fixture
def mock_click_context():
    ctx = MagicMock()
    ctx.obj = {
        'token': 'test-token',
        'debug': False,
        'log_level': 'INFO'
    }
    return ctx

# Mock version objects
@pytest.fixture
def mock_eos_versions():
    return [
        EosVersion.from_str("4.29.3M"),
        EosVersion.from_str("4.30.1F"),
    ]
```

---

**End of Implementation Plan**

*This plan should increase coverage from 60% to >80% over approximately 3-4 weeks of focused effort.*
