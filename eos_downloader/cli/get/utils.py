"""Generic functions for the CLI."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import os
import sys
from typing import cast, Optional, Union, Any
import subprocess

import click
from rich.console import Console

from eos_downloader.cli.utils import cli_logging, console_configuration
from eos_downloader.models.data import RTYPE_FEATURE, RTYPES
from eos_downloader.models.types import ReleaseType
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier, AristaXmlObjects
from eos_downloader.exceptions import AuthenticationError
from eos_downloader.logging_config import configure_logging, get_logger
from eos_downloader.helpers.security import mask_token


def initialize(ctx: click.Context) -> tuple[Console, str, bool, str]:
    """Initializes the CLI context with necessary configurations.

    Parameters
    ----------
    ctx : click.Context
        The Click context object containing command-line parameters.

    Returns
    -------
    tuple[Console, str, bool, str]
        A tuple containing the console configuration, token, debug flag, and log level.
    """

    console = console_configuration()
    token = ctx.obj["token"]
    debug = ctx.obj["debug"]
    log_level = ctx.obj["log_level"]

    # Configure centralized logging
    configure_logging(level=log_level.upper())
    logger = get_logger()

    # Log token usage securely (masked)
    if token and debug:
        logger.debug(f"Using token: {mask_token(token)}")

    # Legacy logging for backward compatibility
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

    Parameters
    ----------
    console : Console
        The console object used for printing messages.
    token : str
        The authentication token for accessing the EOS API.
    version : str or None
        The specific version of EOS to search for. If None, other parameters are used.
    latest : bool
        If True, search for the latest EOS version.
    branch : str or None
        The branch of EOS to search for. If None, the default branch is used.
    file_format : str
        The format of the EOS version (e.g., 'tar', 'zip').
    release_type : str
        The type of release (e.g., 'feature', 'maintenance').

    Returns
    -------
    str or None
        The version of EOS found based on the search criteria.
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
        try:
            querier = AristaXmlQuerier(token=token)
            rtype: ReleaseType = cast(
                ReleaseType, release_type if release_type in RTYPES else RTYPE_FEATURE
            )
            version_obj = querier.latest(package="eos", branch=branch, rtype=rtype)
            version = str(version_obj)
        except AuthenticationError as auth_error:
            console.print(f"[red]Authentication Error: [/red] {str(auth_error)}")
            sys.exit(1)
    return version


def handle_cli_error(
    console: Console,
    debug: bool,
    error_message: str,
    exit_code: int = 1,
    should_exit: bool = True,
) -> None:
    """Handles CLI errors with appropriate output based on debug mode.

    Parameters
    ----------
    console : Console
        The console object for printing messages.
    debug : bool
        If True, prints full exception traceback with locals.
        If False, prints user-friendly error message.
    error_message : str
        The error message to display in normal mode.
    exit_code : int, optional
        The exit code to use. Defaults to 1.
    should_exit : bool, optional
        If True, exits the program. If False, only prints the error.
        Defaults to True.

    Notes
    -----
    Exits with the specified exit_code if should_exit is True.
    """
    if debug:
        console.print_exception(show_locals=True)
    else:
        console.print(f"[red]{error_message}[/red]")

    if should_exit:
        sys.exit(exit_code)


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

    Parameters
    ----------
    console : Console
        The console object for printing messages.
    cli : Any
        The CLI object used to perform download and checksum operations.
    arista_dl_obj : AristaXmlObjects
        The EOS download object containing version and filename information.
    output : str
        The output directory where the files will be saved.
    rich_interface : bool
        Flag to indicate if rich interface should be used.
    debug : bool
        Flag to indicate if debug information should be printed.
    checksum_format : str, optional
        The checksum format to use for verification. Defaults to "sha512sum".

    Notes
    -----
    Exits with code 1 if ValueError or CalledProcessError occurs.
    In debug mode, prints full exception traceback with local variables.
    In normal mode, prints user-friendly error message without stacktrace.
    """

    console.print(
        f"Starting download for EOS version [green]{arista_dl_obj.version}[/green] for [blue]{arista_dl_obj.image_type}[/blue] format."
    )
    try:
        # downloads() returns a tuple (path, was_cached)
        _file_path, was_cached = cli.downloads(
            arista_dl_obj, file_path=output, rich_interface=rich_interface
        )
        cli.checksum(checksum_format)

        # Display appropriate message based on cache status
        if was_cached:
            console.print(
                f"[green]✓[/green] File [cyan]{arista_dl_obj.filename}[/cyan] "
                f"found in cache: [blue]{output}[/blue]"
            )
            console.print("   [dim]Use --force to re-download[/dim]")
        else:
            console.print(
                f"[green]✓[/green] Arista file [cyan]{arista_dl_obj.filename}[/cyan] "
                f"downloaded in: [blue]{output}[/blue]"
            )
    except ValueError as e:
        handle_cli_error(console, debug, f"Error: {e}")

    except subprocess.CalledProcessError:
        handle_cli_error(
            console, debug, f"Checksum error for file {arista_dl_obj.filename}"
        )


def handle_docker_import(
    console: Console,
    cli: Any,
    arista_dl_obj: AristaXmlObjects,
    output: str,
    docker_name: str,
    docker_tag: Optional[str],
    debug: bool,
    force: bool = False,
) -> int:
    """Handles the import of a Docker image using the provided CLI tool.

    Parameters
    ----------
    console : Console
        The console object used for printing messages.
    cli : Any
        The CLI tool object that provides the import_docker method.
    arista_dl_obj : AristaXmlObjects
        An object containing information about the EOS download,
        including version and filename.
    output : str
        The directory where the Docker image file is located.
    docker_name : str
        The name to assign to the Docker image.
    docker_tag : str or None
        The tag to assign to the Docker image. If None, the version
        from arista_dl_obj is used.
    debug : bool
        A boolean indicating whether to print detailed exception information.
    force : bool, optional
        If True, import even if the Docker image already exists.
        Defaults to False.

    Returns
    -------
    int
        0 if the Docker image is imported successfully or cached,
        1 if a FileNotFoundError occurs.
    """

    console.print("Importing docker image...")

    if docker_tag is None:
        docker_tag = arista_dl_obj.version

    if arista_dl_obj.filename is None:
        console.print("[red]Invalid filename[/red]")
        return 1

    console.print(
        f"Importing docker image [green]{docker_name}: {docker_tag}[/green] "
        f"from [blue]{os.path.join(output, arista_dl_obj.filename)}[/blue]..."
    )

    try:
        was_cached = cli.import_docker(
            local_file_path=os.path.join(output, arista_dl_obj.filename),
            docker_name=docker_name,
            docker_tag=docker_tag,
            force=force,
        )
    except FileNotFoundError:
        handle_cli_error(
            console,
            debug,
            f"\nFile not found: {os.path.join(output, arista_dl_obj.filename)}",
            exit_code=1,
            should_exit=False,
        )
        return 1

    # Display appropriate message based on whether image was cached or imported
    if was_cached:
        console.print(
            f"Docker image [green]{docker_name}: {docker_tag}[/green] "
            f"is already in docker"
        )
    else:
        console.print(
            f"Docker image imported successfully: [green]{docker_name}: {docker_tag}[/green]"
        )

    return 0
