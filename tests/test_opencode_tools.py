from pathlib import Path


TOOLS_DIRECTORY = Path(__file__).parents[1] / ".config/opencode/tools"
TOOL_FILES = ("gmail.ts", "clipboard.ts", "pdf.ts")


def test_opencode_custom_tools_are_dependency_free_json_schema_definitions() -> None:
    for filename in TOOL_FILES:
        source = (TOOLS_DIRECTORY / filename).read_text()

        assert "@opencode-ai/plugin" not in source
        assert "tool.schema" not in source
        assert "description:" in source
        assert "args:" in source
        assert "async execute(" in source


def test_opencode_custom_tools_preserve_their_exported_names() -> None:
    gmail_source = (TOOLS_DIRECTORY / "gmail.ts").read_text()
    clipboard_source = (TOOLS_DIRECTORY / "clipboard.ts").read_text()
    pdf_source = (TOOLS_DIRECTORY / "pdf.ts").read_text()

    assert "export const analyze =" in gmail_source
    assert "export const report =" in gmail_source
    assert "export const execute =" in gmail_source
    assert "export default =" not in clipboard_source
    assert "export default {" in clipboard_source
    assert "export const extract =" in pdf_source
