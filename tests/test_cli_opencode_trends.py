from unittest.mock import patch

from typer.testing import CliRunner

from dot_tools.cli.main import cli
from dot_tools.opencode_costs import SessionRecord


def test_trends_help_and_output() -> None:
    runner = CliRunner()
    session = SessionRecord(
        "one", None, "/project", "agent", "gpt-5.6-luna", 1760000000000, 1.0,
        {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "one", "ok",
    )
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = [session]
        result = runner.invoke(cli, ["opencode", "trends", "--since", "2025-10-09"])

    assert result.exit_code == 0
    assert "OpenCode recorded cost trends" in result.output
    assert "gpt-5.6-luna" in result.output


def test_trends_provider_option_filters_sessions_and_help_discloses_option() -> None:
    runner = CliRunner()
    sessions = [
        SessionRecord("work", None, "/personal/repo", "agent", "github-copilot/gpt-5.6-luna", 1760000000000, 1.0,
                      {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "work", "ok"),
        SessionRecord("personal", None, "/personal/repo", "agent", "openai/gpt-5.6-luna", 1760000000000, 2.0,
                      {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "personal", "ok"),
    ]
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = sessions
        result = runner.invoke(cli, ["opencode", "trends", "--provider", "github-copilot"])
    assert result.exit_code == 0
    assert "provider: github-copilot" in result.output
    assert "($1.00)" in result.output
    assert "($2.00)" not in result.output
    help_output = runner.invoke(cli, ["opencode", "trends", "--help"]).output
    assert "--provider" in help_output
    assert "--scope" not in help_output


def test_trends_empty_data_is_successful() -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = []
        result = runner.invoke(cli, ["opencode", "trends"])

    assert result.exit_code == 0
    assert "No recorded OpenCode usage" in result.output


def test_trends_accepts_max_models() -> None:
    runner = CliRunner()
    session = SessionRecord(
        "one", None, "/project", "agent", "gpt-5.6-luna", 1760000000000, 1.0,
        {"input": 1, "output": 1, "reasoning": 0, "cache_read": 0, "cache_write": 0}, None, "one", "ok",
    )
    with patch("dot_tools.cli.opencode.OpenCodeSessionStore") as store:
        store.return_value.__enter__.return_value.sessions.return_value = [session]
        result = runner.invoke(cli, ["opencode", "trends", "--max-models", "0"])

    assert result.exit_code == 0
    assert "other" in result.output
