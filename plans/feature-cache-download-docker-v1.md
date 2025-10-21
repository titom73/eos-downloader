---
goal: Implement smart caching for downloads and Docker image imports
version: 1.0
date_created: 2025-10-21
last_updated: 2025-10-21
owner: Development Team
status: Planned
tags: ['feature', 'performance', 'cache', 'docker', 'download', 'optimization']
---

# Implementation Plan: Smart Caching for Downloads and Docker Image Imports

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Introduction

This implementation plan adds intelligent caching mechanisms to avoid redundant downloads and Docker image imports. Currently, `eos-downloader` re-downloads files even when they already exist locally and attempts to import Docker images even when the tag already exists in the local registry.

**Key improvements:**
- ✅ Check if file exists locally before downloading
- ✅ Verify Docker image tag exists before importing
- ✅ Add `--force` option to override cache behavior
- ✅ Add `--cache-dir` option to specify custom cache location
- ✅ Validate file integrity using checksums when using cached files
- ✅ Provide clear user feedback about cache hits/misses

## 1. Requirements & Constraints

### Functional Requirements

- **REQ-001**: Check if target file exists in output directory before initiating download
- **REQ-002**: Verify Docker image with specific tag exists in local registry before import
- **REQ-003**: Provide `--force` CLI flag to bypass cache checks and force download/import
- **REQ-004**: Provide `--cache-dir` CLI option to specify custom cache location (default: output directory)
- **REQ-005**: When using cached files, verify integrity using checksums (md5sum or sha512sum)
- **REQ-006**: Provide clear console output indicating cache hits vs fresh downloads
- **REQ-007**: Support cache invalidation when checksum verification fails
- **REQ-008**: Maintain backward compatibility with existing CLI options

### Non-Functional Requirements

- **NFR-001**: Cache checks must complete in <100ms for typical filesystems
- **NFR-002**: Docker registry queries must timeout after 5 seconds
- **NFR-003**: Failed checksum verification must trigger automatic re-download
- **NFR-004**: All cache operations must respect dry-run mode

### Security Requirements

- **SEC-001**: Never cache or reuse files with failed checksum validation
- **SEC-002**: Ensure file permissions are preserved when using cached files
- **SEC-003**: Validate file paths to prevent directory traversal attacks

### Constraints

- **CON-001**: Must work with existing `SoftManager` class architecture
- **CON-002**: Must not break existing CLI command interfaces
- **CON-003**: Docker commands must work with both `docker` and `podman`
- **CON-004**: Cache behavior must be clearly documented in help text

### Guidelines

- **GUD-001**: Follow Python coding standards from `.github/instructions/python.instructions.md`
- **GUD-002**: Use Rich library for console output formatting
- **GUD-003**: Add comprehensive logging at DEBUG level for troubleshooting
- **GUD-004**: Write unit tests achieving >80% coverage for new code

### Patterns

- **PAT-001**: Use pathlib.Path for all file system operations
- **PAT-002**: Use type hints for all function signatures
- **PAT-003**: Follow AAA (Arrange-Act-Assert) pattern in tests
- **PAT-004**: Use Click's option decorators for CLI flags

## 2. Implementation Steps

### Phase 1: Core Cache Logic for File Downloads

**GOAL-001**: Implement file existence checking and cache validation in `SoftManager`

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Add `_file_exists_and_valid()` method to `SoftManager` class in `eos_downloader/logics/download.py` to check if file exists and optionally validate checksum | | |
| TASK-002 | Add `force_download` parameter to `SoftManager.__init__()` constructor | | |
| TASK-003 | Modify `download_file()` method to check cache before downloading | | |
| TASK-004 | Modify `downloads()` method to check cache before downloading multiple files | | |
| TASK-005 | Add logging statements for cache hits and misses | | |
| TASK-006 | Update docstrings for modified methods with cache behavior documentation | | |

**Implementation Details for TASK-001:**

