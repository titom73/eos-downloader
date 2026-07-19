#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""CLI commands for managing ardl configuration."""

import os
from pathlib import Path

import typer

from eos_downloader.config import find_config_file, generate_template, load_config
from eos_downloader.helpers.security import mask_token
from eos_downloader.cli.utils import AliasedTyperGroup

app = typer.Typer(
    cls=AliasedTyperGroup, no_args_is_help=True, help="Manage ardl configuration."
)


@app.command(name="init")
def init(
    output: str = typer.Option(
        str(Path("~/.eos-downloader.toml").expanduser()),
        "--output",
        "-o",
        help="Path for the configuration file",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration file",
    ),
) -> None:
    """Generate a configuration file template.

    Creates a commented TOML configuration file with all available options.
    The file is created with restricted permissions (0600) since it may
    contain an API token.
    """
    output_path = Path(output).expanduser()

    if output_path.exists() and not force:
        typer.echo(
            f"Configuration file already exists: {output_path}\n"
            "Use --force to overwrite.",
            err=True,
        )
        raise typer.Exit(1)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template = generate_template()
    output_path.write_text(template, encoding="utf-8")

    # Set restrictive permissions (token may be stored here)
    os.chmod(output_path, 0o600)

    typer.echo(f"Configuration file created: {output_path}")


@app.command(name="show")
def show() -> None:
    """Display the active configuration file.

    Shows the path of the active configuration file and its content,
    with the token masked for security.
    """
    config_path = find_config_file()

    if config_path is None:
        typer.echo("No configuration file found.")
        typer.echo("Run 'ardl config init' to create one.")
        return

    typer.echo(f"Active configuration file: {config_path}\n")

    config = load_config(config_path)
    if not config:
        typer.echo("Configuration file is empty or invalid.")
        return

    # Re-read raw content for display, masking the token
    content = config_path.read_text(encoding="utf-8")

    # Mask token value if present
    token = config.get("ardl", {}).get("token")
    if token:
        masked = mask_token(token)
        content = content.replace(token, masked)

    typer.echo(content)
