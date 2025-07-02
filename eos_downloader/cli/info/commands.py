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

import click
from rich import print_json
from rich.panel import Panel

from eos_downloader.models.data import software_mapping
from eos_downloader.models.types import AristaPackage, ReleaseType, AristaMapping
import eos_downloader.logics.arista_xml_server
from eos_downloader.cli.utils import console_configuration
from eos_downloader.cli.utils import cli_logging

# """
# Commands for ARDL CLI to list data.
# """


@click.command()
@click.option(
    "--format",
    type=click.Choice(["json", "text", "fancy"]),
    default="fancy",
    help="Output format",
)
@click.option(
    "--package", type=click.Choice(["eos", "cvp"]), default="eos", required=False
)
@click.option("--branch", "-b", type=str, required=False)
@click.option("--release-type", type=str, required=False)
@click.pass_context
def versions(
    ctx: click.Context,
    package: AristaPackage,
    branch: str,
    release_type: ReleaseType,
    format: str,
) -> None:
    """List available package versions from Arista server."""

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    cli_logging(log_level)

    querier = eos_downloader.logics.arista_xml_server.AristaXmlQuerier(token=token)

    received_versions = None
    try:
        received_versions = querier.available_public_versions(
            package=package, branch=branch, rtype=release_type
        )
    except ValueError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print("[red]No versions found[/red]")
            return

    if format == "text":
        console.print("Listing available versions")
        if received_versions is None:
            console.print("[red]No versions found[/red]")
            return
        for version in received_versions:
            console.print(f"  - version: [blue]{version}[/blue]")
    elif format == "fancy":
        lines_output = []
        if received_versions is None:
            console.print("[red]No versions found[/red]")
            return
        for version in received_versions:
            lines_output.append(f"  - version: [blue]{version}[/blue]")
        console.print("")
        console.print(
            Panel("\n".join(lines_output), title="Available versions", padding=1)
        )
    elif format == "json":
        response = []
        if received_versions is None:
            console.print("[red]No versions found[/red]")
            return
        for version in received_versions:
            out = {}
            out["version"] = str(version)
            out["branch"] = str(version.branch)
            response.append(out)
        response = json.dumps(response)  # type: ignore
        print_json(response)


@click.command()
@click.option(
    "--format",
    type=click.Choice(["json", "text", "fancy"]),
    default="fancy",
    help="Output format",
)
@click.option(
    "--package", type=click.Choice(["eos", "cvp"]), default="eos", required=False
)
@click.option("--branch", "-b", type=str, required=False)
@click.option("--release-type", type=str, required=False)
@click.pass_context
def latest(
    ctx: click.Context,
    package: AristaPackage,
    branch: str,
    release_type: ReleaseType,
    format: str,
) -> None:
    """List available versions of Arista packages (eos or CVP) packages."""

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    cli_logging(log_level)
    querier = eos_downloader.logics.arista_xml_server.AristaXmlQuerier(token=token)
    received_version = None
    try:
        received_version = querier.latest(
            package=package, branch=branch, rtype=release_type
        )
    except ValueError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print("[red]No versions found[/red]")

    if format in ["text", "fancy"]:
        version_info = f"Latest version for [green]{package}[/green]: [blue]{received_version}[/blue]"
        if branch:
            version_info += f" for branch [blue]{branch}[/blue]"

        if format == "text":
            console.print("")
            console.print(version_info)
        else:  # fancy format
            console.print("")
            console.print(Panel(version_info, title="Latest version", padding=1))
    else:  # json format
        print_json(json.dumps({"version": str(received_version)}))


@click.command()
@click.option(
    "--package", type=click.Choice(["eos", "cvp"]), default="eos", required=False
)
@click.option(
    "--format",
    type=click.Choice(["json", "text", "fancy"]),
    default="fancy",
    help="Output format",
)
@click.option(
    "--details",
    is_flag=True,
    show_default=True,
    default=False,
    help="Show details for each flavor",
)
@click.pass_context
def mapping(
    ctx: click.Context, package: AristaPackage, details: bool, format: str
) -> None:
    """List available flavors of Arista packages (eos or CVP) packages."""

    mapping_pkg_name: AristaMapping = "EOS"
    if package == "eos":
        mapping_pkg_name = "EOS"
    elif package == "cvp":
        mapping_pkg_name = "CloudVision"
    console = console_configuration()
    log_level = ctx.obj["log_level"]
    console.print(f"Log Level is: {log_level}")
    cli_logging(log_level)

    if mapping_pkg_name in software_mapping.model_fields:  # pylint: disable = unsupported-membership-test
        mapping_entries = getattr(software_mapping, mapping_pkg_name, None)
        if format == "text":
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
        elif format == "fancy":
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
        elif format == "json":
            mapping_json = software_mapping.model_dump()[package.upper()]
            print_json(json.dumps(mapping_json))
