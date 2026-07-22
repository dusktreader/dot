import hashlib
import json
import re
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typing import Any

from dot_tools.opencode_costs import (
    OpenCodeError,
    OpenCodeSessionStore,
    REPORT_COLUMNS,
    ReportColumns,
    SessionRecord,
    Report,
    normalize_model,
)
from dot_tools.cli.opencode import _parse_sort


def make_database(path: Path, *, optional: bool = True) -> None:
    columns = "agent TEXT, model TEXT, cost REAL, tokens_input INTEGER, tokens_output INTEGER, " \
        "tokens_reasoning INTEGER, tokens_cache_read INTEGER, tokens_cache_write INTEGER, metadata TEXT," if optional else ""
    with sqlite3.connect(path) as connection:
        connection.execute(f"CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT, directory TEXT NOT NULL, time_created INTEGER NOT NULL, {columns} title TEXT)")
        connection.executemany(
            "INSERT INTO session VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("root", None, "/project", 1760000000000, "executor", '{"providerID":"github-copilot","id":"gpt-5.6-luna"}', 1.25, 100, 50, 10, 20, 5, '{"ok": true}', "Root"),
                ("child", "root", "/project", 1760001000000, "reviewer", '{"providerID":"github-copilot","id":"claude-sonnet-5"}', 0.0, 0, 0, 0, 0, 0, None, "Child"),
            ],
        )


def test_store_loads_sessions_and_resolves_root(tmp_path: Path) -> None:
    path = tmp_path / "opencode.db"
    make_database(path)
    with OpenCodeSessionStore(path) as store:
        sessions = store.sessions()
    assert sessions[0].root_id == "root"
    assert sessions[1].root_id == "root"
    assert sessions[1].parent_id == "root"
    assert sessions[1].metadata is None


def test_store_normalizes_json_model_and_keeps_provider_for_filtering(tmp_path: Path) -> None:
    path = tmp_path / "opencode.db"
    make_database(path)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE session SET model = ? WHERE id = 'root'", ('{"providerID":"openai","id":"gpt-5.6-luna"}',))
    with OpenCodeSessionStore(path) as store:
        loaded = store.sessions()[0]
    assert loaded.model == "openai/gpt-5.6-luna"
    assert normalize_model('{"providerID":"openai","id":"gpt-5.6-luna"}') == "openai/gpt-5.6-luna"


def test_store_reports_missing_malformed_and_unreadable_databases(tmp_path: Path) -> None:
    with pytest.raises(OpenCodeError, match="does not exist"):
        OpenCodeSessionStore(tmp_path / "missing.db")
    malformed = tmp_path / "malformed.db"
    malformed.write_text("not sqlite")
    with pytest.raises(OpenCodeError, match="Malformed|Cannot read"):
        OpenCodeSessionStore(malformed)
    missing = tmp_path / "missing-table.db"
    sqlite3.connect(missing).close()
    with pytest.raises(OpenCodeError, match="no tables found"):
        OpenCodeSessionStore(missing)


def test_store_is_read_only_and_does_not_change_bytes(tmp_path: Path) -> None:
    path = tmp_path / "opencode.db"
    make_database(path)
    before = hashlib.sha256(path.read_bytes()).digest()
    with OpenCodeSessionStore(path) as store:
        store.sessions()
    assert hashlib.sha256(path.read_bytes()).digest() == before


def test_store_rejects_incomplete_schema(tmp_path: Path) -> None:
    path = tmp_path / "partial.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE session (id TEXT, parent_id TEXT, directory TEXT, time_created INTEGER)")
    with pytest.raises(OpenCodeError, match="missing columns"):
        OpenCodeSessionStore(path)


def session(**overrides: Any) -> ReportColumns:
    values = dict(session_id="one", parent_id=None, directory="/project", agent="executor", model="gpt-5.6-luna",
                  time_created=1760000000000, cost=2.0, tokens={"input": 100, "output": 50, "reasoning": 10,
                  "cache_read": 20, "cache_write": 5}, metadata=None, root_id="one", ancestry_status="ok")
    values.update(overrides)
    return REPORT_COLUMNS.populate(
        session_id=values["session_id"], root_session=values["root_id"], parent_session=values["parent_id"],
        directory=values["directory"], agent=values["agent"], model=values["model"],
        date="2025-10-09",
        recorded_cost=values["cost"], local_estimate=2.0,
        tokens=values["tokens"],
        cache_ratio=20 / 160,
        cache_ratio_status="available",
        ancestry_status=values["ancestry_status"],
        outlier=False,
        outlier_metric=None,
        outlier_threshold=None,
    )


