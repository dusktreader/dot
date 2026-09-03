"""Tests for source-aware Markdown parsing."""

from pathlib import Path
from typing import cast

import pytest

from dot_tools.markdown_formatter import format_document
from dot_tools.markdown_formatter.parser import (
    CodePayload,
    SourceSpan,
    StructureError,
    TableRow,
    UnsupportedSyntaxError,
    parse_document,
)


FIXTURES = Path(__file__).parent / "fixtures" / "parser"


def test_parser_owns_blocks_and_inline_source() -> None:
    source = (FIXTURES / "basic.md").read_bytes()
    document = parse_document(source)

    assert [block.kind for block in document.blocks] == [
        "heading_1",
        "paragraph",
        "bullet_list",
        "blockquote",
        "fence",
    ]
    paragraph = document.blocks[1]
    assert b"**strong**" in paragraph.source
    assert [node.kind for node in paragraph.inline] == [
        "text", "strong", "text", "emphasis", "text", "code", "text", "link", "text", "image", "hardbreak", "text"
    ]
    assert b"".join(node.source for node in paragraph.inline) == paragraph.source.rstrip(b"\r\n")


def test_parser_preserves_opaque_unowned_block() -> None:
    document = parse_document(b"# title\n\n\x00 extension\n")
    assert document.blocks[1].opaque is not None
    assert document.blocks[1].opaque.source == b"\x00 extension\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_html_looking_body_text_is_accepted(line_ending: bytes) -> None:
    source = b"# title" + line_ending * 2 + b"text <span>raw</span>" + line_ending
    document = parse_document(source)
    assert document.blocks[1].opaque is None
    assert format_document(source) == b"# title\n\ntext <span>raw</span>\n"


def test_code_looking_html_is_accepted() -> None:
    document = parse_document(b"# title\n\n```text\n<div>not raw</div>\n```\n")
    assert document.blocks[1].kind == "fence"


def test_h1_policy_is_top_level_and_thematic_break_requires_descent() -> None:
    with pytest.raises(StructureError):
        parse_document(b"text\n\n# title\n")
    with pytest.raises(UnsupportedSyntaxError):
        parse_document(b"# title\n\n---\n\n## child\n\n---\n\n## sibling\n")


def test_utf8_spans_use_bytes_and_support_crlf_astral_and_missing_final_lf() -> None:
    source = "# 😀\r\n\r\nText 😀 **x**".encode()
    document = parse_document(source)
    assert document.blocks[0].span is not None
    assert document.blocks[1].span is not None
    assert document.blocks[0].span.end == len("# 😀\r\n".encode())
    assert document.blocks[1].span.end == len(source)
    assert "😀".encode() in document.blocks[1].inline[0].source


@pytest.mark.parametrize(
    ("body", "kinds", "sources"),
    [
        (b"[same](url) [same](other)", ["link", "text", "link"], [b"[same](url)", b" ", b"[same](other)"]),
        (b"**outer *inner***", ["strong"], [b"**outer *inner***"]),
        (b"![label](a(b) 'title')", ["image"], [b"![label](a(b) 'title')"]),
        ("[😀](url)  \r\nnext".encode(), ["link", "hardbreak", "text"], ["[😀](url)".encode(), b"  \r\n", b"next"]),
    ],
)
def test_inline_nodes_own_exact_source_and_children(body: bytes, kinds: list[str], sources: list[bytes]) -> None:
    document = parse_document(b"# title\n\n" + body)
    paragraph = document.blocks[1]

    assert paragraph.opaque is None
    assert [node.kind for node in paragraph.inline] == kinds
    assert [node.source for node in paragraph.inline] == sources
    assert all(node.span is not None and node.span.end - node.span.start == len(node.source) for node in paragraph.inline)
    link = next((node for node in paragraph.inline if node.kind in {"link", "image"}), None)
    if link is not None:
        assert [child.source for child in link.children] == [b"label" if link.kind == "image" else b"same"] if body.startswith(b"[same") else [b"label"]


