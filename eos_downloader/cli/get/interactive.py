"""Interactive wizard for ``ardl get eos`` / ``ardl get cvp``.

Instead of requiring the user to know every flag value, the wizard presents the
available choices (format, release type, branch, version) with arrow-key
selection, offers format-dependent options (Docker import for cEOS, EVE-NG for
vEOS), and confirms with the equivalent non-interactive command before starting
the download. The collected parameters are returned so the calling command can
reuse its normal download path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

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
        """Render the equivalent non-interactive ``ardl get`` command."""
        parts: List[str] = [
            f"ardl get {self.package}",
            f"--format {self.image_format}",
            f"--version {self.version}",
            f"--output {self.output}",
        ]
        if self.force:
            parts.append("--force")
        if self.import_docker:
            parts.append("--import-docker")
            parts.append(f"--docker-name {self.docker_name}")
            if self.docker_tag:
                parts.append(f"--docker-tag {self.docker_tag}")
        if self.eve_ng:
            parts.append("--eve-ng")
        return " ".join(parts)


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

    # 1. Format
    image_format = questionary.select(
        "Select image format:", choices=_formats_for(package)
    ).ask()
    if image_format is None:
        return None

    # 2. Release type (EOS only)
    rtype: Optional[str] = None
    if package == "eos":
        rtype = questionary.select("Select release type:", choices=RTYPES).ask()
        if rtype is None:
            return None

    # 3. Branch
    branches = querier.branches(package=package)
    if not branches:
        console.print("[red]No branches found for this package.[/red]")
        return None
    branch = questionary.select("Select branch:", choices=branches).ask()
    if branch is None:
        return None

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
    version = questionary.select("Select version:", choices=version_choices).ask()
    if version is None:
        return None

    result = InteractiveResult(
        package=package,
        image_format=image_format,
        version=version,
        output=output_default,
    )

    # 5. Format-dependent options (EOS only)
    if package == "eos":
        if image_format in CEOS_FORMATS:
            if questionary.confirm("Import into Docker?", default=False).ask():
                result.import_docker = True
                result.docker_name = (
                    questionary.text("Docker image name:", default="arista/ceos").ask()
                    or "arista/ceos"
                )
                result.docker_tag = (
                    questionary.text("Docker image tag:", default=version).ask()
                    or version
                )
        elif image_format.startswith(VEOS_PREFIX):
            result.eve_ng = bool(
                questionary.confirm("Provision EVE-NG?", default=False).ask()
            )

    # Common options
    output = questionary.path("Output directory:", default=output_default).ask()
    result.output = output or output_default
    result.force = bool(
        questionary.confirm("Force re-download if cached?", default=False).ask()
    )

    # 6. Recap + confirmation
    console.print("\n[bold]Equivalent command:[/bold]")
    console.print(f"  [cyan]{result.to_command()}[/cyan]\n")
    if not questionary.confirm("Start download?", default=True).ask():
        console.print("[yellow]Aborted.[/yellow]")
        return None

    return result
