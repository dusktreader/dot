"""OpenCode CLI commands."""

from datetime import date
from pathlib import Path
import sys
from typing import Annotated

import dateparser
from auto_name_enum import AutoNameEnum, auto
import typer
from typerdrive import handle_errors, log_error

from dot_tools.exceptions import OpenCodeError
from dot_tools.opencode_costs import REPORT_COLUMNS, OpenCodeSessionStore, Report, fields
from dot_tools.opencode_staleness_guard import check_before_edit, record_read
from dot_tools.opencode_trends import DEFAULT_MAX_MODELS, aggregate_daily_model_costs, render_trends


cli = typer.Typer(no_args_is_help=True)
staleness_guard_cli = typer.Typer(no_args_is_help=True)
cli.add_typer(staleness_guard_cli, name="staleness-guard")


class OutputFormat(AutoNameEnum):
    table = auto()
    json = auto()
    csv = auto()


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
            OpenCodeError.require_condition(direction in {"asc", "desc"}, f"Invalid sort direction {direction!r}; use 'asc' or 'desc'")
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
