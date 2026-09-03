"""Render normalized Markdown state."""

import re

from .normalize import (
    HeadingSeparator,
    NormalizedCode,
    NormalizedContainer,
    NormalizedDocument,
    NormalizedHeading,
    NormalizedList,
    NormalizedListItem,
    NormalizedOpaque,
    NormalizedParagraph,
    NormalizedTable,
)
from .parser import _backtick_run, _code_span_close, _exact_backtick_run


def _table(document: NormalizedTable) -> bytes:
    """Render a lossless aligned table."""
    if not document.rows:
        return b""
    count = len(document.rows[0])
    escaped: list[list[bytes]] = []
    for row in document.rows:
        rendered: list[bytes] = []
        for cell in row:
            value = cell.strip(b" ")
            out = bytearray()
            index = 0
            code_ticks = 0
            while index < len(value):
                if value[index:index + 1] == b"`":
                    run = _backtick_run(value, index) if code_ticks else _exact_backtick_run(value, index)
                    if not run:
                        out.append(value[index])
                        index += 1
                        continue
                    if code_ticks:
                        if run == code_ticks:
                            code_ticks = 0
                    elif _code_span_close(value, index + run, len(value), run) >= 0:
                        code_ticks = run
                    out.extend(value[index:index + run])
                    index += run
                    continue
                if value[index:index + 1] == b"|" and not code_ticks:
                    run = 0
                    while out and out[-1] == 92:
                        run += 1
                        out.pop()
                    semantic_run = run // 2
                    out.extend(b"\\" * (2 * semantic_run + 1))
                    out.extend(b"|")
                else:
                    out.append(value[index])
                index += 1
            rendered.append(bytes(out))
        escaped.append(rendered + [b""] * (count - len(rendered)))
    widths = [
        max(3 + (2 if alignment == "center" else 1 if alignment in {"left", "right"} else 0),
            *(len(row[index].decode("utf-8")) for row in escaped))
        for index, alignment in enumerate(document.alignments)
    ]
    separator: list[bytes] = []
    for width, alignment in zip(widths, document.alignments, strict=True):
        dashes = b"-" * width
        if alignment == "left":
            dashes = b":" + b"-" * (width - 1)
        elif alignment == "right":
            dashes = b"-" * (width - 1) + b":"
        elif alignment == "center":
            dashes = b":" + b"-" * (width - 2) + b":"
        separator.append(dashes)
    lines = []
    for row in [escaped[0], separator, *escaped[1:]]:
        values = row
        padded = []
        for index, value in enumerate(values):
            # Widths are Unicode code-point widths, not UTF-8 byte widths.
            text = value.decode("utf-8")
            padded.append((text + " " * (widths[index] - len(text))).encode("utf-8"))
        lines.append(b"| " + b" | ".join(padded) + b" |")
    return b"\n".join(lines)


def _list(value: NormalizedList) -> bytes:
    """Render list items and nested containers using each item's content column."""
    if not value.items and value.source:
        return value.source.rstrip(b"\r\n")
    lines: list[bytes] = []
    for item in value.items:
        lines.extend(_list_item(item, b"", value.ordered))
    return b"\n".join(lines)