```python
def _file_exists_and_valid(
    self,
    file_path: Path,
    checksum_file: Optional[Path] = None,
    check_type: Literal["md5sum", "sha512sum", "skip"] = "skip"
) -> bool:
    """
    Check if file exists and optionally validate its checksum.
    
    Parameters
    ----------
    file_path : Path
        Path to the file to check
    checksum_file : Optional[Path]
        Path to checksum file for validation
    check_type : Literal["md5sum", "sha512sum", "skip"]
        Type of checksum validation to perform
        
    Returns
    -------
    bool
        True if file exists and passes validation, False otherwise
        
    Examples
    --------
    >>> manager = SoftManager()
    >>> manager._file_exists_and_valid(Path("EOS-4.29.3M.swi"))
    True
    """
    import logging
    
    # Check if file exists
    if not file_path.exists():
        logging.debug(f"File not found in cache: {file_path}")
        return False
    
    # If no checksum validation requested, file is valid
    if check_type == "skip" or checksum_file is None:
        logging.info(f"File found in cache (no validation): {file_path}")
        return True
    
    # Validate checksum if requested
    try:
        is_valid = self.checksum(
            file=str(file_path),
            checksum_file=str(checksum_file),
            check_type=check_type
        )
        if is_valid:
            logging.info(f"File found in cache (checksum valid): {file_path}")
            return True
        else:
            logging.warning(f"Cached file checksum invalid: {file_path}")
            return False
    except Exception as e:
        logging.warning(f"Checksum validation failed: {e}")
        return False
```

**Implementation Details for TASK-002:**

```python
def __init__(self, dry_run: bool = False, force_download: bool = False) -> None:
    """
    Initialize SoftManager.
    
    Parameters
    ----------
    dry_run : bool, optional
        If True, simulate operations without executing them, by default False
    force_download : bool, optional
        If True, bypass cache and force download/import, by default False
    """
    self.dry_run = dry_run
    self.force_download = force_download
    self.file: Dict[str, str] = {}
```

**Implementation Details for TASK-003:**

```python
def download_file(
    self, 
    url: str, 
    file_path: str, 
    filename: str, 
    rich_interface: bool = True,
    force: bool = False
) -> Union[None, str]:
    """
    Downloads a file from URL with caching support.
    
    Parameters
    ----------
    url : str
        URL to download from
    file_path : str
        Directory path where file will be saved
    filename : str
        Name of the file to save
    rich_interface : bool, optional
        Use rich progress interface, by default True
    force : bool, optional
        If True, download even if file exists locally. Defaults to False.
        
    Returns
    -------
    Union[None, str]
        Path to the downloaded or cached file, or None on error
        
    Examples
    --------
    >>> manager = SoftManager()
    >>> manager.download_file(
    ...     url="https://example.com/file.swi",
    ...     file_path="/downloads",
    ...     filename="EOS-4.29.3M.swi"
    ... )
    '/downloads/EOS-4.29.3M.swi'
    """
    full_path = Path(file_path) / filename
    
    # Check cache unless force flag is set
    if not force and not self.force_download:
        if full_path.exists():
            logging.info(f"Using cached file: {full_path}")
            return str(full_path)
    
    # Log download action
    logging.info(
        f"{'[DRY-RUN] Would download' if self.dry_run else 'Downloading'} {filename}"
    )
    
    # Handle dry-run mode
    if self.dry_run:
        return str(full_path)
    
    # Proceed with download
    if url is not False:
        if not rich_interface:
            return self._download_file_raw(url, str(full_path))
        
        rich_downloader = eos_downloader.helpers.DownloadProgressBar()
        rich_downloader.download(urls=[url], dest_dir=file_path)
        return str(full_path)
    
    return None
```

### Phase 2: Docker Image Cache Checking

**GOAL-002**: Implement Docker image tag existence checking before import

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Add `_docker_image_exists()` static method to `SoftManager` to check if Docker image:tag exists locally | | |
| TASK-008 | Add `force_import` parameter to `import_docker()` method | | |
| TASK-009 | Modify `import_docker()` to check if image:tag exists before importing | | |
| TASK-010 | Add support for both `docker` and `podman` CLI tools | | |
| TASK-011 | Handle Docker daemon not running gracefully | | |
| TASK-012 | Add comprehensive logging for Docker operations | | |

**Implementation Details for TASK-007:**

