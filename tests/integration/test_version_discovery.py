#!/usr/bin/env python
# coding: utf-8 -*-
"""Integration tests for EOS download workflow.

Tests the complete workflow from version discovery to file download,
using mocked API responses for reproducible testing.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock

import pytest
import responses

from tests.integration.mock_arista_api import (
    MOCK_XML_CATALOG,
    MOCK_DOWNLOAD_RESPONSE,
    MOCK_SESSION_RESPONSE,
    mock_arista_token,
    mock_download_dir,
    mock_eos_image_content,
    mock_arista_api_responses,
    mock_arista_api_auth_error,
    integration_test_data,
)

from eos_downloader.models.version import EosVersion
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier
from eos_downloader.defaults import DEFAULT_SOFTWARE_FOLDER_TREE, DEFAULT_SERVER_SESSION


def setup_api_mocks() -> None:
    """Set up common API mocks for session and catalog endpoints."""
    responses.add(
        responses.POST,
        DEFAULT_SERVER_SESSION,
        json=MOCK_SESSION_RESPONSE,
        status=200
    )
    responses.add(
        responses.POST,
        DEFAULT_SOFTWARE_FOLDER_TREE,
        json={"data": {"xml": MOCK_XML_CATALOG}},
        status=200
    )


@pytest.mark.integration
class TestVersionDiscoveryWorkflow:
    """Test version discovery workflow using mocked API."""

    @responses.activate
    def test_discover_eos_versions_from_catalog(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test discovering EOS versions from mocked XML catalog."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="eos")

        assert len(versions) > 0, "Should discover at least one version"
        version_strings = [str(v) for v in versions]

        assert "4.32.3M" in version_strings
        assert "4.32.2F" in version_strings
        assert "4.31.5M" in version_strings

    @responses.activate
    def test_discover_versions_filtered_by_branch(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test filtering versions by branch."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="eos", branch="4.32")

        assert len(versions) >= 2, "Should find versions in 4.32 branch"
        for version in versions:
            assert version.branch == "4.32", f"Version {version} should be in 4.32 branch"

    @responses.activate
    def test_discover_versions_filtered_by_rtype(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test filtering versions by release type."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="eos", rtype="M")

        assert len(versions) >= 1, "Should find at least one M release"
        for version in versions:
            assert version.rtype == "M", f"Version {version} should be M release"

    @responses.activate
    def test_discover_latest_version_in_branch(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test finding latest version in a branch."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="eos", branch="4.32")

        if versions:
            latest = max(versions)
            assert str(latest) == "4.32.3M", "Latest in 4.32 should be 4.32.3M"


@pytest.mark.integration
class TestVersionComparison:
    """Test version comparison across discovered versions."""

    def test_version_sorting(self) -> None:
        """Test that discovered versions can be properly sorted."""
        versions = [
            EosVersion.from_str("4.31.5M"),
            EosVersion.from_str("4.32.3M"),
            EosVersion.from_str("4.32.2F"),
        ]

        sorted_versions = sorted(versions)
        assert str(sorted_versions[0]) == "4.31.5M"
        assert str(sorted_versions[-1]) == "4.32.3M"

    def test_find_latest_in_multiple_branches(self) -> None:
        """Test finding latest version across multiple branches."""
        versions = [
            EosVersion.from_str("4.31.5M"),
            EosVersion.from_str("4.32.3M"),
            EosVersion.from_str("4.32.2F"),
            EosVersion.from_str("4.30.8M"),
        ]

        branches: dict[str, list[EosVersion]] = {}
        for v in versions:
            if v.branch not in branches:
                branches[v.branch] = []
            branches[v.branch].append(v)

        latest_per_branch = {
            branch: max(vers) for branch, vers in branches.items()
        }

        assert str(latest_per_branch["4.32"]) == "4.32.3M"
        assert str(latest_per_branch["4.31"]) == "4.31.5M"
        assert str(latest_per_branch["4.30"]) == "4.30.8M"


@pytest.mark.integration
class TestAuthenticationWorkflow:
    """Test authentication scenarios."""

    @responses.activate
    def test_invalid_token_returns_error(self) -> None:
        """Test that invalid token results in authentication error."""
        responses.add(
            responses.POST,
            DEFAULT_SERVER_SESSION,
            json={"error": "Unauthorized"},
            status=401
        )

        with pytest.raises(Exception):
            querier = AristaXmlQuerier(token="invalid-token")


@pytest.mark.integration
class TestCVPVersionDiscovery:
    """Test CloudVision Portal version discovery."""

    @responses.activate
    def test_discover_cvp_versions(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test discovering CVP versions from catalog."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="cvp")

        assert len(versions) >= 1, "Should discover at least one CVP version"


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @responses.activate
    def test_full_version_discovery_to_selection(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test complete workflow: discover -> filter -> select latest."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)

        all_versions = querier.available_public_versions(package="eos")
        assert len(all_versions) > 0

        maintenance_versions = [v for v in all_versions if v.rtype == "M"]
        assert len(maintenance_versions) > 0

        latest_maintenance = max(maintenance_versions)
        assert latest_maintenance.rtype == "M"

        version_4_32 = [v for v in all_versions if v.branch == "4.32"]
        assert len(version_4_32) >= 2

    @responses.activate
    def test_workflow_with_branch_filter(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test workflow with specific branch filtering."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)

        branch_431 = querier.available_public_versions(package="eos", branch="4.31")
        branch_432 = querier.available_public_versions(package="eos", branch="4.32")

        assert all(v.branch == "4.31" for v in branch_431)
        assert all(v.branch == "4.32" for v in branch_432)


@pytest.mark.integration
class TestDataIntegrity:
    """Test data integrity in version parsing and handling."""

    @responses.activate
    def test_version_attributes_consistency(
        self,
        mock_arista_token: str,
    ) -> None:
        """Test that version attributes are consistent after parsing."""
        setup_api_mocks()

        querier = AristaXmlQuerier(token=mock_arista_token)
        versions = querier.available_public_versions(package="eos")

        for version in versions:
            reconstructed = EosVersion.from_str(str(version))
            assert version.major == reconstructed.major
            assert version.minor == reconstructed.minor
            assert version.patch == reconstructed.patch
            assert version.rtype == reconstructed.rtype
            assert version.branch == reconstructed.branch

    def test_version_serialization_roundtrip(self) -> None:
        """Test version can be serialized and deserialized."""
        original = EosVersion.from_str("4.32.3M")

        as_dict = original.model_dump()
        reconstructed = EosVersion(**as_dict)

        assert original == reconstructed
        assert str(original) == str(reconstructed)
