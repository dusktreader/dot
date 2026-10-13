from pathlib import Path

from typer.testing import CliRunner

from dot_tools.cli.main import cli


def test_format_markdown_formats_file(tmp_path: Path):
    path = tmp_path / "example.md"
    path.write_text("# Example\n\nA paragraph with trailing spaces.   \n", encoding="utf-8")

    result = CliRunner().invoke(cli, ["format", "markdown", str(path)])

    assert result.exit_code == 0
    assert f"formatted: {path}" in result.output
    assert path.read_text(encoding="utf-8") == "# Example\n\nA paragraph with trailing spaces.\n"


def test_format_markdown_check_does_not_change_file(tmp_path: Path):
    path = tmp_path / "example.md"
    contents = "# Example\n\nA paragraph.\n"
    path.write_text(contents, encoding="utf-8")

    result = CliRunner().invoke(cli, ["format", "markdown", "--check", str(path)])

    assert result.exit_code == 0
    assert "Markdown format check passed for 1 file(s)." in result.output
    assert path.read_text(encoding="utf-8") == contents


def test_format_markdown_check_reports_issues(tmp_path: Path):
    path = tmp_path / "example.md"
    contents = "A paragraph without a title.\n"
    path.write_text(contents, encoding="utf-8")

    result = CliRunner().invoke(cli, ["format", "markdown", "--check", str(path)])

    assert result.exit_code == 1
    assert "Markdown documents must begin with one H1 title." in result.output
    assert path.read_text(encoding="utf-8") == contents