def test_escaped_and_astral_inline_spans_use_utf8_boundaries() -> None:
    paragraph = parse_document("# title\n\n\\* 😀 `x`".encode()).blocks[1]

    assert paragraph.opaque is None
    assert b"\\*" in paragraph.inline[0].source
    assert any(node.kind == "code" and node.source == b"`x`" for node in paragraph.inline)


@pytest.mark.parametrize("body", [b"`<div>`", b"``<div>``", b"```\n<div>\n```", b"    <div>"])
def test_html_inside_each_code_form_is_ignored(body: bytes) -> None:
    source = b"# title\n\n" + body + (b"\n" if not body.endswith(b"\n") else b"")

    parse_document(source)


def test_html_adjacent_to_code_is_accepted() -> None:
    document = parse_document(b"# title\n\n`<div>` <span>bad</span>\n")
    assert document.blocks[1].opaque is None


@pytest.mark.parametrize("marker", [b"---", b"***", b"___"])
def test_source_break_is_owned_only_by_immediate_downward_transition(marker: bytes) -> None:
    document = parse_document(b"# title\n\n" + marker + b"\n\n## child\n")

    assert document.blocks[1].kind == "thematic_break"
    assert document.blocks[1].metadata["heading_transition"] is True


def test_source_break_with_intervening_body_is_rejected() -> None:
    with pytest.raises(UnsupportedSyntaxError):
        parse_document(b"# title\n\n---\n\nbody\n\n## child\n")


def test_parser_preserves_sibling_and_nested_container_relationships() -> None:
    document = parse_document(b"# title\n\n- parent\n  - child\n- sibling\n")

    assert [block.kind for block in document.blocks] == ["heading_1", "bullet_list"]
    list_block = document.blocks[1]
    assert [item.kind for item in list_block.children] == ["list_item", "list_item"]
    assert [child.kind for child in list_block.children[0].children] == ["paragraph", "bullet_list"]
    assert [child.kind for child in list_block.children[0].children[1].children] == ["list_item"]


@pytest.mark.parametrize("marker", [b"[ ]", b"[x]", b"[X]"])
def test_task_marker_is_metadata_and_not_paragraph_content(marker: bytes) -> None:
    item = parse_document(b"# title\n\n- " + marker + b" task\n").blocks[1].children[0]

    assert item.metadata["task"] is (marker != b"[ ]")
    paragraph = item.children[0]
    assert paragraph.inline[0].source == b"task"


@pytest.mark.parametrize("body", [b"<https://x.example>", b"<foo@example.com>", "😀 <https://x.example>".encode()])
def test_commonmark_autolinks_are_owned_links_and_not_raw_html(body: bytes) -> None:
    paragraph = parse_document(b"# title\n\n" + body + b"\n").blocks[1]

    link = next(node for node in paragraph.inline if node.kind == "link")
    assert link.source == body[-len(link.source):]
    assert link.span is not None
    assert link.span.end - link.span.start == len(link.source)


def test_nested_link_source_is_preserved() -> None:
    source = b"# title\n\n[a [b](u)](v)\n"
    paragraph = parse_document(source).blocks[1]

    assert paragraph.opaque is not None
    assert paragraph.opaque.source == b"[a [b](u)](v)\n"


@pytest.mark.parametrize("body", [b"<ftp://example.com>", b"<urn:isbn:1>", b"<x-custom:value>"])
def test_uri_autolinks_use_the_parser_owned_scheme_rule(body: bytes) -> None:
    paragraph = parse_document(b"# title\n\n" + body + b"\n").blocks[1]

    assert paragraph.inline[0].kind == "link"


def test_parser_owned_html_block_is_preserved_as_opaque() -> None:
    source = b"# title\n\n<?xml version=\"1.0\"?>\n"
    block = parse_document(source).blocks[1]
    assert block.opaque is not None
    assert block.opaque.source == source[len(b"# title\n\n"):]


def test_backtick_info_fence_keeps_one_block_and_source_span() -> None:
    source = b"# title\n\n```foo`bar\npayload\n```\n"
    document = parse_document(source)
    fence = document.blocks[1]

    assert [block.kind for block in document.blocks] == ["heading_1", "fence"]
    assert fence.source == source[len(b"# title\n\n"):]
    assert fence.span == SourceSpan(len(b"# title\n\n"), len(source))
    code = fence.metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.info == "foo`bar"
    assert code.payload == b"payload\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
