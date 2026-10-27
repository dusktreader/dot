"""OpenCode CLI commands."""

import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Annotated

import dateparser
import typer
from auto_name_enum import AutoNameEnum, auto
from rich.console import Console
from rich.table import Table
from rich.text import Text
from typerdrive import handle_errors, log_error

from dot_tools.exceptions import OpenCodeError
from dot_tools.opencode_costs import (
    REPORT_COLUMNS,
    OpenCodeSessionStore,
    Report,
    _NoWrapPager,
    display_directory,
    fields,
    session_summary_rows,
)
from dot_tools.opencode_profile import MODEL_ALIASES, OpenCodeProfileError, personal_lifecycle, routing_tier, validate_model
from dot_tools.opencode_staleness_guard import check_before_edit, record_read
from dot_tools.opencode_trends import DEFAULT_MAX_MODELS, aggregate_daily_model_costs, render_trends

cli = typer.Typer(no_args_is_help=True)
staleness_guard_cli = typer.Typer(no_args_is_help=True)
cli.add_typer(staleness_guard_cli, name="staleness-guard")


class OutputFormat(AutoNameEnum):
    table = auto()
    json = auto()
    csv = auto()


@cli.command(
    "launch",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def launch(
    ctx: typer.Context,
    model: Annotated[str, typer.Option("--model", help="Model alias: light-luna, light-haiku, standard-terra, standard-sonnet, premium-sol, or premium-opus")] = "light-luna",
    premium_ok: Annotated[bool, typer.Option("--premium-ok", help="Allow switching to a premium model after launch")] = False,
    session: Annotated[str | None, typer.Option("--session", "-s", help="Resume an existing OpenCode session")] = None,
) -> None:
    """
    Launch OpenCode through the personal LiteLLM router.

    The default `light-luna` model uses the tool-capable Luna route. Select one of the supported aliases with
    `--model`; premium models authorize premium routing, and `--premium-ok` authorizes switching to premium later.
    Invalid models fail before router startup.

    OpenCode arguments are passed through unchanged. The personal router listens only on `127.0.0.1:4010` and keeps
    OpenCode, Copilot, XDG, PID, log, and cache state under `~/.local/state/personal`. `HOME` remains unchanged so
    the shared `~/.agents` directory remains available.

    Use `dt opencode status` to inspect the router and `dt opencode stop` to stop only the profile-owned router. The
    personal light route may fall back to OpenCode Zen; the work profile never uses that fallback. Routing profile,
    capability, and tier metadata come from the launcher and plugin, not model-generated text.
    """
    try:
        validate_model(model)
        arguments = ["--session", session] if session is not None else []
        personal_lifecycle().launch([*arguments, *ctx.args], model, premium_ok)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    except OpenCodeProfileError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@cli.command("prompt")
def prompt(
    prompt_text: Annotated[str, typer.Argument(help="Prompt to send to OpenCode")],
    model: Annotated[str, typer.Option("--model", help="Model alias: light-luna, light-haiku, standard-terra, standard-sonnet, premium-sol, or premium-opus")] = "light-luna",
) -> None:
    """Run a single prompt through the personal LiteLLM router."""
    try:
        validate_model(model)
        personal_lifecycle().launch(["run", prompt_text], model)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    except OpenCodeProfileError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@cli.command("models")
def models() -> None:
    """List model aliases available through the personal LiteLLM router."""
    for model in sorted(MODEL_ALIASES):
        typer.echo(f"{model}\t{routing_tier(model)}")


@cli.command("auth")
def auth(
    provider: Annotated[str, typer.Argument(help="Provider to authenticate: copilot or zen")] = "copilot",
) -> None:
    """Authenticate a provider for the personal OpenCode profile."""
    lifecycle = personal_lifecycle()
    try:
        if provider == "zen":
            api_key = typer.prompt("OpenCode Zen API key", hide_input=True, confirmation_prompt=True)
            lifecycle.bind_zen_api_key(api_key)
            typer.echo("OpenCode Zen API key stored. Run `dt opencode stop` and relaunch to apply it.")
            return
        if provider != "copilot":
            typer.echo("Provider must be 'copilot' or 'zen'.", err=True)
            raise typer.Exit(code=2)
        lifecycle.authenticate()
    except OpenCodeProfileError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@cli.command("status")
def status() -> None:
    """Show the personal OpenCode router status."""
    try:
        personal_lifecycle().status()
    except OpenCodeProfileError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@cli.command("stop")
def stop() -> None:
    """Stop the personal OpenCode router when this profile owns it."""
    try:
        personal_lifecycle().stop()
    except OpenCodeProfileError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@cli.command("logs")
def logs(
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Continue printing new log entries")] = False,
    lines: Annotated[int, typer.Option("-n", "--lines", min=1, help="Number of recent lines to show")] = 30,
) -> None:
    """Show the personal OpenCode application log."""
    log_file = personal_lifecycle().open_code_log_file
    if not log_file.is_file():
        typer.echo(f"OpenCode log file not found: {log_file}", err=True)
        raise typer.Exit(code=1)

    command = ["tail", f"-n{lines}"]
    if follow:
        command.append("-f")
    result = subprocess.run([*command, str(log_file)], check=False)
    if result.returncode:
        raise typer.Exit(code=result.returncode)


@cli.command("sessions")
@handle_errors("Failed to list OpenCode sessions", do_except=log_error)
def sessions(
    since: Annotated[str | None, typer.Option(help="Inclusive start date for last activity")] = None,
    sort: Annotated[
        str | None,
        typer.Option(
            help="Sort by session ID, working directory, or last activity; prefix with asc: or desc: "
            "(default: last activity descending)"
        ),
    ] = None,
    all_sessions: Annotated[bool, typer.Option("--all", help="Include child and subagent sessions")] = False,
) -> None:
    """List OpenCode sessions, working directories, and last activity."""
    parsed_sort = _parse_session_sort(sort) if sort is not None else None
    since_date = _parse_date(since) if since is not None else None
    with OpenCodeSessionStore() as store:
        summaries = store.session_summaries()

    if since_date is not None:
        summaries = [
            summary
            for summary in summaries
            if datetime.fromtimestamp(summary.last_activity / 1000, tz=timezone.utc).date() >= since_date
        ]
    if not all_sessions:
        summaries = [summary for summary in summaries if summary.parent_id is None]

    rows = session_summary_rows(summaries, parsed_sort)
    if not rows:
        typer.echo("No OpenCode sessions found.")
        return

    table = Table(title="OpenCode sessions", show_lines=False)
    table.add_column("Session", no_wrap=True, overflow="ignore")
    table.add_column("Working directory", no_wrap=True, overflow="ignore")
    table.add_column("Last activity", no_wrap=True, overflow="ignore")
    for summary, session_display in rows:
        is_child = session_display.lstrip().startswith(("├─", "└─"))
        directory = display_directory(summary.directory)
        if is_child:
            directory = f" ↳ {directory}"
        last_activity = datetime.fromtimestamp(summary.last_activity / 1000, tz=timezone.utc).isoformat(timespec="seconds")
        if is_child:
            last_activity = f" ↳ {last_activity}"
        table.add_row(
            Text(session_display, style="dim" if is_child else "bold"),
            Text(directory, style="dim bright_blue" if is_child else "bold bright_blue"),
            Text(last_activity, style="dim" if is_child else "bold"),
        )

    console = Console()
    if console.is_terminal and (len(rows) + 4 > console.height or console.measure(table).maximum > console.width):
        with console.pager(pager=_NoWrapPager(), styles=True):
            console.print(table)
    else:
        console.print(table)


@staleness_guard_cli.command("read")
def staleness_guard_read(file_paths: Annotated[list[Path], typer.Argument()]) -> None:
    """Record files after OpenCode reads them."""
    for file_path in file_paths:
        record_read(file_path)


@staleness_guard_cli.command("check")
def staleness_guard_check(file_paths: Annotated[list[Path], typer.Argument()]) -> None:
    """Reject files changed since OpenCode last read them."""
    for file_path in file_paths:
        error = check_before_edit(file_path)
        if error is not None:
            typer.echo(error, err=True)
            raise typer.Exit(code=1)


def _parse_sort(value: str) -> list[tuple[str, bool]]:
    """Parse comma-separated sort keys into (field, descending) pairs, last key first."""
    report_columns = [getattr(REPORT_COLUMNS, f.name) for f in fields(REPORT_COLUMNS)]
    sortable_columns = [column for column in report_columns if column.label]
    parsed: list[tuple[str, bool]] = []
    for item in value.split(","):
        direction, separator, column = item.strip().partition(":")
        if separator:
            direction = direction.casefold()
            OpenCodeError.require_condition(
                direction in {"asc", "desc"}, f"Invalid sort direction {direction!r}; use 'asc' or 'desc'"
            )
        else:
            direction, column = "desc", item.strip()
        query = column.strip().casefold()
        matches = [
            sort_column
            for sort_column in sortable_columns
            if all(part in sort_column.label.casefold() for part in query.split())
        ]
        choices = ", ".join(sort_column.label for sort_column in sortable_columns)
        field = OpenCodeError.enforce_defined(
            matches[0].field if len(matches) == 1 else None,
            (
                f"Ambiguous sort column {column.strip()!r}; matches: {', '.join(match.label for match in matches)}"
                if matches
                else f"Invalid sort column {column.strip()!r}; choose one of: {choices}"
            ),
        )
        parsed.insert(0, (field, direction == "desc"))
    return parsed


def _parse_session_sort(value: str) -> list[tuple[str, bool]]:
    """Parse session sort keys into (field, descending) pairs, last key first."""
    columns = [
        ("session_id", "Session ID"),
        ("directory", "Working directory"),
        ("last_activity", "Last activity"),
    ]
    parsed: list[tuple[str, bool]] = []
    for item in value.split(","):
        direction, separator, column = item.strip().partition(":")
        if separator:
            direction = direction.casefold()
            OpenCodeError.require_condition(
                direction in {"asc", "desc"}, f"Invalid sort direction {direction!r}; use 'asc' or 'desc'"
            )
        else:
            direction, column = "desc", item.strip()
        query = column.strip().casefold()
        OpenCodeError.require_condition(bool(query), "Sort column cannot be empty")
        matches = [
            (field, label)
            for field, label in columns
            if all(part in label.casefold() for part in query.split())
        ]
        choices = ", ".join(label for _, label in columns)
        field = OpenCodeError.enforce_defined(
            matches[0][0] if len(matches) == 1 else None,
            (
                f"Ambiguous sort column {column.strip()!r}; matches: {', '.join(label for _, label in matches)}"
                if matches
                else f"Invalid sort column {column.strip()!r}; choose one of: {choices}"
            ),
        )
        parsed.insert(0, (field, direction == "desc"))
    return parsed


def _parse_date(value: str) -> date:
    """Parse ISO 8601 or natural-language date expression for a CLI option."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass
    parsed = dateparser.parse(value, settings={"RETURN_AS_TIMEZONE_AWARE": True, "PREFER_DAY_OF_MONTH": "first"})
    return OpenCodeError.enforce_defined(parsed, f"Cannot parse date {value!r}").date()


@cli.command()
@handle_errors("Failed to report OpenCode costs", do_except=log_error)
def costs(
    ctx: typer.Context,
    since: Annotated[date | None, typer.Option(help="Inclusive start date", parser=_parse_date)] = None,
    until: Annotated[date | None, typer.Option(help="Inclusive end date", parser=_parse_date)] = None,
    directory: Annotated[str | None, typer.Option(help="Exact project directory filter")] = None,
    agent: Annotated[str | None, typer.Option(help="Exact agent filter")] = None,
    model: Annotated[str | None, typer.Option(help="Exact model filter")] = None,
    sort: Annotated[str | None, typer.Option(help="Sort rows: [asc:|desc:]<column>[,...]")] = None,
    format: Annotated[OutputFormat, typer.Option("--format", help="Output format")] = OutputFormat.table,
    file: Annotated[Path | None, typer.Option("--file", help="Write output to an existing parent directory")] = None,
    provider: Annotated[str | None, typer.Option(help="Exact model provider filter")] = None,
) -> None:
    """Report recorded and locally estimated OpenCode session costs."""
    parsed_sort = _parse_sort(sort) if sort is not None else None
    OpenCodeError.require_condition(
        file is None or file.parent.is_dir(),
        f"Output parent directory does not exist: {file.parent}" if file is not None else "",
    )
    with OpenCodeSessionStore() as store:
        report = Report.build(store.sessions(), since, until, directory, agent, model, parsed_sort, provider)
    if file is None and format is OutputFormat.table and sys.stdout.isatty():
        report.display()
    elif file is None:
        print(report.render(format.value))
    else:
        rendered = report.render(format.value)
        file.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""))


@cli.command()
@handle_errors("Failed to report OpenCode usage trends", do_except=log_error)
def trends(
    ctx: typer.Context,
    since: Annotated[date | None, typer.Option(help="Inclusive start date", parser=_parse_date)] = None,
    max_models: Annotated[
        int,
        typer.Option(
            min=0,
            help=f"Maximum named models before grouping the rest as other (default: {DEFAULT_MAX_MODELS})",
        ),
    ] = DEFAULT_MAX_MODELS,
    provider: Annotated[str | None, typer.Option(help="Exact model provider filter")] = None,
) -> None:
    """Chart recorded OpenCode session costs over time."""
    with OpenCodeSessionStore() as store:
        series = aggregate_daily_model_costs(store.sessions(), since, max_models, provider)
    print(render_trends(series))
