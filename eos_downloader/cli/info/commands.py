#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# flake8: noqa E501

"""CLI commands for listing Arista package information.

This module provides CLI commands to query and display version information for Arista packages (EOS and CVP).
It includes commands to:
- List all available versions with filtering options
- Get the latest version for a given package/branch

The commands use Click for CLI argument parsing and support both text and JSON output formats.
Authentication is handled via a token passed through Click context.

Commands:
    versions: Lists all available versions with optional filtering
    latest: Shows the latest version matching the filter criteria

Dependencies:
    click: CLI framework
    rich: For pretty JSON output
    eos_downloader.logics.arista_server: Core logic for querying Arista servers
"""

import json
import sys
from enum import Enum
from typing import Any, List, Optional, Union, cast

import typer
from rich import print_json
from rich.panel import Panel

from eos_downloader.models.data import software_mapping
from eos_downloader.models.types import AristaPackage, AristaMapping, ReleaseType
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier
from eos_downloader.models.version import EosVersion, CvpVersion
from eos_downloader.cli.utils import console_configuration, AliasedTyperGroup
from eos_downloader.logging_config import configure_logging
from eos_downloader.exceptions import AuthenticationError

# """
# Commands for ARDL CLI to list data.
# """

app = typer.Typer(
    cls=AliasedTyperGroup,
    no_args_is_help=True,
    help="List information from Arista website",
)


class OutputFormat(str, Enum):
    """Output format for info commands."""

    json = "json"
    text = "text"
    fancy = "fancy"


class Package(str, Enum):
    """Arista package selector."""

    eos = "eos"
    cvp = "cvp"


