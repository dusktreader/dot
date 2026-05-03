import os
from pathlib import Path
from typing import Annotated

import typer
from typerdrive import attach_logging, handle_errors, log_error

from dot_tools.ssh_tools import connect_host, _default_key_path

cli = typer.Typer(help="Commands to manage SSH connections")


@cli.callback(invoke_without_command=True)
def ssh_main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@cli.command(no_args_is_help=True)
@handle_errors("Failed to connect host", do_except=log_error)
@attach_logging()
def connect(
    ctx: typer.Context,
    host: Annotated[str, typer.Argument(help="Hostname or IP address of the target machine")],
    alias: Annotated[str, typer.Argument(help="Alias name to use in ~/.ssh/config")],
    user: Annotated[str, typer.Option(help="Remote username")] = os.getlogin(),
    port: Annotated[int, typer.Option(help="SSH port")] = 22,
    key: Annotated[Path, typer.Option(help="Path to the local private key")] = _default_key_path(),
):
    """
    Set up SSH access to a remote host.

    Copies your public key to the remote's authorized_keys and adds a named
    entry to your local ~/.ssh/config.
    """
    connect_host(host=host, alias=alias, user=user, port=port, key_path=key)
