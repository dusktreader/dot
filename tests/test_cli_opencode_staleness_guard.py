from pathlib import Path

from typer.testing import CliRunner

from dot_tools.cli.main import cli


def test_staleness_guard_allows_an_unchanged_file_and_rejects_a_changed_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    file_path = tmp_path / "file.txt"
    file_path.write_text("before")
    runner = CliRunner()

    assert runner.invoke(cli, ["opencode", "staleness-guard", "read", str(file_path)]).exit_code == 0
    assert runner.invoke(cli, ["opencode", "staleness-guard", "check", str(file_path)]).exit_code == 0

    file_path.write_text("after")
    result = runner.invoke(cli, ["opencode", "staleness-guard", "check", str(file_path)])

    assert result.exit_code == 1
    assert "Re-read the file before editing" in result.output


def test_staleness_guard_ignores_files_that_were_not_read(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    result = CliRunner().invoke(cli, ["opencode", "staleness-guard", "check", str(file_path)])

    assert result.exit_code == 0


def test_staleness_guard_plugin_is_dependency_free_bridge() -> None:
    plugin = Path(__file__).parents[1] / ".config/opencode/plugins/staleness-guard.js"
    source = plugin.read_text()

    assert "@opencode-ai/plugin" not in source
    assert '"opencode", "staleness-guard"' in source
    assert 'run("read"' in source
    assert 'run("check"' in source
