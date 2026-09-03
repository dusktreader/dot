import importlib.util
from pathlib import Path


def test_wrapper_resolves_operands_from_entry_cwd_and_delegates(monkeypatch, tmp_path: Path) -> None:
    script = Path(__file__).parents[2] / ".agents/tools/markdown-format.py"
    spec = importlib.util.spec_from_file_location("markdown_wrapper", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda args, **kwargs: calls.append((args, kwargs)) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(module.sys, "argv", [str(script), "check", "doc.md"])
    monkeypatch.chdir(tmp_path)

    assert module.main() == 0
    assert calls[0][0][4:7] == ["dt", "markdown", "check"]
    assert calls[0][0][7] == str(tmp_path / "doc.md")
    assert calls[0][1]["cwd"] == tmp_path


def test_wrapper_returns_two_when_no_project_can_be_discovered(monkeypatch, tmp_path: Path) -> None:
    source_script = Path(__file__).parents[2] / ".agents/tools/markdown-format.py"
    script = tmp_path / ".agents/tools/markdown-format.py"
    script.parent.mkdir(parents=True)
    script.write_text(source_script.read_text(encoding="utf-8"), encoding="utf-8")
    spec = importlib.util.spec_from_file_location("markdown_wrapper_without_project", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.sys, "argv", [str(script), "check", "doc.md"])
    monkeypatch.chdir(tmp_path)

    assert module.main() == 2
