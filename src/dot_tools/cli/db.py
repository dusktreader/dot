from typing import Annotated
from urllib.parse import unquote, urlsplit

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typerdrive import attach_logging, handle_errors

from dot_tools import db_tools

cli = typer.Typer(help="Postgres sessions through temporary k8s port-forwarding pods", no_args_is_help=True)

Alias = Annotated[str, typer.Argument(help="Alias for the database")]
Namespace = Annotated[str | None, typer.Option("-n", "--namespace", help="k8s namespace for the forwarding pod")]
Profile = Annotated[str | None, typer.Option("-p", "--profile", help="AWS profile to use for kubectl")]


def _url_option(url: str | None, current: str | None = None) -> str:
    """Return the given url, or interactively prompt for its components (defaulting to `current`'s)."""
    if url is not None:
        return url
    parts = urlsplit(current) if current else None
    host = typer.prompt("Host (as seen from inside the cluster)", default=(parts and parts.hostname) or "")
    port = typer.prompt("Port", type=int, default=(parts and parts.port) or 5432)
    dbname = typer.prompt("Database name", default=unquote(parts.path.lstrip("/")) if parts else "")
    user = typer.prompt("User", default=unquote(parts.username or "") if parts else "")
    password = typer.prompt(
        "Password (enter to keep current)" if parts and parts.password else "Password",
        hide_input=True,
        default=unquote(parts.password or "") if parts else "",
        show_default=False,
    )
    return db_tools.build_url(user, password, host, port, dbname)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't configure database")
@attach_logging()
def configure(
    ctx: typer.Context,
    alias: Alias,
    url: Annotated[str | None, typer.Argument(help="postgresql://USER:PASS@HOST:PORT/DBNAME (prompted if omitted)")] = None,
    namespace: Namespace = None,
    profile: Profile = None,
):
    """Add a database alias."""
    db_tools.add_db(alias, _url_option(url), namespace, profile)
    typer.echo(f"Configured {alias}")


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't update database")
@attach_logging()
def update(
    ctx: typer.Context,
    alias: Alias,
    url: Annotated[str | None, typer.Argument(help="New URL (prompted if no url, namespace, or profile is given)")] = None,
    namespace: Namespace = None,
    profile: Profile = None,
):
    """Change the URL (and optionally namespace) of an alias."""
    if url is None and namespace is None and profile is None:
        url = _url_option(None, db_tools.get_db(alias).url.get_secret_value())
    db_tools.update_db(alias, url, namespace, profile)
    typer.echo(f"Updated {alias}")


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't remove database")
@attach_logging()
def remove(ctx: typer.Context, alias: Alias):
    """Drop a database alias."""
    db_tools.remove_db(alias)
    typer.echo(f"Removed {alias}")


@cli.command("list")
@handle_errors("Couldn't list databases")
@attach_logging()
def list_(ctx: typer.Context):
    """Show configured databases (passwords masked)."""
    dbs = db_tools.list_dbs()
    if not dbs:
        typer.echo("No databases configured. Use `dt db configure <alias>`.")
        return
    table = Table(title="Databases", title_style="bold cyan", border_style="blue", box=box.ROUNDED)
    table.add_column("Alias", style="green", no_wrap=True)
    table.add_column("Namespace", style="yellow")
    table.add_column("AWS profile", style="magenta")
    table.add_column("URL", style="dim")
    for alias, entry in sorted(dbs.items()):
        table.add_row(alias, entry.namespace or "(current)", entry.profile or "(default)", db_tools.mask_url(entry.url.get_secret_value()))
    Console().print(table)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't log in to database")
@attach_logging()
def login(ctx: typer.Context, alias: Alias, namespace: Namespace = None, profile: Profile = None):
    """Open a pgcli session via a temporary port-forwarding pod, removed on exit."""
    code = db_tools.login(alias, namespace, profile)
    if code:
        raise typer.Exit(code=code)
