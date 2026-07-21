import csv
import io
import json
import sqlite3
from contextlib import redirect_stdout
from dataclasses import dataclass, fields, replace
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Generic, Iterable, Literal, TypeVar

from rich.align import Align
from rich.console import Console
from rich.table import Table
from rich.text import Text


from dot_tools.exceptions import OpenCodeError


T = TypeVar("T")


@dataclass(frozen=True)
class ReportColumn(Generic[T]):
    label: str
    field: str
    db_column: str = ""
    required: bool = True
    value: T | None = None


@dataclass(frozen=True)
class ReportColumns:
    session: ReportColumn[str] = ReportColumn("Session", "session_id", "id")
    root: ReportColumn[str | None] = ReportColumn("Root", "root_session")
    parent: ReportColumn[str | None] = ReportColumn("", "parent_session")
    directory: ReportColumn[str] = ReportColumn("Directory", "directory", "directory")
    agent: ReportColumn[str | None] = ReportColumn("Agent", "agent", "agent")
    model: ReportColumn[str | None] = ReportColumn("Model", "model", "model")
    date: ReportColumn[str] = ReportColumn("Date", "date")
    recorded: ReportColumn[float | None] = ReportColumn("Recorded", "recorded_cost", "cost")
    estimate: ReportColumn[float | None] = ReportColumn("Estimate", "local_estimate")
    estimate_status: ReportColumn[str] = ReportColumn("Estimate Status", "estimate_status")
    tokens: ReportColumn[dict[str, int | None]] = ReportColumn("", "tokens")
    cache_ratio: ReportColumn[float | None] = ReportColumn("Cache Ratio", "cache_ratio")
    cache_ratio_status: ReportColumn[str] = ReportColumn("", "cache_ratio_status")
    ancestry_status: ReportColumn[str] = ReportColumn("", "ancestry_status")
    outlier: ReportColumn[bool] = ReportColumn("Outlier", "outlier")
    outlier_metric: ReportColumn[str | None] = ReportColumn("", "outlier_metric")
    outlier_threshold: ReportColumn[float | None] = ReportColumn("", "outlier_threshold")
    parent_id: ReportColumn[str | None] = ReportColumn("", "", "parent_id")
    time_created: ReportColumn[int] = ReportColumn("", "", "time_created")
    tokens_input: ReportColumn[int | None] = ReportColumn("", "", "tokens_input")
    tokens_output: ReportColumn[int | None] = ReportColumn("", "", "tokens_output")
    tokens_reasoning: ReportColumn[int | None] = ReportColumn("", "", "tokens_reasoning")
    tokens_cache_read: ReportColumn[int | None] = ReportColumn("", "", "tokens_cache_read")
    tokens_cache_write: ReportColumn[int | None] = ReportColumn("", "", "tokens_cache_write")
    metadata: ReportColumn[dict[str, object] | None] = ReportColumn("", "", "metadata")

    @classmethod
    def populate(cls, **values: object) -> "ReportColumns":
        """Create populated columns from values keyed by report field name."""
        definitions = cls()
        populated = {
            report_field.name: replace(column, value=values.get(column.field))
            for report_field in fields(definitions)
            if (column := getattr(definitions, report_field.name)).field
        }
        return replace(definitions, **populated)

    def all_columns(self) -> list[ReportColumn[object]]:
        """Return all columns in definition order."""
        return [getattr(self, f.name) for f in fields(self)]

    def get_value(self, field: str) -> object:
        """Return a populated value by its report field name."""
        return next(column.value for column in self.all_columns() if column.field == field)

    def to_dict(self) -> dict[str, object]:
        """Serialize populated columns by their public field names."""
        return {column.field: column.value for column in self.all_columns() if column.field}


REPORT_COLUMNS = ReportColumns()


def default_database_path() -> Path:
    return Path.home() / ".local" / "share" / "opencode" / "opencode.db"


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    parent_id: str | None
    directory: str
    agent: str | None
    model: str | None
    time_created: int
    cost: float | None
    tokens: dict[str, int | None]
    metadata: dict[str, object] | None
    root_id: str | None
    ancestry_status: str