```python
@staticmethod
def _docker_image_exists(image_name: str, image_tag: str) -> bool:
    """
    Check if Docker image with specified tag exists locally.
    
    Parameters
    ----------
    image_name : str
        Docker image name (e.g., 'arista/ceos')
    image_tag : str
        Docker image tag (e.g., '4.29.3M')
        
    Returns
    -------
    bool
        True if image:tag exists in local registry, False otherwise
        
    Examples
    --------
    >>> SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
    True
    
    Notes
    -----
    This method tries both 'docker' and 'podman' commands in order.
    It uses 'docker images -q' to check for image existence.
    """
    import subprocess
    import shutil
    import logging
    
    # Try docker first, then podman
    for cmd in ['docker', 'podman']:
        # Check if command is available
        if not shutil.which(cmd):
            logging.debug(f"{cmd} command not found in PATH")
            continue
        
        try:
            # Query for specific image:tag
            result = subprocess.run(
                [cmd, 'images', '-q', f'{image_name}:{image_tag}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # If output is not empty, image exists
            if result.stdout.strip():
                logging.info(
                    f"Docker image {image_name}:{image_tag} found in local registry"
                )
                return True
            else:
                logging.debug(
                    f"Docker image {image_name}:{image_tag} not found in local registry"
                )
                return False
                
        except subprocess.TimeoutExpired:
            logging.warning(f"{cmd} command timed out after 5 seconds")
            continue
            
        except Exception as e:
            logging.debug(f"Error checking {cmd} images: {e}")
            continue
    
    # If we get here, neither docker nor podman worked
    logging.warning("Unable to check Docker images (docker/podman not available)")
    return False
```

**Implementation Details for TASK-009:**

```python
def import_docker(
    self,
    local_file_path: str,
    docker_name: str = "arista/ceos",
    docker_tag: str = "latest",
    force: bool = False
) -> None:
    """
    Import local file into Docker with caching support.
    
    Parameters
    ----------
    local_file_path : str
        Path to the local file to import
    docker_name : str, optional
        Docker image name, by default "arista/ceos"
    docker_tag : str, optional
        Docker image tag, by default "latest"
    force : bool, optional
        If True, import even if image:tag already exists. Defaults to False.
        
    Raises
    ------
    FileNotFoundError
        If the local file does not exist
        
    Examples
    --------
    >>> manager = SoftManager()
    >>> manager.import_docker(
    ...     local_file_path="/downloads/cEOS-4.29.3M.tar.xz",
    ...     docker_name="arista/ceos",
    ...     docker_tag="4.29.3M"
    ... )
    """
    import logging
    
    # Check if file exists
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"File {local_file_path} not found")
    
    # Check cache unless force flag is set
    if not force and not self.force_download:
        if self._docker_image_exists(docker_name, docker_tag):
            logging.info(
                f"Docker image {docker_name}:{docker_tag} already exists locally. "
                f"Use --force to re-import."
            )
            return
    
    # Log import action
    logging.info(
        f"{'[DRY-RUN] Would import' if self.dry_run else 'Importing'} "
        f"{docker_name}:{docker_tag}"
    )
    
    # Handle dry-run mode
    if self.dry_run:
        return
    
    # Proceed with import
    cmd = f"$(which docker) import {local_file_path} {docker_name}:{docker_tag}"
    logging.debug(f"Executing: {cmd}")
    os.system(cmd)
    logging.info(f"Docker image {docker_name}:{docker_tag} imported successfully")
```

### Phase 3: CLI Integration

**GOAL-003**: Add CLI options for cache control

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Add `--force` flag to `eos` command in `cli/get/commands.py` | | |
| TASK-014 | Add `--force` flag to `cvp` command in `cli/get/commands.py` | | |
| TASK-015 | Add `--force` flag to `path` command in `cli/get/commands.py` | | |
| TASK-016 | Add `--cache-dir` option to `eos` command for custom cache location | | |
| TASK-017 | Update `initialize()` function in `cli/get/utils.py` to handle force flag | | |
| TASK-018 | Update CLI help text to document cache behavior | | |

**Implementation Details for TASK-013:**

```python
@click.command()
@click.option("--format", default="vmdk", help="Image format", show_default=True)
@click.option(
    "--output",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save image",
    type=click.Path(),
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--force",
    is_flag=True,
    help="Force download and import even if files/images already exist",
    default=False,
    show_default=True,
)
@click.option(
    "--cache-dir",
    default=None,
    help="Directory to use for caching downloaded files (default: same as --output)",
    type=click.Path(exists=False),
    show_default=True,
)
# ... other options ...
@click.pass_context
def eos(
    ctx: click.Context,
    format: str,
    output: str,
    force: bool,
    cache_dir: Optional[str],
    # ... other parameters ...
) -> int:
    """
    Download EOS image from Arista server.
    
    This command downloads Arista EOS images with intelligent caching.
    By default, if a file already exists in the output directory, it will
    be reused. Use --force to bypass the cache and re-download.
    
    Examples:
    
        # Download with caching (default)
        $ ardl get eos --version 4.29.3M --format cEOS
        
        # Force re-download
        $ ardl get eos --version 4.29.3M --format cEOS --force
        
        # Use custom cache directory
        $ ardl get eos --version 4.29.3M --cache-dir ~/.eos-cache
    """
    console, token, debug, log_level = initialize(ctx)
    
    # Determine cache directory
    effective_cache_dir = cache_dir if cache_dir else output
    
    # Initialize SoftManager with force flag
    cli = SoftManager(dry_run=dry_run, force_download=force)
    
    # Rest of implementation...
```

