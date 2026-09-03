"""Test normalized Markdown state without involving rendering."""

from dot_tools.markdown_formatter.normalize import (
    HeadingSeparator,
    NormalizedCode,
    NormalizedDocument,
    NormalizedHeading,
    NormalizedList,
    NormalizedOpaque,
    NormalizedTable,
    normalize_document,
)
from dot_tools.markdown_formatter.parser import parse_document


def normalize(source: bytes) -> NormalizedDocument:
    """Parse and normalize a body for state assertions."""
    return normalize_document(parse_document(source))


def test_wraps_prose_and_preserves_unicode_code_point_limit() -> None:
    document = normalize(b"# title\n\n" + ("word " * 30).encode() + b"\n")
    paragraphs = [block for block in document.blocks if isinstance(block, bytes)]
    assert len(paragraphs) == 1
    assert all(len(line.decode()) <= 120 for line in paragraphs[0].splitlines())
    assert b"\n" in paragraphs[0]


def test_normalizes_headings_and_inserts_descent_separator() -> None:
    document = normalize(b"# title\n\nbody\n\n## child\n")
    assert document.blocks[0] == NormalizedHeading(1, b"title")
    assert isinstance(document.blocks[2], HeadingSeparator)
    assert document.blocks[3] == NormalizedHeading(2, b"child", 2)


def test_normalizes_lists_with_start_and_task_state() -> None:
    document = normalize(b"# title\n\n3. [x] first\n   9. second\n   10. third\n")
    value = next(block for block in document.blocks if isinstance(block, NormalizedList))
    assert value.ordered is True
    assert value.start == 3
    assert [item.marker for item in value.items] == ["3."]
    assert value.items[0].task is True
    assert value.items[0].continuation_column == 7


def test_normalizes_tables_with_alignment_and_padded_data() -> None:
    document = normalize(b"# title\n\n| a | longer |\n| :- | --: |\n| x |\n")
    table = next(block for block in document.blocks if isinstance(block, NormalizedTable))
    assert table.alignments == ("left", "right")
    assert table.rows == ((b"a", b"longer"), (b"x", b""))
    assert table.widths == (4, 6)


def test_normalizes_code_without_wrapping_and_normalizes_shell_info() -> None:
    document = normalize(b"# title\n\n```bash\n" + b"x " * 100 + b"\n```\n")
    code = next(block for block in document.blocks if isinstance(block, NormalizedCode))
    assert code.info == "shell"
    assert code.payload == b"x " * 100 + b"\n"
    assert code.fence == "`" * 3


def test_preserves_opaque_blocks() -> None:
    document = normalize(b"# title\n\n\x00 extension\r\n")
    opaque = next(block for block in document.blocks if isinstance(block, NormalizedOpaque))
    assert opaque.source == b"\x00 extension\r\n"