def _list_item(item: NormalizedListItem, prefix: bytes, ordered: bool = False) -> list[bytes]:
    """Render one item, indenting continuation and nested list lines from the active marker column."""
    marker = item.marker.encode()
    first = prefix + marker + (b" " + item.content if item.content else b"")
    continuation = prefix + b" " * item.continuation_column
    structural = prefix + b" " * (item.structural_column or len(marker) + 1)
    lines = [first]
    lines.extend(continuation + line for line in item.continuation)
    for child_index, child in enumerate(item.children):
        child_lines = _render_block_lines(child)
        if isinstance(child, NormalizedList):
            # A nested list continues the item's content at its active column. It
            # is a structural child, not a secondary paragraph, so inserting a
            # blank line here would change the list hierarchy when reparsed.
            nested_continuation = prefix + b" " * (len(marker) + 1)
            if child.ordered and item.content:
                lines.append(b"")
            lines.extend(nested_continuation + line if line else b"" for line in child_lines)
            continue
        if isinstance(child, NormalizedCode):
            if child_index == 0 and not item.content:
                # Put the opening fence on the list marker line. A blank item
                # has no paragraph to establish a continuation block, so a
                # separately indented fence would reparse as top-level code.
                rendered_code = _render_block(child)
                opening, separator, remainder = rendered_code.partition(b"\n")
                lines[0] = prefix + marker + b" " + _list_task_prefix(item) + opening
                if separator:
                    lines.append(_prefix_lines(remainder, continuation))
                continue
            lines.append(b"")
            lines.append(_prefix_lines(child_lines[0], structural))
            continue
        if child_index == 0 and not item.content and child_lines:
            lines[0] = prefix + marker + b" " + _list_task_prefix(item) + child_lines[0]
            lines.extend(continuation + line for line in child_lines[1:])
            continue
        # A secondary paragraph is a block child, not a lazy continuation.
        # Keep the blank line so reparsing cannot merge it into the first
        # paragraph and flatten the list item on the next pass.
        lines.append(b"")
        child_prefix = structural if isinstance(child, (NormalizedContainer, NormalizedHeading, NormalizedList,
                                                        NormalizedParagraph)) else continuation
        lines.extend(child_prefix + line for line in child_lines)
    for nested in item.nested:
        nested_lines = _list(nested).splitlines()
        nested_prefix = prefix + b" " * (len(marker) + 1)
        lines.extend(nested_prefix + line for line in nested_lines)
    return lines


def _list_task_prefix(item: NormalizedListItem) -> bytes:
    """Return the task marker already represented by an empty item's first child."""
    return b"[x] " if item.task is True else b"[ ] " if item.task is False else b""


def _render_block_lines(block: object) -> list[bytes]:
    """Render one block into physical lines without changing its structural spacing."""
    if isinstance(block, NormalizedCode):
        return [_render_block(block)]
    return _render_block(block).splitlines()


def _render_block(block: object) -> bytes:
    """Render one nested block without adding document-level spacing."""
    if isinstance(block, NormalizedContainer):
        inner = _render_blocks(block.blocks)
        return _prefix_lines(inner, block.prefix)
    if isinstance(block, NormalizedCode):
        marker = block.fence.encode()
        payload = block.payload if not block.payload or block.payload.endswith((b"\n", b"\r")) else block.payload + b"\n"
        return marker + block.info.encode() + b"\n" + payload + marker
    if isinstance(block, NormalizedHeading):
        return b"#" * block.level + b" " + block.content
    if isinstance(block, NormalizedOpaque):
        return block.source
    if isinstance(block, NormalizedParagraph):
        return block.content
    if isinstance(block, bytes):
        return block
    if isinstance(block, NormalizedList):
        return _list(block)
    if isinstance(block, NormalizedTable):
        return _table(block)
    if isinstance(block, HeadingSeparator):
        return block.text.rstrip(b"\n")
    return b""


def render_document(document: NormalizedDocument) -> bytes:
    """Render normalized nodes with LF separators and a final newline unless EOF is opaque."""
    rendered: list[bytes] = []
    for block in document.blocks:
        if isinstance(block, HeadingSeparator):
            rendered.append(b"---")
        elif isinstance(block, NormalizedHeading):
            rendered.append(b"#" * block.level + b" " + block.content)
        elif isinstance(block, NormalizedCode):
            marker = block.fence.encode()
            separator = block.payload if not block.payload or block.payload.endswith((b"\n", b"\r")) else block.payload + b"\n"
            rendered.append(marker + block.info.encode() + b"\n" + separator + marker)
        elif isinstance(block, NormalizedTable):
            rendered.append(_table(block))
        elif isinstance(block, NormalizedList):
            rendered.append(_list(block))
        elif isinstance(block, NormalizedContainer):
            nested = _render_blocks(block.blocks)
            rendered.append(_prefix_lines(nested, block.prefix))
        elif isinstance(block, NormalizedOpaque):
            rendered.append(block.source)
        elif isinstance(block, bytes):
            rendered.append(block)
        else:
            rendered.append(b"")
    if not rendered:
        return b""
    output = _join_blocks(document.blocks, rendered)
    if output.endswith(b"\n") or _preserves_eof(rendered[-1], document.blocks[-1]):
        return output
    return output + b"\n"