### Phase 4: User Feedback Enhancement

**GOAL-004**: Improve console output to clearly communicate cache behavior

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-019 | Add Rich console messages for cache hits in `download_files()` function | | |
| TASK-020 | Add Rich console messages for cache hits in `handle_docker_import()` function | | |
| TASK-021 | Add summary statistics showing cache hits/misses at end of operation | | |
| TASK-022 | Add `--verbose` mode to show detailed cache checking process | | |

**Implementation Details for TASK-019:**

```python
def download_files(
    console: Console,
    cli: Any,
    arista_dl_obj: AristaXmlObjects,
    output: str,
    rich_interface: bool = True,
    debug: bool = False,
    checksum_format: str = "sha512sum",
) -> None:
    """
    Downloads files with cache awareness.
    
    Parameters
    ----------
    console : Console
        Rich console for output
    cli : Any
        SoftManager instance
    arista_dl_obj : AristaXmlObjects
        Object containing download information
    output : str
        Output directory path
    rich_interface : bool, optional
        Use rich interface, by default True
    debug : bool, optional
        Enable debug output, by default False
    checksum_format : str, optional
        Checksum format to use, by default "sha512sum"
    """
    file_path = Path(output) / arista_dl_obj.filename
    
    # Check cache
    if file_path.exists() and not cli.force_download:
        console.print(
            f"[green]✓[/green] Using cached file: [cyan]{file_path.name}[/cyan]"
        )
        console.print(
            "   [dim]Use --force to re-download[/dim]"
        )
        # Store filename for later use
        cli.file["name"] = str(file_path)
    else:
        # Download file
        console.print(f"Downloading [cyan]{arista_dl_obj.filename}[/cyan]...")
        
        cli.download_file(
            url=arista_dl_obj.url,
            file_path=output,
            filename=arista_dl_obj.filename,
            rich_interface=rich_interface,
        )
        
        console.print(
            f"[green]✓[/green] Downloaded: [cyan]{arista_dl_obj.filename}[/cyan]"
        )
    
    # Download and verify checksum
    if checksum_format != "skip":
        console.print(f"Verifying checksum ({checksum_format})...")
        # ... checksum logic ...
```

**Implementation Details for TASK-020:**

```python
def handle_docker_import(
    console: Console,
    cli: Any,
    arista_dl_obj: AristaXmlObjects,
    output: str,
    docker_name: str,
    docker_tag: Optional[str],
    debug: bool,
) -> int:
    """
    Handle Docker import with cache checking.
    
    Parameters
    ----------
    console : Console
        Rich console for output
    cli : Any
        SoftManager instance
    arista_dl_obj : AristaXmlObjects
        Object containing download information
    output : str
        Output directory path
    docker_name : str
        Docker image name
    docker_tag : Optional[str]
        Docker image tag
    debug : bool
        Enable debug output
        
    Returns
    -------
    int
        Exit code (0 for success)
    """
    if docker_tag is None:
        docker_tag = arista_dl_obj.version

    # Build path to local file
    image_path = Path(output) / arista_dl_obj.filename
    
    # Check if image already exists in Docker
    if cli._docker_image_exists(docker_name, docker_tag) and not cli.force_download:
        console.print(
            f"[green]✓[/green] Docker image [cyan]{docker_name}:{docker_tag}[/cyan] "
            f"already exists"
        )
        console.print(
            "   [dim]Use --force to re-import[/dim]"
        )
        return 0
    
    # Proceed with import
    console.print(
        f"Importing docker image [cyan]{docker_name}:{docker_tag}[/cyan]..."
    )
    
    try:
        cli.import_docker(
            local_file_path=str(image_path),
            docker_name=docker_name,
            docker_tag=docker_tag
        )
        console.print(
            f"[green]✓[/green] Docker image imported successfully"
        )
        return 0
    except Exception as e:
        console.print(f"[red]✗[/red] Docker import failed: {e}")
        if debug:
            console.print_exception()
        return 1
```

### Phase 5: Testing & Documentation

