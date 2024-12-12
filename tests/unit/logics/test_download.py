import os
import pytest
from unittest.mock import Mock, patch, mock_open
from eos_downloader.logics.download import SoftManager
from eos_downloader.logics.arista_server import EosXmlObject


@pytest.fixture
def soft_manager():
    return SoftManager()


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


@pytest.mark.parametrize("dry_run", [True, False])
def test_soft_manager_init(dry_run):
    manager = SoftManager(dry_run=dry_run)
    assert manager.dry_run == dry_run
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