@app.command()
def versions(
    ctx: typer.Context,
    package: Package = typer.Option(Package.eos, "--package"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b"),
    release_type: Optional[str] = typer.Option(None, "--release-type"),
    output_format: OutputFormat = typer.Option(
        OutputFormat.fancy, "--format", help="Output format"
    ),
) -> None:
    """List available package versions from Arista server.

    Parameters
    ----------
    ctx : typer.Context
        Context containing token, debug, and log_level
    package : Package
        Package type ("eos" or "cvp")
    branch : str
        Optional branch filter (e.g., "4.29")
    release_type : ReleaseType
        Optional release type filter ("M" or "F")
    output_format : OutputFormat
        Output format ("text", "fancy", or "json")

    Examples
    --------
    List all EOS versions:

    >>> ardl info versions --package eos

    List maintenance releases for branch 4.29:

    >>> ardl info versions --package eos --branch 4.29 --release-type M
    """
    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    configure_logging(level=log_level.upper())

    try:
        querier = AristaXmlQuerier(token=token)
    except AuthenticationError as auth_error:
        console.print(f"[red]Authentication Error:[/red] {str(auth_error)}")
        if debug:
            console.print_exception(show_locals=True)
        sys.exit(1)

    try:
        received_versions = querier.available_public_versions(
            package=package.value, branch=branch, rtype=release_type
        )
    except ValueError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print("[red]No versions found[/red]")
        return

    # Early return if no versions found
    if not received_versions:
        console.print("[red]No versions found[/red]")
        return

    # Format and display output based on format choice
    _print_versions_output(console, received_versions, output_format.value)


def _print_versions_output(
    console: Any, version_list: List[Union[EosVersion, CvpVersion]], format: str
) -> None:
    """Print versions in the specified format.

    Parameters
    ----------
    console : Console
        Rich console instance for output
    version_list : List[Union[EosVersion, CvpVersion]]
        List of version objects to display
    format : str
        Output format ("text", "fancy", or "json")
    """
    if format == "text":
        _print_text_versions(console, version_list)
    elif format == "fancy":
        _print_fancy_versions(console, version_list)
    elif format == "json":
        _print_json_versions(version_list)


def _print_text_versions(
    console: Any, version_list: List[Union[EosVersion, CvpVersion]]
) -> None:
    """Print versions in plain text format.

    Parameters
    ----------
    console : Console
        Rich console instance for output
    version_list : List[Union[EosVersion, CvpVersion]]
        List of version objects to display
    """
    console.print("Listing available versions")
    for version in version_list:
        console.print(f"  - version: [blue]{version}[/blue]")


def _print_fancy_versions(
    console: Any, version_list: List[Union[EosVersion, CvpVersion]]
) -> None:
    """Print versions in fancy panel format.

    Parameters
    ----------
    console : Console
        Rich console instance for output
    version_list : List[Union[EosVersion, CvpVersion]]
        List of version objects to display
    """
    lines_output = [f"  - version: [blue]{version}[/blue]" for version in version_list]
    console.print("")
    console.print(Panel("\n".join(lines_output), title="Available versions", padding=1))


def _print_json_versions(version_list: List[Union[EosVersion, CvpVersion]]) -> None:
    """Print versions in JSON format.

    Parameters
    ----------
    version_list : List[Union[EosVersion, CvpVersion]]
        List of version objects to display
    """
    response = [
        {"version": str(version), "branch": str(version.branch)}
        for version in version_list
    ]
    print_json(json.dumps(response))


@app.command()
def latest(
    ctx: typer.Context,
    package: Package = typer.Option(Package.eos, "--package"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b"),
    release_type: Optional[str] = typer.Option(None, "--release-type"),
    output_format: OutputFormat = typer.Option(
        OutputFormat.fancy, "--format", help="Output format"
    ),
) -> None:
    """List available versions of Arista packages (eos or CVP) packages."""

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    configure_logging(level=log_level.upper())

    try:
        querier = AristaXmlQuerier(token=token)
    except AuthenticationError as auth_error:
        console.print(f"[red]Authentication Error:[/red] {str(auth_error)}")
        if debug:
            console.print_exception(show_locals=True)
        sys.exit(1)

    received_version = None
    try:
        received_version = querier.latest(
            package=package.value,
            branch=branch,
            rtype=cast(Optional[ReleaseType], release_type),
        )
    except ValueError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print("[red]No versions found[/red]")

    if output_format in (OutputFormat.text, OutputFormat.fancy):
        version_info = f"Latest version for [green]{package.value}[/green]: [blue]{received_version}[/blue]"
        if branch:
            version_info += f" for branch [blue]{branch}[/blue]"

        if output_format == OutputFormat.text:
            console.print("")
            console.print(version_info)
        else:  # fancy format
            console.print("")
            console.print(Panel(version_info, title="Latest version", padding=1))
    else:  # json format
        print_json(json.dumps({"version": str(received_version)}))


def _get_mapping_name(package: AristaPackage) -> AristaMapping:
    """Get the mapping name for the given package."""
    return "EOS" if package == "eos" else "CloudVision"


def _print_text_mapping(
    console: Any,
    package: str,
    mapping_pkg_name: str,
    mapping_entries: Any,
    details: bool,
) -> None:
    """Print mapping in text format."""
    console.print(
        f"Following flavors for [red]{package}/{mapping_pkg_name}[/red] have been found:"
    )
    if mapping_entries is None:
        console.print("[red]No flavors found[/red]")
        return

    for mapping_entry in mapping_entries:
        console.print(f"   * Flavor: [blue]{mapping_entry}[/blue]")
        if details:
            console.print(
                f"     - Information: [black]{mapping_entries[mapping_entry]}[/black]"
            )
    console.print("\n")


def _print_fancy_mapping(console: Any, mapping_entries: Any, details: bool) -> None:
    """Print mapping in fancy format."""
    lines_output = []
    if mapping_entries is None:
        lines_output.append("[red]No flavors found[/red]")
        console.print("\n".join(lines_output))
        return

    for mapping_entry in mapping_entries:
        lines_output.append(f"   * Flavor: [blue]{mapping_entry}[/blue]")
        if details:
            lines_output.append(
                f"     - Information: [black]{mapping_entries[mapping_entry]}[/black]"
            )
    console.print("")
    console.print(Panel("\n".join(lines_output), title="Flavors", padding=1))
    console.print("\n")


@app.command()
def mapping(
    ctx: typer.Context,
    package: Package = typer.Option(Package.eos, "--package"),
    output_format: OutputFormat = typer.Option(
        OutputFormat.fancy, "--format", help="Output format"
    ),
    details: bool = typer.Option(
        False,
        "--details",
        help="Show details for each flavor",
    ),
) -> None:
    """List available flavors of Arista packages (eos or CVP) packages."""

    mapping_pkg_name = _get_mapping_name(package.value)
    console = console_configuration()
    log_level = ctx.obj["log_level"]

    # Only print log level for non-JSON formats to avoid contaminating JSON output
    if output_format != OutputFormat.json:
        console.print(f"Log Level is: {log_level}")
    configure_logging(level=log_level.upper())

    if not hasattr(software_mapping, mapping_pkg_name):
        console.print(f"[red]Unknown package type: {mapping_pkg_name}[/red]")
        return

    mapping_entries = getattr(software_mapping, mapping_pkg_name, None)

    if output_format == OutputFormat.text:
        _print_text_mapping(
            console, package.value, mapping_pkg_name, mapping_entries, details
        )
    elif output_format == OutputFormat.fancy:
        _print_fancy_mapping(console, mapping_entries, details)
    elif output_format == OutputFormat.json:
        mapping_json = software_mapping.model_dump()[package.value.upper()]
        print_json(data=mapping_json)
