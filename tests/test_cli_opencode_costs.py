import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from dot_tools.cli.main import cli
from dot_tools.cli.opencode import _parse_sort
from dot_tools.exceptions import OpenCodeError
from dot_tools.opencode_costs import SessionRecord


def test_costs_help_and_json_output() -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = [SessionRecord(
            "one", None, "/p", "agent", "gpt-5.6-luna", 1760000000000, 1.0,
            {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "one", "ok")
        ]
        result = runner.invoke(cli, ["opencode", "costs", "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.output)["rows"][0]["session_id"] == "one"


def test_costs_table_output_is_aligned_and_file_output_has_no_terminal_codes(tmp_path: Path) -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = [SessionRecord(
            "one", None, "/project", "agent", "gpt-5.6-luna", 1760000000000, 1.0,
            {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "one", "ok",
        )]
        terminal = runner.invoke(cli, ["opencode", "costs"])
        output_file = tmp_path / "costs.txt"
        written = runner.invoke(cli, ["opencode", "costs", "--file", str(output_file)])

    assert terminal.exit_code == 0
    assert "Session" in terminal.output
    assert "│" in terminal.output
    assert written.exit_code == 0
    assert "\x1b[" not in output_file.read_text()
    assert re.sub(r"\x1b\[[0-9;]*m", "", terminal.output) == output_file.read_text()


def test_costs_rejects_invalid_format_and_missing_parent(tmp_path: Path) -> None:
    runner = CliRunner()
    invalid_format = runner.invoke(cli, ["opencode", "costs", "--format", "xml"])
    assert invalid_format.exit_code == 2
    assert "Invalid value for '--format'" in invalid_format.output
    result = runner.invoke(cli, ["opencode", "costs", "--file", str(tmp_path / "missing" / "out.csv")])
    assert result.exit_code != 0


def test_costs_reports_database_error() -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore", side_effect=OpenCodeError("bad database")):
        result = runner.invoke(cli, ["opencode", "costs"])
    assert result.exit_code != 0


@pytest.mark.parametrize("sort", ["asc:Nope", "sideways:Recorded"])
def test_costs_rejects_invalid_sort_with_actionable_error(sort: str) -> None:
    with pytest.raises(OpenCodeError, match="Invalid sort"):
        _parse_sort(sort)


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--since", "2025-10-10"),
        ("--until", "2025-10-09"),
        ("--directory", "/project"),
        ("--agent", "executor"),
        ("--model", "gpt-5.6-luna"),
    ],
)
def test_costs_applies_each_filter_at_the_cli_boundary(option: str, value: str) -> None:
    runner = CliRunner()
    sessions = [
        SessionRecord(
            "earlier", None, "/project", "executor", "gpt-5.6-luna", 1760000000000, 1.0,
            {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "earlier", "ok",
        ),
        SessionRecord(
            "later", None, "/other", "reviewer", "gpt-5.6-terra", 1760086400000, 2.0,
            {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "later", "ok",
        ),
    ]
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = sessions
        result = runner.invoke(cli, ["opencode", "costs", option, value, "--format", "json"])
    assert result.exit_code == 0
    expected = "later" if option == "--since" else "earlier"
    assert [row["session_id"] for row in json.loads(result.output)["rows"]] == [expected]
