"""Parse CommonMark into a byte-addressed, conservatively owned AST."""

from dataclasses import dataclass, field
import re
from typing import Iterator

from markdown_it import MarkdownIt
from markdown_it.token import Token


class ParseError(ValueError):
    """Report a Markdown parser failure."""


class StrictUtf8Error(ParseError):
    """Report invalid UTF-8 input."""


class StructureError(ValueError):
    """Report invalid document structure."""


class UnsupportedSyntaxError(ValueError):
    """Report unsupported syntax that cannot be safely normalized."""


class TableError(ValueError):
    """Report an invalid recognized table."""


@dataclass(frozen=True)
class SourceSpan:
    """Represent a half-open UTF-8 byte interval."""

    start: int
    end: int


@dataclass(frozen=True)
class CodePayload:
    """Represent code payload bytes and its info string."""

    payload: bytes
    info: str = ""
    marker_span: SourceSpan | None = None
    info_span: SourceSpan | None = None
    payload_span: SourceSpan | None = None


@dataclass(frozen=True)
class TableCell:
    """Represent one semantic table cell and its exact encoded source span."""

    source: bytes
    span: SourceSpan


@dataclass(frozen=True)
class TableRow:
    """Represent one physical table row without assigning framing pipes to cells."""

    source: bytes
    span: SourceSpan
    cells: tuple[TableCell, ...]


@dataclass(frozen=True)
class OpaqueBlock:
    """Represent a parser-delimited region preserved byte-for-byte."""

    source: bytes
    span: SourceSpan | None = None


@dataclass
class InlineNode:
    """Represent an owned inline source interval."""

    kind: str
    source: bytes = b""
    children: list["InlineNode"] = field(default_factory=list)
    span: SourceSpan | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class BlockNode:
    """Represent a block and its source association."""

    kind: str
    source: bytes = b""
    children: list["BlockNode"] = field(default_factory=list)
    inline: list[InlineNode] = field(default_factory=list)
    span: SourceSpan | None = None
    opaque: OpaqueBlock | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class DocumentAst:
    """Represent the parsed Markdown body."""

    blocks: list[BlockNode] = field(default_factory=list)
    frontmatter: object | None = None
    body: bytes = b""


def parse_document(body: bytes) -> DocumentAst:
    """Parse `body`, retaining only source intervals proven by CommonMark tokens."""
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise StrictUtf8Error(str(error)) from error
    starts = _line_starts(text)
    _reject_zero_cell_table_rows(body)
    try:
        tokens = MarkdownIt("commonmark").enable("table").parse(text)
    except Exception as error:
        raise ParseError(str(error)) from error
    blocks = _blocks(tokens, body, starts)
    _validate_h1(blocks)
    _validate_breaks(blocks)
    return DocumentAst(blocks=blocks, body=body)


def _reject_zero_cell_table_rows(body: bytes) -> None:
    """Reject framing-only rows when adjacent source lines prove a table."""
    lines = body.splitlines()
    for index in range(len(lines) - 2):
        header, separator, data = lines[index:index + 3]
        header_cells = _physical_table_cells(header)
        separator_cells = _physical_table_cells(separator)
        if not header_cells or len(header_cells) != len(separator_cells):
            continue
        if not all(re.fullmatch(rb":?-{3,}:?", cell.strip(b" ")) for cell in separator_cells):
            continue
        if data.strip(b" |"):
            continue
        if re.fullmatch(rb"\|+", data.strip(b" ")):
            raise TableError("table row has zero cells")


def _physical_table_cells(line: bytes) -> list[bytes]:
    """Split one unquoted table row without interpreting inline semantics."""
    value = line.strip(b" ")
    if value.startswith(b"|"):
        value = value[1:]
    if value.endswith(b"|") and not _escaped_by_odd_backslashes(value, len(value) - 1):
        value = value[:-1]
    cells: list[bytes] = []
    start = 0
    ticks = 0
    index = 0
    while index < len(value):
        byte = value[index]
        if byte == 96:
            run = _backtick_run(value, index) if ticks else _exact_backtick_run(value, index)
            if not run:
                index += 1
                continue
            if ticks:
                if run == ticks:
                    ticks = 0
            elif _code_span_close(value, index + run, len(value), run) >= 0:
                ticks = run
        elif byte == 124 and not ticks and not _escaped_by_odd_backslashes(value, index):
            cells.append(value[start:index].strip(b" "))
            start = index + 1
        index += run if byte == 96 and run else 1
    cells.append(value[start:].strip(b" "))
    return cells


def _escaped_by_odd_backslashes(value: bytes, index: int) -> bool:
    """Return whether the byte at `index` has an odd backslash run before it."""
    count = 0
    index -= 1
    while index >= 0 and value[index:index + 1] == b"\\":
        count += 1
        index -= 1
    return count % 2 == 1


