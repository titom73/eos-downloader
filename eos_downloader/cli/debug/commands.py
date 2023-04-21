#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
# pylint: disable=line-too-long
# pylint: disable=duplicate-code
# flake8: noqa E501

"""
Commands for ARDL CLI to get data.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

import click
from loguru import logger
from rich.console import Console

import eos_downloader.eos


@click.command()
@click.pass_context
@click.option('--output', default=str('arista.xml'), help='Path to save XML file', type=click.Path(), show_default=True)
@click.option('--log-level', '--log', help='Logging level of the command', default=None, type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
def xml(ctx: click.Context, output: str, log_level: str) -> None:
    # sourcery skip: remove-unnecessary-cast
    """Extract XML directory structure"""
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

    my_download.authenticate()
    xml_object: ET.ElementTree = my_download._get_folder_tree()  # pylint: disable=protected-access
    xml_content = xml_object.getroot()

    xmlstr = minidom.parseString(ET.tostring(xml_content)).toprettyxml(indent="    ", newl='')
    with open(output, "w", encoding='utf-8') as f:
        f.write(str(xmlstr))

    console.print(f'XML file saved in: { output }')