@pytest.mark.parametrize("payload", [b"x", b"", b"x "])
def test_fenced_code_payload_span_slices_exact_source_bytes(line_ending: bytes, payload: bytes) -> None:
    source = b"# title" + line_ending * 2 + b"```text" + line_ending + payload + line_ending + b"```"
    code = parse_document(source).blocks[1].metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.payload_span is not None
    assert source[code.payload_span.start:code.payload_span.end] == code.payload


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
def test_bare_cr_fence_keeps_code_ownership_and_normalizes_on_first_pass(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"~~~bash" + line_ending + b"value" + line_ending + b"~~~" + line_ending
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    document = parse_document(first)

    assert first == b"# T\n\n```shell\nvalue" + line_ending + b"```\n"
    assert first == second == third
    assert document.blocks[1].kind == "fence"
    assert document.blocks[1].opaque is None


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_nested_fence_uses_semantic_payload_and_optional_source_span(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"> - item" + line_ending + b">   ```text" + line_ending
              + b">   x" + line_ending + b">   ```" + line_ending)
    document = parse_document(source)
    fence = document.blocks[1].children[0].children[0].children[1]
    code = fence.metadata["code"]

    assert isinstance(code, CodePayload)
    assert code.payload == b"x" + line_ending
    assert code.payload_span is None
    assert fence.span is not None
    assert source[fence.span.start:fence.span.end] == fence.source


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("source", [b"# T\n\n```text\nvalue\n```", b"# T\n\n```text\n", b"# T\n\n```text\n\n```", b"# T\n\n```text\nvalue\n```\n"])
def test_code_payload_metadata_spans_slice_marker_info_and_payload(source: bytes, line_ending: bytes) -> None:
    source = source.replace(b"\n", line_ending)
    code = parse_document(source).blocks[1].metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.marker_span is not None
    assert code.info_span is not None
    assert code.payload_span is not None
    assert source[code.marker_span.start:code.marker_span.end] == b"```"
    assert source[code.info_span.start:code.info_span.end] == b"text"
    assert source[code.payload_span.start:code.payload_span.end] == code.payload


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_table_rows_and_cells_have_explicit_exact_ownership(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"| a\\|b | `c|d` |" + line_ending + b"| --- | --- |" + line_ending + b"| x | y |" + line_ending
    table = parse_document(source).blocks[1]
    rows = cast(tuple[TableRow, ...], table.metadata["rows"])
    assert len(rows) == 3
    assert [cell.source for cell in rows[0].cells] == [b"a\\|b", b"`c|d`"]
    assert [cell.source for cell in rows[1].cells] == [b"---", b"---"]
    assert [cell.source for cell in rows[2].cells] == [b"x", b"y"]
    for row in rows:
        assert source[row.span.start:row.span.end] == row.source
        for cell in row.cells:
            assert source[cell.span.start:cell.span.end] == cell.source


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_table_cell_spans_slice_exact_source_bytes(line_ending: bytes) -> None:
    source = b"# title" + line_ending * 2 + b"| `a|b` | c |" + line_ending + b"| --- | --- |" + line_ending + b"| x | y |" + line_ending
    table = next(block for block in parse_document(source).blocks if block.kind == "table")
    for inline in table.inline:
        assert inline.span is not None
        assert source[inline.span.start:inline.span.end] == inline.source


def test_owned_inline_spans_slice_source_inside_nested_containers() -> None:
    source = b"# title\n\n> one\n> two\n\n- first\n  second\n"
    document = parse_document(source)

    for block in document.blocks:
        for node in _walk_blocks(block):
            for inline in node.inline:
                assert inline.span is not None
                assert source[inline.span.start:inline.span.end] == inline.source


def _walk_blocks(block: object):
    """Yield block descendants for span assertions."""
    yield block
    for child in getattr(block, "children", []):
        yield from _walk_blocks(child)
