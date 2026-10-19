import json
import os
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from typing import Annotated

import pyperclip
import typer
from typerdrive import (
    add_logs_subcommand,
    add_settings_subcommand,
    log_error,
    terminal_message,
    attach_logging,
    handle_errors,
)

from dot_tools.cli.git import cli as git_cli
from dot_tools.cli.ssh import cli as ssh_cli
from dot_tools.cli.creds import cli as creds_cli
from dot_tools.cli.opencode import cli as opencode_cli
from dot_tools.cli.format import cli as format_cli
from dot_tools.cli.worktree import cli as worktree_cli
from dot_tools.cli.worktree import drop_worktree, jump_to_worktree
from dot_tools.configure import DotInstaller
from dot_tools.settings import Settings
from dot_tools.line_length import get_config_line_length
from dot_tools.version import get_version


cli = typer.Typer(rich_markup_mode="rich")
add_settings_subcommand(cli, Settings)
add_logs_subcommand(cli)

cli.add_typer(git_cli, name="git")
cli.add_typer(ssh_cli, name="ssh")
cli.add_typer(creds_cli, name="creds")
cli.add_typer(opencode_cli, name="opencode")
cli.add_typer(format_cli, name="format")
cli.add_typer(worktree_cli, name="worktree")
cli.add_typer(worktree_cli, name="worktrees")


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't find worktree")
@attach_logging()
def jump(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Text to match against worktree branches")],
):
    """Navigate to a matching worktree."""
    jump_to_worktree(query)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't remove worktree")
@attach_logging()
def drop(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Text to match against worktree branches")],
    delete_branch: Annotated[bool, typer.Option("--branch", help="Delete the branch after removing the worktree")] = False,
):
    """Remove a matching worktree."""
    drop_worktree(query, delete_branch)


_SSH_TUNNEL_OPTIONS = (
    "-N",
    "-T",
    "-o",
    "ExitOnForwardFailure=yes",
    "-o",
    "ServerAliveInterval=60",
    "-o",
    "ServerAliveCountMax=3",
)


def _format_tunnel_forward(spec: str) -> str:
    """Format a local-to-remote port specification for ``ssh -L``."""
    parts = spec.split(":")
    if len(parts) == 1:
        local_port = remote_port = parts[0]
    elif len(parts) == 2:
        local_port, remote_port = parts
    else:
        raise typer.BadParameter("must be a PORT or LOCAL_PORT:REMOTE_PORT")

    for port in (local_port, remote_port):
        if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
            raise typer.BadParameter(f"port must be an integer between 1 and 65535: {port!r}")

    return f"{int(local_port)}:127.0.0.1:{int(remote_port)}"


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option(help="Print the version of this app and exit")] = False,
):
    """
    Welcome to dot-tools!

    More information can be shown for each command listed below by running it with the
    --help option.
    """

    if version:
        print(get_version())
        ctx.exit()

    if ctx.invoked_subcommand is None:
        ctx.get_help()
        terminal_message(
            "No command provided. Please check [bold magenta]usage[/bold magenta]",
            subject="Need a dot-tools command",
        )
        ctx.exit()


@cli.command(no_args_is_help=True)
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
        Path, typer.Option(help="Root directory for dot", default_factory=lambda: Path.home() / "src/dusktreader/dot")
    ],
    override_home: Annotated[Path | None, typer.Option(help="Install to this path instead of home")] = None,
    force: Annotated[bool, typer.Option(help="Overwrite destination files that differ from source")] = bool(
        os.environ.get("DOT_FORCE")
    ),
    force_ssh: Annotated[bool, typer.Option(help="Overwrite SSH config files that differ from source")] = False,
):
    """
    Configure dot in your system.
    """
    from loguru import logger
    
    installer = DotInstaller(root=root, override_home=override_home, force=force, force_ssh=force_ssh)
    installer.install_dot()
    
    # After dot setup, check for and invoke wdt if present
    # Output is streamed directly (not captured) to allow Rich formatting to render
    # properly in the work layer. Exit code is propagated on failure.
    wdt_path = shutil.which("wdt")
    if wdt_path:
        logger.debug("Found wdt on PATH, invoking wdt configure")
        wdt_cmd = ["wdt", "configure"]
        if override_home:
            wdt_cmd.extend(["--override-home", str(override_home)])
        if force:
            wdt_cmd.append("--force")
        
        result = subprocess.run(wdt_cmd)

        if result.returncode != 0:
            raise typer.Exit(code=result.returncode)


@cli.command(no_args_is_help=True)
def tunnel(
    target: Annotated[str, typer.Argument(help="SSH destination, such as user@example.com")],
    ports: Annotated[list[str], typer.Argument(help="Local port or LOCAL_PORT:REMOTE_PORT")],
    debug: Annotated[bool, typer.Option(help="Show verbose SSH diagnostics")] = False,
):
    """
    Open an SSH tunnel to a remote host.

    A bare port forwards the same port on both sides. A LOCAL_PORT:REMOTE_PORT
    specification forwards different local and remote ports.
    """
    forwards = [_format_tunnel_forward(port_spec) for port_spec in ports]
    for forward in forwards:
        local_port = forward.split(":", 1)[0]
        remote_port = forward.rsplit(":", 1)[1]
        typer.echo(f"Forwarding localhost:{local_port} to {target}:{remote_port}", err=True)

    command = ["ssh"]
    if debug:
        command.append("-vvv")
    command.extend(_SSH_TUNNEL_OPTIONS)
    for forward in forwards:
        command.extend(("-L", forward))
    command.append(target)

    try:
        result = subprocess.run(command)
    except OSError as error:
        typer.echo(f"Failed to start SSH tunnel: {error}", err=True)
        raise typer.Exit(code=127) from error

    if result.returncode != 0:
        typer.echo(f"SSH tunnel exited with status {result.returncode}.", err=True)
        raise typer.Exit(code=result.returncode)


@cli.command()
@handle_errors("Failed to url encode the provided string", do_except=log_error)
@attach_logging()
def urlencode(
    ctx: typer.Context,
    text: Annotated[str | None, typer.Argument(help="Text to url encode. If not provided, read from stdin")] = None,
):
    """
    URL Encode the provided text
    """
    if text is None:
        text = input()
    dump = urllib.parse.quote(text)
    print(dump)
    pyperclip.copy(dump)
