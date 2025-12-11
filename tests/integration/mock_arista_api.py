#!/usr/bin/env python
# coding: utf-8 -*-
"""Mock Arista API fixtures for integration tests.

Provides complete mock responses for Arista software download API.
Uses responses library to mock HTTP requests.
"""

from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import pytest
import responses

from eos_downloader.defaults import (
    DEFAULT_SOFTWARE_FOLDER_TREE,
    DEFAULT_DOWNLOAD_URL,
    DEFAULT_SERVER_SESSION,
)


MOCK_XML_CATALOG = """<?xml version="1.0"?>
<cvpFolderList>
    <dir label="EOS">
        <dir label="Active Releases">
            <dir label="4.32">
                <dir label="EOS-4.32.3M">
                    <dir label="vEOS-lab">
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/vEOS-lab/vEOS-lab-4.32.3M.vmdk">vEOS-lab-4.32.3M.vmdk</file>
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/vEOS-lab/vEOS-lab-4.32.3M.vmdk.md5sum">vEOS-lab-4.32.3M.vmdk.md5sum</file>
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/vEOS-lab/vEOS-lab-4.32.3M.vmdk.sha512sum">vEOS-lab-4.32.3M.vmdk.sha512sum</file>
                    </dir>
                    <dir label="cEOS-lab">
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/cEOS-lab/cEOS-lab-4.32.3M.tar.xz">cEOS-lab-4.32.3M.tar.xz</file>
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/cEOS-lab/cEOS-lab-4.32.3M.tar.xz.md5sum">cEOS-lab-4.32.3M.tar.xz.md5sum</file>
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/cEOS-lab/cEOS-lab-4.32.3M.tar.xz.sha512sum">cEOS-lab-4.32.3M.tar.xz.sha512sum</file>
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/cEOS-lab/cEOS64-lab-4.32.3M.tar.xz">cEOS64-lab-4.32.3M.tar.xz</file>
                    </dir>
                    <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/EOS-4.32.3M.swi">EOS-4.32.3M.swi</file>
                    <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/EOS-4.32.3M.swi.md5sum">EOS-4.32.3M.swi.md5sum</file>
                    <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/EOS-4.32.3M.swi.sha512sum">EOS-4.32.3M.swi.sha512sum</file>
                    <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.3M/EOS64-4.32.3M.swi">EOS64-4.32.3M.swi</file>
                </dir>
                <dir label="EOS-4.32.2F">
                    <dir label="vEOS-lab">
                        <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.2F/vEOS-lab/vEOS-lab-4.32.2F.vmdk">vEOS-lab-4.32.2F.vmdk</file>
                    </dir>
                    <file path="/support/download/EOS-USA/Active Releases/4.32/EOS-4.32.2F/EOS-4.32.2F.swi">EOS-4.32.2F.swi</file>
                </dir>
            </dir>
            <dir label="4.31">
                <dir label="EOS-4.31.5M">
                    <file path="/support/download/EOS-USA/Active Releases/4.31/EOS-4.31.5M/EOS-4.31.5M.swi">EOS-4.31.5M.swi</file>
                    <file path="/support/download/EOS-USA/Active Releases/4.31/EOS-4.31.5M/EOS64-4.31.5M.swi">EOS64-4.31.5M.swi</file>
                </dir>
            </dir>
        </dir>
    </dir>
    <dir label="CloudVision">
        <dir label="Active Releases">
            <dir label="cloudvision-2024.3.0">
                <file path="/support/download/CloudVision/Active Releases/cloudvision-2024.3.0/cvp-rpm-installer-2024.3.0-1.x86_64.rpm">cvp-rpm-installer-2024.3.0-1.x86_64.rpm</file>
                <file path="/support/download/CloudVision/Active Releases/cloudvision-2024.3.0/cvp-upgrade-2024.3.0.tgz">cvp-upgrade-2024.3.0.tgz</file>
            </dir>
            <dir label="cloudvision-2024.2.1">
                <file path="/support/download/CloudVision/Active Releases/cloudvision-2024.2.1/cvp-rpm-installer-2024.2.1-1.x86_64.rpm">cvp-rpm-installer-2024.2.1-1.x86_64.rpm</file>
            </dir>
        </dir>
    </dir>
</cvpFolderList>
"""

MOCK_DOWNLOAD_RESPONSE = {
    "data": {
        "url": "https://download.arista.com/mock/EOS-4.32.3M.swi",
        "size": 1024000,
        "md5sum": "abc123def456",
        "sha512sum": "sha512abcdef1234567890",
    }
}

