import os
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from eos_downloader.logics.download import SoftManager
from eos_downloader.logics.arista_xml_server import EosXmlObject


@pytest.fixture
def soft_manager():
    return SoftManager()


@pytest.fixture
def soft_manager_force():
    """SoftManager with force_download enabled."""
    return SoftManager(force_download=True)


@pytest.fixture
def mock_eos_object():
    mock = Mock(spec=EosXmlObject)
    mock.version = "4.28.0F"
    mock.filename = "EOS-4.28.0F.swi"
    mock.urls = {
        "image": "http://example.com/EOS-4.28.0F.swi",
        "md5sum": "http://example.com/EOS-4.28.0F.swi.md5",
        "sha512sum": "http://example.com/EOS-4.28.0F.swi.sha512",
    }
    mock.hash_filename = Mock(return_value="EOS-4.28.0F.swi.md5")
    return mock


@pytest.mark.parametrize("dry_run,force_download", [
    (True, False),
    (False, False),
    (False, True),
    (True, True),
])
def test_soft_manager_init(dry_run, force_download):
    """Test SoftManager initialization with various flags."""
    manager = SoftManager(dry_run=dry_run, force_download=force_download)
    assert manager.dry_run == dry_run
    assert manager.force_download == force_download
    assert manager.file == {"name": None, "md5sum": None, "sha512sum": None}


@patch("requests.get")
@patch("tqdm.tqdm")
def test_download_file_raw(mock_tqdm, mock_requests):
    # Setup mock response
    mock_response = Mock()
    mock_response.headers = {"Content-Length": "1024"}
    mock_response.iter_content.return_value = [b"data"]
    mock_requests.return_value = mock_response

    with patch("builtins.open", mock_open()) as mock_file:
        result = SoftManager._download_file_raw("http://test.com/file", "/tmp/file")
        assert result == "/tmp/file"
        mock_file().write.assert_called_with(b"data")


@patch("os.makedirs")
def test_create_destination_folder(mock_makedirs):
    SoftManager._create_destination_folder("/test/path")
    mock_makedirs.assert_called_once_with("/test/path", exist_ok=True)


def test_compute_hash_md5sum(soft_manager):
    test_data = b"test data"
    expected_hash = "eb733a00c0c9d336e65691a37ab54293"

    with patch("builtins.open", mock_open(read_data=test_data)):
        result = soft_manager._compute_hash_md5sum("test_file", expected_hash)
        assert result is True

        # Test with incorrect hash
        result = soft_manager._compute_hash_md5sum("test_file", "wrong_hash")
        assert result is False


# @pytest.mark.parametrize(
#     "check_type,valid_hash", [("md5sum", True), ("sha512sum", True)]
# )
# def test_checksum(soft_manager, check_type, valid_hash):
#     soft_manager.file = {
#         "name": "test.swi",
#         "md5sum": "test.swi.md5",
#         "sha512sum": "test.swi.sha512",
#     }

#     mock_hash = "a" * (128 if check_type == "sha512sum" else 32)

#     with patch(
#         "builtins.open",
#         mock_open(read_data=f"{mock_hash if valid_hash else 'wrong'} test.swi"),
#     ) as mock_file:
#         if valid_hash:
#             with patch(
#                 "hashlib.sha512" if check_type == "sha512sum" else "hashlib.md5"
#             ) as mock_hash_func:
#                 mock_hash_instance = Mock()
#                 mock_hash_instance.hexdigest.return_value = mock_hash
#                 mock_hash_func.return_value = mock_hash_instance
#                 assert soft_manager.checksum(check_type) is True
#         else:
#             with pytest.raises(ValueError):
#                 soft_manager.checksum(check_type)


@patch("eos_downloader.logics.download.SoftManager._download_file_raw")
@patch("eos_downloader.helpers.DownloadProgressBar")
def test_download_file(mock_progress_bar, mock_download_raw, soft_manager):
    url = "http://test.com/file"
    file_path = "/tmp"
    filename = "test.swi"

    # Test with rich interface
    result = soft_manager.download_file(url, file_path, filename, rich_interface=True)
    assert result == os.path.join(file_path, filename)
    mock_progress_bar.assert_called_once()


@patch("eos_downloader.logics.download.SoftManager.download_file")
def test_downloads(mock_download, soft_manager, mock_eos_object):
    result = soft_manager.downloads(
        mock_eos_object, "/tmp/downloads", rich_interface=True
    )
    assert result == "/tmp/downloads"
    assert mock_download.call_count == len(mock_eos_object.urls)


@patch("shutil.which")
@patch("os.system")
def test_import_docker(mock_system, mock_which, soft_manager):
    mock_which.return_value = "/usr/bin/docker"

    # Test with existing file
    with patch("os.path.exists", return_value=True):
        soft_manager.import_docker("/tmp/test.swi", "arista/ceos", "latest")
        mock_system.assert_called_once()

    # Test with non-existing file
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            soft_manager.import_docker("/tmp/nonexistent.swi")


