#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# flake8: noqa E501

"""
Commands for ARDL CLI to get data.
"""

import os
import sys
from typing import Union

import click
from loguru import logger
from rich.console import Console

import eos_downloader.eos
from eos_downloader.models.version import BASE_VERSION_STR, RTYPE_FEATURE, RTYPES

EOS_IMAGE_TYPE = ['64', 'INT', '2GB-INT', 'cEOS', 'cEOS64', 'vEOS', 'vEOS-lab', 'EOS-2GB', 'default']
CVP_IMAGE_TYPE = ['ova', 'rpm', 'kvm', 'upgrade']

@click.command(no_args_is_help=True)
@click.pass_context
@click.option('--image-type', default='default', help='EOS Image type', type=click.Choice(EOS_IMAGE_TYPE), required=True)
@click.option('--version', default=None, help='EOS version', type=str, required=False)
@click.option('--latest', '-l', is_flag=True, type=click.BOOL, default=False, help='Get latest version in given branch. If --branch is not use, get the latest branch with specific release type')
@click.option('--release-type', '-rtype', type=click.Choice(RTYPES, case_sensitive=False), default=RTYPE_FEATURE, help='EOS release type to search')
@click.option('--branch', '-b', type=click.STRING, default=None, help='EOS Branch to list releases')
@click.option('--docker-name', default='arista/ceos', help='Docker image name (default: arista/ceos)', type=str, show_default=True)
@click.option('--output', default=str(os.path.relpath(os.getcwd(), start=os.curdir)), help='Path to save image', type=click.Path(),show_default=True)
# Debugging
@click.option('--log-level', '--log', help='Logging level of the command', default=None, type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
# Boolean triggers
@click.option('--eve-ng', is_flag=True, help='Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server)', default=False)
@click.option('--disable-ztp', is_flag=True, help='Disable ZTP process in vEOS image (only available with --eve-ng)', default=False)
@click.option('--import-docker', is_flag=True, help='Import docker image (only available with --image_type cEOSlab)', default=False)
def eos(
    ctx: click.Context, image_type: str, output: str, log_level: str, eve_ng: bool, disable_ztp: bool,
    import_docker: bool, docker_name: str, version: Union[str, None] = None, release_type: str = RTYPE_FEATURE,
    latest: bool = False, branch: Union[str,None] = None
    ) -> int:
    """Download EOS image from Arista website"""
    console = Console()
    # Get from Context
    token = ctx.obj['token']
    if token is None or token == '':
        console.print('❗ Token is unset ! Please configure ARISTA_TOKEN or use --token option', style="bold red")
        sys.exit(1)

    logger.remove()
    if log_level is not None:
        logger.add("eos-downloader.log", rotation="10 MB", level=log_level.upper())

    console.print("🪐 [bold blue]eos-downloader[/bold blue] is starting...", )
    console.print(f'    - Image Type: {image_type}')
    console.print(f'    - Version: {version}')


    if version is not None:
        my_download = eos_downloader.eos.EOSDownloader(
            image=image_type,
            software='EOS',
            version=version,
            token=token,
            hash_method='sha512sum')
        my_download.authenticate()

    elif latest:
        my_download = eos_downloader.eos.EOSDownloader(
            image=image_type,
            software='EOS',
            version='unset',
            token=token,
            hash_method='sha512sum')
        my_download.authenticate()
        if branch is None:
            branch = str(my_download.latest_branch(rtype=release_type).branch)
        latest_version = my_download.latest_eos(branch, rtype=release_type)
        if str(latest_version) == BASE_VERSION_STR:
            console.print(f'[red]Error[/red], cannot find any version in {branch} for {release_type} release type')
            sys.exit(1)
        my_download.version = str(latest_version)

    if eve_ng:
        my_download.provision_eve(noztp=disable_ztp, checksum=True)
    else:
        my_download.download_local(file_path=output, checksum=True)

    if import_docker:
        my_download.docker_import(
            image_name=docker_name
        )
    console.print('✅  processing done !')
    sys.exit(0)



@click.command(no_args_is_help=True)
@click.pass_context
@click.option('--format', default='upgrade', help='CVP Image type', type=click.Choice(CVP_IMAGE_TYPE), required=True)
@click.option('--version', default=None, help='CVP version', type=str, required=True)
@click.option('--output', default=str(os.path.relpath(os.getcwd(), start=os.curdir)), help='Path to save image', type=click.Path(),show_default=True)
@click.option('--log-level', '--log', help='Logging level of the command', default=None, type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
def cvp(ctx: click.Context, version: str, format: str, output: str, log_level: str) -> int:
    """Download CVP image from Arista website"""
    console = Console()
    # Get from Context
    token = ctx.obj['token']
    if token is None or token == '':
        console.print('❗ Token is unset ! Please configure ARISTA_TOKEN or use --token option', style="bold red")
        sys.exit(1)

    logger.remove()
    if log_level is not None:
        logger.add("eos-downloader.log", rotation="10 MB", level=log_level.upper())

    console.print("🪐 [bold blue]eos-downloader[/bold blue] is starting...", )
    console.print(f'    - Image Type: {format}')
    console.print(f'    - Version: {version}')

    my_download = eos_downloader.eos.EOSDownloader(
        image=format,
        software='CloudVision',
        version=version,
        token=token,
        hash_method='md5sum')

    my_download.authenticate()

    my_download.download_local(file_path=output, checksum=False)
    console.print('✅  processing done !')
    sys.exit(0)
