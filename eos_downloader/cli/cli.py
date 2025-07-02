#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=cyclic-import
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument


"""
ARDL CLI Baseline.
"""

import click

from eos_downloader import __version__
from eos_downloader.cli.debug import commands as debug_commands
from eos_downloader.cli.info import commands as info_commands
from eos_downloader.cli.get import commands as get_commands

from eos_downloader.cli.utils import AliasedGroup


@click.group(
    cls=AliasedGroup, no_args_is_help=True, invoke_without_command=True
)
@click.version_option(__version__)
@click.pass_context
@click.option(
    "--token",
    show_envvar=True,
    default=None,
    help="Arista Token from your customer account",
)
@click.option(
    "--log-level",
    "--log",
    help="Logging level of the command",
    default="error",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
)
# Boolean triggers
@click.option(
    "--debug-enabled",
    "--debug",
    is_flag=True,
    help="Activate debug mode for ardl cli",
    default=False,
)
def ardl(
    ctx: click.Context, token: str, log_level: str, debug_enabled: bool
) -> None:
    """Arista Network Download CLI"""
    ctx.ensure_object(dict)
    ctx.obj["token"] = token
    ctx.obj["log_level"] = log_level
    ctx.obj["debug"] = debug_enabled

    # If no command is provided, show help and exit with code 0
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@ardl.group(cls=AliasedGroup, no_args_is_help=True)
@click.pass_context
def get(ctx: click.Context, cls: click.Group = AliasedGroup) -> None:
    # pylint: disable=redefined-builtin
    """Download Arista from Arista website"""


@ardl.group(cls=AliasedGroup, no_args_is_help=True)
@click.pass_context
def info(ctx: click.Context, cls: click.Group = AliasedGroup) -> None:
    # pylint: disable=redefined-builtin
    """List information from Arista website"""


@ardl.group(cls=AliasedGroup, no_args_is_help=True)
@click.pass_context
def debug(ctx: click.Context, cls: click.Group = AliasedGroup) -> None:
    # pylint: disable=redefined-builtin
    """Debug commands to work with ardl"""


# Load commands at module import time
# Load group commands for get
get.add_command(get_commands.eos)
get.add_command(get_commands.cvp)
get.add_command(get_commands.path)

# Debug
debug.add_command(debug_commands.xml)

# Get info commands
info.add_command(info_commands.versions)
info.add_command(info_commands.latest)
info.add_command(info_commands.mapping)


# ANTA CLI Execution
def cli() -> None:
    """Load ANTA CLI"""
    # Load CLI
    ardl(obj={}, auto_envvar_prefix="arista")


if __name__ == "__main__":
    cli()