**GOAL-005**: Comprehensive testing and documentation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-023 | Write unit tests for `_file_exists_and_valid()` method | | |
| TASK-024 | Write unit tests for `_docker_image_exists()` method | | |
| TASK-025 | Write integration tests for cache behavior in download workflow | | |
| TASK-026 | Write integration tests for cache behavior in Docker import workflow | | |
| TASK-027 | Update documentation in `docs/usage/eos.md` with cache examples | | |
| TASK-028 | Update documentation in `docs/usage/cvp.md` with cache examples | | |
| TASK-029 | Add FAQ entry about cache behavior to `docs/faq.md` | | |
| TASK-030 | Update README.md with cache feature highlights | | |

**Test File Structure:**

```python
# tests/unit/logics/test_download_cache.py

"""Unit tests for download caching functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from eos_downloader.logics.download import SoftManager


class TestFileCache:
    """Test suite for file caching functionality."""
    
    def test_file_exists_and_valid_with_existing_file(self, tmp_path: Path):
        """Test cache hit when file exists."""
        # Arrange
        manager = SoftManager()
        test_file = tmp_path / "test.swi"
        test_file.write_text("test content")
        
        # Act
        result = manager._file_exists_and_valid(test_file, check_type="skip")
        
        # Assert
        assert result is True
        
    def test_file_exists_and_valid_with_missing_file(self, tmp_path: Path):
        """Test cache miss when file doesn't exist."""
        # Arrange
        manager = SoftManager()
        test_file = tmp_path / "nonexistent.swi"
        
        # Act
        result = manager._file_exists_and_valid(test_file)
        
        # Assert
        assert result is False
        
    def test_file_exists_with_checksum_validation(self, tmp_path: Path):
        """Test cache validation with checksum."""
        # Arrange
        manager = SoftManager()
        test_file = tmp_path / "test.swi"
        test_file.write_text("test content")
        checksum_file = tmp_path / "test.swi.sha512sum"
        
        with patch.object(manager, 'checksum', return_value=True):
            # Act
            result = manager._file_exists_and_valid(
                test_file,
                checksum_file=checksum_file,
                check_type="sha512sum"
            )
            
            # Assert
            assert result is True
        
    def test_file_exists_with_invalid_checksum(self, tmp_path: Path):
        """Test cache invalidation on checksum mismatch."""
        # Arrange
        manager = SoftManager()
        test_file = tmp_path / "test.swi"
        test_file.write_text("test content")
        checksum_file = tmp_path / "test.swi.sha512sum"
        
        with patch.object(manager, 'checksum', return_value=False):
            # Act
            result = manager._file_exists_and_valid(
                test_file,
                checksum_file=checksum_file,
                check_type="sha512sum"
            )
            
            # Assert
            assert result is False


class TestDockerCache:
    """Test suite for Docker image caching."""
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_docker_image_exists_returns_true(self, mock_which, mock_run):
        """Test Docker image existence check returns True."""
        # Arrange
        mock_which.return_value = '/usr/bin/docker'
        mock_run.return_value = Mock(stdout='abc123def456\n')
        
        # Act
        result = SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
        
        # Assert
        assert result is True
        mock_run.assert_called_once()
        
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_docker_image_exists_returns_false(self, mock_which, mock_run):
        """Test Docker image existence check returns False."""
        # Arrange
        mock_which.return_value = '/usr/bin/docker'
        mock_run.return_value = Mock(stdout='')
        
        # Act
        result = SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
        
        # Assert
        assert result is False
        
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_docker_image_exists_timeout(self, mock_which, mock_run):
        """Test Docker check handles timeout gracefully."""
        # Arrange
        import subprocess
        mock_which.return_value = '/usr/bin/docker'
        mock_run.side_effect = subprocess.TimeoutExpired('docker', 5)
        
        # Act
        result = SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
        
        # Assert
        assert result is False
        
    @patch('shutil.which')
    def test_docker_image_exists_no_docker(self, mock_which):
        """Test behavior when Docker is not installed."""
        # Arrange
        mock_which.return_value = None
        
        # Act
        result = SoftManager._docker_image_exists('arista/ceos', '4.29.3M')
        
        # Assert
        assert result is False


class TestCacheIntegration:
    """Integration tests for cache workflow."""
    
    @patch('eos_downloader.logics.download.SoftManager._download_file_raw')
    def test_download_with_cache_hit(self, mock_download, tmp_path: Path):
        """Test full download workflow with cache hit."""
        # Arrange
        manager = SoftManager()
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()
        cached_file = output_dir / "test.swi"
        cached_file.write_text("cached content")
        
        # Act
        result = manager.download_file(
            url="https://example.com/test.swi",
            file_path=str(output_dir),
            filename="test.swi",
            rich_interface=False
        )
        
        # Assert
        assert result == str(cached_file)
        mock_download.assert_not_called()
        
    @patch('eos_downloader.logics.download.SoftManager._download_file_raw')
    def test_download_with_force_flag(self, mock_download, tmp_path: Path):
        """Test cache bypass with --force flag."""
        # Arrange
        manager = SoftManager(force_download=True)
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()
        cached_file = output_dir / "test.swi"
        cached_file.write_text("cached content")
        mock_download.return_value = str(cached_file)
        
        # Act
        result = manager.download_file(
            url="https://example.com/test.swi",
            file_path=str(output_dir),
            filename="test.swi",
            rich_interface=False
        )
        
        # Assert
        mock_download.assert_called_once()
        
    @patch('eos_downloader.logics.download.SoftManager._docker_image_exists')
    @patch('os.system')
    def test_docker_import_with_cache_hit(self, mock_system, mock_exists, tmp_path):
        """Test Docker import skips when image exists."""
        # Arrange
        manager = SoftManager()
        test_file = tmp_path / "test.tar"
        test_file.write_text("test content")
        mock_exists.return_value = True
        
        # Act
        manager.import_docker(
            local_file_path=str(test_file),
            docker_name="arista/ceos",
            docker_tag="4.29.3M"
        )
        
        # Assert
        mock_exists.assert_called_once_with("arista/ceos", "4.29.3M")
        mock_system.assert_not_called()
        
    @patch('eos_downloader.logics.download.SoftManager._docker_image_exists')
    @patch('os.system')
    def test_docker_import_with_force_flag(self, mock_system, mock_exists, tmp_path):
        """Test Docker import with --force flag."""
        # Arrange
        manager = SoftManager(force_download=True)
        test_file = tmp_path / "test.tar"
        test_file.write_text("test content")
        mock_exists.return_value = True
        
        # Act
        manager.import_docker(
            local_file_path=str(test_file),
            docker_name="arista/ceos",
            docker_tag="4.29.3M"
        )
        
        # Assert
        mock_system.assert_called_once()
```

