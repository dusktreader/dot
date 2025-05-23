import json
from typing import Annotated

import typer
from typerdrive import add_logs_subcommand, add_settings_subcommand, terminal_message

from dot_tools.cli.branches import cli as branches_cli
from dot_tools.settings import Settings


cli = typer.Typer(rich_markup_mode="rich")
add_settings_subcommand(cli, Settings)
add_logs_subcommand(cli)

cli.add_typer(branches_cli, name="branch")


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
):
    """
    Welcome to dot-tools!

    More information can be shown for each command listed below by running it with the
    --help option.
    """

    if ctx.invoked_subcommand is None:
        ctx.get_help()
        terminal_message(
            "No command provided. Please check [bold magenta]usage[/bold magenta]",
            subject="Need a dot-tools command",
        )
        ctx.exit()


@cli.command()
def kv(
    kv: Annotated[list[str], typer.Argument(help="Key value pairs to include in the produced json")],
    sep: Annotated[str, typer.Option(help="Separator for key value pairs")] = "->",
    include_quotes: Annotated[bool, typer.Option(help="Include quotes in the produced json")] = False,
):
    """
    Produce a JSON string with the provided key/value pairs
    """
    output = json.dumps({k: v for (k, v) in [s.split(sep) for s in kv]})
    if include_quotes:
        output = f"'{output}'"
    print(output)
