"""OpenCode CLI commands."""

from datetime import date
from pathlib import Path
from typing import Annotated

import dateparser
from auto_name_enum import AutoNameEnum, auto
import typer
from typerdrive import handle_errors, log_error

from dot_tools.exceptions import OpenCodeError
from dot_tools.opencode_costs import REPORT_COLUMNS, OpenCodeSessionStore, Report, fields


cli = typer.Typer(no_args_is_help=True)


class OutputFormat(AutoNameEnum):
    table = auto()
    json = auto()
    csv = auto()


def _parse_sort(value: str) -> list[tuple[str, bool]]:
    """Parse comma-separated sort keys into (field, descending) pairs, last key first."""
    report_columns = [getattr(REPORT_COLUMNS, f.name) for f in fields(REPORT_COLUMNS)]
    sort_lookup = {col.label.lower(): col.field for col in report_columns if col.label}
    parsed: list[tuple[str, bool]] = []
    for item in value.split(","):
        direction, separator, column = item.strip().partition(":")
        if separator:
            direction = direction.casefold()
            OpenCodeError.require_condition(direction in {"asc", "desc"}, f"Invalid sort direction {direction!r}; use 'asc' or 'desc'")
        else:
            direction, column = "desc", item.strip()
        field = OpenCodeError.enforce_defined(
            sort_lookup.get(column.strip().casefold()),
            f"Invalid sort column {column.strip()!r}; choose one of: {', '.join(col.label for col in report_columns if col.label)}",
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
) -> None:
    """Report recorded and locally estimated OpenCode session costs."""
    parsed_sort = _parse_sort(sort) if sort is not None else None
    OpenCodeError.require_condition(
        file is None or file.parent.is_dir(),
        f"Output parent directory does not exist: {file.parent}" if file is not None else "",
    )
    with OpenCodeSessionStore() as store:
        report = Report.build(store.sessions(), since, until, directory, agent, model, parsed_sort)
    rendered = report.render(format.value, color_system="auto" if file is None else None)
    if file is None:
        typer.echo(rendered)
    else:
        file.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""))
