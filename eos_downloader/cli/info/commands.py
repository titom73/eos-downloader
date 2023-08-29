#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# flake8: noqa E501

"""
Commands for ARDL CLI to list data.
"""

import sys
from typing import Union

import click
from loguru import logger
from rich.console import Console
from rich.pretty import pprint

import eos_downloader.eos
from eos_downloader.models.version import BASE_VERSION_STR, RTYPE_FEATURE, RTYPES


@click.command(no_args_is_help=True)
@click.pass_context
@click.option(
    "--latest",
    "-l",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Get latest version in given branch. If --branch is not use, get the latest branch with specific release type",
)
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
    "--verbose",
    "-v",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Human readable output. Default is none to use output in script)",
)
@click.option(
    "--log-level",
    "--log",
    help="Logging level of the command",
    default="warning",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
)
def eos_versions(
    ctx: click.Context,
    log_level: str,
    branch: Union[str, None] = None,
    release_type: str = RTYPE_FEATURE,
    latest: bool = False,
    verbose: bool = False,
) -> None:
    # pylint: disable = too-many-branches
    """
    List Available EOS version on Arista.com website.

    Comes with some filters to get latest release (F or M) as well as branch filtering

      - To get latest M release available (without any branch): ardl info eos-versions --latest -rtype m

      - To get latest F release available: ardl info eos-versions --latest -rtype F
    """
    console = Console()
    # Get from Context
    token = ctx.obj["token"]

    logger.remove()
    if log_level is not None:
        logger.add("eos-downloader.log", rotation="10 MB", level=log_level.upper())

    my_download = eos_downloader.eos.EOSDownloader(
        image="unset",
        software="EOS",
        version="unset",
        token=token,
        hash_method="sha512sum",
    )

    auth = my_download.authenticate()
    if verbose and auth:
        console.print("✅ Authenticated on arista.com")

    if release_type is not None:
        release_type = release_type.upper()

    if latest:
        if branch is None:
            branch = str(my_download.latest_branch(rtype=release_type).branch)
        latest_version = my_download.latest_eos(branch, rtype=release_type)
        if str(latest_version) == BASE_VERSION_STR:
            console.print(
                f"[red]Error[/red], cannot find any version in {branch} for {release_type} release type"
            )
            sys.exit(1)
        if verbose:
            console.print(
                f"Branch {branch} has been selected with release type {release_type}"
            )
            if branch is not None:
                console.print(f"Latest release for {branch}: {latest_version}")
            else:
                console.print(f"Latest EOS release: {latest_version}")
        else:
            console.print(f"{ latest_version }")
    else:
        versions = my_download.get_eos_versions(branch=branch, rtype=release_type)
        if verbose:
            console.print(
                f'List of available versions for {branch if branch is not None else "all branches"}'
            )
            for version in versions:
                console.print(f"  → {str(version)}")
        else:
            pprint([str(version) for version in versions])
