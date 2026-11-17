from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typerdrive import attach_logging, handle_errors

from dot_tools.settings import SrcMode
from dot_tools.src_tools import default_mode, go_to_root, jump_to_folder, current_branch, list_folders, mode_root


cli = typer.Typer(help="Navigate source code folders", no_args_is_help=True)


@cli.callback()
def main(
    ctx: typer.Context,
    mode: Annotated[SrcMode | None, typer.Option("--mode", help="Which source root to use")] = None,
    mine: Annotated[bool, typer.Option("--mine", help="Shortcut for --mode mine")] = False,
    work: Annotated[bool, typer.Option("--work", help="Shortcut for --mode work")] = False,
    others: Annotated[bool, typer.Option("--others", help="Shortcut for --mode others")] = False,
):
    """Navigate source code folders."""
    chosen = [m for m, flag in ((SrcMode.mine, mine), (SrcMode.work, work), (SrcMode.others, others)) if flag]
    if mode is not None:
        chosen.append(mode)
    if len(set(chosen)) > 1:
        raise typer.BadParameter("Specify only one mode")
    ctx.obj = chosen[0] if chosen else default_mode()


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't find folder")
@attach_logging()
def jump(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Text to match against folder names")],
):
    """Navigate to a matching folder in the mode's root."""
    jump_to_folder(ctx.obj, query)


@cli.command()
@handle_errors("Couldn't find source root")
@attach_logging()
def root(ctx: typer.Context):
    """Navigate to the mode's root."""
    go_to_root(ctx.obj)


@cli.command("list")
@handle_errors("Couldn't list folders")
@attach_logging()
def list_(ctx: typer.Context):
    """Show the folders in the mode's root."""
    root = mode_root(ctx.obj)
    folders = list_folders(ctx.obj)
    if not folders:
        typer.echo(f"No folders found in {root}.")
        return
    table = Table(
        title=f"Source folders ({ctx.obj.value})",
        title_style="bold cyan",
        header_style="bold white",
        border_style="blue",
        box=box.ROUNDED,
    )
    table.add_column("Folder", style="green", no_wrap=True)
    table.add_column("Branch", style="yellow", no_wrap=True)
    table.add_column("Path", style="dim")
    for folder in folders:
        table.add_row(folder.name, current_branch(folder), str(folder))
    Console().print(table)