def _preserves_eof(rendered: bytes, block: object) -> bool:
    """Return whether the terminal block deliberately has no synthetic EOF newline."""
    if isinstance(block, NormalizedOpaque):
        return block.preserve_eof and not rendered.endswith((b"\n", b"\r"))
    if isinstance(block, NormalizedContainer) and block.blocks:
        return _preserves_eof(rendered, block.blocks[-1])
    if isinstance(block, NormalizedList) and block.items:
        return any(_preserves_eof(rendered, child) for child in block.items[-1].children[-1:])
    return False


def _render_blocks(blocks: tuple[object, ...] | list[object]) -> bytes:
    """Join blocks using the document spacing policy at every container depth."""
    return _join_blocks(blocks, [_render_block(block) for block in blocks])


def _join_blocks(blocks: tuple[object, ...] | list[object], rendered: list[bytes]) -> bytes:
    """Join blocks without changing opaque bytes at generated separator boundaries."""
    if not rendered:
        return b""
    output = bytearray(rendered[0])
    for previous, current, value in zip(blocks, blocks[1:], rendered[1:], strict=False):
        separator = b"\n\n"
        if isinstance(previous, HeadingSeparator) and isinstance(current, NormalizedHeading):
            separator = b"\n\n"
        elif isinstance(current, NormalizedHeading):
            separator = b"\n" * (current.blank_lines_before + 1)
        if isinstance(previous, NormalizedOpaque) and isinstance(current, HeadingSeparator):
            separator = b"\n" * max(0, 2 - _trailing_line_breaks(bytes(output)))
        elif isinstance(previous, HeadingSeparator) and isinstance(current, NormalizedOpaque):
            separator = b"\n" * max(0, 2 - _leading_line_breaks(value))
        output.extend(separator)
        output.extend(value)
    return bytes(output)


def _trailing_line_breaks(value: bytes) -> int:
    """Count terminal LF or CRLF line endings while ignoring preserved trailing spaces."""
    cursor = len(value.rstrip(b" \t"))
    count = 0
    while cursor:
        if value[cursor - 2:cursor] == b"\r\n":
            cursor -= 2
        elif value[cursor - 1:cursor] in {b"\n", b"\r"}:
            cursor -= 1
        else:
            break
        count += 1
    return count


def _leading_line_breaks(value: bytes) -> int:
    """Count leading LF or CRLF line endings after preserved horizontal whitespace."""
    cursor = len(value) - len(value.lstrip(b" \t"))
    count = 0
    while cursor < len(value):
        if value[cursor:cursor + 2] == b"\r\n":
            cursor += 2
        elif value[cursor:cursor + 1] in {b"\n", b"\r"}:
            cursor += 1
        else:
            break
        count += 1
    return count


def _prefix_lines(value: bytes, prefix: bytes) -> bytes:
    """Prefix physical lines while retaining every payload line-ending byte."""
    if not value:
        return prefix
    parts = re.split(rb"(\r\n|\n|\r)", value)
    result = bytearray()
    at_line_start = True
    for part in parts:
        if at_line_start:
            result.extend(prefix)
            at_line_start = False
        result.extend(part)
        if part in {b"\r\n", b"\n", b"\r"}:
            at_line_start = True
    return bytes(result)
