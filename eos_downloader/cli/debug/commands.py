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

# Standard library imports
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Third party imports
import click

# Local imports
import eos_downloader.defaults
import eos_downloader.logics.arista_server
from eos_downloader.cli.utils import cli_logging


@click.command()
@click.pass_context
@click.option(
    "--output",
    default=str("arista.xml"),
    help="Path to save XML file",
    type=click.Path(),
    show_default=True,
)
@click.option(
    "--log-level",
    "--log",
    help="Logging level of the command",
    default="INFO",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
)
def xml(ctx: click.Context, output: str, log_level: str) -> None:
    """Downloads and saves XML data from Arista EOS server.

    This function authenticates with an Arista server, retrieves XML data,
    and saves it to a file in a prettified format.

    Args:
        ctx (click.Context): Click context object containing authentication token
        output (str): File path where the XML output should be saved
        log_level (str): Logging level to use for output messages

    Raises:
        Exception: If authentication with the server fails

    Example:
        >>> xml(ctx, "output.xml", "INFO")
        INFO: connected to server aaa.bbb.ccc
        INFO: XML file saved under output.xml
    """

    log = cli_logging(log_level)
    token = ctx.obj["token"]
    server = eos_downloader.logics.arista_server.AristaServer(
        token=token, session_server=eos_downloader.defaults.DEFAULT_SERVER_SESSION
    )
    try:
        server.authenticate()
    except Exception as error:  # pylint: disable=W0703
        log.error(f"Cant connect to server: {error}")
    log.info(f"connected to server {eos_downloader.defaults.DEFAULT_SERVER_SESSION}")
    xml_data = server.get_xml_data()
    if xml_data is None:
        log.error("No XML data received")
        return
    xml_object: ET.ElementTree = xml_data  # pylint: disable=protected-access
    xml_content = xml_object.getroot()

    if xml_content is None:
        log.error("XML root element is None")
        return

    xmlstr = minidom.parseString(ET.tostring(xml_content)).toprettyxml(
        indent="    ", newl=""
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(str(xmlstr))
    log.info(f"XML file saved under {output}")