## 3. Alternatives

### Alternative Approaches Considered

- **ALT-001**: **Database-backed cache with metadata**
  - **Description**: Use SQLite database to track downloaded files with metadata (download date, checksum, source URL)
  - **Pros**: More robust tracking, easier cache management, supports advanced queries
  - **Cons**: Adds complexity, requires schema management, overkill for simple cache
  - **Reason Not Chosen**: Simple filesystem-based approach is sufficient and maintains simplicity

- **ALT-002**: **Content-addressable storage (CAS) using file hashes**
  - **Description**: Store files using their hash as filename (like Git objects)
  - **Pros**: Automatic deduplication, robust integrity checking
  - **Cons**: Complex to implement, breaks user-friendly filenames, requires significant refactoring
  - **Reason Not Chosen**: Too complex for user-facing download tool; users expect normal filenames

- **ALT-003**: **Separate cache directory with symlinks**
  - **Description**: Store actual files in `~/.eos-downloader/cache` and symlink to output directory
  - **Pros**: Centralized cache, better disk space usage, works across projects
  - **Cons**: Symlinks may confuse users, permission issues, Windows compatibility concerns
  - **Reason Not Chosen**: Added complexity without significant benefit; users prefer files in specified location

- **ALT-004**: **HTTP ETag-based caching**
  - **Description**: Use HTTP ETags to check if remote file has changed before downloading
  - **Pros**: Ensures local file is up-to-date, leverages HTTP caching standards
  - **Cons**: Requires API support for ETags, extra network round-trip, complex to implement
  - **Reason Not Chosen**: Arista API may not support ETags; local checksums are sufficient

## 4. Dependencies

### External Dependencies

- **DEP-001**: No new external Python packages required
- **DEP-002**: Requires `docker` or `podman` CLI for Docker image checking (already required)
- **DEP-003**: Requires `subprocess` module (Python stdlib)
- **DEP-004**: Requires `pathlib` module (Python stdlib)

### Internal Dependencies

- **DEP-005**: `SoftManager` class in `eos_downloader/logics/download.py`
- **DEP-006**: CLI commands in `eos_downloader/cli/get/commands.py`
- **DEP-007**: Utility functions in `eos_downloader/cli/get/utils.py`
- **DEP-008**: Rich Console for output formatting

### Documentation Dependencies

- **DEP-009**: Update user documentation in `docs/` directory
- **DEP-010**: Update help text in CLI commands
- **DEP-011**: Update examples in README.md

## 5. Files

### Files to Modify

