"""Shared helpers for the ``ardl get`` command implementations."""

from __future__ import annotations

from typing import Any, NoReturn, Optional, TypeVar

import typer
from rich.console import Console

from eos_downloader.cli.get.interactive import (
    InteractiveResult,
    require_interactive_context,
    run_interactive,
)
from eos_downloader.exceptions import AuthenticationError
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier
from eos_downloader.models.types import AristaPackage, ProgressMode

T = TypeVar("T")


def progress_mode_from_flag(no_progress: bool) -> ProgressMode:
    """Translate the CLI ``--no-progress`` flag into a progress mode."""
    return "none" if no_progress else "auto"


def ensure_selection_mode_exclusive(
    version: Optional[str],
    latest: bool,
    branch: Optional[str],
    *,
    option_name: str,
) -> None:
    """Ensure a special selection mode is not mixed with explicit selectors."""
    if version is not None or latest or branch is not None:
        raise typer.BadParameter(
            f"{option_name} is mutually exclusive with --version, --latest, and --branch"
        )


def maybe_run_interactive(
    package: AristaPackage,
    console: Console,
    token: str,
    output: str,
    *,
    interactive: bool,
    version: Optional[str],
    latest: bool,
    branch: Optional[str],
) -> Optional[InteractiveResult]:
    """Run the shared interactive flow when enabled."""
    if not interactive:
        return None
    ensure_selection_mode_exclusive(
        version,
        latest,
        branch,
        option_name="--interactive",
    )
    require_interactive_context(console, token)
    return run_interactive(package, console, token, output)


def print_exception_and_exit(
    console: Console, debug: bool, error: Exception
) -> NoReturn:
    """Render a CLI-safe exception and raise ``typer.Exit(1)``."""
    if debug:
        console.print_exception(show_locals=True)
    else:
        console.print(f"\n[red]Exception raised: {error}[/red]")
    raise typer.Exit(1) from error


def build_download_object(
    factory: type[T],
    console: Console,
    debug: bool,
    **kwargs: Any,
) -> T:
    """Instantiate a download object with consistent CLI error handling."""
    try:
        return factory(**kwargs)
    except Exception as error:  # pylint: disable=broad-exception-caught
        print_exception_and_exit(console, debug, error)


def resolve_cvp_version(
    console: Console,
    token: str,
    *,
    version: Optional[str],
    latest: bool,
    branch: Optional[str],
    file_format: str,
    debug: bool,
) -> Optional[str]:
    """Resolve the CVP version selection, including latest/branch flows."""
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

    if branch is None and not latest:
        return version

    try:
        querier = AristaXmlQuerier(token=token)
        version_obj = querier.latest(package="cvp", branch=branch)
        return str(version_obj)
    except AuthenticationError as auth_error:
        console.print(f"[red]Authentication Error:[/red] {str(auth_error)}")
        raise typer.Exit(1) from auth_error
    except Exception as error:  # pylint: disable=broad-exception-caught
        print_exception_and_exit(console, debug, error)
