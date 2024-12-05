#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=inconsistent-return-statements


"""
Extension for the python ``click`` module
to provide a group or command with aliases.
"""

import logging
from typing import Any
import click

from rich import pretty
from rich.logging import RichHandler
from rich.console import Console


class AliasedGroup(click.Group):
    """
    Implements a subclass of Group that accepts a prefix for a command.
    If there were a command called push, it would accept pus as an alias (so long as it was unique)
    """

    def get_command(self, ctx: click.Context, cmd_name: str) -> Any:
        """Documentation to build"""
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx: click.Context, args: Any) -> Any:
        """Documentation to build"""
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


def cli_logging(level: str = "error") -> logging.Logger:
    """
    Configures and returns a logger with the specified logging level.

    This function sets up the logging configuration using the RichHandler
    to provide rich formatted log messages. The log messages will include
    the time and can contain markup and rich tracebacks.

    Args:
        level (str): The logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

    Returns:
        logging.Logger: A configured logger instance.
    """

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=level.upper(),
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                show_path=True,
                show_time=True,
                show_level=True,
                markup=True,
                rich_tracebacks=True,
                tracebacks_suppress=[click],
            )
        ],
    )
    log = logging.getLogger("rich")
    return log


def console_configuration() -> Console:
    """Configure Rich Terminal for the CLI."""
    pretty.install()
    console = Console()
    return console
