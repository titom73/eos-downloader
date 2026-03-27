import pytest
import requests
from unittest.mock import patch, Mock
from eos_downloader.logics.arista_server import AristaServer

import eos_downloader.exceptions

from tests.lib.fixtures import xml_path, xml_data


@pytest.fixture
def server():
    return AristaServer(token="testtoken")


def test_authenticate_success(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
            "data": {"session_code": "testsessioncode"},
        }
        mock_post.return_value = mock_response

        assert server.authenticate() is True
        assert server._session_id is not None


def test_authenticate_invalid_token(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Invalid access token"}
        }
        mock_post.return_value = mock_response

        with pytest.raises(eos_downloader.exceptions.AuthenticationError):
            server.authenticate()


def test_authenticate_expired_token(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Access token expired"}
        }
        mock_post.return_value = mock_response

        with pytest.raises(eos_downloader.exceptions.AuthenticationError):
            server.authenticate()


def test_authenticate_key_error(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"status": {"message": "Success"}}
        mock_post.return_value = mock_response

        assert server.authenticate() is False
        assert server._session_id is None


def test_get_xml_data_success(server, xml_path):
    with patch("requests.post") as mock_post:
        with open(xml_path, "r") as file:
            xml_content = file.read()

        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
            "data": {"xml": xml_content},
        }
        mock_post.return_value = mock_response

        xml_data = server.get_xml_data()
        assert xml_data is not None
        assert (
            xml_data.getroot().tag == "cvpFolderList"
        )  # Assuming the root tag in data.xml is 'cvpFolderList'


def test_get_xml_data_key_error(server):
    """Test get_xml_data with completely empty response."""
    server._session_id = "test-session"
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        result = server.get_xml_data()
        assert result is None


def test_get_url_success(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
            "data": {"url": "http://example.com/download"},
        }
        mock_post.return_value = mock_response

        url = server.get_url("remote/file/path")
        assert url == "http://example.com/download"


def test_get_url_no_data(server):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
        }
        mock_post.return_value = mock_response

        url = server.get_url("remote/file/path")
        assert url is None


def test_authenticate_token_none():
    """Test authenticate returns False when token is None (lines 155, 157-158)."""
    server = AristaServer(token=None)
    assert server.authenticate() is False


def test_authenticate_with_param_token():
    """Test authenticate accepts token parameter."""
    server = AristaServer(token=None)
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
            "data": {"session_code": "test-session"},
        }
        mock_post.return_value = mock_response

        result = server.authenticate(token="new-token")
        assert result is True
        assert server.token == "new-token"


def test_get_url_network_error(server):
    """Test get_url handles network errors (lines 228-236)."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        # Response without 'data' key and without 'url' key
        mock_response.json.return_value = {
            "status": {"message": "Error"},
            "data": {"error": "something went wrong"},
        }
        mock_post.return_value = mock_response

        url = server.get_url("remote/file/path")
        assert url is None


def test_get_url_triggers_auth_when_no_session(server):
    """Test get_url triggers authentication when session_id is None (lines 228-229)."""
    server._session_id = None
    with patch("requests.post") as mock_post:
        # First call is authenticate, second is get_url
        mock_auth_response = Mock()
        mock_auth_response.json.return_value = {
            "status": {"message": "Success"},
            "data": {"session_code": "new-session"},
        }
        mock_url_response = Mock()
        mock_url_response.json.return_value = {
            "data": {"url": "https://example.com/download"},
        }
        mock_post.side_effect = [mock_auth_response, mock_url_response]

        url = server.get_url("remote/file/path")
        assert url == "https://example.com/download"
        assert mock_post.call_count == 2


def test_authenticate_no_data_in_response(server):
    """Test authenticate returns False when response has no 'data' key (line 188)."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"message": "Success"},
            # No 'data' key
        }
        mock_post.return_value = mock_response

        result = server.authenticate()
        assert result is False


def test_get_xml_data_parse_error(server):
    """Test get_xml_data returns None on XML ParseError (lines 234-236)."""
    server._session_id = "test-session"
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"xml": "this is not valid xml <<<<"},
        }
        mock_post.return_value = mock_response

        result = server.get_xml_data()
        assert result is None


def test_get_xml_data_returns_none_on_key_error(server):
    """Test get_xml_data returns None on KeyError (lines 231-232)."""
    server._session_id = "test-session"
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"no_xml_key": "something"},
        }
        mock_post.return_value = mock_response

        result = server.get_xml_data()
        assert result is None