def _exact_backtick_run(value: bytes, index: int) -> int:
    """Return an unescaped backtick opener run length at `index`, or zero."""
    if value[index:index + 1] != b"`" or _escaped_by_odd_backslashes(value, index):
        return 0
    if index and value[index - 1:index] == b"`":
        return 0
    end = index
    while end < len(value) and value[end:end + 1] == b"`":
        end += 1
    return end - index


def _backtick_run(value: bytes, index: int) -> int:
    """Return the raw backtick run at an inline position, including escaped ticks."""
    if value[index:index + 1] != b"`":
        return 0
    end = index
    while end < len(value) and value[end:end + 1] == b"`":
        end += 1
    return end - index


def _line_starts(text: str) -> list[int]:
    """Return UTF-8 byte offsets for every decoded line boundary."""
    starts = [0]
    for line in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(line.encode("utf-8")))
    return starts


def _span(token: Token, starts: list[int], body_length: int) -> SourceSpan | None:
    if not token.map:
        return None
    start_line, end_line = token.map
    if start_line >= len(starts):
        return None
    end = starts[end_line] if end_line < len(starts) else body_length
    return SourceSpan(starts[start_line], min(end, body_length))


def _blocks(tokens: list[Token], body: bytes, starts: list[int]) -> list[BlockNode]:
    """Build the meaningful block tree from markdown-it's nesting events."""
    roots: list[BlockNode] = []
    stack: list[tuple[str, BlockNode]] = []
    table_cursors: dict[int, int] = {}
    ignored = {"thead", "tbody", "tr", "th", "td"}
    for token in tokens:
        if token.type.endswith("_close"):
            token_type = token.type.removesuffix("_close")
            if stack and stack[-1][0] == token_type:
                stack.pop()
            continue
        token_type = token.type.removesuffix("_open")
        if token_type in ignored:
            continue
        if token.type == "inline":
            if not stack:
                continue
            parent = stack[-1][1]
            if parent.kind == "paragraph" and _is_compatibility_table(parent.source):
                parent.kind = "table"
                parent.inline = _compatibility_table_inlines(parent.source, parent.span.start if parent.span else 0)
                if not parent.inline:
                    parent.opaque = OpaqueBlock(parent.source, parent.span)
                continue
            if parent.kind == "table":
                row_source = body[starts[token.map[0]]:starts[token.map[1]]] if token.map else b""
                if re.search(rb"(?:^|\n)[ \t]*>", row_source):
                    parent.opaque = OpaqueBlock(parent.source, parent.span)
                else:
                    row_nodes = _table_inlines(token, body, starts, table_cursors)
                    if not row_nodes and token.content.strip():
                        parent.opaque = OpaqueBlock(parent.source, parent.span)
                    parent.inline.extend(row_nodes)
                continue
            source = _inline_source(token, parent, body, starts)
            base = _inline_base(token, parent, body, starts, source)
            parent.inline = _scan_inline(source, base) if base is not None else []
            # markdown-it intentionally does not expose an outer link token for
            # a link-like construct nested in a link label.  Do not let the
            # compatibility scanner invent ownership for that case: preserving
            # the complete paragraph is safer than changing the label.
            if _has_nested_link_label(source):
                parent.inline = []
                parent.opaque = OpaqueBlock(parent.source, parent.span)
            list_paragraph = parent.kind == "paragraph" and re.match(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", parent.source) is not None
            empty_heading = parent.kind.startswith("heading_") and not source and not parent.inline
            if b"\x00" in source or (base is None and not list_paragraph and not empty_heading) or (base is not None and not _owned_inline(parent.inline, source, body)):
                parent.inline = []
                parent.opaque = OpaqueBlock(parent.source, parent.span)
            continue
        if token.nesting == -1:
            continue
        span = _span(token, starts, len(body)) or SourceSpan(0, 0)
        kind = token_type
        if kind == "hr":
            kind = "thematic_break"
        elif kind == "heading":
            kind = f"heading_{token.tag[1:]}"
        source = body[span.start:span.end]
        # A canonical inline code span is required to use at least three ticks
        # by the formatter contract.  Markdown-it classifies a span occupying
        # one physical line as a fence, so recover the intended inline node
        # before the block tree is assembled.  Restrict this compatibility
        # path to a line with an explicit closing run; real multiline fences
        # continue through the normal fence path.
        if kind == "fence" and not re.search(rb"\r|\n", source.rstrip(b"\r\n")):
            marker = re.match(rb"^[ \t]*([`~]{3,}).*\1[ \t]*\r?\n?$", source)
            if marker:
                node = BlockNode(kind="paragraph", source=source, span=span, metadata={"token_type": token_type})
                node.inline = _scan_inline(source.rstrip(b"\r\n"), span.start)
                if _owned_inline(node.inline, source.rstrip(b"\r\n"), body):
                    if stack:
                        stack[-1][1].children.append(node)
                    else:
                        roots.append(node)
                    continue
        node = BlockNode(kind=kind, source=source, span=span, metadata={"token_type": token_type})
        if token_type == "html_block":
            node.opaque = OpaqueBlock(source, span)
        if kind == "code_block":
            # markdown-it has already removed CommonMark's four-column
            # indentation here. Keeping its content avoids treating a tab
            # (or a mixed space/tab prefix) as code data later on.
            node.metadata["semantic_content"] = token.content.encode("utf-8")
        if kind == "fence":
            node.metadata["semantic_content"] = token.content.encode("utf-8")
        if kind in {"bullet_list", "ordered_list"} and token.attrs:
            start = token.attrs.get("start")
            if isinstance(start, int):
                node.metadata["start"] = start
        if kind == "list_item":
            task_source = _remove_container_prefixes(source)
            task = re.match(rb"[ \t]*(?:[-+*]|\d+[.)])[ \t]+\[([ xX])\][ \t]+", task_source)
            if task:
                node.metadata["task"] = task.group(1).lower() == b"x"
        if stack:
            stack[-1][1].children.append(node)
        else:
            roots.append(node)
        if token.nesting == 1:
            stack.append((token_type, node))
    _join_split_backtick_fences(roots)
    for node in _walk(roots):
        if node.kind == "table" and node.span:
            node.metadata["rows"] = _table_rows(node.source, node.span.start)
        if node.kind in {"fence", "code_block"}:
            info = ""
            marker: bytes = b""
            closed = True
            if node.kind == "fence":
                first_line = re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", node.source.splitlines()[0])
                marker_match = re.match(rb"[ \t]*([`~]{3,})(.*?)[ \t]*$", first_line)
                marker = marker_match.group(1) if marker_match else b"```"
                info = marker_match.group(2).decode("utf-8") if marker_match else ""
                split_info = node.metadata.get("split_info")
                if isinstance(split_info, str):
                    info = split_info
                node.metadata["fence_marker"] = marker.decode("ascii")
            span = node.span or SourceSpan(0, 0)
            marker_start = 0
            info_start = 0
            marker_length = len(marker) if isinstance(marker, bytes) and node.kind == "fence" else 0
            info_length = len(info.encode("utf-8"))
            if node.kind == "fence" and node.source.splitlines():
                first_line = node.source.splitlines(keepends=True)[0]
                marker_match = re.search(rb"([`~]{3,})([^\r\n]*)", first_line)
                if marker_match:
                    marker_start = marker_match.start(1)
                    info_start = marker_match.start(2)
                    marker_length = len(marker_match.group(1))
                    info_length = len(marker_match.group(2).rstrip(b" \t"))
            payload_start = node.source.find(b"\n") + 1 if node.kind == "fence" else 0
            payload_end = len(node.source)
            semantic_payload: bytes | None = None
            payload_is_contiguous = True
            if node.kind == "fence":
                physical = node.source.splitlines(keepends=True)
                offset = len(physical[0]) if physical else 0
                payload_start = offset
                opening_line = _strip_container_prefix(physical[0]) if physical else b""
                opening_indent = len(opening_line) - len(opening_line.lstrip(b" \t"))
                list_prefix = re.match(rb"[ \t]*(?:[-+*]|\d+[.)])[ \t]+", opening_line)
                if list_prefix:
                    opening_indent = len(list_prefix.group())
                opening_marker = marker[:1] if marker else b"`"
                opening_length = len(marker)
                payload_lines: list[bytes] = []
                closed = False
                for line in physical[1:]:
                    without_container = _strip_container_prefix(line)
                    logical = _strip_indent_bytes(without_container, opening_indent)
                    if _is_fence_closer(logical, opening_marker, opening_length):
                        payload_end = offset
                        closed = True
                        break
                    payload_lines.append(logical)
                    if without_container != line or logical != without_container:
                        payload_is_contiguous = False
                    offset += len(line)
                semantic_payload = b"".join(payload_lines)
            elif node.kind == "code_block":
                candidate = node.metadata.get("semantic_content")
                if isinstance(candidate, bytes):
                    # markdown-it normalizes line endings in ``content``.  Its
                    # visual indentation decisions are authoritative, but the
                    # physical source owns each payload line ending and must be
                    # restored independently.
                    semantic_payload = _restore_code_line_endings(candidate, node.source)
                physical = node.source.splitlines(keepends=True)
                if semantic_payload is not None and physical:
                    payload_start = _structural_indent_end(physical[0], 4)
                    payload_end = payload_start + len(semantic_payload)
                    payload_is_contiguous = node.source[payload_start:payload_end] == semantic_payload
            node.metadata["code"] = CodePayload(
                semantic_payload if semantic_payload is not None else node.source[payload_start:payload_end],
                info,
                SourceSpan(span.start + marker_start, span.start + marker_start + marker_length),
                SourceSpan(span.start + info_start, span.start + info_start + info_length),
                SourceSpan(span.start + payload_start, span.start + payload_end) if payload_is_contiguous else None,
            )
            if not closed and not node.source.endswith((b"\n", b"\r")):
                # A missing EOF line ending is part of the code payload semantics.  There
                # is no safe canonical closer we can add without changing that payload.
                node.metadata["unclosed_eof"] = True
                node.opaque = OpaqueBlock(node.source, node.span)
    _propagate_opaque(roots)
    return roots


def _join_split_backtick_fences(blocks: list[BlockNode]) -> None:
    """Join markdown-it's paragraph/fence split for a backtick-bearing info line."""
    for block in blocks:
        _join_split_backtick_fences(block.children)
    index = 0
    while index + 1 < len(blocks):
        paragraph, fence = blocks[index], blocks[index + 1]
        first_line = paragraph.source.splitlines(keepends=True)[0] if paragraph.source else b""
        opening = re.match(rb"(?:[ \t]*>[ \t]?)*[ \t]*(`{3,})([^\r\n]*)\r?\n", first_line)
        if paragraph.kind == "paragraph" and fence.kind == "fence" and opening:
            combined = paragraph.source + fence.source
            logical_lines = [_strip_container_prefix(line) for line in combined.splitlines()]
            closing = bool(logical_lines) and _is_fence_closer(
                logical_lines[-1], opening.group(1), len(opening.group(1))
            )
            if not closing:
                # The parser has assigned the remainder of the document to an
                # invalid recovery fence.  Its boundary is unknowable, so
                # preserve the containing source instead of swallowing later
                # headings, paragraphs, or containers into code.
                opaque = BlockNode("paragraph", combined, span=SourceSpan(
                    paragraph.span.start if paragraph.span else 0,
                    fence.span.end if fence.span else len(combined),
                ))
                opaque.opaque = OpaqueBlock(combined, opaque.span)
                blocks[index:index + 2] = [opaque]
                continue
            fence.source = paragraph.source + fence.source
            if paragraph.span and fence.span:
                fence.span = SourceSpan(paragraph.span.start, fence.span.end)
            fence.metadata["fence_marker"] = opening.group(1).decode("ascii")
            fence.metadata["split_info"] = opening.group(2).decode("utf-8")
            del blocks[index]
            continue
        index += 1


def _inline_source(token: Token, parent: BlockNode, body: bytes, starts: list[int]) -> bytes:
    """Extract the exact inline content, removing only its Markdown container prefix."""
    if parent.span and token.map:
        raw = body[starts[token.map[0]]:starts[token.map[1]]]
        lines = raw.splitlines(keepends=True)
        lines = [_strip_container_prefix(line) for line in lines]
        if parent.kind.startswith("heading_"):
            if lines:
                # Remove a proven list marker before recording heading content.
                lines[0] = re.sub(
                    rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?",
                    b"",
                    lines[0],
                    count=1,
                )
                line_ending = lines[0][len(lines[0].rstrip(b"\r\n")):]
                heading_line = lines[0].rstrip(b"\r\n")
                lines[0] = re.sub(rb"^[ \t]{0,3}#{1,6}[ \t]+", b"", heading_line, count=1) + line_ending
                if re.fullmatch(rb"[ \t]{0,3}#{1,6}[ \t]*", heading_line):
                    lines[0] = line_ending
        elif parent.kind == "paragraph":
            # The inline token map identifies the paragraph lines. Remove only the
            # active list marker/task prefix on its first line; continuation lines
            # retain their source indentation as part of the owned interval.
            if lines:
                lines[0] = re.sub(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?", b"", lines[0], count=1)
                lines[0] = re.sub(rb"^[ \t]+", b"", lines[0], count=1)
                lines = [re.sub(rb"^[ \t]+", b"", line, count=1) for line in lines]
        return b"".join(lines).rstrip(b"\r\n")
    return token.content.encode()


def _strip_container_prefix(line: bytes) -> bytes:
    """Remove every leading block-quote prefix from one physical source line."""
    return re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", line)


def _strip_indent_bytes(line: bytes, width: int) -> bytes:
    """Remove the fence's structural indentation while preserving line endings."""
    index = 0
    while index < len(line) and index < width and line[index:index + 1] in {b" ", b"\t"}:
        index += 1
    return line[index:]


def _structural_indent_end(line: bytes, width: int) -> int:
    """Return the byte offset after one CommonMark structural indentation width."""
    columns = 0
    index = 0
    while index < len(line) and columns < width and line[index:index + 1] in {b" ", b"\t"}:
        if line[index:index + 1] == b" ":
            columns += 1
        else:
            columns += 4 - columns % 4
        index += 1
    return index


def _restore_code_line_endings(semantic: bytes, source: bytes) -> bytes:
    """Combine parser-stripped code content with source-owned line endings."""
    endings = [match.group() for match in re.finditer(rb"\r\n|\n|\r", source)]
    semantic_lines = semantic.splitlines(keepends=True)
    restored: list[bytes] = []
    for index, line in enumerate(semantic_lines):
        content = line.rstrip(b"\r\n")
        ending = endings[index] if index < len(endings) else line[len(content):]
        restored.append(content + ending)
    return b"".join(restored)


def _is_fence_closer(line: bytes, marker: bytes, minimum_length: int) -> bool:
    """Return whether `line` contains an eligible CommonMark closing marker."""
    match = re.fullmatch(rb"[ \t]*([`~]+)[ \t]*\r?\n?", line)
    if not match or _indent_columns(match.group(0)) > 3:
        return False
    marker_run = match.group(1)
    return bool(marker_run[:1] == marker[:1] and all(byte == marker[0] for byte in marker_run)
                and len(marker_run) >= minimum_length)


def _indent_columns(line: bytes) -> int:
    """Count leading space and tab columns using tab stops of four columns."""
    columns = 0
    for byte in line:
        if byte == ord(" "):
            columns += 1
        elif byte == ord("\t"):
            columns += 4 - columns % 4
        else:
            break
    return columns


def _remove_container_prefixes(source: bytes) -> bytes:
    """Remove quote prefixes so list metadata can be read from nested containers."""
    return b"\n".join(_strip_container_prefix(line) for line in source.split(b"\n"))


def _inline_base(token: Token, parent: BlockNode, body: bytes, starts: list[int], source: bytes) -> int | None:
    """Return a base only when the inline payload is one exact source interval.

    Container prefixes make a multi-line Markdown token physically discontiguous.  Guessing an
    interval for that token produces spans that point at quote or list markers, so callers must
    fall back to the complete containing block instead.
    """
    if parent.span:
        if not source:
            return parent.span.start
        candidates = [index for index in range(parent.span.start, parent.span.end + 1)
                      if body[index:index + len(source)] == source]
        if len(candidates) == 1:
            return candidates[0]
    return None


def _owned_inline(nodes: list[InlineNode], source: bytes, body: bytes) -> bool:
    """Prove that every inline node and recursive child span slices its claimed bytes."""
    if not _reconstruct(nodes, source):
        return False
    for inline in _inline_walk(nodes):
        if inline.span is None or body[inline.span.start:inline.span.end] != inline.source:
            return False
    return True


def _table_inlines(token: Token, body: bytes, starts: list[int], cursors: dict[int, int]) -> list[InlineNode]:
    """Build exact inline nodes for every parser-owned table cell token."""
    if not token.map:
        return []
    line_start = starts[token.map[0]]
    line_end = starts[token.map[1]] if token.map[1] < len(starts) else len(body)
    line = body[line_start:line_end].rstrip(b"\r\n")
    # A paragraph promoted to a table by the compatibility path has one
    # inline token for the whole row group rather than one token per cell.
    # Associate every physical cell independently in that case.  This keeps
    # code-span pipes and escaped pipes source-addressable instead of falling
    # back to a lossy substring search.
    if token.map[1] - token.map[0] > 1:
        result: list[InlineNode] = []
        offset = 0
        for row_with_ending in line.splitlines(keepends=True):
            row = row_with_ending.rstrip(b"\r\n")
            physical = _physical_table_cells_with_offsets(row)
            for cell_offset, encoded in physical:
                result.extend(_scan_inline(encoded, line_start + offset + cell_offset))
            offset += len(row_with_ending)
        return result
    physical = _physical_table_cells_with_offsets(line)
    cell_index = cursors.get(token.map[0], 0)
    if cell_index >= len(physical):
        return []
    offset, encoded = physical[cell_index]
    # The table rule's inline content is not a source of truth for physical
    # cells: markdown-it stops the token content at a pipe inside a code span,
    # and decodes escaped pipes.  The physical splitter has already proven the
    # cell boundary using code-span state and backslash parity.  Requiring the
    # decoded token content to equal the source would therefore reject the
    # recognized cases that the formatter must canonicalize.  Exact source
    # reconstruction below remains the ownership proof.
    span = SourceSpan(line_start + offset, line_start + offset + len(encoded))
    nodes = _scan_inline(encoded, span.start)
    if not _reconstruct(nodes, encoded):
        return []
    cursors[token.map[0]] = cell_index + 1
    return nodes


def _physical_table_cells_with_offsets(line: bytes) -> list[tuple[int, bytes]]:
    """Return physical table cells and their offsets within the stripped row."""
    value = line.strip(b" ")
    leading = len(line) - len(line.lstrip(b" "))
    if value.startswith(b"|"):
        leading += 1
        value = value[1:]
    if value.endswith(b"|") and not _escaped_by_odd_backslashes(value, len(value) - 1):
        value = value[:-1]
    result: list[tuple[int, bytes]] = []
    start = 0
    ticks = 0
    index = 0
    while index < len(value):
        byte = value[index]
        if byte == 96:
            run = _backtick_run(value, index) if ticks else _exact_backtick_run(value, index)
            if not run:
                index += 1
                continue
            if ticks:
                if run == ticks:
                    ticks = 0
            elif _code_span_close(value, index + run, len(value), run) >= 0:
                ticks = run
        elif byte == 124 and not ticks and not _escaped_by_odd_backslashes(value, index):
            raw_cell = value[start:index]
            cell = raw_cell.strip(b" ")
            result.append((leading + start + (len(raw_cell) - len(raw_cell.lstrip(b" "))), cell))
            start = index + 1
        index += run if byte == 96 and run else 1
    raw_cell = value[start:]
    cell = raw_cell.strip(b" ")
    result.append((leading + start + (len(raw_cell) - len(raw_cell.lstrip(b" "))), cell))
    return result


def _table_rows(source: bytes, base: int) -> tuple[TableRow, ...]:
    """Build explicit physical table rows using actual LF or CRLF byte lengths."""
    rows: list[TableRow] = []
    offset = 0
    for physical in source.splitlines(keepends=True):
        row = physical.rstrip(b"\r\n")
        cells = tuple(
            TableCell(cell, SourceSpan(base + offset + cell_offset, base + offset + cell_offset + len(cell)))
            for cell_offset, cell in _physical_table_cells_with_offsets(row)
        )
        rows.append(TableRow(row, SourceSpan(base + offset, base + offset + len(row)), cells))
        offset += len(physical)
    return tuple(rows)


def _is_compatibility_table(source: bytes) -> bool:
    """Recognize only paragraph-shaped tables with a matching physical schema."""
    rows = source.replace(b"\r\n", b"\n").splitlines()
    if len(rows) < 2:
        return False
    header = _physical_table_cells(rows[0])
    separator = _physical_table_cells(rows[1])
    return bool(header) and len(header) == len(separator) and all(
        re.fullmatch(rb":?-{3,}:?", cell.strip()) for cell in separator
    )


def _compatibility_table_inlines(source: bytes, base: int) -> list[InlineNode]:
    """Own cells of a bounded table shape when markdown-it omits table tokens."""
    result: list[InlineNode] = []
    offset = 0
    for row_with_ending in source.splitlines(keepends=True):
        row = row_with_ending.rstrip(b"\r\n")
        for cell_offset, cell in _physical_table_cells_with_offsets(row):
            nodes = _scan_inline(cell, base + offset + cell_offset)
            if not _reconstruct(nodes, cell):
                return []
            result.extend(nodes)
        offset += len(row_with_ending)
    return result


def _propagate_opaque(blocks: list[BlockNode]) -> bool:
    """Preserve a complete recognized container when a descendant is not owned."""
    has_opaque = False
    for block in blocks:
        descendant_opaque = _propagate_opaque(block.children)
        if block.opaque is not None or descendant_opaque:
            if block.opaque is None:
                block.opaque = OpaqueBlock(block.source, block.span)
            if descendant_opaque:
                block.metadata["unclosed_eof"] = any(
                    child.metadata.get("unclosed_eof") is True for child in block.children
                )
            has_opaque = True
    return has_opaque


def _walk(nodes: list[BlockNode]) -> Iterator[BlockNode]:
    for node in nodes:
        yield node
        yield from _walk(node.children)


def _scan_inline(source: bytes, base: int) -> list[InlineNode]:
    """Build inline ownership from markdown-it's semantic child-token stream.

    The old implementation attempted to implement delimiter matching a second time.  That is
    particularly dangerous for delimiter runs, because CommonMark's flanking rules are not a
    ``find the next closer`` operation.  The semantic token stream is authoritative; if its
    tokens cannot be mapped back to one exact source interval we return an empty result and the
    caller makes the containing block opaque.
    """
    # markdown-it treats a bare two-tick boundary as ordinary text, although
    # the formatter contract reserves it as the empty inline-code spelling.
    # Keep this compatibility case bounded to an all-tick source so ordinary
    # prose containing backticks is still authoritative parser output.
    if len(source) >= 2 and set(source) == {ord("`")}:
        return [InlineNode("code", source, span=SourceSpan(base, base + len(source)), metadata={"payload": b""})]
    semantic = _scan_inline_tokens(source, base)
    if semantic is not None:
        return semantic
    # A parser text token may omit insignificant cell-edge whitespace. It is
    # safe to retain that source only when no construct could be invented.
    if not any(marker in source for marker in (b"`", b"*", b"_", b"[", b"]", b"!", b"<", b"\\")):
        return [InlineNode("text", source, span=SourceSpan(base, base + len(source)))]
    return []


def _has_nested_link_label(source: bytes) -> bool:
    """Return whether a link label contains another link-like label."""
    for match in re.finditer(rb"\[", source):
        close = _label_end(source, match.end(), len(source))
        if close is None or source[close:close + 2] != b"](":
            continue
        nested = source[match.end():close]
        if b"](" in nested:
            return True
    return False


def _scan_inline_tokens(source: bytes, base: int) -> list[InlineNode] | None:
    """Associate markdown-it inline children with sequential, exact byte intervals."""
    try:
        text = source.decode("utf-8")
        tokens = next(token for token in MarkdownIt("commonmark").parse(text) if token.type == "inline").children or []
    except (UnicodeDecodeError, StopIteration):
        return None
    result: list[InlineNode] = []
    stack: list[tuple[InlineNode, int]] = []
    cursor = 0

    def add(node: InlineNode) -> None:
        (stack[-1][0].children if stack else result).append(node)

    for token in tokens:
        kind = {"em_open": "emphasis", "strong_open": "strong", "link_open": "link", "image": "image"}.get(token.type)
        if token.type in {"em_open", "strong_open", "link_open"}:
            marker = token.markup.encode()
            if token.type == "link_open":
                marker = b"<" if token.attrs and token.attrs.get("href") and source.startswith(b"<", cursor) else b"![" if token.attrs and token.attrs.get("src") else b"["
            if not source.startswith(marker, cursor) and not (token.type == "link_open" and source.startswith(b"[", cursor)):
                return None
            node = InlineNode(kind or "text", marker, [], SourceSpan(base + cursor, base + cursor + len(marker)), {})
            if token.type == "link_open" and marker == b"![":
                node.kind = "image"
            add(node)
            stack.append((node, cursor))
            cursor += len(marker)
            continue
        if token.type in {"em_close", "strong_close", "link_close"}:
            if not stack:
                return None
            node, start = stack.pop()
            marker = token.markup.encode() if token.type != "link_close" else b"]"
            if token.type == "link_close" and source[start:start + 1] == b"<":
                if not source.startswith(b">", cursor):
                    return None
                cursor += 1
                node.source = source[start:cursor]
                node.span = SourceSpan(base + start, base + cursor)
                continue
            if not source.startswith(marker, cursor):
                return None
            cursor += len(marker)
            if token.type == "link_close":
                if not source.startswith(b"(", cursor):
                    return None
                finish = _balanced_destination(source, cursor + 1, len(source))
                if finish is None:
                    return None
                cursor = finish
            node.source = source[start:cursor]
            node.span = SourceSpan(base + start, base + cursor)
            node.metadata["child_source"] = source[start + len(source[start:cursor].split(b"[", 1)[0]) : cursor - len(marker)] if node.kind in {"emphasis", "strong"} else b""
            if node.kind in {"emphasis", "strong"}:
                node.metadata["child_source"] = b"".join(child.source for child in node.children)
            continue
        if token.type == "code_inline":
            run = len(source[cursor:]) - len(source[cursor:].lstrip(b"`"))
            if not run:
                return None
            close = _code_span_close(source, cursor + run, len(source), run)
            if close < 0:
                return None
            end = close + run
            node = InlineNode("code", source[cursor:end], [], SourceSpan(base + cursor, base + end), {"payload": token.content.encode(), "payload_span": (cursor + run, close)})
            add(node)
            cursor = end
            continue
        if token.type == "softbreak":
            line_end = re.match(rb"\r\n|\n|\r", source[cursor:])
            if line_end is None:
                return None
            length = len(line_end.group())
            add(InlineNode("text", line_end.group(), [], SourceSpan(base + cursor, base + cursor + length), {}))
            cursor += length
            continue
        if token.type in {"text", "hardbreak", "escape", "autolink", "html_inline", "image"}:
            if token.type == "hardbreak":
                match = re.match(rb"(?:\\\r?\n| {2,}\r?\n)", source[cursor:])
                if not match:
                    return None
                length = len(match.group())
                add(InlineNode("hardbreak", match.group(), [], SourceSpan(base + cursor, base + cursor + length), {}))
                cursor += length
                continue
            if token.type == "image":
                if not source.startswith(b"![", cursor):
                    return None
                close = _label_end(source, cursor + 2, len(source))
                if close is None or not source.startswith(b"](", close):
                    return None
                finish = _balanced_destination(source, close + 2, len(source))
                if finish is None:
                    return None
                label = source[cursor + 2:close]
                children = [] if not label else _scan_inline_tokens(label, base + cursor + 2)
                if children is None:
                    return None
                add(InlineNode("image", source[cursor:finish], children,
                               SourceSpan(base + cursor, base + finish), {"child_source": label}))
                cursor = finish
                continue
            if token.type in {"text", "softbreak"} and not token.content:
                continue
            if token.type == "autolink":
                end = source.find(b">", cursor + 1)
                if cursor >= len(source) or source[cursor:cursor + 1] != b"<" or end < 0:
                    return None
                end += 1
            elif token.type == "text":
                autolink = re.match(rb"<(?:[A-Za-z][A-Za-z0-9+.-]*:[^ <>]+|[^ <>@]+@[^ <>@]+)>", source[cursor:])
                if autolink:
                    end = cursor + len(autolink.group())
                else:
                    end = _consume_semantic_text(source, cursor, token.content)
                    if end is None:
                        return None
            else:
                end = _consume_semantic_text(source, cursor, token.content)
                if end is None:
                    return None
            node = InlineNode("link" if token.type == "autolink" else "text", source[cursor:end], [], SourceSpan(base + cursor, base + end), {})
            add(node)
            cursor = end
            continue
    if stack:
        return None
    if cursor != len(source):
        trailing = source[cursor:]
        if not result or any(byte not in b" \t" for byte in trailing) or result[-1].kind != "text":
            return None
        result[-1].source += trailing
        if result[-1].span is not None:
            result[-1].span = SourceSpan(result[-1].span.start, result[-1].span.end + len(trailing))
        cursor = len(source)
    for node in _inline_walk(result):
        if node.kind in {"emphasis", "strong", "link", "image"} and not node.metadata.get("child_source"):
            node.metadata["child_source"] = b"".join(child.source for child in node.children)
    return result


def _consume_semantic_text(source: bytes, start: int, content: str) -> int | None:
    """Consume source bytes whose CommonMark text value equals ``content``."""
    if content == "":
        return start
    value: list[str] = []
    cursor = start
    while cursor < len(source) and "".join(value) != content:
        if (
            source[cursor:cursor + 1] == b"\\"
            and cursor + 1 < len(source)
            and source[cursor + 1:cursor + 2] in b"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        ):
            cursor += 1
        try:
            character = source[cursor:].decode("utf-8")[0]
        except (UnicodeDecodeError, IndexError):
            return None
        value.append(" " if character in "\r\n" else character)
        cursor += len(character.encode("utf-8"))
        if not content.startswith("".join(value)):
            return None
    return cursor if "".join(value) == content else None


def _code_span_close(source: bytes, begin: int, end: int, run: int) -> int:
    """Find a code-span closer whose tick run has exactly the opener length.

    A run of ticks cannot be reused as a shorter delimiter.  This small rule is
    the difference between the CommonMark `` `a``b` `` span and two invented
    spans, and keeps the source interval indivisible for later rendering.
    """
    marker = b"`" * run
    index = begin
    while index < end:
        close = source.find(marker, index, end)
        if close < 0:
            return -1
        before = close == 0 or source[close - 1:close] != b"`"
        after = close + run >= end or source[close + run:close + run + 1] != b"`"
        if before and after:
            return close
        index = close + 1
    return -1


def _balanced_destination(source: bytes, begin: int, end: int) -> int | None:
    """Find the closing parenthesis while ignoring quoted title content."""
    depth = 1
    index = begin
    quote: int | None = None
    while index < end:
        if source[index:index + 1] == b"\\":
            index += 2
            continue
        if quote is not None:
            if source[index] == quote:
                quote = None
            index += 1
            continue
        if source[index:index + 1] in {b"'", b'"'}:
            quote = source[index]
            index += 1
            continue
        if source[index:index + 1] == b"(":
            depth += 1
        elif source[index:index + 1] == b")":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _label_end(source: bytes, begin: int, end: int) -> int | None:
    """Find a balanced link-label close, respecting escaped brackets."""
    depth = 0
    index = begin
    while index < end:
        if source[index:index + 1] == b"\\":
            index += 2
            continue
        if source[index:index + 1] == b"[":
            depth += 1
        elif source[index:index + 1] == b"]":
            if depth == 0:
                return index
            depth -= 1
        index += 1
    return None


def _reconstruct(nodes: list[InlineNode], source: bytes) -> bool:
    if b"".join(node.source for node in nodes) != source:
        return False
    for current in nodes:
        if not current.children:
            continue
        child_source = current.metadata.get("child_source")
        if not isinstance(child_source, bytes):
            return False
        if not _reconstruct(current.children, child_source):
            return False
    return True


def _validate_h1(blocks: list[BlockNode]) -> None:
    headings = [block for block in blocks if block.kind.startswith("heading_")]
    if not blocks or blocks[0].kind != "heading_1" or sum(block.kind == "heading_1" for block in headings) != 1:
        raise StructureError("body must begin with exactly one top-level H1")


def _inline_walk(nodes: list[InlineNode]) -> Iterator[InlineNode]:
    """Yield inline nodes and their descendants in source order."""
    for node in nodes:
        yield node
        yield from _inline_walk(node.children)


def _validate_breaks(blocks: list[BlockNode]) -> None:
    """Validate source separators independently in each recognized container."""
    for index, block in enumerate(blocks):
        if block.kind == "thematic_break":
            next_heading = blocks[index + 1] if index + 1 < len(blocks) else None
            previous_heading = next((candidate for candidate in reversed(blocks[:index]) if candidate.kind.startswith("heading_")), None)
            if next_heading is None or not next_heading.kind.startswith("heading_") or previous_heading is None:
                raise UnsupportedSyntaxError("thematic break is only allowed before a downward heading")
            if int(next_heading.kind[-1]) <= int(previous_heading.kind[-1]):
                raise UnsupportedSyntaxError("thematic break is only allowed before a downward heading")
            block.metadata["heading_transition"] = True
        _validate_breaks(block.children)
