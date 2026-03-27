#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Configuration file support for eos-downloader.

This module provides optional TOML configuration file loading for the ``ardl`` CLI.
The configuration file allows users to set default values for CLI options,
following a dotfiles/chezmoi approach.

Priority order (highest to lowest):
    1. CLI options
    2. Environment variables (``ARISTA_*``)
    3. Configuration file
    4. Click defaults

Search paths (first found wins):
    1. ``~/.eos-downloader.toml``
    2. ``$XDG_CONFIG_HOME/eos-downloader/config.toml``
       (defaults to ``~/.config/eos-downloader/config.toml``)

Functions
---------
find_config_file
    Search for the configuration file in standard locations
load_config
    Parse a TOML configuration file
config_to_default_map
    Transform config dict into Click's ``default_map`` format
get_default_map
    Combine find + load + transform in one call
generate_template
    Generate a commented TOML template with all available options
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError as exc:
        raise ImportError(
            "Python < 3.11 requires the 'tomli' package. "
            "Install it with: pip install tomli"
        ) from exc


CONFIG_SEARCH_PATHS: List[Tuple[str, str]] = [
    ("~/.eos-downloader.toml", "home directory"),
    (
        os.path.join(
            os.environ.get("XDG_CONFIG_HOME", "~/.config"),
            "eos-downloader",
            "config.toml",
        ),
        "XDG config directory",
    ),
]
"""Ordered list of (path_template, description) tuples to search for config files."""


def find_config_file() -> Optional[Path]:
    """Search for the configuration file in standard locations.

    Returns
    -------
    Optional[Path]
        Path to the first existing configuration file, or None if not found.
    """
    for path_template, description in CONFIG_SEARCH_PATHS:
        path = Path(path_template).expanduser()
        if path.is_file():
            logger.debug("Found config file in {}: {}", description, path)
            return path
    logger.debug("No configuration file found")
    return None


def load_config(path: Path) -> Dict[str, Any]:
    """Parse a TOML configuration file.

    Parameters
    ----------
    path : Path
        Path to the TOML configuration file.

    Returns
    -------
    Dict[str, Any]
        Parsed configuration dictionary, or empty dict on error.
    """
    try:
        with open(path, "rb") as f:
            config = tomllib.load(f)
        logger.debug("Loaded configuration from {}", path)
        return config
    except tomllib.TOMLDecodeError as e:
        logger.warning("Invalid TOML in configuration file {}: {}", path, e)
        return {}
    except OSError as e:
        logger.warning("Cannot read configuration file {}: {}", path, e)
        return {}


def config_to_default_map(config: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a parsed config dict into Click's ``default_map`` format.

    The config structure follows the CLI hierarchy::

        [ardl]              → root group options (token, log_level, ...)
        [ardl.get.eos]      → ``ardl get eos`` options
        [ardl.info]         → shared defaults for all ``ardl info`` subcommands
        [ardl.info.latest]  → ``ardl info latest`` specific options

    Group-level defaults (e.g. ``[ardl.info]``) are merged into each
    subcommand within that group, with subcommand-specific values taking
    precedence.

    Parameters
    ----------
    config : Dict[str, Any]
        Parsed TOML configuration dictionary.

    Returns
    -------
    Dict[str, Any]
        Click-compatible ``default_map`` dictionary.
    """
    ardl_config = config.get("ardl", {})
    if not ardl_config:
        return {}

    default_map: Dict[str, Any] = {}

    for key, value in ardl_config.items():
        if isinstance(value, dict):
            # This is a command group (e.g., "get", "info", "debug")
            group_defaults: Dict[str, Any] = {}
            subcommands: Dict[str, Dict[str, Any]] = {}

            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    # Subcommand (e.g., "eos", "latest")
                    subcommands[sub_key] = sub_value
                else:
                    # Group-level default shared across subcommands
                    group_defaults[sub_key] = sub_value

            # Build nested default_map for the group
            group_map: Dict[str, Any] = {}
            if subcommands:
                for cmd_name, cmd_opts in subcommands.items():
                    # Merge group defaults with subcommand-specific options
                    merged = {**group_defaults, **cmd_opts}
                    group_map[cmd_name] = merged
            if group_defaults and not subcommands:
                # Only group defaults, no subcommands defined
                group_map = group_defaults

            # If there are group defaults but also subcommands,
            # ensure subcommands that aren't explicitly listed
            # still get the group defaults via the group_map
            if group_defaults and subcommands:
                # Store group defaults at the group level too
                # so Click can pick them up for unlisted subcommands
                for gk, gv in group_defaults.items():
                    if gk not in group_map:
                        group_map[gk] = gv

            default_map[key] = group_map
        else:
            # Root-level option (e.g., token, log_level)
            default_map[key] = value

    return default_map


def get_default_map() -> Optional[Dict[str, Any]]:
    """Find, load, and transform the configuration file into a default_map.

    This is a convenience function combining :func:`find_config_file`,
    :func:`load_config`, and :func:`config_to_default_map`.

    Returns
    -------
    Optional[Dict[str, Any]]
        Click-compatible ``default_map``, or None if no config file found.
    """
    config_path = find_config_file()
    if config_path is None:
        return None

    config = load_config(config_path)
    if not config:
        return None

    default_map = config_to_default_map(config)
    if not default_map:
        return None

    return default_map


def generate_template() -> str:
    """Generate a commented TOML template with all available options.

    Returns
    -------
    str
        A TOML string with all options commented out and documented.
    """
    return '''\
# eos-downloader configuration file
# Place this file at ~/.eos-downloader.toml
# or $XDG_CONFIG_HOME/eos-downloader/config.toml
#
# Priority order (highest to lowest):
#   1. CLI options
#   2. Environment variables (ARISTA_*)
#   3. This configuration file
#   4. Click defaults

[ardl]
# token = "your-arista-api-token"
# log_level = "error"
# debug_enabled = false

[ardl.get.eos]
# format = "vmdk"
# output = "."
# latest = false
# eve_ng = false
# import_docker = false
# skip_download = false
# docker_name = "arista/ceos"
# docker_tag = ""
# version = ""
# release_type = "F"
# branch = ""
# dry_run = false
# force = false
# containerlab_topology = ""

[ardl.get.cvp]
# format = "ova"
# output = "."
# latest = false
# version = ""
# branch = ""
# dry_run = false
# force = false

[ardl.get.path]
# source = ""
# output = "."
# import_docker = false
# docker_name = "arista/ceos:raw"
# docker_tag = "dev"
# force = false

[ardl.info.versions]
# format = "fancy"
# package = "eos"
# branch = ""
# release_type = ""

[ardl.info.latest]
# format = "fancy"
# package = "eos"
# branch = ""
# release_type = ""

[ardl.info.mapping]
# package = "eos"
# format = "fancy"
# details = false

[ardl.debug.xml]
# output = "arista.xml"
# log_level = "INFO"
'''
