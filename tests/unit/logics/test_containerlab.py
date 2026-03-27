#!/usr/bin/env python
# coding: utf-8 -*-
"""Tests for eos_downloader.logics.containerlab module."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from eos_downloader.logics.containerlab import (
    _parse_version_from_image,
    _resolve_env_vars,
    extract_ceos_versions,
)


class TestResolveEnvVars:
    """Tests for _resolve_env_vars function."""

    def test_assign_default_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR:=default} uses default when env not set."""
        monkeypatch.delenv("EOS_VERSION", raising=False)
        monkeypatch.delenv("EOS_IMAGE", raising=False)
        assert _resolve_env_vars("${EOS_IMAGE:=arista/ceos}:${EOS_VERSION:=4.34.2.1F}") == "arista/ceos:4.34.2.1F"

    def test_dash_default_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR:-default} uses default when env not set."""
        monkeypatch.delenv("EOS_VERSION", raising=False)
        assert _resolve_env_vars("arista/ceos:${EOS_VERSION:-4.33.1F}") == "arista/ceos:4.33.1F"

    def test_env_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """os.environ value takes priority over YAML default."""
        monkeypatch.setenv("EOS_VERSION", "4.30.1F")
        monkeypatch.setenv("EOS_IMAGE", "custom/ceos")
        assert _resolve_env_vars("${EOS_IMAGE:=arista/ceos}:${EOS_VERSION:=4.34.2.1F}") == "custom/ceos:4.30.1F"

    def test_plain_var_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR} (no default) reads from os.environ."""
        monkeypatch.setenv("EOS_VERSION", "4.30.1F")
        assert _resolve_env_vars("arista/ceos:${EOS_VERSION}") == "arista/ceos:4.30.1F"

    def test_plain_var_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR} with no env set resolves to empty string."""
        monkeypatch.delenv("EOS_VERSION", raising=False)
        assert _resolve_env_vars("arista/ceos:${EOS_VERSION}") == "arista/ceos:"

    def test_no_vars(self) -> None:
        """Literal string passes through unchanged."""
        assert _resolve_env_vars("arista/ceos:4.33.1F") == "arista/ceos:4.33.1F"


class TestParseVersionFromImage:
    """Tests for _parse_version_from_image function."""

    def test_valid_image(self) -> None:
        """Parse version from standard cEOS image string."""
        assert _parse_version_from_image("arista/ceos:4.33.1F") == "4.33.1F"

    def test_valid_image_maintenance(self) -> None:
        """Parse maintenance version from cEOS image string."""
        assert _parse_version_from_image("arista/ceos:4.29.3M") == "4.29.3M"

    def test_no_tag(self) -> None:
        """Return None when no tag is present."""
        assert _parse_version_from_image("arista/ceos") is None

    def test_custom_registry(self) -> None:
        """Parse version from custom registry image string."""
        result = _parse_version_from_image("registry.example.com/arista/ceos:4.33.1F")
        assert result == "4.33.1F"

    def test_invalid_tag(self) -> None:
        """Return None for non-EOS version tag."""
        assert _parse_version_from_image("arista/ceos:latest") is None

    def test_short_image_name(self) -> None:
        """Parse version from short image name."""
        assert _parse_version_from_image("ceos:4.30.1F") == "4.30.1F"

    def test_env_var_with_assign_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Resolve ${VAR:=default} and parse version."""
        monkeypatch.delenv("EOS_IMAGE", raising=False)
        monkeypatch.delenv("EOS_VERSION", raising=False)
        assert _parse_version_from_image("${EOS_IMAGE:=arista/ceos}:${EOS_VERSION:=4.34.2.1F}") == "4.34.2.1F"

    def test_env_var_with_dash_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Resolve ${VAR:-default} and parse version."""
        monkeypatch.delenv("EOS_VERSION", raising=False)
        assert _parse_version_from_image("arista/ceos:${EOS_VERSION:-4.33.1F}") == "4.33.1F"

    def test_env_var_whole_image(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Resolve when entire image is a single env var with default containing a colon."""
        monkeypatch.delenv("EOS_IMAGE", raising=False)
        assert _parse_version_from_image("${EOS_IMAGE:-arista/ceos:4.33.1F}") == "4.33.1F"

    def test_env_var_no_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Plain env vars with no values resolve to empty, yielding no version."""
        monkeypatch.delenv("EOS_IMAGE", raising=False)
        monkeypatch.delenv("EOS_VERSION", raising=False)
        assert _parse_version_from_image("${EOS_IMAGE}:${EOS_VERSION}") is None

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """os.environ takes priority over YAML default."""
        monkeypatch.setenv("EOS_VERSION", "4.30.1F")
        assert _parse_version_from_image("arista/ceos:${EOS_VERSION:=4.34.2.1F}") == "4.30.1F"


class TestExtractCeosVersions:
    """Tests for extract_ceos_versions function."""

    def test_kinds_only(self, tmp_path: Path) -> None:
        """Extract versions when all nodes inherit from kinds.ceos.image."""
        topo = {
            "topology": {
                "kinds": {"ceos": {"image": "arista/ceos:4.33.1F"}},
                "nodes": {
                    "spine1": {"kind": "ceos"},
                    "spine2": {"kind": "ceos"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.33.1F"]

    def test_node_overrides(self, tmp_path: Path) -> None:
        """Extract versions when nodes override the kind-level image."""
        topo = {
            "topology": {
                "kinds": {"ceos": {"image": "arista/ceos:4.33.1F"}},
                "nodes": {
                    "spine1": {"kind": "ceos", "image": "arista/ceos:4.29.3M"},
                    "leaf1": {"kind": "ceos", "image": "arista/ceos:4.30.1F"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.29.3M", "4.30.1F"]

    def test_mixed_inheritance_and_override(self, tmp_path: Path) -> None:
        """Some nodes inherit kind image, others override."""
        topo = {
            "topology": {
                "kinds": {"ceos": {"image": "arista/ceos:4.33.1F"}},
                "nodes": {
                    "spine1": {"kind": "ceos"},
                    "leaf1": {"kind": "ceos", "image": "arista/ceos:4.29.3M"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.29.3M", "4.33.1F"]

    def test_non_ceos_ignored(self, tmp_path: Path) -> None:
        """Nodes with kind != ceos are skipped."""
        topo = {
            "topology": {
                "kinds": {
                    "ceos": {"image": "arista/ceos:4.33.1F"},
                    "srl": {"image": "ghcr.io/nokia/srlinux:latest"},
                },
                "nodes": {
                    "spine1": {"kind": "ceos"},
                    "srl1": {"kind": "srl"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.33.1F"]

    def test_deduplication(self, tmp_path: Path) -> None:
        """Same version in multiple nodes yields one entry."""
        topo = {
            "topology": {
                "nodes": {
                    "spine1": {"kind": "ceos", "image": "arista/ceos:4.33.1F"},
                    "spine2": {"kind": "ceos", "image": "arista/ceos:4.33.1F"},
                    "leaf1": {"kind": "ceos", "image": "arista/ceos:4.33.1F"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.33.1F"]

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            extract_ceos_versions(tmp_path / "nonexistent.yaml")

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        """Raise exception for invalid YAML."""
        topo_file = tmp_path / "bad.yaml"
        topo_file.write_text(":\n  invalid: [yaml: {broken")

        with pytest.raises(Exception):
            extract_ceos_versions(topo_file)

    def test_no_ceos_nodes(self, tmp_path: Path) -> None:
        """Return empty list when no ceos nodes exist."""
        topo = {
            "topology": {
                "nodes": {
                    "srl1": {"kind": "srl", "image": "ghcr.io/nokia/srlinux:latest"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == []

    def test_invalid_image_tag_skipped(self, tmp_path: Path) -> None:
        """Malformed image tag is skipped, valid ones are kept."""
        topo = {
            "topology": {
                "nodes": {
                    "spine1": {"kind": "ceos", "image": "arista/ceos:4.33.1F"},
                    "spine2": {"kind": "ceos", "image": "arista/ceos:latest"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == ["4.33.1F"]

    def test_no_image_for_ceos_node(self, tmp_path: Path) -> None:
        """cEOS node with no image at node or kind level is skipped."""
        topo = {
            "topology": {
                "nodes": {
                    "spine1": {"kind": "ceos"},
                },
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == []

    def test_env_var_in_kinds_image(self, tmp_path: Path) -> None:
        """End-to-end: extract version from kinds image with env var defaults."""
        topo = {
            "topology": {
                "kinds": {"ceos": {"image": "${EOS_IMAGE:=arista/ceos}:${EOS_VERSION:=4.34.2.1F}"}},
                "nodes": {"spine1": {"kind": "ceos"}},
            }
        }
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))
        assert extract_ceos_versions(topo_file) == ["4.34.2.1F"]

    def test_empty_topology(self, tmp_path: Path) -> None:
        """Empty topology section returns empty list."""
        topo = {"topology": {}}
        topo_file = tmp_path / "topo.clab.yaml"
        topo_file.write_text(yaml.dump(topo))

        result = extract_ceos_versions(topo_file)
        assert result == []
