#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# flake8: noqa E501

"""CLI commands for listing Arista package information."""

import os
from pathlib import Path
from typing import Optional

import typer

from eos_downloader.models.data import RTYPE_FEATURE
from eos_downloader.logics.download import SoftManager
from eos_downloader.logics.arista_server import AristaServer
from eos_downloader.logics.arista_xml_server import (
    EosXmlObject,
    AristaXmlQuerier,
    CvpXmlObject,
)
from eos_downloader.exceptions import AuthenticationError

from eos_downloader.cli.utils import AliasedTyperGroup

from .utils import (
    initialize,
    search_version,
    download_files,
    handle_docker_import,
    download_from_containerlab_topology,
)

app = typer.Typer(
    cls=AliasedTyperGroup,
    no_args_is_help=True,
    help="Download Arista from Arista website",
)

_DEFAULT_OUTPUT = str(os.path.relpath(os.getcwd(), start=os.curdir))


@app.command()
def eos(
    ctx: typer.Context,
    format: str = typer.Option("vmdk", "--format", help="Image format"),
    output: str = typer.Option(
        _DEFAULT_OUTPUT, "--output", help="Path to save image", show_envvar=True
    ),
    latest: bool = typer.Option(
        False,
        "--latest",
        help="Get latest version. If --branch is not use, get the latest branch with specific release type",
        show_envvar=True,
    ),
    eve_ng: bool = typer.Option(
        False,
        "--eve-ng",
        help="Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server)",
        show_envvar=True,
    ),
    import_docker: bool = typer.Option(
        False,
        "--import-docker",
        help="Import docker image to local docker",
        show_envvar=True,
    ),
    skip_download: bool = typer.Option(
        False,
        "--skip-download",
        help="Skip download process - for debug only",
    ),
    docker_name: str = typer.Option(
        "arista/ceos",
        "--docker-name",
        help="Docker image name",
        show_envvar=True,
    ),
    docker_tag: Optional[str] = typer.Option(
        None,
        "--docker-tag",
        help="Docker image tag",
        show_envvar=True,
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="EOS version to download",
        show_envvar=True,
    ),
    release_type: str = typer.Option(
        RTYPE_FEATURE,
        "--release-type",
        help="Release type (M for Maintenance, F for Feature)",
        show_envvar=True,
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        help="Branch to download",
        show_envvar=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Enable dry-run mode: only run code without system changes",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force download/import even if cached files or Docker images exist",
        show_envvar=True,
    ),
    containerlab_topology: Optional[Path] = typer.Option(
        None,
        "--containerlab-topology",
        "--clab",
        help="Path to containerlab topology file to download all cEOS images.",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
) -> int:
    """Download EOS image from Arista server."""
    # pylint: disable=unused-variable
    console, token, debug, log_level = initialize(ctx)

    if containerlab_topology is not None:
        if version is not None or latest or branch is not None:
            raise typer.BadParameter(
                "--containerlab-topology is mutually exclusive with --version, --latest, and --branch"
            )
        # Auto-default to cEOS format when using containerlab topology
        ceos_formats = ("cEOS", "cEOS64", "cEOSarm")
        if format not in ceos_formats:
            console.print(
                f"[yellow]Format '{format}' is not a cEOS format. "
                f"Auto-defaulting to 'cEOS' for containerlab topology.[/yellow]"
            )
            format = "cEOS"
        return download_from_containerlab_topology(
            console=console,
            token=token,
            topology_file=Path(containerlab_topology),
            image_format=format,
            output=output,
            docker_name=docker_name,
            docker_tag=docker_tag,
            dry_run=dry_run,
            force=force,
            debug=debug,
            skip_download=skip_download,
        )

    version = search_version(
        console, token, version, latest, branch, format, release_type
    )
    if version is None:
        raise ValueError("Version is not set correctly")
    try:
        eos_dl_obj = EosXmlObject(
            searched_version=version, token=token, image_type=format
        )
    except Exception as exc:
        # Only dump the locals-rich traceback in debug mode: it contains the
        # Arista token and other sensitive locals.
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {exc}[/red]")
        raise typer.Exit(1) from exc

    cli = SoftManager(dry_run=dry_run, force_download=force)

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
                raise typer.Exit(1)

    if import_docker:
        if dry_run:
            effective_tag = docker_tag or version
            console.print(
                f"[DRY-RUN] Would import docker image [green]{docker_name}:{effective_tag}[/green]"
            )
            return 0
        return handle_docker_import(
            console, cli, eos_dl_obj, output, docker_name, docker_tag, debug, force
        )

    return 0


@app.command()
def cvp(
    ctx: typer.Context,
    latest: bool = typer.Option(
        False,
        "--latest",
        help="Get latest version. If --branch is not use, get the latest branch with specific release type",
        show_envvar=True,
    ),
    format: str = typer.Option(
        "ova",
        "--format",
        help="Image format",
        show_envvar=True,
    ),
    output: str = typer.Option(
        _DEFAULT_OUTPUT,
        "--output",
        help="Path to save image",
        show_envvar=True,
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="EOS version to download",
        show_envvar=True,
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        help="Branch to download",
        show_envvar=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Enable dry-run mode: only run code without system changes",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force download even if cached files exist",
        show_envvar=True,
    ),
) -> int:
    """Download CVP image from Arista server."""
    # pylint: disable=unused-variable
    console, token, debug, log_level = initialize(ctx)

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

    if branch is not None or latest:
        try:
            querier = AristaXmlQuerier(token=token)
            version_obj = querier.latest(package="cvp", branch=branch)
            version = str(version_obj)
        except AuthenticationError as auth_error:
            console.print(f"[red]Authentication Error:[/red] {str(auth_error)}")
            raise typer.Exit(1) from auth_error
        except Exception as e:
            # Never echo the token; only show the locals-rich traceback (which
            # also contains the token) when debug mode is enabled.
            if debug:
                console.print_exception(show_locals=True)
            else:
                console.print(f"\n[red]Exception raised: {e}[/red]")
            raise typer.Exit(1) from e

    console.print(f"version to download is {version}")

    if version is None:
        raise ValueError("Version is not set correctly")
    try:
        cvp_dl_obj = CvpXmlObject(
            searched_version=version, token=token, image_type=format
        )
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        raise typer.Exit(1)

    cli = SoftManager(dry_run=dry_run, force_download=force)
    download_files(
        console,
        cli,
        cvp_dl_obj,
        output,
        rich_interface=True,
        debug=debug,
        checksum_format="md5sum",
    )

    console.print(f"CVP file is saved under: {output}")
    return 0


@app.command()
def path(
    ctx: typer.Context,
    source: Optional[str] = typer.Option(
        None,
        "--source",
        "-s",
        help="Image path to download from Arista Website",
    ),
    output: str = typer.Option(
        _DEFAULT_OUTPUT,
        "--output",
        "-o",
        help="Path to save downloaded package",
        show_envvar=True,
    ),
    import_docker: bool = typer.Option(
        False,
        "--import-docker",
        help="Import docker image to local docker",
        show_envvar=True,
    ),
    docker_name: str = typer.Option(
        "arista/ceos:raw",
        "--docker-name",
        help="Docker image name",
        show_envvar=True,
    ),
    docker_tag: str = typer.Option(
        "dev",
        "--docker-tag",
        help="Docker image tag",
        show_envvar=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force download/import even if cached files or Docker images exist",
        show_envvar=True,
    ),
) -> int:
    """Download image from Arista server using direct path."""
    console, token, debug, log_level = initialize(ctx)

    if source is None:
        console.print("[red]Source is not set correctly ![/red]")
        raise typer.Exit(1)

    filename = os.path.basename(source)

    console.print(f"Downloading file {filename} from source: {source}")
    console.print(f"Saving file to: {output}")

    ar_server = AristaServer(token=token)

    try:
        file_url = ar_server.get_url(source)
        if log_level == "debug":
            console.print(f"URL to download file is: {file_url}")
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        raise typer.Exit(1)

    if file_url is None:
        console.print("File URL is set to None when we expect a string")
        raise typer.Exit(1)

    # At this point, mypy knows file_url is not None due to the check above
    assert file_url is not None  # Type assertion for mypy

    cli = SoftManager(dry_run=False, force_download=force)

    try:
        cli.download_file(file_url, output, filename=filename, force=force)
    except Exception as e:
        if debug:
            console.print_exception(show_locals=True)
        else:
            console.print(f"\n[red]Exception raised: {e}[/red]")
        raise typer.Exit(1)

    if import_docker:
        console.print(
            f"Importing docker image [green]{docker_name}:{docker_tag}[/green] "
            f"from [blue]{os.path.join(output, filename)}[/blue]..."
        )

        try:
            cli.import_docker(
                local_file_path=os.path.join(output, filename),
                docker_name=docker_name,
                docker_tag=docker_tag,
                force=force,
            )
        except FileNotFoundError as exc:
            if debug:
                console.print_exception(show_locals=True)
            else:
                console.print(
                    f"\n[red]File not found: {os.path.join(output, filename)}[/red]"
                )
            raise typer.Exit(1) from exc

        console.print(
            f"Docker image imported successfully: [green]{docker_name}:{docker_tag}[/green]"
        )

    return 0