@patch("os.system")
@patch("os.path.exists")
def test_provision_eve(mock_exists, mock_system, soft_manager, mock_eos_object):
    mock_exists.return_value = False

    with patch("eos_downloader.logics.download.SoftManager.download_file"):
        soft_manager.provision_eve(mock_eos_object, noztp=False)
        # Check if qemu-img convert and unl_wrapper commands were called
        assert mock_system.call_count == 2


# ============================================================================
# CACHE TESTS - Phase 5
# ============================================================================


class TestFileCache:
    """Test suite for file caching functionality."""

    @patch("pathlib.Path.exists")
    def test_file_exists_and_valid_file_not_found(self, mock_exists):
        """Test that cache check returns False when file doesn't exist."""
        mock_exists.return_value = False
        manager = SoftManager()
        result = manager._file_exists_and_valid(Path("/tmp/test.swi"))
        assert result is False

    @patch("pathlib.Path.exists")
    def test_file_exists_and_valid_skip_checksum(self, mock_exists):
        """Test cache check with skip checksum returns True if file exists."""
        mock_exists.return_value = True
        manager = SoftManager()
        result = manager._file_exists_and_valid(
            Path("/tmp/test.swi"),
            check_type="skip"
        )
        assert result is True

    @patch("pathlib.Path.exists")
    @patch("eos_downloader.logics.download.SoftManager.checksum")
    def test_file_exists_and_valid_with_checksum(
        self, mock_checksum, mock_exists
    ):
        """Test cache check validates checksum when requested."""
        mock_exists.return_value = True
        mock_checksum.return_value = True
        manager = SoftManager()
        manager.file = {"name": "test.swi"}

        result = manager._file_exists_and_valid(
            Path("/tmp/test.swi"),
            checksum_file=Path("/tmp/test.swi.md5"),
            check_type="md5sum"
        )
        assert result is True
        mock_checksum.assert_called_once_with(check_type="md5sum")

    @patch("pathlib.Path.exists")
    @patch("eos_downloader.logics.download.SoftManager.checksum")
    def test_file_exists_and_valid_checksum_fails(
        self, mock_checksum, mock_exists
    ):
        """Test cache check returns False when checksum validation fails."""
        mock_exists.return_value = True
        mock_checksum.side_effect = ValueError("Checksum mismatch")
        manager = SoftManager()
        manager.file = {"name": "test.swi"}

        result = manager._file_exists_and_valid(
            Path("/tmp/test.swi"),
            checksum_file=Path("/tmp/test.swi.md5"),
            check_type="md5sum"
        )
        assert result is False

    @patch("pathlib.Path.exists")
    @patch("eos_downloader.logics.download.SoftManager._download_file_raw")
    def test_download_file_uses_cache(self, mock_download, mock_exists):
        """Test that download_file uses cached file when available."""
        mock_exists.return_value = True
        manager = SoftManager()

        cached_path = manager.download_file(
            "http://test.com/file.swi",
            "/tmp",
            "test.swi",
            rich_interface=False
        )

        # Should return cached path without downloading
        assert cached_path == "/tmp/test.swi"
        mock_download.assert_not_called()

    @patch("pathlib.Path.exists")
    @patch("eos_downloader.logics.download.SoftManager._download_file_raw")
    def test_download_file_bypasses_cache_with_force(
        self, mock_download, mock_exists
    ):
        """Test that force flag bypasses cache."""
        mock_exists.return_value = True
        mock_download.return_value = "/tmp/test.swi"
        manager = SoftManager(force_download=True)

        downloaded_path = manager.download_file(
            "http://test.com/file.swi",
            "/tmp",
            "test.swi",
            rich_interface=False
        )

        # Should download despite cache
        assert downloaded_path is not None
        mock_download.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("eos_downloader.logics.download.SoftManager._download_file_raw")
    def test_download_file_force_parameter(self, mock_download, mock_exists):
        """Test that force parameter overrides cache."""
        mock_exists.return_value = True
        mock_download.return_value = "/tmp/test.swi"
        manager = SoftManager()

        forced_path = manager.download_file(
            "http://test.com/file.swi",
            "/tmp",
            "test.swi",
            rich_interface=False,
            force=True
        )

        # Should download despite cache
        assert forced_path is not None
        mock_download.assert_called_once()


