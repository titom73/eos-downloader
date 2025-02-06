#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# pylint: disable=broad-exception-caught
# flake8: noqa E501

"""CLI commands for listing Arista package information."""

import os
from typing import Union
import click
from eos_downloader.models.data import RTYPE_FEATURE
from eos_downloader.logics.download import SoftManager
from eos_downloader.logics.arista_server import AristaServer
from eos_downloader.logics.arista_xml_server import (
    EosXmlObject,
    AristaXmlQuerier,
    CvpXmlObject,
)

from .utils import initialize, search_version, download_files, handle_docker_import


@click.command()
@click.option("--format", default="vmdk", help="Image format", show_default=True)
@click.option(
    "--output",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save image",
    type=click.Path(),
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--latest",
    is_flag=True,
    help="Get latest version. If --branch is not use, get the latest branch with specific release type",
    default=False,
    show_envvar=True,
)
@click.option(
    "--eve-ng",
    is_flag=True,
    help="Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server)",
    default=False,
    show_envvar=True,
)
@click.option(
    "--import-docker",
    is_flag=True,
    help="Import docker image to local docker",
    default=False,
    show_envvar=True,
)
@click.option(
    "--skip-download",
    is_flag=True,
    help="Skip download process - for debug only",
    default=False,
)
@click.option(
    "--docker-name",
    default="arista/ceos",
    help="Docker image name",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--docker-tag",
    default=None,
    help="Docker image tag",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--version",
    default=None,
    help="EOS version to download",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--release-type",
    default=RTYPE_FEATURE,
    help="Release type (M for Maintenance, F for Feature)",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--branch",
    default=None,
    help="Branch to download",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Enable dry-run mode: only run code without system changes",
    default=False,
)
@click.pass_context
def eos(
    ctx: click.Context,
    format: str,
    output: str,
    eve_ng: bool,
    import_docker: bool,
    skip_download: bool,
    docker_name: str,
    docker_tag: str,
    version: Union[str, None],
    release_type: str,
    latest: bool,
    branch: Union[str, None],
    dry_run: bool,
) -> int:
    """Download EOS image from Arista server."""
    # pylint: disable=unused-variable
    console, token, debug, log_level = initialize(ctx)
    version = search_version(
        console, token, version, latest, branch, format, release_type
    )
    if version is None:
        raise ValueError("Version is not set correctly")
    try:
        eos_dl_obj = EosXmlObject(
            searched_version=version, token=token, image_type=format
        )
    except Exception:
        console.print_exception(show_locals=True)
        return 1

    cli = SoftManager(dry_run=dry_run)

    if not skip_download:
        if not eve_ng:
            download_files(
                console, cli, eos_dl_obj, output, rich_interface=True, debug=debug
            )
        else:
            try:
                cli.provision_eve(eos_dl_obj, noztp=True)
            except Exception as e:
                if debug:
                    console.print_exception(show_locals=True)
                else:
                    console.print(f"\n[red]Exception raised: {e}[/red]")
                return 1

    if import_docker:
        return handle_docker_import(
            console, cli, eos_dl_obj, output, docker_name, docker_tag, debug
        )

    return 0


@click.command()
@click.option(
    "--format",
    default="ova",
    help="Image format",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--output",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save image",
    type=click.Path(),
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--latest",
    is_flag=True,
    help="Get latest version. If --branch is not use, get the latest branch with specific release type",
    default=False,
    show_envvar=True,
)
@click.option(
    "--version",
    default=None,
    help="EOS version to download",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--branch",
    default=None,
    help="Branch to download",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Enable dry-run mode: only run code without system changes",
    default=False,
)
@click.pass_context
def cvp(
    ctx: click.Context,
    latest: bool,
    format: str,
    output: str,
    version: Union[str, None],
    branch: Union[str, None],
    dry_run: bool = False,
) -> int:
    """Download CVP image from Arista server."""
    # pylint: disable=unused-variable
    console, token, debug, log_level = initialize(ctx)

    if version is not None:
        console.print(
            f"Searching for EOS version [green]{version}[/green] for [blue]{format}[/blue] format..."
        )
    elif latest:
        console.print(
            f"Searching for [blue]latest[/blue] EOS version for [blue]{format}[/blue] format..."
        )
    elif branch is not None:
        console.print(
            f"Searching for EOS [b]latest[/b] version for [blue]{branch}[/blue] branch for [blue]{format}[/blue] format..."
        )

    if branch is not None or latest:
        try:
            querier = AristaXmlQuerier(token=token)
            version_obj = querier.latest(package="cvp", branch=branch)
            version = str(version_obj)
        except Exception as e:
            console.print(f"Token is set to: {token}")
            console.print_exception(show_locals=True)
            return 1

    console.print(f"version to download is {version}")

    if version is None:
        raise ValueError("Version is not set correctly")
    try:
        cvp_dl_obj = CvpXmlObject(
            searched_version=version, token=token, image_type=format
        )
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        return 1

    cli = SoftManager(dry_run=dry_run)
    download_files(
        console,
        cli,
        cvp_dl_obj,
        output,
        rich_interface=True,
        debug=debug,
        checksum_format="md5sum",
    )

    console.print(f"CVP file is saved under: {output}")
    return 0


@click.command()
@click.option(
    "--source",
    "-s",
    help="Image path to download from Arista Website",
    type=str,
    show_default=False,
    show_envvar=False,
)
@click.option(
    "--output",
    "-o",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save downloaded package",
    type=click.Path(),
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--import-docker",
    is_flag=True,
    help="Import docker image to local docker",
    default=False,
    show_envvar=True,
)
@click.option(
    "--docker-name",
    default="arista/ceos:raw",
    help="Docker image name",
    show_default=True,
    show_envvar=True,
)
@click.option(
    "--docker-tag",
    default="dev",
    help="Docker image tag",
    show_default=True,
    show_envvar=True,
)
@click.pass_context
# pylint: disable=too-many-branches
def path(
    ctx: click.Context,
    output: str,
    source: str,
    import_docker: bool,
    docker_name: str,
    docker_tag: str,
) -> int:
    """Download image from Arista server using direct path."""
    console, token, debug, log_level = initialize(ctx)

    if source is None:
        console.print("[red]Source is not set correctly ![/red]")
        return 1

    filename = os.path.basename(source)

    console.print(f"Downloading file {filename} from source: {source}")
    console.print(f"Saving file to: {output}")

    ar_server = AristaServer(token=token)

    try:
        file_url = ar_server.get_url(source)
        if log_level == "debug":
            console.print(f"URL to download file is: {file_url}")
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        return 1

    if file_url is None:
        console.print("File URL is set to None when we expect a string")
        return 1

    cli = SoftManager(dry_run=False)

    try:
        cli.download_file(file_url, output, filename=filename)
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        return 1

    if import_docker:
        console.print(
            f"Importing docker image [green]{docker_name}:{docker_tag}[/green] from [blue]{os.path.join(output, filename)}[/blue]..."
        )

        try:
            cli.import_docker(
                local_file_path=os.path.join(output, filename),
                docker_name=docker_name,
                docker_tag=docker_tag,
            )
        except FileNotFoundError:
            if debug:
                console.print_exception(show_locals=True)
            else:
                console.print(
                    f"\n[red]File not found: {os.path.join(output, filename)}[/red]"
                )
            return 1

        console.print(
            f"Docker image imported successfully: [green]{docker_name}:{docker_tag}[/green]"
        )

    return 0
