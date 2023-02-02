#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=no-value-for-parameter
# pylint: disable=cyclic-import
# pylint: disable=too-many-arguments


"""
ARDL CLI Baseline.
"""

import click
from eos_downloader.cli.get import commands as get_commands


@click.group()
@click.pass_context
@click.option('--token', show_envvar=True, default=None, help='Arista Token from your customer account')
def arista(ctx: click.Context, token: str) -> None:
    """Arista Network Download CLI"""
    ctx.ensure_object(dict)
    ctx.obj['token'] = token


@arista.group(no_args_is_help=True)
@click.pass_context
def get(ctx: click.Context) -> None:
    # pylint: disable=redefined-builtin
    """Download Arista from Arista website"""


# ANTA CLI Execution


def cli() -> None:
    """Load ANTA CLI"""
    # Load group commands
    get.add_command(get_commands.eos)
    # Load CLI
    arista(
        obj={},
        auto_envvar_prefix='arista'
    )


if __name__ == '__main__':
    cli()
