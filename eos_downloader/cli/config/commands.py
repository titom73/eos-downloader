#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""CLI commands for managing ardl configuration."""

import os
from pathlib import Path

import click

from eos_downloader.config import find_config_file, generate_template, load_config
from eos_downloader.helpers.security import mask_token


@click.command(name="init")
@click.option(
    "--output",
    "-o",
    default=str(Path("~/.eos-downloader.toml").expanduser()),
    help="Path for the configuration file",
    type=click.Path(),
    show_default=True,
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Overwrite existing configuration file",
)
def init(output: str, force: bool) -> None:
    """Generate a configuration file template.

    Creates a commented TOML configuration file with all available options.
    The file is created with restricted permissions (0600) since it may
    contain an API token.
    """
    output_path = Path(output).expanduser()

    if output_path.exists() and not force:
        click.echo(
            f"Configuration file already exists: {output_path}\n"
            "Use --force to overwrite.",
            err=True,
        )
        raise SystemExit(1)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template = generate_template()
    output_path.write_text(template, encoding="utf-8")

    # Set restrictive permissions (token may be stored here)
    os.chmod(output_path, 0o600)

    click.echo(f"Configuration file created: {output_path}")


@click.command(name="show")
def show() -> None:
    """Display the active configuration file.

    Shows the path of the active configuration file and its content,
    with the token masked for security.
    """
    config_path = find_config_file()

    if config_path is None:
        click.echo("No configuration file found.")
        click.echo("Run 'ardl config init' to create one.")
        return

    click.echo(f"Active configuration file: {config_path}\n")

    config = load_config(config_path)
    if not config:
        click.echo("Configuration file is empty or invalid.")
        return

    # Re-read raw content for display, masking the token
    content = config_path.read_text(encoding="utf-8")

    # Mask token value if present
    token = config.get("ardl", {}).get("token")
    if token:
        masked = mask_token(token)
        content = content.replace(token, masked)

    click.echo(content)