class TestDockerCache:
    """Test suite for Docker image caching functionality."""

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_docker_image_exists_found(self, mock_which, mock_run):
        """Test that _docker_image_exists returns True when image found."""
        mock_which.return_value = "/usr/bin/docker"
        mock_result = Mock()
        mock_result.stdout = "abc123def456\n"
        mock_run.return_value = mock_result

        result = SoftManager._docker_image_exists("arista/ceos", "4.29.3M")
        assert result is True

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_docker_image_exists_not_found(self, mock_which, mock_run):
        """Test that _docker_image_exists returns False when image missing."""
        mock_which.return_value = "/usr/bin/docker"
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = SoftManager._docker_image_exists("arista/ceos", "4.29.3M")
        assert result is False

    @patch("shutil.which")
    def test_docker_image_exists_no_docker(self, mock_which):
        """Test graceful handling when docker/podman not available."""
        mock_which.return_value = None

        result = SoftManager._docker_image_exists("arista/ceos", "4.29.3M")
        assert result is False

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_docker_image_exists_podman_fallback(self, mock_which, mock_run):
        """Test that podman is tried when docker is unavailable."""
        # Docker not found, podman found
        mock_which.side_effect = lambda x: (
            "/usr/bin/podman" if x == "podman" else None
        )
        mock_result = Mock()
        mock_result.stdout = "image123\n"
        mock_run.return_value = mock_result

        result = SoftManager._docker_image_exists("arista/ceos", "4.29.3M")
        assert result is True

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_docker_image_exists_timeout(self, mock_which, mock_run):
        """Test handling of subprocess timeout."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.side_effect = Exception("Timeout")

        result = SoftManager._docker_image_exists("arista/ceos", "4.29.3M")
        assert result is False

    @patch("eos_downloader.logics.download.SoftManager._docker_image_exists")
    @patch("os.path.exists")
    @patch("os.system")
    @patch("shutil.which")
    def test_import_docker_uses_cache(
        self, mock_which, mock_system, mock_exists, mock_docker_exists
    ):
        """Test that import_docker skips import when image exists."""
        mock_which.return_value = "/usr/bin/docker"
        mock_exists.return_value = True
        mock_docker_exists.return_value = True

        manager = SoftManager()
        manager.import_docker("/tmp/test.tar", "arista/ceos", "4.29.3M")

        # Should not call docker import
        mock_system.assert_not_called()

    @patch("eos_downloader.logics.download.SoftManager._docker_image_exists")
    @patch("os.path.exists")
    @patch("os.system")
    @patch("shutil.which")
    def test_import_docker_force_reimport(
        self, mock_which, mock_system, mock_exists, mock_docker_exists
    ):
        """Test that force flag causes re-import."""
        mock_which.return_value = "/usr/bin/docker"
        mock_exists.return_value = True
        mock_docker_exists.return_value = True

        manager = SoftManager()
        manager.import_docker(
            "/tmp/test.tar",
            "arista/ceos",
            "4.29.3M",
            force=True
        )

        # Should call docker import despite cache
        mock_system.assert_called_once()

    @patch("eos_downloader.logics.download.SoftManager._docker_image_exists")
    @patch("os.path.exists")
    @patch("os.system")
    @patch("shutil.which")
    def test_import_docker_force_download_flag(
        self, mock_which, mock_system, mock_exists, mock_docker_exists
    ):
        """Test that force_download flag causes re-import."""
        mock_which.return_value = "/usr/bin/docker"
        mock_exists.return_value = True
        mock_docker_exists.return_value = True

        manager = SoftManager(force_download=True)
        manager.import_docker("/tmp/test.tar", "arista/ceos", "4.29.3M")

        # Should call docker import
        mock_system.assert_called_once()


class TestCacheIntegration:
    """Integration tests for cache functionality."""

    @patch("eos_downloader.logics.download.SoftManager.download_file")
    def test_downloads_propagates_force_flag(self, mock_download):
        """Test that downloads() propagates force_download to download_file."""
        mock_eos = Mock()
        mock_eos.version = "4.29.3M"
        mock_eos.filename = "test.swi"
        mock_eos.urls = {"image": "http://test.com/test.swi"}
        mock_eos.hash_filename = Mock(return_value="test.swi.md5")

        manager = SoftManager(force_download=True)
        manager.downloads(mock_eos, "/tmp")

        # Verify force was passed to download_file
        mock_download.assert_called()
        call_kwargs = mock_download.call_args[1]
        assert call_kwargs.get("force") is True

    @patch("pathlib.Path.exists")
    def test_dry_run_with_cache(self, mock_exists):
        """Test dry-run mode reports cache status correctly."""
        mock_exists.return_value = True

        mock_eos = Mock()
        mock_eos.version = "4.29.3M"
        mock_eos.filename = "test.swi"
        mock_eos.urls = {"image": "http://test.com/test.swi"}
        mock_eos.hash_filename = Mock(return_value="test.swi.md5")

        manager = SoftManager(dry_run=True)
        result = manager.downloads(mock_eos, "/tmp")

        # Should complete without actual download
        assert result == "/tmp"