@dataclass(frozen=True)
class Report:
    rows: list[ReportColumns]
    filters: dict[str, str | None]
    sort: list[tuple[str, bool]] | None = None
    recorded_total: float = 0.0
    estimated_total: float | None = 0.0
    outlier_metric: str = "recorded_cost"
    outlier_threshold: float | None = None
    outlier_eligible_count: int = 0

    @staticmethod
    def _estimate(session: SessionRecord) -> tuple[float | None, str]:
        """Estimate cost with the pinned local pricing adaptation."""
        if not session.model:
            return None, "unsupported-model:missing-model"
        pricing = {"gpt-5.6-luna": (0.40, 1.60), "gpt-5.6-terra": (2.00, 8.00), "gpt-5.6-sol": (5.00, 20.00)}
        model_key = session.model.rsplit("/", 1)[-1]
        rates = pricing.get(model_key)
        if rates is None:
            return None, f"unsupported-model:{session.model}"
        if any(value is None for value in session.tokens.values()):
            return None, "incomplete-token-data"
        input_tokens = sum(session.tokens[name] or 0 for name in ("input", "cache_read", "cache_write"))
        output_tokens = (session.tokens["output"] or 0) + (session.tokens["reasoning"] or 0)
        return (input_tokens * rates[0] + output_tokens * rates[1]) / 1_000_000, "estimated"

    @classmethod
    def build(
        cls,
        sessions: Iterable[SessionRecord],
        since: date | None = None,
        until: date | None = None,
        directory: str | None = None,
        agent: str | None = None,
        model: str | None = None,
        sort: list[tuple[str, bool]] | None = None,
    ) -> "Report":
        """Filter sessions, calculate metrics, and identify population outliers."""
        OpenCodeError.require_condition(
            not (since and until and since > until),
            "--since cannot be later than --until",
        )
        selected: list[SessionRecord] = []
        for session in sessions:
            session_date = datetime.fromtimestamp(session.time_created / 1000, tz=timezone.utc).date()
            if since and session_date < since or until and session_date > until:
                continue
            if directory is not None and session.directory != directory:
                continue
            if agent is not None and session.agent != agent:
                continue
            if model is not None and session.model != model:
                continue
            selected.append(session)
        estimates = [cls._estimate(session) for session in selected]
        numeric = [value for value, _ in estimates if value is not None]
        recorded = [session.cost for session in selected if session.cost is not None]
        threshold = mean(recorded) + 2 * pstdev(recorded) if len(recorded) > 1 else None
        rows: list[ReportColumns] = []
        for session, (estimate, status) in zip(selected, estimates):
            totals = [session.tokens[name] for name in ("input", "output", "reasoning", "cache_read", "cache_write")]
            denominator = sum(
                value
                for value in (session.tokens["input"], session.tokens["output"], session.tokens["reasoning"])
                if value is not None
            )
            cache_ratio = (
                ((session.tokens["cache_read"] or 0) / denominator)
                if denominator and all(value is not None for value in totals)
                else None
            )
            cache_status = "available" if cache_ratio is not None else "unavailable:missing-or-zero-denominator"
            rows.append(
                ReportColumns.populate(
                    session_id=session.session_id,
                    root_session=session.root_id,
                    parent_session=session.parent_id,
                    directory=session.directory,
                    agent=session.agent,
                    model=session.model,
                    date=datetime.fromtimestamp(session.time_created / 1000, tz=timezone.utc).date().isoformat(),
                    recorded_cost=session.cost,
                    local_estimate=estimate,
                    estimate_status=status,
                    tokens=session.tokens,
                    cache_ratio=cache_ratio,
                    cache_ratio_status=cache_status,
                    ancestry_status=session.ancestry_status,
                    outlier=threshold is not None and session.cost is not None and session.cost > threshold,
                    outlier_metric="recorded_cost" if threshold is not None else None,
                    outlier_threshold=threshold,
                )
            )
        recorded_total = sum(row.get_value("recorded_cost") or 0 for row in rows)
        estimated_total = sum(numeric) if len(numeric) == len(rows) else (sum(numeric) if numeric else None)
        return cls(
            sort_report_rows(rows, sort),
            {
                "since": since.isoformat() if since is not None else None,
                "until": until.isoformat() if until is not None else None,
                "directory": directory,
                "agent": agent,
                "model": model,
            },
            sort=sort,
            recorded_total=recorded_total,
            estimated_total=estimated_total,
            outlier_threshold=threshold,
            outlier_eligible_count=len(recorded),
        )

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "rows": [row.to_dict() for row in self.rows],
            "filters": self.filters,
            "recorded_total": self.recorded_total,
            "estimated_total": self.estimated_total,
            "outlier_metric": self.outlier_metric,
            "outlier_threshold": self.outlier_threshold,
            "outlier_eligible_count": self.outlier_eligible_count,
        }
        result["metadata"] = {
            "row_count": len(self.rows),
            "outlier_metric": self.outlier_metric,
            "outlier_threshold": self.outlier_threshold,
            "outlier_eligible_count": self.outlier_eligible_count,
            "outlier_count": sum(row.get_value("outlier") is True for row in self.rows),
        }
        return result

    def render(self, output_format: str, color_system: Literal["auto", "standard", "256", "truecolor", "windows"] | None = None) -> str:
        """Render this report as a table, JSON, or CSV."""
        if output_format == "json":
            return json.dumps(self.to_dict(), indent=2, sort_keys=True)
        if output_format == "csv":
            output = io.StringIO()
            table_fields = [
                column.field
                for report_field in fields(REPORT_COLUMNS)
                if (column := getattr(REPORT_COLUMNS, report_field.name)).label
            ]
            extra_fields = [
                "parent_session",
                "cache_ratio_status",
                "ancestry_status",
                "outlier_metric",
                "outlier_threshold",
            ]
            csv_fields = table_fields + extra_fields
            writer = csv.DictWriter(output, fieldnames=csv_fields)
            writer.writeheader()
            for row in self.rows:
                data = row.to_dict()
                data["tokens"] = json.dumps(data["tokens"], sort_keys=True)
                writer.writerow({field: data[field] for field in csv_fields})
            return output.getvalue()
        table = Table(title="OpenCode session costs", show_lines=False, expand=False)
        columns = [
            getattr(REPORT_COLUMNS, report_field.name)
            for report_field in fields(REPORT_COLUMNS)
            if getattr(REPORT_COLUMNS, report_field.name).label
            and getattr(REPORT_COLUMNS, report_field.name).field != "root_session"
        ]
        columns.append(ReportColumn("Total Cost", "total_cost"))
        rendered_rows: list[list[str]] = []
        for row, session_display, total_cost in table_rows(self.rows, self.sort):
            values = row.to_dict()
            values["session_id"] = session_display
            values["total_cost"] = total_cost
            values["directory"] = display_directory(str(values["directory"]))
            for metric_field in ("recorded_cost", "local_estimate", "total_cost"):
                if values[metric_field] is not None:
                    values[metric_field] = f"${values[metric_field]:.2f}"
            if values["cache_ratio"] is not None:
                values["cache_ratio"] = f"{values['cache_ratio']:.2f}"
            status = values["estimate_status"]
            values["estimate_status"] = (
                "estimated"
                if status == "estimated"
                else ("incomplete" if status == "incomplete-token-data" else "unsupported")
            )
            rendered_rows.append(
                [str(values[column.field]) if values[column.field] is not None else "" for column in columns]
            )

        for column in columns:
            table.add_column(
                column.label,
                no_wrap=True,
                overflow="ignore",
            )
        right_aligned_fields = {"recorded_cost", "local_estimate", "cache_ratio", "total_cost"}
        cell_styles = {
            "recorded_cost": "green",
            "total_cost": "green",
            "local_estimate": "yellow",
            "directory": "blue",
            "model": "purple",
        }
        for values in rendered_rows:
            table.add_row(
                *[
                    Align.right(Text(value, style=cell_styles.get(field))) if field in right_aligned_fields else Text(
                        value, style=cell_styles.get(field)
                    )
                    for value, column in zip(values, columns)
                    for field in [column.field]
                ]
            )

        column_widths = [len(column.label) for column in columns]
        for values in rendered_rows:
            column_widths = [max(width, len(value)) for width, value in zip(column_widths, values)]
        table_width = sum(column_widths) + (3 * len(column_widths)) + 1

        summary = Table(box=None, show_header=False, show_lines=False, expand=False)
        summary.add_column(no_wrap=True)
        summary.add_column(no_wrap=True, justify="right")

        def summary_value(value: str | float | int | None, style: str) -> str:
            if value is None:
                return "[dim]unavailable[/dim]"
            return f"[{style}]{value}[/]"

        flagged_count = sum(row.get_value("outlier") is True for row in self.rows)
        summary.add_row("[bold]Recorded total[/bold]", summary_value(f"${self.recorded_total:.2f}", "green"))
        summary.add_row("[bold]Local estimate[/bold]", summary_value(
            f"${self.estimated_total:.2f}" if self.estimated_total is not None else None, "green"
        ))
        summary.add_row("[bold]Outlier metric[/bold]", summary_value(self.outlier_metric, "yellow"))
        summary.add_row("[bold]Outlier threshold[/bold]", summary_value(
            f"${self.outlier_threshold:.2f}" if self.outlier_threshold is not None else None, "yellow"
        ))
        summary.add_row("[bold]Outlier eligible count[/bold]", summary_value(self.outlier_eligible_count, "yellow"))
        summary.add_row("[bold]Outlier flagged count[/bold]", summary_value(flagged_count, "yellow"))

        output = io.StringIO()
        # Match the capture width to the unwrapped table so Rich does not impose a terminal-sized crop.
        console = Console(
            file=output,
            record=True,
            force_terminal=color_system == "auto",
            color_system=color_system,
            width=max(80, table_width),
        )
        with redirect_stdout(output):
            console.print(table)
            console.print(summary)
        return output.getvalue().rstrip("\n")


