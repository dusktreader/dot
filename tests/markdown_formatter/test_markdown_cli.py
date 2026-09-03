from typer.testing import CliRunner

from dot_tools.cli.main import cli


def test_markdown_group_and_commands_have_help() -> None:
    runner = CliRunner()
    for args in (("markdown", "--help"), ("markdown", "format", "--help"), ("markdown", "check", "--help")):
        result = runner.invoke(cli, list(args))
        assert result.exit_code == 0, result.stdout


def test_format_prints_records_and_summary(tmp_path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# Title")

    result = CliRunner().invoke(cli, ["markdown", "format", str(path)])

    assert result.exit_code == 0
    assert "FORMATTED" in result.stdout
    assert "summary format SUCCESS 1" in result.stdout


def test_recursive_discovery_failure_is_reported_by_cli(monkeypatch, tmp_path) -> None:
    def fail_discovery(self, pattern):
        raise OSError("discovery fail")

    monkeypatch.setattr(__import__("pathlib").Path, "rglob", fail_discovery)
    result = CliRunner(mix_stderr=False).invoke(cli, ["markdown", "check", str(tmp_path)])

    assert result.exit_code == 3
    assert result.stdout == f"READ_ERROR {tmp_path}\nsummary check READ_ERROR 1\n"
    assert result.stderr == f"{tmp_path}: READ_ERROR: discovery fail\n"
