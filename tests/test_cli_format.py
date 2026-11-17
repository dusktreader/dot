from pathlib import Path
from types import SimpleNamespace

from typer.testing import CliRunner

from dot_tools.cli.main import cli


def test_format_markdown_runs_rumdl_with_project_configuration(tmp_path: Path, monkeypatch):
    path = tmp_path / "example.md"
    path.write_text("# Example\nText\n## Section\n", encoding="utf-8")
    commands = []

    def run_rumdl(command: list[str], check: bool):
        commands.append(command)
        path.write_text("# Example\n\nText\n\n\n## Section\n\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("dot_tools.markdown_format.subprocess.run", run_rumdl)

    result = CliRunner().invoke(cli, ["format", "markdown", str(path)])

    assert result.exit_code == 0
    assert commands == [["rumdl", "fmt", str(path)]]
    assert f"formatted: {path}" in result.output
    assert path.read_text(encoding="utf-8") == "# Example\n\nText\n\n\n## Section\n\n"


def test_format_markdown_check_runs_rumdl_without_changing_file(tmp_path: Path, monkeypatch):
    path = tmp_path / "example.md"
    contents = "# Example\n\nText.\n"
    path.write_text(contents, encoding="utf-8")
    commands = []

    def run_rumdl(command: list[str], check: bool):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("dot_tools.markdown_format.subprocess.run", run_rumdl)

    result = CliRunner().invoke(cli, ["format", "markdown", "--check", str(path)])

    assert result.exit_code == 0
    assert commands == [["rumdl", "fmt", "--check", str(path)]]
    assert "Markdown format check passed for 1 file(s)." in result.output
    assert path.read_text(encoding="utf-8") == contents


def test_format_markdown_check_reports_rumdl_failure(tmp_path: Path, monkeypatch):
    path = tmp_path / "example.md"
    contents = "# Example\nText.\n## Section\n"
    path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(
        "dot_tools.markdown_format.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1),
    )

    result = CliRunner().invoke(cli, ["format", "markdown", "--check", str(path)])

    assert result.exit_code == 1
    assert "rumdl format check failed with status 1." in result.output
    assert path.read_text(encoding="utf-8") == contents


def test_format_markdown_reports_missing_rumdl(tmp_path: Path, monkeypatch):
    path = tmp_path / "example.md"
    path.write_text("# Example\n", encoding="utf-8")

    def run_rumdl(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("dot_tools.markdown_format.subprocess.run", run_rumdl)

    result = CliRunner().invoke(cli, ["format", "markdown", str(path)])

    assert result.exit_code == 127
    assert "rumdl is required" in result.output
