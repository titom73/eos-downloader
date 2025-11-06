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
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        with pytest.raises(KeyError):
            server.get_xml_data()


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
