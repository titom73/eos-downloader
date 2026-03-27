"""Containerlab topology parser for extracting cEOS version information.

This module parses containerlab topology YAML files and extracts
the EOS versions used by cEOS nodes, enabling batch download of
all required cEOS images.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from loguru import logger
from pydantic import BaseModel, ConfigDict

from eos_downloader.models.version import EosVersion


class ContainerlabKind(BaseModel):
    """Represents a kind definition in a containerlab topology."""

    model_config = ConfigDict(extra="allow")
    image: Optional[str] = None


class ContainerlabNode(BaseModel):
    """Represents a node definition in a containerlab topology."""

    model_config = ConfigDict(extra="allow")
    kind: Optional[str] = None
    image: Optional[str] = None


class ContainerlabTopologyData(BaseModel):
    """Represents the topology section of a containerlab file."""

    model_config = ConfigDict(extra="allow")
    kinds: Dict[str, ContainerlabKind] = {}
    nodes: Dict[str, ContainerlabNode] = {}


class ContainerlabFile(BaseModel):
    """Represents a containerlab topology file."""

    model_config = ConfigDict(extra="allow")
    topology: ContainerlabTopologyData = ContainerlabTopologyData()


_ENV_VAR_WITH_DEFAULT = re.compile(
    r"\$\{(?P<name>[^:}]+)(?::?[=\-])(?P<default>[^}]*)\}"
)
_ENV_VAR_PLAIN = re.compile(r"\$\{(?P<name>[^}]+)\}")


def _resolve_env_vars(value: str) -> str:
    """Resolve shell-style variable references using os.environ with YAML defaults as fallback.

    Supported patterns:
    - ${VAR:=default} / ${VAR:-default} -- use os.environ[VAR] if set, else default
    - ${VAR=default} / ${VAR-default} -- same (colon is optional)
    - ${VAR} -- use os.environ[VAR] if set, else empty string
    """

    def _replace_with_default(m: re.Match[str]) -> str:
        name = m.group("name")
        default = m.group("default")
        return os.environ.get(name, default)

    def _replace_plain(m: re.Match[str]) -> str:
        return os.environ.get(m.group("name"), "")

    result = _ENV_VAR_WITH_DEFAULT.sub(_replace_with_default, value)
    result = _ENV_VAR_PLAIN.sub(_replace_plain, result)
    return result


def _parse_version_from_image(image: str) -> Optional[str]:
    """Extract and validate an EOS version from a Docker image string.

    Parameters
    ----------
    image : str
        Docker image string (e.g., "arista/ceos:4.33.1F").

    Returns
    -------
    Optional[str]
        The version string if valid, None otherwise.
    """
    image = _resolve_env_vars(image)

    if ":" not in image:
        logger.warning(f"No tag found in image string: {image}")
        return None

    tag = image.split(":")[-1]
    version = EosVersion.from_str(tag)

    # from_str returns a default SemVer(major=0) when parsing fails
    if version.major == 0:
        logger.warning(f"Invalid EOS version tag: {tag}")
        return None

    return tag


def extract_ceos_versions(topology_file: Path) -> List[str]:
    """Extract deduplicated cEOS versions from a containerlab topology file.

    Parameters
    ----------
    topology_file : Path
        Path to the containerlab topology YAML file.

    Returns
    -------
    List[str]
        Sorted list of unique EOS version strings found in cEOS nodes.

    Raises
    ------
    FileNotFoundError
        If the topology file does not exist.
    yaml.YAMLError
        If the file contains invalid YAML.
    """
    if not topology_file.exists():
        raise FileNotFoundError(f"Topology file not found: {topology_file}")

    with topology_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        logger.warning(f"Empty topology file: {topology_file}")
        return []

    topology = ContainerlabFile.model_validate(data)

    # Get the default ceos image from kinds if defined
    ceos_kind = topology.topology.kinds.get("ceos")
    default_image = ceos_kind.image if ceos_kind else None

    versions: set[str] = set()

    for node_name, node in topology.topology.nodes.items():
        # Only process ceos nodes
        if node.kind != "ceos":
            continue

        # Resolve image: node-level overrides kind-level
        image = node.image or default_image

        if image is None:
            logger.warning(f"cEOS node '{node_name}' has no resolvable image")
            continue

        version = _parse_version_from_image(image)
        if version is not None:
            versions.add(version)

    return sorted(versions)
