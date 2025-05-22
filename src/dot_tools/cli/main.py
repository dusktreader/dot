import typer
from typerdrive import add_logs_subcommand, add_settings_subcommand, terminal_message

from dot_tools.cli.git import cli as git_cli
from dot_tools.settings import Settings


cli = typer.Typer(rich_markup_mode="rich")
add_settings_subcommand(cli, Settings)
add_logs_subcommand(cli)

cli.add_typer(git_cli, name="git")


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


