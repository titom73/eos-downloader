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
from rich.console import Console
import eos_downloader
from eos_downloader.cli.get import commands as get_commands
from eos_downloader.cli.debug import commands as debug_commands
from eos_downloader.cli.info import commands as info_commands


@click.group()
@click.pass_context
@click.option('--token', show_envvar=True, default=None, help='Arista Token from your customer account')
def ardl(ctx: click.Context, token: str) -> None:
    """Arista Network Download CLI"""
    ctx.ensure_object(dict)
    ctx.obj['token'] = token


@click.command()
def version() -> None:
    """Display version of ardl"""
    console = Console()
    console.print(f'ardl is running version {eos_downloader.__version__}')


@ardl.group(no_args_is_help=True)
@click.pass_context
def get(ctx: click.Context) -> None:
    # pylint: disable=redefined-builtin
    """Download Arista from Arista website"""


@ardl.group(no_args_is_help=True)
@click.pass_context
def info(ctx: click.Context) -> None:
    # pylint: disable=redefined-builtin
    """List information from Arista website"""


@ardl.group(no_args_is_help=True)
@click.pass_context
def debug(ctx: click.Context) -> None:
    # pylint: disable=redefined-builtin
    """Debug commands to work with ardl"""

# ANTA CLI Execution


def cli() -> None:
    """Load ANTA CLI"""
    # Load group commands
    get.add_command(get_commands.eos)
    get.add_command(get_commands.cvp)
    info.add_command(info_commands.eos_versions)
    debug.add_command(debug_commands.xml)
    ardl.add_command(version)
    # Load CLI
    ardl(
        obj={},
        auto_envvar_prefix='arista'
    )


if __name__ == '__main__':
    cli()
