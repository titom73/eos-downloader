#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=inconsistent-return-statements


"""
Extension for the python ``click`` module
to provide a group or command with aliases.
"""

from typing import Any
from typer.core import TyperGroup

from rich import pretty
from rich.console import Console


class AliasedTyperGroup(TyperGroup):
    """Command group that accepts an unambiguous prefix as a command alias.

    If there were a command called ``push``, it would accept ``pus`` as an alias
    (so long as it was unique). Typer compiles its applications onto its own
    (vendored) Click ``TyperGroup``, so the aliasing logic lives on that base for
    the Typer root application and every sub-application. An ambiguous prefix
    fails with the list of matches.
    """

    def get_command(self, ctx: Any, cmd_name: str) -> Any:
        """Resolve ``cmd_name`` allowing an unambiguous prefix as an alias."""
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return super().get_command(ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx: Any, args: Any) -> Any:
        """Always return the full command name for a resolved (aliased) command."""
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


def console_configuration() -> Console:
    """Configure Rich Terminal for the CLI."""
    pretty.install()
    console = Console()
    return console