def normalize_model(value: str | None) -> str | None:
    """Normalize an OpenCode model JSON value to `providerID/id` display form."""
    if value is None:
        return None
    with OpenCodeError.handle_errors(f"Cannot parse model metadata: {value!r}"):
        parsed = json.loads(value)
        provider = parsed["providerID"]
        model = parsed["id"]
    return f"{provider}/{model}"


def display_directory(value: str) -> str:
    """Display directories below the home directory with a `~` prefix."""
    try:
        relative = Path(value).relative_to(Path.home())
        return "~" if str(relative) == "." else f"~/{relative}"
    except ValueError:
        return value


class OpenCodeSessionStore:
    """Open an OpenCode SQLite database strictly in read-only mode."""

    REQUIRED_COLUMNS = {
        column.db_column
        for report_field in fields(REPORT_COLUMNS)
        for column in (getattr(REPORT_COLUMNS, report_field.name),)
        if column.db_column and column.required
    }
    conn: sqlite3.Connection | None
    columns: dict[str, set[str]]

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or default_database_path()
        self.conn: sqlite3.Connection | None = None
        OpenCodeError.require_condition(self.db_path.exists(), f"OpenCode database does not exist: {self.db_path}")
        with OpenCodeError.handle_errors(
            f"Cannot read OpenCode database {self.db_path}", do_except=lambda dep: self.close()
        ):
            uri = f"file:{self.db_path.absolute()}?mode=ro"
            self.conn = sqlite3.connect(uri, uri=True, timeout=1.0)
            self.conn.row_factory = sqlite3.Row
            self.columns = self._load_schema()

    def _load_schema(self) -> dict[str, set[str]]:
        """Validate the minimum schema and return available columns."""
        conn = OpenCodeError.enforce_defined(
            self.conn, f"Connection unexpectedly closed before schema validation: {self.db_path}"
        )
        with OpenCodeError.handle_errors(f"Malformed OpenCode database {self.db_path}"):
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            OpenCodeError.require_condition(tables, "no tables found")

            columns = {row[1] for row in conn.execute("PRAGMA table_info(session)")}

            missing = self.REQUIRED_COLUMNS - columns
            OpenCodeError.require_condition(len(missing) == 0, f"missing columns {', '.join(sorted(missing))}")
        return {"session": columns}

    def close(self) -> None:
        """Close the read-only connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> "OpenCodeSessionStore":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _row_to_session(self, row: sqlite3.Row) -> SessionRecord:
        """Convert one SQLite row to a SessionRecord."""
        metadata: dict[str, object] | None = None
        if row["metadata"] is not None:
            with OpenCodeError.handle_errors(f"Cannot parse session metadata for {row['id']}"):
                parsed = json.loads(row["metadata"])
                metadata = parsed if isinstance(parsed, dict) else None
        tokens: dict[str, int | None] = {
            name.removeprefix("tokens_"): row[name]
            for name in ("tokens_input", "tokens_output", "tokens_reasoning", "tokens_cache_read", "tokens_cache_write")
        }
        return SessionRecord(
            session_id=row["id"],
            parent_id=row["parent_id"],
            directory=row["directory"],
            agent=row["agent"],
            model=normalize_model(row["model"]),
            time_created=row["time_created"],
            cost=row["cost"],
            tokens=tokens,
            metadata=metadata,
            root_id=None,
            ancestry_status="unresolved",
        )

    def sessions(self) -> list[SessionRecord]:
        """Load sessions and resolve parent chains in memory."""
        OpenCodeError.require_condition(
            self.conn is not None,
            f"Connection unexpectedly closed before loading sessions: {self.db_path}",
        )
        all_columns = ", ".join(
            column.db_column
            for report_field in fields(REPORT_COLUMNS)
            if (column := getattr(REPORT_COLUMNS, report_field.name)).db_column
        )
        conn = OpenCodeError.enforce_defined(
            self.conn, f"Connection unexpectedly closed before loading sessions: {self.db_path}"
        )
        with OpenCodeError.handle_errors(f"Cannot query OpenCode database {self.db_path}"):
            raw = [
                self._row_to_session(row)
                for row in conn.execute(f"SELECT {all_columns} FROM session ORDER BY time_created, id")
            ]
        by_id = {session.session_id: session for session in raw}
        resolved: list[SessionRecord] = []
        for session in raw:
            current = session
            seen: set[str] = set()
            status = "ok"
            root_id: str | None = session.session_id
            while current.parent_id is not None:
                if current.session_id in seen:
                    status, root_id = "broken-ancestry-cycle", None
                    break
                seen.add(current.session_id)
                parent = by_id.get(current.parent_id)
                if parent is None:
                    status, root_id = "broken-ancestry-missing-parent", None
                    break
                root_id = parent.session_id
                current = parent
            resolved.append(
                SessionRecord(
                    session_id=session.session_id,
                    parent_id=session.parent_id,
                    directory=session.directory,
                    agent=session.agent,
                    model=session.model,
                    time_created=session.time_created,
                    cost=session.cost,
                    tokens=session.tokens,
                    metadata=session.metadata,
                    root_id=root_id,
                    ancestry_status=status,
                )
            )
        return resolved



def sort_report_rows(rows: list[ReportColumns], sort: list[tuple[str, bool]] | None) -> list[ReportColumns]:
    """Sort report rows by requested keys, keeping unavailable values last."""
    sorted_rows = rows[:]
    for sort_field, reverse in (sort or []):
        available = [row for row in sorted_rows if row.get_value(sort_field) is not None]
        unavailable = [row for row in sorted_rows if row.get_value(sort_field) is None]
        available.sort(key=lambda row: row.get_value(sort_field), reverse=reverse)
        sorted_rows = available + unavailable
    return sorted_rows


def table_rows(
    rows: list[ReportColumns], sort: list[tuple[str, bool]] | None,
) -> list[tuple[ReportColumns, str, float | None]]:
    """Return table rows grouped by resolved session ancestry."""
    by_id = {str(row.get_value("session_id")): row for row in rows}
    children: dict[str, list[ReportColumns]] = {session_id: [] for session_id in by_id}
    roots: list[ReportColumns] = []
    for row in rows:
        parent_id = row.get_value("parent_session")
        root_id = row.get_value("root_session")
        parent = by_id.get(str(parent_id)) if parent_id is not None else None
        if parent is not None and root_id is not None and root_id == parent.get_value("root_session"):
            children[str(parent_id)].append(row)
        else:
            roots.append(row)

    rendered: list[tuple[ReportColumns, str, float | None]] = []
    visited: set[str] = set()

    def add_subtree(row: ReportColumns, prefix: str, is_last: bool, is_root: bool = False) -> float:
        session_id = str(row.get_value("session_id"))
        if session_id in visited:
            return 0.0
        visited.add(session_id)
        display = session_id if is_root else f"{'└─ ' if is_last else '├─ '}{session_id}"
        rendered_index = len(rendered)
        rendered.append((row, prefix + display, None))
        descendants = children[session_id]
        child_prefix = prefix + ("   " if is_last else "│  ") if not is_root else ""
        total_cost = row.get_value("recorded_cost") or 0.0
        for index, child in enumerate(descendants):
            total_cost += add_subtree(child, child_prefix, index == len(descendants) - 1)
        if is_root:
            rendered[rendered_index] = (row, prefix + display, total_cost)
        return total_cost

    for root in sort_report_rows(roots, sort):
        add_subtree(root, "", True, is_root=True)
    for row in rows:
        if str(row.get_value("session_id")) not in visited:
            add_subtree(row, "", True, is_root=True)
    return rendered
