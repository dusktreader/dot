import json
from pathlib import Path
from typing import Annotated

import typer
from typerdrive import (
    add_logs_subcommand,
    add_settings_subcommand,
    log_error,
    terminal_message,
    attach_logging,
    handle_errors,
)

from dot_tools.cli.branches import cli as branches_cli
from dot_tools.configure import DotInstaller
from dot_tools.settings import Settings
from dot_tools.line_length import get_config_line_length


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


@cli.command()
@attach_logging()
def line_length(ctx: typer.Context):
    """
    Get the line length for source files in a project.
    """
    print(get_config_line_length())


@cli.command()
@handle_errors("Failed to complete dot setup", do_except=log_error)
@attach_logging()
def configure(
    ctx: typer.Context,
    root: Annotated[
        Path,
        typer.Option(
            help="Root directory for dot",
            default_factory=lambda: Path.home() / "git-repos/personal/dot"
        )
    ],
    override_home: Annotated[Path | None, typer.Option(help="Install to this path instead of home")] = None,
):
    """
    Configure dot in your system.
    """
    installer = DotInstaller(root=root, override_home=override_home)
    installer.install_dot()
