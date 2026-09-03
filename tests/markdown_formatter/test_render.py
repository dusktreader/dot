"""Test deterministic rendering of normalized Markdown state."""

import pytest

from dot_tools.markdown_formatter.normalize import (
    NormalizedCode,
    NormalizedDocument,
    NormalizedHeading,
    NormalizedList,
    NormalizedListItem,
    NormalizedOpaque,
    NormalizedTable,
)
from dot_tools.markdown_formatter.normalize import _inline_code
from dot_tools.markdown_formatter.parser import InlineNode
from dot_tools.markdown_formatter.render import render_document


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (b"", b"``````"),
        (b"   ", b"```   ```"),
        (b" x", b"``` x```"),
        (b"x ", b"```x ```"),
        (b" x ", b"```x```"),
        (b"`x`", b"``` `x` ```"),
    ],
)
def test_render_code_span_boundaries(payload: bytes, expected: bytes) -> None:
    source = b"`" + (b" `x` " if payload == b"`x`" else payload) + b"`"
    assert _inline_code(InlineNode("code", source)) == expected


def test_render_document_preserves_code_payload_and_opaque_bytes() -> None:
    document = NormalizedDocument(
        blocks=[
            NormalizedHeading(1, b"Title"),
            NormalizedCode(b"line  \r\n", "text", "```"),
            NormalizedOpaque(b"extension\r\n  "),
        ]
    )
    assert render_document(document) == (
        b"# Title\n\n```text\nline  \r\n```\n\nextension\r\n  \n"
    )


def test_render_lists_tables_and_headings() -> None:
    document = NormalizedDocument(
        blocks=[
            NormalizedHeading(1, b"Title"),
            NormalizedList(
                ordered=True,
                start=3,
                items=(
                    NormalizedListItem("3.", b"first"),
                    NormalizedListItem("4.", b"second"),
                ),
            ),
            NormalizedTable(((b"a", b"long"), (b"x", b"")), ("left", "right"), (4, 4)),
        ]
    )
    assert render_document(document) == (
        b"# Title\n\n3. first\n4. second\n\n| a    | long |\n| :--- | ---: |\n| x    |      |\n"
    )