def record(**overrides: Any) -> SessionRecord:
    values = dict(session_id="one", parent_id=None, directory="/project", agent="executor", model="gpt-5.6-luna",
                  time_created=1760000000000, cost=2.0, tokens={"input": 100, "output": 50, "reasoning": 10,
                  "cache_read": 20, "cache_write": 5}, metadata=None, root_id="one", ancestry_status="ok")
    values.update(overrides)
    return SessionRecord(**values)


def test_report_filters_metrics_estimates_and_outliers() -> None:
    report = Report.build([record(), record(session_id="two", directory="/other", model="unsupported")], directory="/project")
    row = report.rows[0]
    assert row.estimate.value == pytest.approx(0.000146)
    assert row.recorded.value == 2.0
    assert row.cache_ratio.value == pytest.approx(20 / 160)
    assert report.recorded_total == 2.0


def test_report_rejects_dates_and_handles_empty_and_incomplete_data() -> None:
    with pytest.raises(OpenCodeError, match="later"):
        Report.build([], since=date(2026, 2, 1), until=date(2026, 1, 1))
    empty = Report.build([], since=date(2026, 1, 1))
    assert empty.rows == []
    incomplete = Report.build([record(tokens={"input": None, "output": 1, "reasoning": 1, "cache_read": 0, "cache_write": 0})])
    assert incomplete.rows[0].estimate.value is None


def test_report_sorts_descending_by_default_and_case_insensitively() -> None:
    report = Report.build(
        [record(session_id="low", cost=1.0), record(session_id="high", cost=3.0)],
        sort=_parse_sort("ACTUAL"),
    )
    assert [row.session.value for row in report.rows] == ["high", "low"]


@pytest.mark.parametrize(("sort", "expected"), [("asc:Actual Cost", ["low", "high"]), ("desc:Actual Cost", ["high", "low"])])
def test_report_sorts_in_explicit_direction(sort: str, expected: list[str]) -> None:
    report = Report.build(
        [record(session_id="low", cost=1.0), record(session_id="high", cost=3.0)],
        sort=_parse_sort(sort),
    )
    assert [row.session.value for row in report.rows] == expected


def test_report_resolves_multiple_sort_keys_left_to_right() -> None:
    rows = [record(session_id="b-high", agent="b", cost=3.0), record(session_id="a-low", agent="a", cost=1.0),
            record(session_id="a-high", agent="a", cost=3.0)]
    report = Report.build(rows, sort=_parse_sort("asc:Agent,desc:Actual Cost"))
    assert [row.session.value for row in report.rows] == ["a-high", "a-low", "b-high"]


def test_table_renders_session_groups_depth_first_with_unicode_prefixes() -> None:
    report = Report.build([
        record(session_id="root", root_id="root", cost=1.0),
        record(session_id="child", parent_id="root", root_id="root", cost=2.0),
        record(session_id="grandchild", parent_id="child", root_id="root", cost=3.0),
        record(session_id="sibling", parent_id="root", root_id="root", cost=4.0),
    ])

    table = report.render("table")

    assert "Session" in table
    assert "Root" not in table
    assert "Directory" in table
    assert "Actual Cost" in table
    assert "Total Cost" in table
    root_line = next(line for line in table.splitlines() if "root" in line and "child" not in line)
    assert "$10.00" in root_line
    assert table.index("root") < table.index("├─ child") < table.index("│  └─ grandchild") < table.index("└─ sibling")


def test_table_total_cost_is_blank_for_children_and_remains_table_only() -> None:
    report = Report.build([
        record(session_id="root", root_id="root", cost=1.0),
        record(session_id="child", parent_id="root", root_id="root", cost=2.0),
    ])

    table = report.render("table")
    json_output = report.render("json")
    csv_output = report.render("csv")

    root_line = next(line for line in table.splitlines() if "root" in line and "child" not in line)
    child_line = next(line for line in table.splitlines() if "└─ child" in line)
    assert "$3.00" in root_line
    assert child_line.count("$2.00") == 1
    assert "Total Cost" not in json_output
    assert "total_cost" not in csv_output


def test_table_sorts_root_groups_by_total_cost() -> None:
    report = Report.build([
        record(session_id="root-low", root_id="root-low", cost=1.0),
        record(session_id="low-child", parent_id="root-low", root_id="root-low", cost=2.0),
        record(session_id="root-high", root_id="root-high", cost=2.0),
        record(session_id="high-child", parent_id="root-high", root_id="root-high", cost=4.0),
    ], sort=_parse_sort("total"))

    table = report.render("table")

    assert table.index("root-high") < table.index("└─ high-child") < table.index("root-low")


