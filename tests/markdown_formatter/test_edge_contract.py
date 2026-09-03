"""Cover the formatter boundary matrix required by the generic contract."""

from typing import cast

import pytest

from dot_tools.markdown_formatter import format_document
from dot_tools.markdown_formatter.frontmatter import extract_frontmatter, serialize_frontmatter
from dot_tools.markdown_formatter.normalize import (
    HeadingSeparator, NormalizedCode, NormalizedHeading, NormalizedList, normalize_document,
)
from dot_tools.markdown_formatter.parser import CodePayload, TableRow, parse_document


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (b"# T\n\n~~~bash\nvalue\n~~~\n", b"# T\n\n```shell\nvalue\n```\n"),
        (b"# T\n\n~~~\n\n~~~\n", b"# T\n\n```text\n\n```\n"),
        (b"# T\n\n    indented\n", b"# T\n\n```text\nindented\n```\n"),
    ],
)
def test_code_fence_info_payload_and_indented_fallback(source: bytes, expected: bytes) -> None:
    assert format_document(source) == expected


def test_inline_and_block_html_are_accepted() -> None:
    assert format_document(b"# T\n\n`<span>`\n") == b"# T\n\n```<span>```\n"
    assert format_document(b"# T\n\n```text\n<div>\n```\n") == b"# T\n\n```text\n<div>\n```\n"
    assert format_document(b"# T\n\n`<span>` <span>bad</span>\n") == b"# T\n\n```<span>``` <span>bad</span>\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_escaped_and_inline_html_angles_are_accepted(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"\\<div>" + line_ending
    parsed = parse_document(source)
    paragraph = parsed.blocks[1]
    assert paragraph.opaque is None
    assert b"".join(node.source for node in paragraph.inline) == b"\\<div>"
    output = format_document(source)
    assert output == b"# T\n\n\\<div>\n"
    assert format_document(output) == format_document(format_document(output)) == output
    html = parse_document(b"# T" + line_ending * 2 + b"<div>" + line_ending)
    assert html.blocks[1].opaque is not None


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_block_and_opaque_html_preserve_their_source_bytes(line_ending: bytes) -> None:
    block_source = b"# T" + line_ending * 2 + b"<section>block</section>" + line_ending
    opaque_source = b"# T" + line_ending * 2 + b"\x00 opaque <section>text</section>" + line_ending

    assert format_document(block_source) == b"# T\n\n<section>block</section>" + line_ending
    assert format_document(opaque_source) == b"# T\n\n\x00 opaque <section>text</section>" + line_ending


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("indent", [b"\t", b" \t", b"  \t"])
def test_indented_code_uses_parser_semantic_payload_for_visual_indentation(
    line_ending: bytes, indent: bytes,
) -> None:
    source = b"# T" + line_ending * 2 + indent + b"code" + line_ending
    original = parse_document(source).blocks[1].metadata["code"]
    assert isinstance(original, CodePayload)
    assert original.payload == b"code" + line_ending
    if original.payload_span is not None:
        assert source[original.payload_span.start:original.payload_span.end] == original.payload
    output = format_document(source)
    assert output == b"# T\n\n```text\ncode" + line_ending + b"```\n"
    reparsed = parse_document(output).blocks[1].metadata["code"]
    assert isinstance(reparsed, CodePayload)
    assert reparsed.payload == original.payload
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_table_code_span_pipe_uses_exact_opener_run_and_preserves_cell_ownership(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"| ``a`b|c`` | ``a`b|c`` |\n" +
              b"| --- | --- |" + line_ending + b"| x | x |" + line_ending)
    table = parse_document(source).blocks[1]
    assert table.opaque is None
    rows = cast(tuple[TableRow, ...], table.metadata["rows"])
    assert len(rows[0].cells) == 2
    assert [cell.source for cell in rows[0].cells] == [b"``a`b|c``", b"``a`b|c``"]
    assert all(source[row.span.start:row.span.end] == row.source for row in rows)
    assert all(source[cell.span.start:cell.span.end] == cell.source for row in rows for cell in row.cells)
    output = format_document(source)
    expected = b"# T\n\n| ```a`b|c``` | ```a`b|c``` |\n| ----------- | ----------- |\n| x           | x           |\n"
    assert output == expected
    reparsed = parse_document(output).blocks[1]
    assert reparsed.opaque is None
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_empty_list_nested_code_stays_inside_item_across_three_passes(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"-" + line_ending + b"  ```text" + line_ending + b"  x  " + line_ending + b"  ```" + line_ending
    output = format_document(source)
    expected = b"# T\n\n- ```text\n  x  " + line_ending + b"  ```\n"
    assert output == expected
    parsed = parse_document(output)
    assert parsed.blocks[1].kind == "bullet_list"
    item = parsed.blocks[1].children[0]
    assert item.children[0].kind == "fence"
    code = item.children[0].metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.payload == b"x  " + line_ending
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_empty_list_nested_code_preserves_parser_payload_and_source_ownership(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"-" + line_ending + b"  ```text" + line_ending + b"  x  " + line_ending + b"  ```" + line_ending
    original = parse_document(source).blocks[1].children[0].children[0].metadata["code"]
    assert isinstance(original, CodePayload)
    assert original.payload == b"x  " + line_ending
    original_fence = parse_document(source).blocks[1].children[0].children[0]
    assert original_fence.span is not None
    assert source[original_fence.span.start:original_fence.span.end] == original_fence.source
    if original.payload_span is not None:
        assert source[original.payload_span.start:original.payload_span.end] == original.payload
    output = format_document(source)
    reparsed = parse_document(output).blocks[1].children[0].children[0].metadata["code"]
    assert isinstance(reparsed, CodePayload)
    assert reparsed.payload == original.payload
    assert format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_escaped_backticks_leave_table_pipe_as_extra_cell(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"| h | z |" + line_ending + b"| --- | --- |" + line_ending
              + b"| \\`a|b\\` | c |" + line_ending)
    with pytest.raises(ValueError, match="too many cells"):
        format_document(source)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_lazy_list_continuation_is_preserved_when_standalone_ownership_is_ambiguous(line_ending: bytes) -> None:
    list_source = b"10. [x] one" + line_ending + b"    11. [ ] two" + line_ending + b"        > quote" + line_ending + b"        > line" + line_ending
    source = b"# T" + line_ending * 2 + list_source
    expected = b"# T\n\n" + list_source

    parsed = parse_document(source)
    assert parsed.blocks[1].kind == "ordered_list"
    assert parsed.blocks[1].opaque is None
    first = format_document(source)
    assert first == expected
    assert format_document(first) == format_document(format_document(first)) == first
    reparsed = parse_document(first)
    assert reparsed.blocks[1].kind == "ordered_list"
    assert reparsed.blocks[1].children[0].source == parsed.blocks[1].children[0].source
    assert b"11. [ ] two" in first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("backslashes", [b"\\", b"\\\\"])
def test_code_span_closer_ignores_backslash_parity_and_preserves_source_span(
    line_ending: bytes, backslashes: bytes,
) -> None:
    source = b"# T" + line_ending * 2 + b"`a" + backslashes + b"`b`" + line_ending
    paragraph = parse_document(source).blocks[1]
    assert paragraph.opaque is None
    code = paragraph.inline[0]
    assert code.kind == "code"
    assert code.span is not None
    assert source[code.span.start:code.span.end] == b"`a" + backslashes + b"`"
    assert code.metadata["payload"] == b"a" + backslashes
    first = format_document(source)
    assert parse_document(first).blocks[1].opaque is None
    assert format_document(first) == format_document(format_document(first)) == first


def test_code_span_pipe_is_owned_but_extra_physical_cell_is_rejected() -> None:
    valid = b"# T\n\n| h |\n| --- |\n| `a|b` |\n"
    assert parse_document(valid).blocks[1].opaque is None
    assert format_document(valid) == b"# T\n\n| h         |\n| --------- |\n| ```a|b``` |\n"
    invalid = valid.replace(b"` |", b"` | c |")
    with pytest.raises(ValueError, match="too many cells"):
        format_document(invalid)


def test_equal_level_sibling_headings_use_two_blank_lines() -> None:
    source = b"# T\n\n## A\n## B\n"
    expected = b"# T\n\n---\n\n## A\n\n\n## B\n"
    normalized = normalize_document(parse_document(source))
    headings = [block for block in normalized.blocks if isinstance(block, NormalizedHeading)]
    assert [heading.blank_lines_before for heading in headings] == [1, 1, 2]
    assert format_document(source) == expected
    assert format_document(expected) == format_document(format_document(expected)) == expected


def test_list_item_heading_descent_shares_container_state() -> None:
    source = b"# T\n\n- # H1\n  ## H2\n"
    expected = b"# T\n\n- # H1\n\n  ---\n\n  ## H2\n"
    assert format_document(source) == expected
    assert format_document(expected) == format_document(format_document(expected)) == expected
    normalized = normalize_document(parse_document(source))
    listing = next(block for block in normalized.blocks if isinstance(block, NormalizedList))
    assert any(isinstance(child, HeadingSeparator) for child in listing.items[0].children)


@pytest.mark.parametrize("label", [b"", b"!"])
def test_empty_owned_link_and_image_labels_use_destination_and_title_codecs(label: bytes) -> None:
    opener = b"![" if label == b"!" else b"["
    source = b"# T\n\n" + opener + b"](foo\\bar 'title')\n"
    expected = b"# T\n\n" + opener + b"](<foo\\\\bar> \"title\")\n"
    assert format_document(source) == expected
    assert format_document(expected) == expected


def test_heading_trailing_structural_whitespace_is_removed() -> None:
    for source, expected in ((b"# T   \n", b"# T\n"), (b"# T\n\n> ## H   \n", b"# T\n\n> ## H\n")):
        assert format_document(source) == expected
        assert format_document(expected) == format_document(format_document(expected)) == expected


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_task_nested_list_reparses_with_task_state_and_same_shape(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"- [x] first" + line_ending + b"  - [ ] nested" + line_ending
    expected = b"# T\n\n- [x] first\n  - [ ] nested\n"
    first = format_document(source)
    assert first == expected
    reparsed = parse_document(first)
    parent, nested = reparsed.blocks[1].children[0], reparsed.blocks[1].children[0].children[1]
    assert parent.metadata["task"] is True
    assert nested.kind == "bullet_list"
    assert nested.children[0].metadata["task"] is False
    assert format_document(first) == format_document(format_document(first)) == first


def test_empty_link_and_image_table_cells_use_the_same_canonical_codecs() -> None:
    source = b"# T\n\n| links | images |\n| --- | --- |\n| [](foo\\bar 't') | ![](foo\\bar 't') |\n"
    expected = b'# T\n\n| links              | images              |\n| ------------------ | ------------------- |\n| [](<foo\\\\bar> "t") | ![](<foo\\\\bar> "t") |\n'
    assert format_document(source) == expected
    assert format_document(expected) == expected


def test_single_line_canonical_code_span_is_stable_when_markdown_it_calls_it_a_fence() -> None:
    source = b"# T\n\n`<span>`\n"
    expected = b"# T\n\n```<span>```\n"
    assert format_document(source) == expected
    assert format_document(expected) == expected


def test_nested_inline_nodes_have_exact_recursive_source_slices() -> None:
    source = b"# T\n\n[a [b](u)](v)\n"
    paragraph = parse_document(source).blocks[1]
    assert paragraph.opaque is not None
    assert paragraph.opaque.source == b"[a [b](u)](v)\n"


@pytest.mark.parametrize("code", [b"`<x>`", b"```text\n<x>\n```", b"    <x>"])
def test_astral_prefix_does_not_change_html_or_code_handling(code: bytes) -> None:
    source = b"# T \xf0\x9f\x98\x80\n\n" + code + (b"\n" if not code.endswith(b"\n") else b"")
    format_document(source)


def test_table_header_code_and_html_text_are_accepted() -> None:
    assert format_document(b"# T\n\n| ` <x> ` |\n| --- |\n") == b"# T\n\n| ```<x>``` |\n| --------- |\n"


def test_commonmark_inline_boundaries_and_angle_destination_are_exact() -> None:
    source = b"# T\n\nfoo_bar_baz  \n[x](<url with space>)\n"
    assert format_document(source) == b"# T\n\nfoo_bar_baz\\\n[x](<url with space>)\n"


def test_inline_codec_canonicalizes_delimiters_and_preserves_nested_label_semantics() -> None:
    source = b'# T\n\n__outer [inner](<url>)__ [x](url \'title\') `a``b`\n'
    expected = b'# T\n\n**outer [inner](url)** [x](url "title") ```a``b```\n'

    output = format_document(source)

    assert output == expected
    assert format_document(output) == output


def test_mixed_inline_paragraph_wraps_around_indivisible_atoms() -> None:
    source = b"# T\n\n" + b" ".join([b"word"] * 35) + b" [label](url)\n"

    output = format_document(source)

    lines = output.splitlines()
    assert lines[1] == b""
    assert len(lines[2].decode("utf-8")) <= 120
    content_lines = [line for line in lines[2:] if line]
    assert all(len(line.decode("utf-8")) <= 120 for line in content_lines)
    assert content_lines[-1].endswith(b"[label](url)")
    assert format_document(output) == output


def test_unclosed_fence_preserves_payload_exactly() -> None:
    assert format_document(b"# T\n\n```text\npayload\n") == b"# T\n\n```text\npayload\n```\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_unclosed_eof_fence_without_terminal_line_ending_preserves_payload_and_source(
    line_ending: bytes,
) -> None:
    source = b"# T" + line_ending * 2 + b"```text" + line_ending + b"x"
    original = parse_document(source).blocks[1].metadata["code"]
    assert isinstance(original, CodePayload)
    assert original.payload == b"x"

    output = format_document(source)
    reparsed = parse_document(output).blocks[1].metadata["code"]
    assert isinstance(reparsed, CodePayload)
    assert output == b"# T\n\n```text" + line_ending + b"x"
    assert reparsed.payload == original.payload
    assert format_document(output) == output
    assert format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_nested_unclosed_eof_fence_preserves_payload_and_source(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"> ```text" + line_ending + b"> x"
    original = parse_document(source).blocks[1].children[0].metadata["code"]
    assert isinstance(original, CodePayload)
    assert original.payload == b"x"

    output = format_document(source)
    reparsed = parse_document(output).blocks[1].children[0].metadata["code"]
    assert isinstance(reparsed, CodePayload)
    assert output == b"# T\n\n> ```text" + line_ending + b"> x"
    assert reparsed.payload == original.payload
    assert format_document(output) == output
    assert format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_fence_closer_uses_only_the_actual_marker_run(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"```text" + line_ending + b"x" + line_ending
              + b"  ``" + line_ending + b"~~~" + line_ending + b"````" + line_ending)
    parsed = parse_document(source)
    code = parsed.blocks[1].metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.payload == b"x" + line_ending + b"  ``" + line_ending + b"~~~" + line_ending
    output = format_document(source)
    assert b"  ``" + line_ending in output
    assert b"~~~" + line_ending in output
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("indent", [b"", b"   ", b"    "])
def test_fence_closer_indentation_preserves_payload_boundaries(line_ending: bytes, indent: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"```text" + line_ending + b"x" + line_ending + indent
              + b"```" + line_ending + b"y" + line_ending + b"```" + line_ending)
    parsed = parse_document(source)
    code = parsed.blocks[1].metadata["code"]
    assert isinstance(code, CodePayload)
    expected_payload = b"x" + line_ending + (indent + b"```" + line_ending + b"y" + line_ending if len(indent) == 4 else b"")
    assert code.payload == expected_payload
    output = format_document(source)
    reparsed = parse_document(output).blocks[1].metadata["code"]
    assert isinstance(reparsed, CodePayload)
    assert reparsed.payload == expected_payload
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_multiline_padded_code_uses_parser_semantics_without_fallback(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"`  x  `" + line_ending + b"x" + line_ending
    paragraph = parse_document(source).blocks[1]
    assert paragraph.opaque is None
    code = paragraph.inline[0]
    assert code.kind == "code"
    assert code.span is not None
    assert source[code.span.start:code.span.end] == b"`  x  `"
    assert code.metadata["payload"] == b" x "
    first = format_document(source)
    assert first == b"# T\n\n```  x  ```\nx\n"
    assert format_document(first) == format_document(format_document(first)) == first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_unclosed_split_fence_text_remains_one_opaque_paragraph(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"```foo`bar" + line_ending + b"x" + line_ending + b"## H" + line_ending
    paragraph = parse_document(source).blocks[1]
    assert paragraph.opaque is None
    assert all(node.kind == "text" for node in paragraph.inline)
    assert b"".join(node.source for node in paragraph.inline) == paragraph.source.rstrip(b"\r\n")
    first = format_document(source)
    assert b"```foo`bar" in first
    assert format_document(first) == format_document(format_document(first)) == first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_opaque_boundary_before_generated_heading_separator_is_exact(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"\x00 opaque \t" + line_ending + b"## H" + line_ending
    expected = b"# T\n\n\x00 opaque \t" + line_ending + b"\n---\n\n## H\n"
    first = format_document(source)
    assert first == expected
    assert format_document(first) == format_document(format_document(first)) == first


def test_backtick_info_fence_inside_blockquote_remains_one_code_block() -> None:
    source = b"# T\n\n> ```foo`bar\n> payload\n> ```\n"
    expected = b"# T\n\n> ~~~foo`bar\n> payload\n> ~~~\n"

    output = format_document(source)

    assert output == expected
    assert format_document(output) == output


def test_nested_blockquote_code_keeps_each_active_prefix_once() -> None:
    source = b"# T\n\n> outer\n>\n> > inner\n> >\n> >     code\n"
    expected = b"# T\n\n> outer\n> \n> > inner\n> > \n> > ```text\n> > code\n> > ```\n"

    output = format_document(source)

    assert output == expected
    assert format_document(output) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_list_blockquote_fence_preserves_payload_and_converges_in_three_passes(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"> - a" + line_ending + b">" + line_ending
              + b">   ```text" + line_ending + b">   x" + line_ending + b">   ```" + line_ending)
    expected = b"# T\n\n> - a\n> \n>   ```text\n>   x" + line_ending + b">   ```\n"

    first = format_document(source)

    assert first == expected
    assert format_document(first) == first
    assert format_document(format_document(first)) == first
    code = next(block for block in _walk_normalized(normalize_document(parse_document(source)).blocks)
                if isinstance(block, NormalizedCode))
    assert code.payload == b"x" + line_ending


def test_long_inline_code_is_indivisible_and_idempotent() -> None:
    value = b" ".join([b"word"] * 40)
    output = format_document(b"# T\n\n`" + value + b"`\n")
    assert output == b"# T\n\n```" + value + b"```\n"
    assert format_document(output) == output


def test_empty_two_tick_inline_code_uses_the_canonical_empty_payload() -> None:
    source = b"# T\n\n``\n"
    expected = b"# T\n\n``````\n"

    assert format_document(source) == expected
    assert format_document(expected) == expected


def test_long_list_prose_wraps_and_retains_its_prefix_for_three_passes() -> None:
    source = b"# T\n\n- " + b" ".join([b"word"] * 50) + b"\n"

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == second == third
    assert all(len(line.decode("utf-8")) <= 122 for line in first.splitlines()[2:])
    assert all(line.startswith((b"- ", b"  ")) for line in first.splitlines()[2:])


@pytest.mark.parametrize("source", [b"# T\n\n- parent\n  - child\n    continuation\n", b"# T\n\n12. first\n13. second\n"])
def test_nested_and_multidigit_lists_preserve_container_shape(source: bytes) -> None:
    output = format_document(source)
    assert (b"child" in output) == (b"child" in source)
    assert b"continuation" in output or b"12. first" in output
    assert format_document(output) == output


@pytest.mark.parametrize("row", [b"a\\|b", b"a\\\\\\|b", b"`a|b`"])
def test_table_pipe_escaping_is_lossless_and_idempotent(row: bytes) -> None:
    source = b"# T\n\n| value |\n| --- |\n| " + row + b" |\n"
    output = format_document(source)
    assert format_document(output) == output
    if row.startswith(b"`"):
        assert b"`a|b`" in output


def test_even_backslash_parity_remains_a_real_table_delimiter() -> None:
    source = b"# T\n\n| left | right |\n| --- | --- |\n| a\\\\|b | c |\n"

    with pytest.raises(ValueError, match="too many cells"):
        format_document(source)


@pytest.mark.parametrize("row", [b"a\\|", b"a\\\\\\|", b"`a|`"])
def test_table_literal_trailing_pipes_keep_their_semantic_backslash_run(row: bytes) -> None:
    source = b"# T\n\n| value |\n| --- |\n| " + row + b" |\n"

    output = format_document(source)

    assert format_document(output) == output
    assert row in output


def test_center_table_minimum_is_three_dashes_plus_two_markers() -> None:
    source = b"# T\n\n| a |\n| :---: |\n| x |\n"

    assert format_document(source) == b"# T\n\n| a     |\n| :---: |\n| x     |\n"


def test_unescaped_table_pipe_is_an_extra_cell_error() -> None:
    with pytest.raises(ValueError, match="too many cells"):
        format_document(b"# T\n\n| value |\n| --- |\n| a|b |\n")


@pytest.mark.parametrize("row", [b"|", b"||"])
def test_table_framing_only_rows_are_rejected(row: bytes) -> None:
    with pytest.raises(ValueError, match="table row has zero cells"):
        format_document(b"# T\n\n| value |\n| --- |\n" + row + b"\n")


def test_table_empty_cell_is_distinct_from_framing_only_row() -> None:
    source = b"# T\n\n| value |\n| --- |\n| |\n"
    assert format_document(source) == b"# T\n\n| value |\n| ----- |\n|       |\n"


def test_frontmatter_float_boundaries_round_trip_and_empty_mapping() -> None:
    for value in (1e-6, 1.2345678, 1e20, 1e21, 1e-7, 5e-324, -0.0):
        encoded = serialize_frontmatter({"value": value})
        parsed, _ = extract_frontmatter(encoded)
        assert parsed == {"value": value}
    assert extract_frontmatter(b"---\n---\n# T\n")[0] == {}


def test_parser_inline_ownership_handles_nested_escaped_astral_and_crlf() -> None:
    source = "# T\r\n\r\n**outer [😀](url) \\*inner\\***\r\n".encode()
    paragraph = parse_document(source).blocks[1]
    assert paragraph.opaque is None
    assert paragraph.inline[0].kind == "strong"
    assert paragraph.inline[0].span is not None
    assert paragraph.inline[0].span.end - paragraph.inline[0].span.start == len(paragraph.inline[0].source)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (b"foo_bar_baz", b"foo_bar_baz"),
        (b"***foo***bar", b"***foo***bar"),
        (b"**foo__bar__**", b"**foo__bar__**"),
        (b"`  x  `", b"```  x  ```"),
    ],
)
def test_commonmark_semantics_survive_canonical_reparse(body: bytes, expected: bytes) -> None:
    source = b"# T\n\n" + body + b"\n"
    output = format_document(source)
    assert output == b"# T\n\n" + expected + b"\n"
    assert format_document(output) == output


def test_code_span_parser_and_reparse_payloads_match_after_one_normalization() -> None:
    source = b"# T\n\n`  x  ` ` x ` `x  ` `  x`\n"
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    assert first == second == third
    original = parse_document(source).blocks[1].inline
    reparsed = parse_document(first).blocks[1].inline
    assert [node.metadata["payload"] for node in original if node.kind == "code"] == [
        node.metadata["payload"] for node in reparsed if node.kind == "code"
    ]


def test_repeated_table_cells_have_distinct_owned_byte_spans() -> None:
    source = b"# T\n\n| x | x |\n| --- | --- |\n"
    table = parse_document(source).blocks[1]
    spans = [node.span for node in table.inline if node.source == b"x"]
    assert len(spans) == 2
    assert spans[0] != spans[1]
    assert all(span is not None and source[span.start:span.end] == b"x" for span in spans)


def test_hard_break_segments_wrap_independently_at_120_code_points() -> None:
    segment = b" ".join([b"word"] * 40)
    source = b"# T\n\n" + segment + b"  \n" + segment + b"\n"

    output = format_document(source)
    prose = output.split(b"\n\n", 1)[1].rstrip(b"\n").splitlines()

    assert all(len(line.decode("utf-8")) <= 120 for line in prose)
    assert b"\\\n" in output
    assert format_document(format_document(output)) == output


def test_list_hard_break_uses_canonical_bytes_and_wraps_each_side_without_prefix() -> None:
    continuation = "😀 " + " ".join(["word"] * 39)
    source = b"# T\n\n- first  \n" + continuation.encode("utf-8") + b"\n"

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == second == third
    assert b"- first\\\n" in first
    assert b"- first  \n" not in first
    assert b"first\\\\\n" not in first
    content_lines = first.splitlines()[2:]
    assert all(len(line.decode("utf-8").removeprefix("  ")) <= 120 for line in content_lines)
    assert "😀".encode("utf-8") in first


def test_nested_list_children_preserve_paragraph_quote_and_fence_payloads() -> None:
    source = b"# T\n\n- first\n  second paragraph\n  > quoted\n  > text\n  ```text\n  code\n  ```\n"

    output = format_document(source)

    assert b"second paragraph" in output
    assert b"> quoted\n  > text" in output
    assert b"```text\n  code\n  ```" in output
    assert format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_blockquote_list_heading_uses_owned_content_and_converges(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"> - # H" + line_ending + b">   text" + line_ending
    expected = b"# T\n\n> - # H\n> \n>   text\n"

    parsed = parse_document(source)
    heading = parsed.blocks[1].children[0].children[0].children[0]
    assert heading.kind == "heading_1"
    assert [node.source for node in heading.inline] == [b"H"]
    span = heading.inline[0].span
    assert span is not None
    assert source[span.start:span.end] == b"H"

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == second == third == expected
    reparsed_heading = parse_document(first).blocks[1].children[0].children[0].children[0]
    assert [node.source for node in reparsed_heading.inline] == [b"H"]


def test_nested_list_fence_in_blockquote_strips_structural_indent_once() -> None:
    source = b"# T\n\n> - item\n>   - nested\n>     ```text\n>     x  \n>     ```\n"
    expected = b"# T\n\n> - item\n>   - nested\n> \n>     ```text\n>     x  \n>     ```\n"

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == second == third == expected
    normalized = normalize_document(parse_document(first))
    code = next(block for block in _walk_normalized(normalized.blocks) if isinstance(block, NormalizedCode))
    assert code.payload == b"x  \n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_nested_code_retains_payload_line_endings_but_canonicalizes_structure(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"> - item" + line_ending + b">" + line_ending
              + b">   ```text" + line_ending + b">   x  " + line_ending + b">   y" + line_ending
              + b">   ```" + line_ending)
    first = format_document(source)
    expected = b"# T\n\n> - item\n> \n>   ```text\n>   x  " + line_ending + b">   y" + line_ending + b">   ```\n"
    assert first == expected
    assert format_document(first) == format_document(format_document(first)) == first


def test_center_table_uses_two_alignment_markers_and_converges() -> None:
    source = b"# T\n\n| a |\n| :---: |\n| x |\n"
    first = format_document(source)
    assert first == b"# T\n\n| a     |\n| :---: |\n| x     |\n"
    assert format_document(first) == first


@pytest.mark.parametrize("source", [b"# T\n\n-\n", b"# T\n\n1.\n", b"# T\n\n-\n  - child\n"])
def test_empty_list_items_are_safe_and_idempotent(source: bytes) -> None:
    first = format_document(source)
    assert format_document(first) == first
    assert format_document(format_document(first)) == first


def _walk_normalized(values: list[object] | tuple[object, ...]):
    """Yield normalized blocks recursively for semantic regression assertions."""
    for value in values:
        yield value
        for attribute in ("blocks", "items", "nested", "children"):
            children = getattr(value, attribute, ())
            if attribute == "items":
                children = [item for item in children]
            if children:
                for child in _walk_normalized(tuple(children)):
                    yield child


def test_table_cell_spans_include_escaped_and_code_pipe_source() -> None:
    source = b"# T\n\n| a\\|b | `c|d` |\n| --- | --- |\n| x | y |\n"
    table = parse_document(source).blocks[1]

    assert table.opaque is None
    assert b"a\\|b" in b"".join(node.source for node in table.inline)
    assert b"`c|d`" in b"".join(node.source for node in table.inline)
    output = format_document(source)
    assert format_document(format_document(output)) == output


def test_parser_owned_table_header_and_data_cells_have_exact_spans_and_output() -> None:
    source = "# T\r\n\r\n| h\\|😀 | `x|y` |\r\n| :--- | ---: |\r\n| a\\|b | `z|q` |\r\n".encode()
    table = parse_document(source).blocks[1]

    assert table.opaque is None
    assert table.metadata["rows"]
    rows = cast(tuple[TableRow, ...], table.metadata["rows"])
    assert isinstance(rows, tuple) and all(isinstance(row, TableRow) for row in rows)
    rows = tuple(row for row in rows if isinstance(row, TableRow))
    for row in rows:
        assert source[row.span.start:row.span.end] == row.source
        for cell in row.cells:
            assert source[cell.span.start:cell.span.end] == cell.source
    expected = "# T\n\n| h\\|😀 | ```x|y``` |\n| :--- | --------: |\n| a\\|b | ```z|q``` |\n".encode()
    first = format_document(source)
    assert first == expected
    assert format_document(first) == first == format_document(first)
    reparsed = parse_document(first)
    assert reparsed.blocks[1].opaque is None


def test_table_output_reparses_semantically_and_converges_in_three_passes() -> None:
    source = b"# T\r\n\r\n| name | value |\r\n| :--- | ---: |\r\n| a\\|b | `x|y` |\r\n"
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == second == third
    reparsed = parse_document(first)
    assert reparsed.blocks[1].kind == "table"
    assert b"a\\|b" in first
    assert b"`x|y`" in first


def test_blockquote_ordered_list_preserves_start_and_reparsed_metadata() -> None:
    source = b"# T\n\n> 12. first\n> 13. second\n"
    first = format_document(source)
    assert first == source
    assert parse_document(first).blocks[1].children[0].metadata["start"] == 12
    assert format_document(first) == format_document(format_document(first)) == first


@pytest.mark.parametrize("destination", [b"foo\\bar", b"<foo\\bar>"])
def test_link_destination_backslashes_use_canonical_angle_form(destination: bytes) -> None:
    source = b"# T\n\n[x](" + destination + b")\n"
    expected = b"# T\n\n[x](<foo\\\\bar>)\n"
    assert format_document(source) == expected
    assert format_document(expected) == expected


def test_link_destination_backslashes_are_canonical_inside_table_cells() -> None:
    source = b"# T\n\n| link |\n| --- |\n| [x](foo\\bar) |\n"
    expected = b"# T\n\n| link            |\n| --------------- |\n| [x](<foo\\\\bar>) |\n"
    assert format_document(source) == expected
    assert parse_document(expected).blocks[1].opaque is None
    assert format_document(expected) == expected


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_table_cell_spans_and_edges_preserve_tabs(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"| \tfoo\t |" + line_ending + b"| --- |" + line_ending + b"| \tbar\t |" + line_ending
    table = parse_document(source).blocks[1]
    rows = cast(tuple[TableRow, ...], table.metadata["rows"])
    assert all(source[cell.span.start:cell.span.end] == cell.source for row in rows for cell in row.cells)
    expected = b"# T\n\n| \tfoo\t |\n| ----- |\n| \tbar\t |\n"
    assert format_document(source) == expected
    assert format_document(expected) == format_document(format_document(expected)) == expected


@pytest.mark.parametrize("source", [
    b"# T\n\n__a**b _c__d_ e\\f__\n",
    b"# T\n\n| h |\n| --- |\n| __a**b _c__d_ e\\f__ |\n",
])
def test_delimiter_codec_preserves_literal_descendant_syntax_and_three_passes(source: bytes) -> None:
    output = format_document(source)
    assert b"__a**b _c__d_ e\\f__" in output
    assert parse_document(output).blocks[1].opaque is None
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("source", [
    b"# T\n\n- parent\n  - child\n",
    b"# T\n\n12. parent\n\n    13. child\n",
    b"# T\n\n- [x] parent\n  - [ ] child\n",
])
def test_same_family_nested_lists_have_safe_boundary_and_reparse_shape(source: bytes, line_ending: bytes) -> None:
    output = format_document(source.replace(b"\n", line_ending))
    listing = parse_document(output).blocks[1]
    parent = listing.children[0]
    nested = next(child for child in parent.children if child.kind in {"bullet_list", "ordered_list"})
    assert nested.children
    assert all(not line.endswith((b" ", b"\t")) for line in output.splitlines())
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_indented_code_preserves_physical_payload_bytes_and_spans(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b" \tcode  " + line_ending + b"\tsecond" + line_ending
    code = parse_document(source).blocks[1].metadata["code"]
    assert isinstance(code, CodePayload)
    assert code.payload == b"code  " + line_ending + b"second" + line_ending
    assert code.payload_span is None or source[code.payload_span.start:code.payload_span.end] == code.payload
    output = format_document(source)
    reparsed_code = parse_document(output).blocks[1].metadata["code"]
    assert isinstance(reparsed_code, CodePayload)
    assert reparsed_code.payload == code.payload
    assert format_document(output) == format_document(format_document(output)) == output


def test_heading_spacing_state_is_rendered_exactly() -> None:
    source = b"# T\n\n## A\nbody\n## B\n### C\n"
    expected = b"# T\n\n---\n\n## A\n\nbody\n\n\n## B\n\n---\n\n### C\n"
    assert format_document(source) == expected
    assert format_document(expected) == format_document(format_document(expected)) == expected


@pytest.mark.parametrize("tail", [b"u 'a\\\\b\\'c'", b"<a\\<b> \"a\\\\b\\\"c\""])
def test_link_title_and_angle_destination_codecs_are_canonical(tail: bytes) -> None:
    output = format_document(b"# T\n\n[x](" + tail + b")\n")
    assert parse_document(output).blocks[1].opaque is None
    assert format_document(output) == format_document(format_document(output)) == output


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("opener", [b"[x]", b"![]"])
@pytest.mark.parametrize("quote", [b"'", b'"'])
def test_link_and_image_titles_with_parentheses_remain_owned(
    line_ending: bytes, opener: bytes, quote: bytes,
) -> None:
    tail = b"(u " + quote + b"a\\)b" + quote + b")"
    source = b"# T" + line_ending * 2 + opener + tail + line_ending
    parsed = parse_document(source)
    paragraph = parsed.blocks[1]
    assert paragraph.opaque is None
    span = paragraph.inline[0].span
    assert span is not None
    assert source[span.start:span.end] == opener + tail
    expected = b"# T\n\n" + opener + b'(u "a)b")\n'
    first = format_document(source)
    assert first == expected
    assert parse_document(first).blocks[1].opaque is None
    assert format_document(format_document(first)) == first


@pytest.mark.parametrize("quote", [b"'", b'"'])
def test_table_cell_title_with_parentheses_has_exact_cell_span(quote: bytes) -> None:
    source = b"# T\n\n| link |\n| --- |\n| [x](u " + quote + b"a\\)b" + quote + b") |\n"
    parsed = parse_document(source)
    table = parsed.blocks[1]
    assert table.opaque is None
    rows = cast(tuple[TableRow, ...], table.metadata["rows"])
    cell = rows[2].cells[0]
    assert source[cell.span.start:cell.span.end] == cell.source
    expected = b'# T\n\n| link         |\n| ------------ |\n| [x](u "a)b") |\n'
    first = format_document(source)
    assert first == expected
    assert parse_document(first).blocks[1].opaque is None
    assert format_document(format_document(first)) == first


@pytest.mark.parametrize("body", [b"*_a_*", b"**_a_**", b"_**a**_", b"***a***"])
def test_nested_delimiter_semantics_are_preserved(body: bytes) -> None:
    source = b"# T\n\n" + body + b"\n"
    first = format_document(source)
    original = parse_document(source).blocks[1].inline
    reparsed = parse_document(first).blocks[1].inline
    def shape(nodes: list) -> list[tuple[str, object]]:
        return [(node.kind, shape(node.children)) for node in nodes]

    assert shape(reparsed) == shape(original)
    assert format_document(format_document(first)) == first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_adjacent_canonical_emphasis_preserves_literal_delimiters(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"a*_g_*" + line_ending
    first = format_document(source)
    assert first == b"# T\n\na\\**g*\\*\n"
    original = parse_document(source).blocks[1].inline
    reparsed = parse_document(first).blocks[1].inline
    assert [node.kind for node in reparsed] == [node.kind for node in original]
    assert format_document(first) == format_document(format_document(first)) == first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_adjacent_canonical_code_preserves_literal_backticks(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"```a`x`" + line_ending
    first = format_document(source)
    assert first == b"# T\n\n\\`\\`\\`a```x```\n"
    original = parse_document(source).blocks[1].inline
    reparsed = parse_document(first).blocks[1].inline
    assert [node.kind for node in reparsed] == [node.kind for node in original]
    assert reparsed[-1].metadata["payload"] == original[-1].metadata["payload"]
    assert format_document(first) == format_document(format_document(first)) == first


def test_empty_headings_are_owned_as_empty_inline_content() -> None:
    for source, expected in ((b"#\n", b"# \n"), (b"# T\n\n##\n", b"# T\n\n---\n\n## \n")):
        parsed = parse_document(source)
        heading = parsed.blocks[0] if len(parsed.blocks) == 1 else parsed.blocks[1]
        assert heading.opaque is None
        assert heading.inline == [] or [node.source for node in heading.inline] == [b""]
        assert format_document(source) == expected
        assert format_document(expected) == expected


def test_table_adjacent_emphasis_and_code_closers_keep_cell_semantics() -> None:
    emphasis_source = b"# T\n\n| h |\n| --- |\n| *a*_b_ |\n"
    emphasis_output = format_document(emphasis_source)
    assert b"*a*_b_" in emphasis_output
    assert format_document(emphasis_output) == emphasis_output

    code_source = b"# T\n\n| h |\n| --- |\n| `a\\\\`b` |\n"
    code_output = format_document(code_source)
    parsed = parse_document(code_source).blocks[1]
    reparsed = parse_document(code_output).blocks[1]
    assert parsed.opaque is None and reparsed.opaque is None
    assert all(node.span is not None and code_source[node.span.start:node.span.end] == node.source
               for node in parsed.inline)
    assert [node.kind for node in reparsed.inline] == [node.kind for node in parsed.inline]
    assert format_document(code_output) == format_document(format_document(code_output)) == code_output


def test_hard_break_owns_its_trailing_source_spaces() -> None:
    source = b"# T\n\na  \nb \n"
    paragraph = parse_document(source).blocks[1]
    hardbreak = next(node for node in paragraph.inline if node.kind == "hardbreak")
    assert hardbreak.source == b"  \n"
    assert hardbreak.span is not None
    assert source[hardbreak.span.start:hardbreak.span.end] == hardbreak.source
    assert format_document(source) == b"# T\n\na\\\nb\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("run_length", [1, 2, 3, 4])
@pytest.mark.parametrize("suffix", [b"", b"[x](u)", b"![x](u)", b"*x*", b"`x`"])
def test_backslash_runs_keep_semantics_across_inline_boundaries(
    line_ending: bytes, run_length: int, suffix: bytes,
) -> None:
    source = b"# T" + line_ending * 2 + b"a" + b"\\" * run_length + suffix + line_ending
    first = format_document(source)
    assert format_document(first) == format_document(format_document(first)) == first
    original = parse_document(source).blocks[1]
    reparsed = parse_document(first).blocks[1]
    assert original.opaque is None and reparsed.opaque is None
    assert [node.kind for node in reparsed.inline] == [node.kind for node in original.inline]
    assert all(node.span is not None and first[node.span.start:node.span.end] == node.source for node in reparsed.inline)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("semantic_slashes", [0, 1, 2])
def test_table_pipe_after_backslash_run_is_lossless(line_ending: bytes, semantic_slashes: int) -> None:
    run = b"\\" * (2 * semantic_slashes + 1)
    source = (b"# T" + line_ending * 2 + b"| h |" + line_ending + b"| --- |" + line_ending
              + b"| a" + run + b"|b |" + line_ending)
    first = format_document(source)
    assert b"a" + run + b"|b" in first
    assert format_document(first) == format_document(format_document(first)) == first
    table = parse_document(first).blocks[1]
    assert table.kind == "table" and table.opaque is None
    assert all(node.span is not None and first[node.span.start:node.span.end] == node.source for node in table.inline)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("body", [b"*a*_a_", b"**a**__a__", b"*a***b**", b"**a***b*"])
def test_adjacent_delimiter_atoms_keep_their_ast_shape(line_ending: bytes, body: bytes) -> None:
    source = b"# T" + line_ending * 2 + body + line_ending
    first = format_document(source)
    original = parse_document(source).blocks[1].inline
    reparsed = parse_document(first).blocks[1].inline
    assert [node.kind for node in reparsed] == [node.kind for node in original]
    assert format_document(first) == format_document(format_document(first)) == first


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_separator_like_paragraph_is_not_promoted_to_a_table(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"a" + line_ending + b"--- | ---" + line_ending
    parsed = parse_document(source)
    assert parsed.blocks[1].kind == "paragraph"
    assert format_document(source) == b"# T\n\na\n--- | ---\n"


def _inline_shape(nodes: list) -> list[tuple[str, object]]:
    """Return the recursive semantic shape of inline nodes."""
    return [(node.kind, _inline_shape(node.children)) for node in nodes]


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_mixed_emphasis_delimiters_preserve_complete_paragraph_shape(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"*a*a*a*" + line_ending
    original = parse_document(source).blocks[1]

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert first == b"# T\n\n*a*a*a*\n"
    assert first == second == third
    assert _inline_shape(parse_document(first).blocks[1].inline) == _inline_shape(original.inline)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_mixed_emphasis_delimiters_preserve_complete_table_cell_shape(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"| h |" + line_ending + b"| --- |" + line_ending
              + b"| *a*a*a* |" + line_ending)
    original = parse_document(source).blocks[1]

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)

    assert b"*a*a*a*" in first
    assert first == second == third
    reparsed = parse_document(first).blocks[1]
    assert _inline_shape(reparsed.inline) == _inline_shape(original.inline)


@pytest.mark.parametrize(
    ("child_source", "child_kind"),
    [(b"  > quote\n", "blockquote"), (b"  # child\n", "heading_1"),
     (b"  ```text\n  payload\n  ```\n", "fence")],
)
@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_task_children_use_structural_indentation_and_reparse_as_containers(
    child_source: bytes, child_kind: str, line_ending: bytes,
) -> None:
    source = b"# T" + line_ending * 2 + b"- [x] task" + line_ending + child_source.replace(b"\n", line_ending)
    original = parse_document(source)
    original_item = original.blocks[1].children[0]
    original_child = original_item.children[1]

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first)
    item = reparsed.blocks[1].children[0]

    assert first == second == third
    assert item.metadata["task"] is True
    assert item.children[1].kind == child_kind
    assert item.children[1].source != b""
    assert original_child.kind == item.children[1].kind


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_task_secondary_paragraph_uses_structural_child_column(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"- [x] task" + line_ending * 2 + b"  second paragraph" + line_ending
    original = parse_document(source)

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first)
    item = reparsed.blocks[1].children[0]

    assert first == b"# T\n\n- [x] task\n\n  second paragraph\n"
    assert first == second == third
    assert item.metadata["task"] is True
    assert [child.kind for child in item.children] == ["paragraph", "paragraph"]
    assert item.children[1].source == b"  second paragraph\n"
    assert [child.kind for child in original.blocks[1].children[0].children] == ["paragraph", "paragraph"]


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
def test_nested_task_secondary_paragraph_uses_nested_structural_column(line_ending: bytes) -> None:
    source = (b"# T" + line_ending * 2 + b"- [x] parent" + line_ending + b"  - [ ] child" + line_ending * 2
              + b"    nested second" + line_ending)

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first)
    parent = reparsed.blocks[1].children[0]
    nested = parent.children[1]
    child = nested.children[0]

    assert first == b"# T\n\n- [x] parent\n  - [ ] child\n\n    nested second\n"
    assert first == second == third
    assert parent.metadata["task"] is True
    assert child.metadata["task"] is False
    assert [block.kind for block in child.children] == ["paragraph", "paragraph"]
    assert child.children[1].source == b"    nested second\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
def test_task_first_paragraph_lazy_continuation_keeps_active_column_with_secondary_paragraph(
    line_ending: bytes,
) -> None:
    source = (b"# T" + line_ending * 2 + b"- [x] first" + line_ending + b"continuation" + line_ending * 2
              + b"  second paragraph" + line_ending)
    original = parse_document(source)
    original_item = original.blocks[1].children[0]

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first)
    item = reparsed.blocks[1].children[0]

    assert first == b"# T\n\n- [x] first\n      continuation\n\n  second paragraph\n"
    assert first == second == third
    assert item.metadata["task"] is True
    assert [child.kind for child in item.children] == ["paragraph", "paragraph"]
    assert [child.kind for child in original_item.children] == ["paragraph", "paragraph"]
    assert item.children[0].source == b"- [x] first\n      continuation\n"
    assert item.children[1].source == b"  second paragraph\n"
    assert all(node.span is not None for node in item.children[0].inline)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
def test_nested_task_first_paragraph_lazy_continuation_keeps_nested_active_column(
    line_ending: bytes,
) -> None:
    source = (b"# T" + line_ending * 2 + b"- [x] parent" + line_ending + b"  - [ ] child" + line_ending
              + b"  continuation" + line_ending * 2 + b"    nested second" + line_ending)
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first)
    child = reparsed.blocks[1].children[0].children[1].children[0]

    assert first == (b"# T\n\n- [x] parent\n  - [ ] child\n        continuation\n\n"
                     b"    nested second\n")
    assert first == second == third
    assert child.metadata["task"] is False
    assert [block.kind for block in child.children] == ["paragraph", "paragraph"]
    assert child.children[0].source == b"  - [ ] child\n        continuation\n"
    assert child.children[1].source == b"    nested second\n"


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
@pytest.mark.parametrize("nested", [False, True])
def test_container_paragraphs_normalize_each_physical_line_once(line_ending: bytes, nested: bool) -> None:
    if nested:
        body = b"> - parent\n>   child\n>   continuation\n"
    else:
        body = b"> quote\n> continuation\n"
    source = b"# T\n\n" + body
    source = source.replace(b"\n", line_ending)
    original = parse_document(source).blocks[1]
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first).blocks[1]

    assert first == second == third
    rendered_body = body.replace(b"\n", line_ending)
    assert first == b"# T\n\n" + rendered_body + (b"\n" if line_ending == b"\r" else b"")
    assert b"> >" not in first
    assert original.span is not None and source[original.span.start:original.span.end] == original.source
    assert reparsed.span is not None and first[reparsed.span.start:reparsed.span.end] == reparsed.source


def test_secondary_paragraphs_use_token_aware_wrapping_at_nested_structural_column() -> None:
    words = b" ".join([b"word"] * 50)
    source = b"# T\n\n- parent\n  - child\n\n    " + words + b"\n"

    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    lines = first.splitlines()

    assert first == second == third
    expected = (b"# T\n\n- parent\n  - child\n\n"
                + b"    " + b" ".join([b"word"] * 24) + b"\n"
                + b"    " + b" ".join([b"word"] * 24) + b"\n    word word\n")
    assert first == expected
    assert all(len(line[4:].decode("utf-8")) <= 120 for line in lines if line.startswith(b"    "))
    reparsed = parse_document(first)
    child = reparsed.blocks[1].children[0].children[1].children[0]
    assert [block.kind for block in child.children] == ["paragraph", "paragraph"]
    assert child.children[1].source.startswith(b"    word")


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
def test_recognized_nested_inline_fallback_normalizes_line_endings(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"***a" + line_ending + b"b***" + line_ending
    original = parse_document(source).blocks[1]
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first).blocks[1]

    assert first == b"# T\n\n***a\nb***\n"
    assert first == second == third
    assert reparsed.opaque is None
    assert _inline_shape(reparsed.inline) == _inline_shape(original.inline)
    assert all(node.span is not None and first[node.span.start:node.span.end] == node.source
               for node in reparsed.inline)


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n", b"\r"])
def test_multiline_link_title_normalizes_line_endings_and_preserves_ownership(line_ending: bytes) -> None:
    source = b"# T" + line_ending * 2 + b"[label](url \"one" + line_ending + b"two\")" + line_ending
    original = parse_document(source).blocks[1]
    first = format_document(source)
    second = format_document(first)
    third = format_document(second)
    reparsed = parse_document(first).blocks[1]

    assert first == b"# T\n\n[label](url \"one\ntwo\")\n"
    assert first == second == third
    assert reparsed.opaque is None
    assert _inline_shape(reparsed.inline) == _inline_shape(original.inline)
    assert reparsed.inline[0].kind == "link"
    assert reparsed.inline[0].span is not None
    assert first[reparsed.inline[0].span.start:reparsed.inline[0].span.end] == reparsed.inline[0].source