MOCK_SESSION_RESPONSE = {
    "status": {"message": "Session created successfully"},
    "data": {"session_code": "mock-session-12345"},
}


@pytest.fixture
def mock_xml_catalog() -> str:
    """Return mock XML catalog for Arista software."""
    return MOCK_XML_CATALOG


@pytest.fixture
def mock_xml_element() -> ET.Element:
    """Return parsed mock XML as ElementTree Element."""
    return ET.fromstring(MOCK_XML_CATALOG)


@pytest.fixture
def mock_arista_token() -> str:
    """Return a mock Arista API token for testing."""
    return "mock-token-abcdef123456789012345678"


@pytest.fixture
def mock_download_dir(tmp_path: Path) -> Path:
    """Create and return a temporary download directory."""
    download_dir = tmp_path / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    return download_dir


@pytest.fixture
def mock_eos_image_content() -> bytes:
    """Return mock EOS image content for download tests."""
    return b"MOCK_EOS_IMAGE_CONTENT_" + b"x" * 1000


@pytest.fixture
def mock_checksum_content() -> str:
    """Return mock checksum file content."""
    return "abc123def456  EOS-4.32.3M.swi\n"


@pytest.fixture
def mock_arista_api_responses(mock_xml_catalog: str, mock_eos_image_content: bytes):
    """Set up mock responses for all Arista API endpoints.

    This fixture mocks:
    - Session authentication
    - Software folder tree (XML catalog)
    - Download URL generation
    - Actual file download
    """
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            DEFAULT_SERVER_SESSION,
            json=MOCK_SESSION_RESPONSE,
            status=200,
        )

        rsps.add(
            responses.POST,
            DEFAULT_SOFTWARE_FOLDER_TREE,
            json={"data": {"xml": mock_xml_catalog}},
            status=200,
        )

        rsps.add(
            responses.POST,
            DEFAULT_DOWNLOAD_URL,
            json=MOCK_DOWNLOAD_RESPONSE,
            status=200,
        )

        rsps.add(
            responses.GET,
            "https://download.arista.com/mock/EOS-4.32.3M.swi",
            body=mock_eos_image_content,
            status=200,
            content_type="application/octet-stream",
        )

        rsps.add(
            responses.GET,
            "https://download.arista.com/mock/EOS-4.32.3M.swi.md5sum",
            body="abc123def456  EOS-4.32.3M.swi\n",
            status=200,
            content_type="text/plain",
        )

        yield rsps


@pytest.fixture
def mock_arista_api_auth_error():
    """Set up mock responses for authentication error (401)."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            DEFAULT_SERVER_SESSION,
            json={"error": "Unauthorized"},
            status=401,
        )
        rsps.add(
            responses.POST,
            DEFAULT_SOFTWARE_FOLDER_TREE,
            json={"error": "Unauthorized"},
            status=401,
        )
        yield rsps


@pytest.fixture
def mock_arista_api_rate_limit():
    """Set up mock responses for rate limiting (429)."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            DEFAULT_SERVER_SESSION,
            json=MOCK_SESSION_RESPONSE,
            status=200,
        )
        rsps.add(
            responses.POST,
            DEFAULT_SOFTWARE_FOLDER_TREE,
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"},
        )
        yield rsps


@pytest.fixture
def mock_arista_api_network_error():
    """Set up mock responses that simulate network errors."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            DEFAULT_SOFTWARE_FOLDER_TREE,
            body=responses.ConnectionError("Network unreachable"),
        )
        yield rsps


@pytest.fixture
def integration_test_data() -> dict[str, Any]:
    """Return test data for integration tests."""
    return {
        "eos_versions": [
            {"version": "4.32.3M", "branch": "4.32", "rtype": "M"},
            {"version": "4.32.2F", "branch": "4.32", "rtype": "F"},
            {"version": "4.31.5M", "branch": "4.31", "rtype": "M"},
        ],
        "cvp_versions": [
            {"version": "2024.3.0"},
            {"version": "2024.2.1"},
        ],
        "image_formats": ["64", "vEOS-lab", "cEOS", "cEOS64"],
        "expected_files": {
            "4.32.3M": {
                "64": "EOS64-4.32.3M.swi",
                "vEOS-lab": "vEOS-lab-4.32.3M.vmdk",
                "cEOS": "cEOS-lab-4.32.3M.tar.xz",
                "cEOS64": "cEOS64-lab-4.32.3M.tar.xz",
            }
        },
    }
