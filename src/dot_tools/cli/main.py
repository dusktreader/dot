import typer
from typerdrive import terminal_message


cli = typer.Typer(rich_markup_mode="rich")


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


