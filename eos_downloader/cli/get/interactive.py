"""Interactive wizard for ``ardl get eos`` / ``ardl get cvp``.

Instead of requiring the user to know every flag value, the wizard presents the
available choices (format, release type, branch, version) with arrow-key
selection, offers format-dependent options (Docker import for cEOS, EVE-NG for
vEOS), and confirms with the equivalent non-interactive command before starting
the download. The collected parameters are returned so the calling command can
reuse its normal download path.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any, List, Optional

import questionary
import typer
from rich.console import Console

from eos_downloader.models.data import RTYPES, software_mapping
from eos_downloader.models.types import AristaPackage
from eos_downloader.logics.arista_xml_server import AristaXmlQuerier

# cEOS container formats that can be imported into Docker.
CEOS_FORMATS = ("cEOS", "cEOS64", "cEOSarm")
# Formats that can be provisioned on EVE-NG.
VEOS_PREFIX = "vEOS"


@dataclass
class InteractiveResult:  # pylint: disable=too-many-instance-attributes
    """Parameters collected by the interactive wizard."""

    package: str
    image_format: str
    version: str
    output: str
    force: bool = False
    import_docker: bool = False
    docker_name: str = "arista/ceos"
    docker_tag: Optional[str] = None
    eve_ng: bool = False

    def to_command(self) -> str:
        """Render the equivalent non-interactive ``ardl get`` command.

        Arguments are quoted with :func:`shlex.join` so the recap stays accurate
        and copy/paste-safe even when values contain spaces or shell
        metacharacters.
        """
        args: List[str] = [
            "ardl",
            "get",
            self.package,
            "--format",
            self.image_format,
            "--version",
            self.version,
            "--output",
            self.output,
        ]
        if self.force:
            args.append("--force")
        if self.import_docker:
            args += ["--import-docker", "--docker-name", self.docker_name]
            if self.docker_tag:
                args += ["--docker-tag", self.docker_tag]
        if self.eve_ng:
            args.append("--eve-ng")
        return shlex.join(args)


def require_interactive_context(console: Console, token: Optional[str]) -> None:
    """Validate that the interactive wizard can run, or exit with a clear error.

    Parameters
    ----------
    console : Console
        Shared Rich console (its ``is_terminal`` gates the wizard).
    token : Optional[str]
        Arista API token; required because the wizard lists branches/versions.

    Raises
    ------
    typer.Exit
        If output is not an interactive terminal, or no token is available.
    """
    if not console.is_terminal:
        console.print(
            "[red]--interactive requires an interactive terminal (TTY).[/red]"
        )
        raise typer.Exit(1)
    if not token:
        console.print(
            "[red]--interactive requires an Arista token "
            "(set --token or ARISTA_TOKEN).[/red]"
        )
        raise typer.Exit(1)


def _formats_for(package: AristaPackage) -> List[str]:
    """Return the selectable image formats for ``package`` (excludes fallbacks)."""
    mapping = software_mapping.CloudVision if package == "cvp" else software_mapping.EOS
    return [fmt for fmt in mapping.keys() if fmt != "default"]


class _Aborted(Exception):
    """Raised internally when the user cancels a prompt (Ctrl+C)."""


def _ask(prompt: Any) -> Any:
    """Return the prompt's answer, or abort the wizard if it was cancelled."""
    answer = prompt.ask()
    if answer is None:
        raise _Aborted
    return answer


def run_interactive(
    package: AristaPackage,
    console: Console,
    token: str,
    output_default: str,
) -> Optional[InteractiveResult]:
    """Run the interactive wizard and return the collected parameters.

    Parameters
    ----------
    package : AristaPackage
        The package being downloaded, ``"eos"`` or ``"cvp"``.
    console : Console
        Shared Rich console for the recap output.
    token : str
        Arista API token (used to list branches and versions).
    output_default : str
        Default output directory.

    Returns
    -------
    Optional[InteractiveResult]
        The collected parameters, or ``None`` if the user aborted (Ctrl+C or
        declined the confirmation, or no versions matched).
    """
    querier = AristaXmlQuerier(token=token)

    # A cancelled prompt (Ctrl+C -> ``.ask()`` returns None) raises _Aborted via
    # _ask(), which is caught here to abort the whole wizard consistently.
    try:
        # 1. Format
        image_format = _ask(
            questionary.select("Select image format:", choices=_formats_for(package))
        )

        # 2. Release type (EOS only)
        rtype: Optional[str] = None
        if package == "eos":
            rtype = _ask(questionary.select("Select release type:", choices=RTYPES))

        # 3. Branch
        branches = querier.branches(package=package)
        if not branches:
            console.print("[red]No branches found for this package.[/red]")
            return None
        branch = _ask(questionary.select("Select branch:", choices=branches))

        # 4. Version (newest first)
        versions = querier.available_public_versions(
            branch=branch, rtype=rtype, package=package
        )
        version_choices = [str(v) for v in sorted(versions, reverse=True)]
        if not version_choices:
            console.print(
                f"[red]No versions found for branch {branch} "
                f"with the selected criteria.[/red]"
            )
            return None
        version = _ask(
            questionary.select("Select version:", choices=version_choices)
        )

        result = InteractiveResult(
            package=package,
            image_format=image_format,
            version=version,
            output=output_default,
        )

        # 5. Format-dependent options (EOS only)
        if package == "eos":
            _collect_eos_options(result, image_format, version)

        # Common options
        output = _ask(
            questionary.path("Output directory:", default=output_default)
        )
        result.output = output or output_default
        result.force = bool(
            _ask(questionary.confirm("Force re-download if cached?", default=False))
        )

        # 6. Recap + confirmation (declining or cancelling aborts)
        console.print("\n[bold]Equivalent command:[/bold]")
        console.print(f"  [cyan]{result.to_command()}[/cyan]\n")
        if not _ask(questionary.confirm("Start download?", default=True)):
            console.print("[yellow]Aborted.[/yellow]")
            return None
    except _Aborted:
        return None

    return result


def _collect_eos_options(
    result: InteractiveResult, image_format: str, version: str
) -> None:
    """Prompt for the EOS format-dependent options, mutating ``result``.

    Raises
    ------
    _Aborted
        If any prompt is cancelled.
    """
    if image_format in CEOS_FORMATS:
        if _ask(questionary.confirm("Import into Docker?", default=False)):
            result.import_docker = True
            result.docker_name = (
                _ask(questionary.text("Docker image name:", default="arista/ceos"))
                or "arista/ceos"
            )
            result.docker_tag = (
                _ask(questionary.text("Docker image tag:", default=version))
                or version
            )
    elif image_format.startswith(VEOS_PREFIX):
        result.eve_ng = bool(
            _ask(questionary.confirm("Provision EVE-NG?", default=False))
        )
