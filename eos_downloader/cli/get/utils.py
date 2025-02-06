"""Generic functions for the CLI."""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import os
from typing import cast, Optional, Union, Any
import subprocess

import click
from rich.console import Console

from eos_downloader.cli.utils import cli_logging, console_configuration
from eos_downloader.models.data import RTYPE_FEATURE, RTYPES
from eos_downloader.models.types import ReleaseType
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier, AristaXmlObjects


def initialize(ctx: click.Context) -> tuple[Console, str, bool, str]:
    """Initializes the CLI context with necessary configurations.

    Args:
        ctx (click.Context): The Click context object containing command-line parameters.

    Returns:
        tuple: A tuple containing the console configuration, token, debug flag, and log level.
    """

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]
    cli_logging(log_level)

    return console, token, debug, log_level


def search_version(
    console: Console,
    token: str,
    version: Optional[str],
    latest: bool,
    branch: Optional[str],
    file_format: str,
    release_type: str,
) -> Union[str, None]:
    """Searches for the specified EOS version based on the provided parameters.

    Args:
        console (Console): The console object used for printing messages.
        token (str): The authentication token for accessing the EOS API.
        version (str or None): The specific version of EOS to search for. If None, other parameters are used.
        latest (bool): If True, search for the latest EOS version.
        branch (str or None): The branch of EOS to search for. If None, the default branch is used.
        format (str): The format of the EOS version (e.g., 'tar', 'zip').
        release_type (str): The type of release (e.g., 'feature', 'maintenance').

    Returns:
        str: The version of EOS found based on the search criteria.
    """

    if version is not None:
        console.print(
            f"Searching for EOS version [green]{version}[/green] for [blue]{file_format}[/blue] format..."
        )
    elif latest:
        console.print(
            f"Searching for [blue]latest[/blue] EOS version for [blue]{file_format}[/blue] format..."
        )
    elif branch is not None:
        console.print(
            f"Searching for EOS [b]latest[/b] version for [blue]{branch}[/blue] branch for [blue]{file_format}[/blue] format..."
        )

    if branch is not None or latest:
        querier = AristaXmlQuerier(token=token)
        rtype: ReleaseType = cast(
            ReleaseType, release_type if release_type in RTYPES else RTYPE_FEATURE
        )
        version_obj = querier.latest(package="eos", branch=branch, rtype=rtype)
        version = str(version_obj)
    return version


def download_files(
    console: Console,
    cli: Any,
    arista_dl_obj: AristaXmlObjects,
    output: str,
    rich_interface: bool,
    debug: bool,
    checksum_format: str = "sha512sum",
) -> None:
    """Downloads EOS files and verifies their checksums.

    Args:
        console (Console): The console object for printing messages.
        cli (CLI): The CLI object used to perform download and checksum operations.
        arista_dl_obj (AristaPackage): The EOS download object containing version and filename information.
        output (str): The output directory where the files will be saved.
        rich_interface (bool): Flag to indicate if rich interface should be used.
        debug (bool): Flag to indicate if debug information should be printed.
        checksum_format (str): The checksum format to use for verification.

    Raises:
        Exception: If there is an error during the checksum verification.
    """

    console.print(
        f"Starting download for EOS version [green]{arista_dl_obj.version}[/green] for [blue]{arista_dl_obj.image_type}[/blue] format."
    )
    cli.downloads(arista_dl_obj, file_path=output, rich_interface=rich_interface)
    try:
        cli.checksum(checksum_format)
    except subprocess.CalledProcessError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(
                f"[red]Checksum error for file {arista_dl_obj.filename}[/red]"
            )
    console.print(
        f"Arista file [green]{arista_dl_obj.filename}[/green] downloaded in: [blue]{output}[/blue]"
    )


def handle_docker_import(
    console: Console,
    cli: Any,
    arista_dl_obj: AristaXmlObjects,
    output: str,
    docker_name: str,
    docker_tag: Optional[str],
    debug: bool,
) -> int:
    """Handles the import of a Docker image using the provided CLI tool.

    Args:
        console: The console object used for printing messages.
        cli: The CLI tool object that provides the import_docker method.
        arista_dl_obj: An object containing information about the EOS download, including version and filename.
        output: The directory where the Docker image file is located.
        docker_name: The name to assign to the Docker image.
        docker_tag: The tag to assign to the Docker image. If None, the version from eos_dl_obj is used.
        debug: A boolean indicating whether to print detailed exception information.

    Returns:
        int: 0 if the Docker image is imported successfully, 1 if a FileNotFoundError occurs.
    """

    console.print("Importing docker image...")

    if docker_tag is None:
        docker_tag = arista_dl_obj.version

    if arista_dl_obj.filename is None:
        console.print("[red]Invalid filename[/red]")
        return 1

    console.print(
        f"Importing docker image [green]{docker_name}:{docker_tag}[/green] from [blue]{os.path.join(output, arista_dl_obj.filename)}[/blue]..."
    )

    try:
        cli.import_docker(
            local_file_path=os.path.join(output, arista_dl_obj.filename),
            docker_name=docker_name,
            docker_tag=docker_tag,
        )
    except FileNotFoundError:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(
                f"\n[red]File not found: {os.path.join(output, arista_dl_obj.filename)}[/red]"
            )
        return 1

    console.print(
        f"Docker image imported successfully: [green]{docker_name}:{docker_tag}[/green]"
    )

    return 0
