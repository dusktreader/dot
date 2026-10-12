from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from dot_tools.cli.main import cli


def test_logs_tails_profile_log_with_follow_and_line_count(tmp_path: Path) -> None:
    log_file = tmp_path / "opencode.log"
    log_file.write_text("entry\n")
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.personal_lifecycle") as factory, patch(
        "dot_tools.cli.opencode.subprocess.run"
    ) as run:
        factory.return_value.open_code_log_file = log_file
        run.return_value.returncode = 0
        result = runner.invoke(cli, ["opencode", "logs", "--follow", "-n30"])

    assert result.exit_code == 0
    run.assert_called_once_with(["tail", "-n30", "-f", str(log_file)], check=False)


def test_logs_reports_missing_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "missing.log"
    with patch("dot_tools.cli.opencode.personal_lifecycle") as factory:
        factory.return_value.open_code_log_file = log_file
        result = CliRunner().invoke(cli, ["opencode", "logs"])

    assert result.exit_code == 1
    assert f"OpenCode log file not found: {log_file}" in result.output


def test_logs_rejects_nonpositive_line_count() -> None:
    result = CliRunner().invoke(cli, ["opencode", "logs", "-n0"])

    assert result.exit_code == 2
    assert "Invalid value" in result.output
