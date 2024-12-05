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
from typing import Union, cast

import click

import eos_downloader.logics.arista_server
import eos_downloader.logics.download
from eos_downloader.cli.utils import cli_logging, console_configuration
from eos_downloader.models.data import RTYPE_FEATURE, RTYPES, eos_package_format
from eos_downloader.models.types import ReleaseType


@click.command(no_args_is_help=True)
@click.pass_context
@click.option(
    "--format",
    "--image-type",
    default="default",
    help="EOS Image type",
    type=click.Choice(eos_package_format),
    required=True,
)
@click.option("--version", default=None, help="EOS version", type=str, required=False)
@click.option(
    "--release-type",
    "-rtype",
    type=click.Choice(RTYPES, case_sensitive=False),
    default=RTYPE_FEATURE,
    help="EOS release type to search",
)
@click.option(
    "--branch",
    "-b",
    type=click.STRING,
    default=None,
    help="EOS Branch to list releases",
)
@click.option(
    "--docker-name",
    default="arista/ceos",
    help="Docker image name (default: arista/ceos)",
    type=str,
    show_default=True,
)
@click.option(
    "--docker-tag",
    help="Docker image tag (default: ceos-version)",
    type=click.STRING,
    default=None,
    show_default=True,
    required=False,
)
@click.option(
    "--output",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save image",
    type=click.Path(),
    show_default=True,
)

# Boolean triggers
@click.option(
    "--latest",
    is_flag=True,
    help="Get latest version. If --branch is not use, get the latest branch with specific release type",
    default=False,
)
# Not yet implemented - waiting for correct internet connection
# @click.option(
#     "--eve-ng",
#     is_flag=True,
#     help="Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server)",
#     default=False,
# )
# @click.option(
#     "--disable-ztp",
#     is_flag=True,
#     help="Disable ZTP process in vEOS image (only available with --eve-ng)",
#     default=False,
# )
@click.option(
    "--import-docker",
    is_flag=True,
    help="Import docker image to local docker",
    default=False,
)
@click.option(
    "--skip-download",
    is_flag=True,
    help="Skip download process - for debug only",
    default=False,
)
def eos(
    ctx: click.Context,
    format: str,
    output: str,
    # eve_ng: bool,
    # disable_ztp: bool,
    import_docker: bool,
    skip_download: bool,
    docker_name: str,
    docker_tag: str,
    version: Union[str, None] = None,
    release_type: str = RTYPE_FEATURE,
    latest: bool = False,
    branch: Union[str, None] = None,
) -> int:
    """Download EOS image from Arista server."""

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    cli_logging(log_level)

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

    eos_dl_obj: eos_downloader.logics.arista_server.EosXmlObject
    if branch is not None or latest:
        querier = eos_downloader.logics.arista_server.AristaXmlQuerier(token=token)
        rtype: ReleaseType = cast(
            ReleaseType, release_type if release_type in RTYPES else RTYPE_FEATURE
        )
        version_obj = querier.latest(package="eos", branch=branch, rtype=rtype)
        version = str(version_obj)
    try:
        eos_dl_obj = eos_downloader.logics.arista_server.EosXmlObject(
            searched_version=version,  # type: ignore[arg-type]
            token=token,
            image_type=format,
        )
    except Exception:
        console.print_exception(show_locals=True)

    cli = eos_downloader.logics.download.SoftManager()

    console.print(
        f"Starting download for EOS version [green]{eos_dl_obj.version}[/green] for [blue]{format}[/blue] format."
    )

    if skip_download is False:
        cli.downloads(eos_dl_obj, file_path=output, rich_interface=True)
        try:
            cli.checksum("sha512sum")
        except Exception:
            console.print_exception(show_locals=True)
            # logging.critical(f"Checksum error for file {eos_dl_obj.filename}")
        console.print(
            f"EOS file [green]{eos_dl_obj.filename}[/green] downloaded in: [blue]{output}[/blue]"
        )

    # Docker management.
    if import_docker:
        console.print("Importing docker image...")
        if docker_tag is None:
            docker_tag = eos_dl_obj.version
        # Not yet implemented - waiting for correct internet connection
        console.print(
            f"Importing docker image [green]{docker_name}:{docker_tag}[/green] from [blue]{os.path.join(output, eos_dl_obj.filename)}[/blue]..."  # type: ignore[arg-type]
        )
        try:
            cli.import_docker(
                local_file_path=os.path.join(output, eos_dl_obj.filename),  # type: ignore[arg-type]
                docker_name=docker_name,
                docker_tag=docker_tag,
            )
        except FileNotFoundError:
            if debug:
                console.print_exception(show_locals=True)
            else:
                console.print(
                    f"\n[red]File not found: {os.path.join(output, eos_dl_obj.filename)}[/red]"  # type: ignore[arg-type]
                )
            return 1
        console.print(
            f"Docker image imported successfully: [green]{docker_name}:{docker_tag}[/green]"
        )
    return 0
