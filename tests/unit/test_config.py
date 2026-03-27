#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Tests for eos_downloader.config module."""

from pathlib import Path
from unittest.mock import patch

from eos_downloader.config import (
    config_to_default_map,
    find_config_file,
    generate_template,
    load_config,
)


VALID_TOML = """\
[ardl]
token = "my-secret-token"
log_level = "info"

[ardl.get.eos]
format = "cEOS"
output = "/tmp/downloads"
import_docker = true

[ardl.info]
format = "json"
package = "eos"

[ardl.info.latest]
branch = "4.29"
"""

INVALID_TOML = """\
[ardl
token = missing bracket
"""


class TestFindConfigFile:
    """Tests for find_config_file()."""

    def test_find_config_file_home(self, tmp_path: Path) -> None:
        """Find config in home directory."""
        config_file = tmp_path / ".eos-downloader.toml"
        config_file.write_text("[ardl]\n")

        search_paths = [
            (str(config_file), "home directory"),
            (str(tmp_path / "xdg" / "config.toml"), "XDG config directory"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            result = find_config_file()

        assert result == config_file

    def test_find_config_file_xdg(self, tmp_path: Path) -> None:
        """Find config in XDG directory when home doesn't exist."""
        xdg_config = tmp_path / "xdg" / "eos-downloader" / "config.toml"
        xdg_config.parent.mkdir(parents=True)
        xdg_config.write_text("[ardl]\n")

        search_paths = [
            (str(tmp_path / ".eos-downloader.toml"), "home directory"),
            (str(xdg_config), "XDG config directory"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            result = find_config_file()

        assert result == xdg_config

    def test_find_config_file_xdg_custom(self, tmp_path: Path) -> None:
        """Finds config at custom XDG-style path."""
        custom_xdg = tmp_path / "custom-config"
        config_file = custom_xdg / "eos-downloader" / "config.toml"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("[ardl]\n")

        search_paths = [
            (str(tmp_path / ".eos-downloader.toml"), "home directory"),
            (str(config_file), "XDG config directory"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            result = find_config_file()

        assert result == config_file

    def test_find_config_file_none(self, tmp_path: Path) -> None:
        """Returns None when no config file exists."""
        search_paths = [
            (str(tmp_path / "nonexistent1.toml"), "home directory"),
            (str(tmp_path / "nonexistent2.toml"), "XDG config directory"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            result = find_config_file()

        assert result is None

    def test_find_config_file_priority(self, tmp_path: Path) -> None:
        """Home directory config takes priority over XDG."""
        home_config = tmp_path / ".eos-downloader.toml"
        home_config.write_text("[ardl]\ntoken = 'home'\n")

        xdg_config = tmp_path / "xdg" / "config.toml"
        xdg_config.parent.mkdir(parents=True)
        xdg_config.write_text("[ardl]\ntoken = 'xdg'\n")

        search_paths = [
            (str(home_config), "home directory"),
            (str(xdg_config), "XDG config directory"),
        ]
        with patch("eos_downloader.config.CONFIG_SEARCH_PATHS", search_paths):
            result = find_config_file()

        assert result == home_config


class TestLoadConfig:
    """Tests for load_config()."""

    def test_load_config_valid(self, tmp_path: Path) -> None:
        """Loads and parses valid TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(VALID_TOML)

        result = load_config(config_file)

        assert result["ardl"]["token"] == "my-secret-token"
        assert result["ardl"]["log_level"] == "info"
        assert result["ardl"]["get"]["eos"]["format"] == "cEOS"
        assert result["ardl"]["info"]["format"] == "json"

    def test_load_config_invalid(self, tmp_path: Path) -> None:
        """Returns empty dict for invalid TOML."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text(INVALID_TOML)

        result = load_config(config_file)

        assert result == {}

    def test_load_config_missing_file(self, tmp_path: Path) -> None:
        """Returns empty dict for missing file."""
        result = load_config(tmp_path / "nonexistent.toml")

        assert result == {}


class TestConfigToDefaultMap:
    """Tests for config_to_default_map()."""

    def test_root_options(self) -> None:
        """Root-level options are placed at top level of default_map."""
        config = {"ardl": {"token": "abc", "log_level": "debug"}}
        result = config_to_default_map(config)

        assert result["token"] == "abc"
        assert result["log_level"] == "debug"

    def test_nested_commands(self) -> None:
        """Nested command options are structured correctly."""
        config = {
            "ardl": {
                "get": {
                    "eos": {"format": "cEOS", "output": "/tmp"},
                    "cvp": {"format": "ova"},
                }
            }
        }
        result = config_to_default_map(config)

        assert result["get"]["eos"]["format"] == "cEOS"
        assert result["get"]["eos"]["output"] == "/tmp"
        assert result["get"]["cvp"]["format"] == "ova"

    def test_group_defaults_merge(self) -> None:
        """Group-level defaults are merged into subcommands."""
        config = {
            "ardl": {
                "info": {
                    "format": "json",
                    "package": "eos",
                    "latest": {"branch": "4.29"},
                }
            }
        }
        result = config_to_default_map(config)

        # Group default merged into subcommand
        assert result["info"]["latest"]["format"] == "json"
        assert result["info"]["latest"]["package"] == "eos"
        # Subcommand-specific option
        assert result["info"]["latest"]["branch"] == "4.29"

    def test_subcommand_overrides_group_default(self) -> None:
        """Subcommand-specific values override group defaults."""
        config = {
            "ardl": {
                "info": {
                    "format": "json",
                    "latest": {"format": "text"},
                }
            }
        }
        result = config_to_default_map(config)

        assert result["info"]["latest"]["format"] == "text"

    def test_empty_config(self) -> None:
        """Returns empty dict for empty config."""
        assert config_to_default_map({}) == {}
        assert config_to_default_map({"ardl": {}}) == {}

    def test_no_ardl_section(self) -> None:
        """Returns empty dict when no [ardl] section."""
        assert config_to_default_map({"other": {"key": "val"}}) == {}


class TestGenerateTemplate:
    """Tests for generate_template()."""

    def test_generate_template(self) -> None:
        """Template contains expected sections."""
        template = generate_template()

        assert "[ardl]" in template
        assert "[ardl.get.eos]" in template
        assert "[ardl.get.cvp]" in template
        assert "[ardl.get.path]" in template
        assert "[ardl.info]\n" in template
        assert "[ardl.info.versions]" in template
        assert "[ardl.info.latest]" in template
        assert "[ardl.info.mapping]" in template
        assert "[ardl.debug.xml]" in template
        # All options should be commented out
        assert '# token = "your-arista-api-token"' in template

    def test_template_is_valid_toml_when_uncommented(self, tmp_path: Path) -> None:
        """Template is valid TOML when lines are uncommented."""
        import sys

        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib  # type: ignore[no-redef]

        template = generate_template()
        # Uncomment all lines
        lines = []
        for line in template.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("# ") and "=" in stripped:
                # Remove the leading "# " comment marker
                indent = line[: len(line) - len(stripped)]
                lines.append(indent + stripped[2:])
            else:
                lines.append(line)
        uncommented = "\n".join(lines)

        # Should parse without error
        config = tomllib.loads(uncommented)
        assert "ardl" in config