def test_table_applies_requested_styles_only_when_color_is_enabled() -> None:
    report = Report.build([record(directory="/project", model="provider/gpt-5.6-luna", cost=2.0)])

    colored = report.render("table", color_system="standard")
    plain = report.render("table")

    assert re.search(r"\x1b\[\d+m\$2\.00\x1b\[0m", colored)
    assert re.search(r"\x1b\[\d+m\$0\.00\x1b\[0m", colored)
    assert re.search(r"\x1b\[\d+m/project\x1b\[0m", colored)
    assert re.search(r"\x1b\[[\d;]+mprovider/gpt-5\.6-luna\x1b\[0m", colored)
    assert "\x1b[" not in plain


def test_table_sorts_root_groups_without_changing_flat_serialized_rows() -> None:
    report = Report.build([
        record(session_id="root-low", root_id="root-low", cost=1.0),
        record(session_id="low-child", parent_id="root-low", root_id="root-low", cost=100.0),
        record(session_id="root-high", root_id="root-high", cost=3.0),
        record(session_id="high-child", parent_id="root-high", root_id="root-high", cost=0.0),
        record(session_id="missing-parent", parent_id="absent", root_id=None, ancestry_status="broken"),
    ], sort=_parse_sort("desc:Actual Cost"))

    table = report.render("table")
    json_rows = json.loads(report.render("json"))["rows"]
    csv_rows = report.render("csv").splitlines()

    assert table.index("root-high") < table.index("└─ high-child") < table.index("root-low")
    assert table.index("root-low") < table.index("└─ low-child")
    assert "missing-parent" in table
    assert [row["session_id"] for row in json_rows] == [
        "low-child", "root-high", "missing-parent", "root-low", "high-child",
    ]
    assert "├─ " not in report.render("json")
    assert "└─ " not in report.render("csv")
    assert [row.split(",")[0] for row in csv_rows[1:]] == [
        "low-child", "root-high", "missing-parent", "root-low", "high-child",
    ]


@pytest.mark.parametrize("sort", ["asc:Nope", "sideways:Actual Cost"])
def test_report_rejects_invalid_sort_parts(sort: str) -> None:
    with pytest.raises(OpenCodeError, match="Invalid sort"):
        _parse_sort(sort)


def test_renderers_produce_table_json_and_csv() -> None:
    report = Report.build([record()])
    table = report.render("table")
    assert "Actual Cost" in table
    assert "Session" in table
    assert "one" in table
    assert "│" in table
    assert "\x1b[" not in table
    assert json.loads(report.render("json"))["rows"][0]["session_id"] == "one"
    assert "session_id" in report.render("csv")


def test_table_formats_cost_metrics_without_changing_serialized_precision() -> None:
    report = Report.build([record(cost=2.3456)])

    table = report.render("table")
    assert "$2.35" in table
    assert "$0.00" in table
    assert "0.12" in table
    assert "Cache Ratio" in table

    data = json.loads(report.render("json"))["rows"][0]
    assert data["recorded_cost"] == 2.3456
    assert data["local_estimate"] == pytest.approx(0.000146)
    assert data["cache_ratio"] == pytest.approx(20 / 160)

    csv_row = report.render("csv").splitlines()[1].split(",")
    assert csv_row[6] == "2.3456"   # recorded_cost is index 6 in REPORT_COLUMNS
    assert csv_row[7] == "0.000146"  # local_estimate
    assert csv_row[8] == "0.125"    # cache_ratio (estimate_status removed, shifted by 1)


def test_table_right_aligns_metric_values_with_cell_padding() -> None:
    table = Report.build([record(cost=2.3456)]).render("table")

    recorded_line = next(line for line in table.splitlines() if "$2.35" in line)
    estimate_line = next(line for line in table.splitlines() if "$0.00" in line)
    cache_line = next(line for line in table.splitlines() if "0.12" in line and "Cache Ratio" not in line)

    assert " $2.35" in recorded_line
    assert " $0.00" in estimate_line
    assert " 0.12" in cache_line


def test_table_uses_compact_status_and_discloses_recorded_outlier_metric() -> None:
    home = Path.home()
    report = Report.build([
        record(directory=str(home / "src" / "project")),
        record(session_id="two", cost=100.0, directory=str(home / "src" / "project")),
    ])
    table = report.render("table")
    assert "Estimate Status" not in table
    assert "Actual Cost" in table
    assert "Estimated Cost" in table
    assert "Outlier metric" in table
    assert "Outlier eligible count" in table
    assert "Outlier flagged count" in table
    assert "~/src/project" in table
    assert "src" in table


def test_table_does_not_wrap_or_truncate_long_fields() -> None:
    long_session_id = "session-with-a-deliberately-long-identifier"
    long_directory = "/project/with/a/directory/path/that/must/remain/visible"
    long_model = "provider/model-with-a-deliberately-long-name"
    table = Report.build([record(
        session_id=long_session_id,
        directory=long_directory,
        model=long_model,
    )]).render("table")

    assert long_session_id in table
    assert long_directory in table
    assert long_model in table
    assert "…" not in table
    assert "-\n" not in table
