# #!/usr/bin/env python
# # coding: utf-8 -*-
# # pylint: disable=no-value-for-parameter
# # pylint: disable=too-many-arguments
# # pylint: disable=line-too-long
# # pylint: disable=redefined-builtin
# # flake8: noqa E501

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

from eos_downloader.models.data import software_mapping
import eos_downloader.logics.arista_server

# """
# Commands for ARDL CLI to list data.
# """


@click.command()
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="text",
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
    package: str,
    branch: str,
    release_type: str,
    format: str,
) -> None:
    """List available package versions from Arista server.

    Args:
        ctx (click.Context): Click context object containing authentication token.
        package (str): Name of the package to query versions for.
        branch (str): Branch name to filter versions.
        release_type (str): Type of release to filter (e.g. 'release', 'engineering').
        format (str): Output format - either 'text' or 'json'.
        log_level (str): Logging level for the command.

    Returns:
        None. Prints version information to stdout in specified format:
        - text: Simple list of versions
        - json: List of dicts with version and branch information

    Example:
        $ eos-dl info versions --package=EOS --branch=4.28 --release-type=release
        Listing versions:
          - version: 4.28.1F
          - version: 4.28.2F
    """
    token = ctx.obj["token"]
    querier = eos_downloader.logics.arista_server.AristaXmlQuerier(token=token)
    received_versions = querier.available_public_versions(
        package=package, branch=branch, rtype=release_type
    )
    if format == "text":
        click.echo("Listing available versions")
        for version in received_versions:
            click.echo(f"  - version: {version}")
    elif format == "json":
        response = []
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
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--package", type=click.Choice(["eos", "cvp"]), default="eos", required=False
)
@click.option("--branch", "-b", type=str, required=False)
@click.option("--release-type", type=str, required=False)
@click.option(
    "--log-level",
    "--log",
    help="Logging level of the command",
    default="info",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
)
@click.pass_context
def latest(
    ctx: click.Context,
    package: str,
    branch: str,
    release_type: str,
    format: str,
) -> None:
    """List available versions of Arista packages (eos or CVP) packages"""
    token = ctx.obj["token"]
    querier = eos_downloader.logics.arista_server.AristaXmlQuerier(token=token)
    received_versions = querier.latest(
        package=package, branch=branch, rtype=release_type
    )
    if format == "text":
        if branch is not None:
            click.echo(
                f"Latest version for {package}: "
                + click.style(f"{received_versions}", fg="blue")
                + f" for branch {branch}"
            )
        else:
            click.echo(
                f"Latest version for {package}: "
                + click.style(f"{received_versions}", fg="blue")
            )
    elif format == "json":
        response = {}
        response["version"] = str(received_versions)
        print_json(json.dumps(response))


@click.command()
@click.option(
    "--package", type=click.Choice(["eos", "cvp"]), default="eos", required=False
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--details",
    is_flag=True,
    show_default=True,
    default=False,
    help="Show details for each flavor",
)
def mapping(package: str, details: bool, format: str) -> None:
    """List available flavors of Arista packages (eos or CVP) packages"""
    if package.upper() in software_mapping.model_fields:
        mapping_entries = software_mapping.getattr(package.upper())
        if format == "text":
            click.echo(f"Following flavors for {package} have been found:")
            for mapping_entry in mapping_entries:
                click.echo(f"   * Flavor: {mapping_entry}")
                if details:
                    click.echo(f"     - Information: {mapping_entries[mapping_entry]}")
        elif format == "json":
            mapping_json = software_mapping.model_dump()[package.upper()]
            print_json(json.dumps(mapping_json))
