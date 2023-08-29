#!/usr/bin/python
# coding: utf-8 -*-
# pylint: disable=inconsistent-return-statements


"""
Extension for the python ``click`` module
to provide a group or command with aliases.
"""


from typing import Any
import click


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
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
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
