from pathlib import Path

from dot_tools.markdown_format import find_markdown_files


def test_find_markdown_files_collects_markdown_from_directories(tmp_path: Path):
    root = tmp_path / "docs"
    nested = root / "nested"
    nested.mkdir(parents=True)
    first = root / "guide.md"
    second = nested / "reference.md"
    ignored = nested / "notes.txt"
    first.touch()
    second.touch()
    ignored.touch()

    result = find_markdown_files([root])

    assert result.files == [first, second]
    assert result.errors == []


def test_find_markdown_files_reports_missing_and_non_markdown_paths(tmp_path: Path):
    text_file = tmp_path / "notes.txt"
    text_file.touch()
    missing = tmp_path / "missing.md"

    result = find_markdown_files([text_file, missing])

    assert result.files == []
    assert result.errors == [f"Not a Markdown file: {text_file}", f"Not found: {missing}"]