- **FILE-001**: `eos_downloader/logics/download.py`
  - Add `_file_exists_and_valid()` method
  - Add `_docker_image_exists()` static method
  - Modify `__init__()` to accept `force_download` parameter
  - Modify `download_file()` to check cache
  - Modify `downloads()` to check cache
  - Modify `import_docker()` to check Docker registry

- **FILE-002**: `eos_downloader/cli/get/commands.py`
  - Add `--force` flag to `eos` command
  - Add `--force` flag to `cvp` command
  - Add `--force` flag to `path` command
  - Add `--cache-dir` option to commands
  - Pass `force` parameter to `SoftManager` initialization

- **FILE-003**: `eos_downloader/cli/get/utils.py`
  - Modify `download_files()` to show cache status
  - Modify `handle_docker_import()` to show cache status
  - Add cache statistics tracking

- **FILE-004**: `docs/usage/eos.md`
  - Add examples of cache usage
  - Document `--force` flag
  - Document `--cache-dir` option

- **FILE-005**: `docs/usage/cvp.md`
  - Add examples of cache usage
  - Document `--force` flag

- **FILE-006**: `docs/faq.md`
  - Add FAQ about cache behavior
  - Add troubleshooting for cache issues

- **FILE-007**: `README.md`
  - Add cache feature to feature list
  - Add basic cache usage example

### Files to Create

- **FILE-008**: `tests/unit/logics/test_download_cache.py`
  - New test file for cache functionality

- **FILE-009**: `tests/integration/test_cache_workflow.py`
  - New integration test file for end-to-end cache testing

## 6. Testing

### Unit Tests

- **TEST-001**: Test `_file_exists_and_valid()` with existing file
- **TEST-002**: Test `_file_exists_and_valid()` with missing file
- **TEST-003**: Test `_file_exists_and_valid()` with checksum validation success
- **TEST-004**: Test `_file_exists_and_valid()` with checksum validation failure
- **TEST-005**: Test `_docker_image_exists()` returns True when image exists
- **TEST-006**: Test `_docker_image_exists()` returns False when image missing
- **TEST-007**: Test `_docker_image_exists()` handles Docker not installed
- **TEST-008**: Test `_docker_image_exists()` handles Docker daemon not running
- **TEST-009**: Test `_docker_image_exists()` handles timeout
- **TEST-010**: Test `download_file()` uses cache when file exists
- **TEST-011**: Test `download_file()` downloads when force=True
- **TEST-012**: Test `import_docker()` skips when image exists
- **TEST-013**: Test `import_docker()` imports when force=True

### Integration Tests

- **TEST-014**: Test complete download workflow with cache hit
- **TEST-015**: Test complete download workflow with cache miss
- **TEST-016**: Test download with --force flag bypasses cache
- **TEST-017**: Test Docker import workflow with existing image
- **TEST-018**: Test Docker import workflow with --force flag
- **TEST-019**: Test cache behavior in dry-run mode
- **TEST-020**: Test checksum validation triggers re-download

### Manual Test Scenarios

- **TEST-021**: Download same EOS version twice, verify second is cached
- **TEST-022**: Import same Docker image twice, verify second is skipped
- **TEST-023**: Use --force flag and verify cache is bypassed
- **TEST-024**: Delete cached file, verify re-download
- **TEST-025**: Corrupt cached file, verify checksum fails and triggers re-download

## 7. Risks & Assumptions

### Risks

- **RISK-001**: **Race condition in concurrent downloads**
  - **Severity**: Medium
  - **Probability**: Low
  - **Mitigation**: Use file locking or atomic operations for cache checks
  - **Fallback**: Document that concurrent downloads to same location are not supported

- **RISK-002**: **Disk space exhaustion with large cache**
  - **Severity**: Medium
  - **Probability**: Medium
  - **Mitigation**: Add cache size monitoring and warning messages
  - **Fallback**: Users can manually clean cache directory

- **RISK-003**: **Docker daemon unavailable during check**
  - **Severity**: Low
  - **Probability**: Medium
  - **Mitigation**: Handle gracefully with timeout and fallback to import anyway
  - **Fallback**: Skip cache check and proceed with import

- **RISK-004**: **Checksum file missing for cached file**
  - **Severity**: Low
  - **Probability**: Low
  - **Mitigation**: Download checksum file if missing, or skip validation
  - **Fallback**: Allow using cached file without validation with warning

- **RISK-005**: **Performance impact of Docker image checks**
  - **Severity**: Low
  - **Probability**: Low
  - **Mitigation**: Use short timeout (5s), cache result in memory during single run
  - **Fallback**: Provide option to disable Docker cache checking

