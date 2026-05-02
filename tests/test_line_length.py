from pathlib import Path

import pytest

from dot_tools.line_length import find_pyproject_toml, get_config_line_length, DEFAULT_LINE_LENGTH


class TestFindPyprojectToml:

    def test_find_pyproject_toml__finds_file_in_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'fake'\n")

        monkeypatch.chdir(tmp_path)
        assert find_pyproject_toml() == pyproject

    def test_find_pyproject_toml__finds_file_in_parent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'fake'\n")
        subdir = tmp_path / "a/b/c"
        subdir.mkdir(parents=True)

        monkeypatch.chdir(subdir)
        assert find_pyproject_toml() == pyproject

    def test_find_pyproject_toml__returns_none_when_not_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        assert find_pyproject_toml() is None


class TestGetConfigLineLength:

    def test_get_config_line_length__returns_ruff_line_length(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.ruff]\nline-length = 100\n")

        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == 100

    def test_get_config_line_length__returns_black_line_length(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.black]\nline-length = 88\n")

        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == 88

    def test_get_config_line_length__prefers_ruff_over_black(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.ruff]\nline-length = 100\n\n[tool.black]\nline-length = 88\n")

        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == 100

    def test_get_config_line_length__returns_default_when_no_pyproject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == DEFAULT_LINE_LENGTH

    def test_get_config_line_length__returns_default_when_no_tool_section(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'fake'\n")

        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == DEFAULT_LINE_LENGTH

    def test_get_config_line_length__returns_default_when_no_formatter_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest]\naddopts = '--tb=short'\n")

        monkeypatch.chdir(tmp_path)
        assert get_config_line_length() == DEFAULT_LINE_LENGTH
