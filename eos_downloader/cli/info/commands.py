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

import os
import sys

import click
from loguru import logger
from rich.console import Console

import eos_downloader.eos
from eos_downloader.models.version import BASE_VERSION_STR, BASE_BRANCH_STR


@click.command()
@click.pass_context
@click.option('--branch', '-b', type=click.STRING, default=None, help='EOS Branch to list releases')
@click.option('--release-type', '-r', type=click.Choice(['m', 'f'], case_sensitive=False), default=None, help='EOS release type to search')
@click.option('--latest/--no-latest', '-l', type=click.BOOL, default=False, help='Get latest version in given branch (require --branch)')
@click.option('--verbose/--no-verbose', '-v', type=click.BOOL, default=False, help='Human readable output. Default is none to use output in script)')
@click.option('--log-level', '--log', help='Logging level of the command', default='warning', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
def eos_versions(ctx: click.Context, log_level: str, branch: str = None, release_type: str = None, latest: bool = False, verbose: bool = False) -> None:
    """
    List Available EOS version on Arista.com website.

    Comes with some filters to get latest release (F or M) as well as branch filtering
    """
    console = Console()
    # Get from Context
    token = ctx.obj['token']

    logger.remove()
    if log_level is not None:
        logger.add("eos-downloader.log", rotation="10 MB", level=log_level.upper())

    my_download = eos_downloader.eos.EOSDownloader(
        image='unset',
        software='EOS',
        version='unset',
        token=token,
        hash_method='sha512sum')

    auth = my_download.authenticate()
    if verbose and auth:
        console.print('✅ Authenticated on arista.com')

    if release_type is not None:
        release_type = release_type.upper()

    if branch is None:
        branch = str(my_download.latest_branch().branch())

    if latest:
        latest_version = my_download.latest_eos(branch,release_type)
        if str(latest_version) == BASE_VERSION_STR:
            latest_version = f'version not found in branch {branch}'
        if verbose:
            if branch is not None:
                console.print(f'Latest release for {branch}: {latest_version}')
            else:
                console.print(f'Latest EOS release: {latest_version}')
        else:
            console.print(f'{ latest_version }')
    else:
        versions = my_download.get_eos_versions(branch=branch)
        if verbose:
            console.print(f'List of available versions for {branch}')
            for version in versions:
                console.print(f'  → {str(version)}')
        else:
            console.print(f'{[str(version) for version in versions]}')
