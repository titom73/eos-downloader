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
from enum import Enum
from xml.dom import minidom

# Third party imports
import typer

# Local imports
import eos_downloader.defaults
import eos_downloader.logics.arista_server
from eos_downloader.logging_config import configure_logging, get_logger
from eos_downloader.cli.utils import AliasedTyperGroup

app = typer.Typer(
    cls=AliasedTyperGroup,
    no_args_is_help=True,
    help="Debug commands to work with ardl",
)


class LogLevel(str, Enum):
    """Logging levels accepted by the ``--log-level`` option."""

    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


@app.command()
def xml(
    ctx: typer.Context,
    output: str = typer.Option(
        "arista.xml",
        "--output",
        help="Path to save XML file",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.info,
        "--log-level",
        "--log",
        help="Logging level of the command",
        case_sensitive=False,
    ),
) -> None:
    """Downloads and saves XML data from Arista EOS server.

    This function authenticates with an Arista server, retrieves XML data,
    and saves it to a file in a prettified format.

    Args:
        ctx (typer.Context): Context object containing authentication token
        output (str): File path where the XML output should be saved
        log_level (str): Logging level to use for output messages

    Raises:
        Exception: If authentication with the server fails

    Example:
        >>> xml(ctx, "output.xml", "INFO")
        INFO: connected to server aaa.bbb.ccc
        INFO: XML file saved under output.xml
    """

    configure_logging(level=log_level.value.upper())
    log = get_logger()
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
