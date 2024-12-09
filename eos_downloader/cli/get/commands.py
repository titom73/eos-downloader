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
from eos_downloader.logics.arista_server import EosXmlObject

from .utils import initialize, search_version, download_files, handle_docker_import


@click.command()
@click.option("--format", default="vmdk", help="Image format", show_default=True)
@click.option(
    "--output",
    default=str(os.path.relpath(os.getcwd(), start=os.curdir)),
    help="Path to save image",
    type=click.Path(),
    show_default=True,
)
@click.option(
    "--latest",
    is_flag=True,
    help="Get latest version. If --branch is not use, get the latest branch with specific release type",
    default=False,
)
@click.option(
    "--eve-ng",
    is_flag=True,
    help="Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server)",
    default=False,
)
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
@click.option(
    "--docker-name", default="arista/ceos", help="Docker image name", show_default=True
)
@click.option("--docker-tag", default=None, help="Docker image tag", show_default=True)
@click.option(
    "--version", default=None, help="EOS version to download", show_default=True
)
@click.option(
    "--release-type",
    default=RTYPE_FEATURE,
    help="Release type (M for Maintenance, F for Feature)",
    show_default=True,
)
@click.option("--branch", default=None, help="Branch to download", show_default=True)
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