### Assumptions

- **ASSUMPTION-001**: Users have stable filesystem with reliable file metadata
- **ASSUMPTION-002**: Docker/Podman CLI commands remain stable across versions
- **ASSUMPTION-003**: File checksums are reliable indicators of file integrity
- **ASSUMPTION-004**: Users understand what "cache" means in this context
- **ASSUMPTION-005**: Most users download to same location repeatedly (home directory, project folder)
- **ASSUMPTION-006**: Network download is significantly slower than local cache check
- **ASSUMPTION-007**: Docker registry queries are fast (<1 second) in normal conditions

## 8. Related Specifications / Further Reading

### Internal Documentation

- [Python Coding Standards](.github/instructions/python.instructions.md)
- [Testing Guidelines](.github/instructions/testing.instructions.md)
- [Arista Domain Instructions](.github/instructions/arista-domain.instructions.md)
- [User Documentation - EOS](docs/usage/eos.md)
- [FAQ](docs/faq.md)

### External References

- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)
- [Podman CLI Reference](https://docs.podman.io/en/latest/Commands.html)
- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Rich Progress Documentation](https://rich.readthedocs.io/en/stable/progress.html)

### Similar Implementations

- **Pip package cache**: `~/.cache/pip/` - stores downloaded packages
- **Docker layer cache**: Docker's built-in layer caching mechanism
- **Git object store**: Content-addressable storage for version control
- **Homebrew cache**: `/Library/Caches/Homebrew/` - caches downloaded formulas

---

## Appendix A: Example Usage

### Before (Current Behavior)

```bash
# First download
$ ardl get eos --version 4.29.3M --format cEOS --output ~/downloads
Downloading EOS-4.29.3M-cEOS.tar.xz...
Downloaded: ~/downloads/EOS-4.29.3M-cEOS.tar.xz (500 MB)

# Second download - unnecessarily downloads again
$ ardl get eos --version 4.29.3M --format cEOS --output ~/downloads
Downloading EOS-4.29.3M-cEOS.tar.xz...
Downloaded: ~/downloads/EOS-4.29.3M-cEOS.tar.xz (500 MB)
```

### After (With Caching)

```bash
# First download
$ ardl get eos --version 4.29.3M --format cEOS --output ~/downloads
Downloading EOS-4.29.3M-cEOS.tar.xz...
Downloaded: ~/downloads/EOS-4.29.3M-cEOS.tar.xz (500 MB)

# Second download - uses cache
$ ardl get eos --version 4.29.3M --format cEOS --output ~/downloads
Checking cache in ~/downloads...
✓ Using cached file: EOS-4.29.3M-cEOS.tar.xz
  Use --force to re-download

# Force re-download
$ ardl get eos --version 4.29.3M --format cEOS --output ~/downloads --force
Downloading EOS-4.29.3M-cEOS.tar.xz...
Downloaded: ~/downloads/EOS-4.29.3M-cEOS.tar.xz (500 MB)
```

### Docker Import with Cache

```bash
# First import
$ ardl get eos --version 4.29.3M --format cEOS --import-docker --docker-name arista/ceos --docker-tag 4.29.3M
Downloading EOS-4.29.3M-cEOS.tar.xz...
Downloaded: ~/downloads/EOS-4.29.3M-cEOS.tar.xz
Importing docker image arista/ceos:4.29.3M...
Docker image imported successfully

# Second import - skips (image already exists)
$ ardl get eos --version 4.29.3M --format cEOS --import-docker --docker-name arista/ceos --docker-tag 4.29.3M
Checking cache in ./...
✓ Using cached file: EOS-4.29.3M-cEOS.tar.xz
  Use --force to re-download
✓ Docker image arista/ceos:4.29.3M already exists
  Use --force to re-import
```

## Appendix B: Performance Impact

### Expected Performance Improvements

| Scenario | Current Time | With Cache | Improvement |
|----------|--------------|------------|-------------|
| Re-download 500MB file | 60 seconds | <1 second | 60x faster |
| Re-import Docker image | 30 seconds | <1 second | 30x faster |
| Download 10 files | 10 minutes | Mixed | 2-10x faster |

### Cache Check Overhead

- File existence check: <10ms
- Checksum validation: ~1-5 seconds for 500MB file
- Docker image check: 100-500ms
- Total overhead: Negligible compared to download time

---

**End of Implementation Plan**

*This plan ensures efficient resource usage and improved user experience by eliminating redundant downloads and imports.*
