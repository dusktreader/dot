"""Convert the parser tree into deterministic, renderable Markdown state."""

from dataclasses import dataclass, field
import re

from .parser import (
    BlockNode, CodePayload, DocumentAst, InlineNode, TableError, _backtick_run, _code_span_close, _exact_backtick_run,
    _scan_inline,
)


def _child_source(node: InlineNode, fallback: bytes) -> bytes:
    """Return the parser-proven source interval owned by an inline container."""
    value = node.metadata.get("child_source", fallback)
    return value if isinstance(value, bytes) else fallback


@dataclass(frozen=True)
class HeadingSeparator:
    """Represent a generated heading separator."""

    text: bytes = b"---\n"


@dataclass(frozen=True)
class NormalizedHeading:
    """Represent a heading and its canonical inline content."""

    level: int
    content: bytes = b""
    blank_lines_before: int = 1


@dataclass(frozen=True)
class NormalizedList:
    """Represent a normalized list source block."""

    ordered: bool = False
    items: tuple["NormalizedListItem", ...] = ()
    source: bytes = b""
    start: int = 1
    prefix: bytes = b""


@dataclass(frozen=True)
class NormalizedListItem:
    """Represent one list item with its canonical marker and content column."""

    marker: str
    content: bytes
    task: bool | None = None
    continuation_column: int = 0
    nested: tuple["NormalizedList", ...] = ()
    continuation: tuple[bytes, ...] = ()
    children: tuple[object, ...] = ()
    structural_column: int = 0


@dataclass(frozen=True)
class NormalizedTable:
    """Represent table rows and alignment markers."""

    rows: tuple[tuple[bytes, ...], ...] = ()
    alignments: tuple[str, ...] = ()
    widths: tuple[int, ...] = ()


@dataclass(frozen=True)
class NormalizedCode:
    """Represent code payload and info string."""

    payload: bytes = b""
    info: str = "text"
    fence: str = "```"


@dataclass(frozen=True)
class NormalizedParagraph:
    """Represent a secondary paragraph rendered at its structural child column."""

    content: bytes


@dataclass(frozen=True)
class NormalizedOpaque:
    """Represent source which must not be normalized."""

    source: bytes
    preserve_eof: bool = False


@dataclass(frozen=True)
class NormalizedContainer:
    """Represent a recursively normalized container with its active prefix."""

    blocks: tuple[object, ...]
    prefix: bytes = b""


@dataclass
class NormalizedDocument:
    """Represent normalized document state."""

    source: bytes = b""
    blocks: list[object] = field(default_factory=list)


def _inline(source: bytes, nodes: list[InlineNode] | None = None, delimiter: bytes | None = None) -> bytes:
    """Encode owned inline nodes while retaining ordinary text and safe punctuation."""
    if nodes is None:
        return source.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    result: list[bytes] = []
    previous_atom_delimiter: bytes | None = None
    for index, node in enumerate(nodes):
        if node.kind == "code":
            result.append(_inline_code(node))
        elif node.kind == "emphasis":
            if _has_nested_delimiter(node):
                result.append(_canonical_lf(node.source))
                continue
            marker = _next_atom_delimiter(previous_atom_delimiter)
            result.append(marker + _inline(_child_source(node, b""), node.children, marker) + marker)
            previous_atom_delimiter = marker
        elif node.kind == "strong":
            if _has_nested_delimiter(node):
                result.append(_canonical_lf(node.source))
                continue
            marker = _next_atom_delimiter(previous_atom_delimiter) * 2
            result.append(marker + _inline(_child_source(node, b""), node.children, marker[:1]) + marker)
            previous_atom_delimiter = marker[:1]
        elif node.kind == "hardbreak":
            result.append(b"\\\n")
        elif node.kind in {"link", "image"}:
            opener = b"![" if node.kind == "image" else b"["
            child_source = _child_source(node, b"")
            label_end = len(opener) + len(child_source)
            if not isinstance(node.metadata.get("child_source"), bytes) or node.source[label_end:label_end + 2] != b"](":
                result.append(node.source)
            else:
                label = _inline(child_source, node.children, delimiter)
                result.append(opener + label + b"](" + _canonical_link_tail(node.source[label_end + 2:]))
        elif node.kind == "text":
            value = node.source.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            if delimiter is not None:
                result.append(_encode_semantic_text(value, {delimiter.decode()}))
                continue
            result.append(_encode_text_node(value, nodes[index - 1] if index else None,
                                             nodes[index + 1] if index + 1 < len(nodes) else None))
        else:
            result.append(_inline(node.source, node.children or None))
    encoded = b"".join(result)
    if nodes is not None and delimiter is None and not _inline_shape_matches(encoded, nodes):
        # Delimiter choice is a CommonMark flanking decision, not a property of
        # the preceding atom alone. If the generated stream changes that
        # decision, retain the proven source rather than changing the AST.
        return b"".join(node.source for node in nodes).replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return encoded


def _inline_shape_matches(source: bytes, nodes: list[InlineNode]) -> bool:
    """Return whether canonical bytes reparse to the same complete inline shape."""
    reparsed = _scan_inline(source, 0)

    def shape(values: list[InlineNode]) -> tuple[tuple[str, tuple], ...]:
        return tuple((value.kind, shape(value.children)) for value in values)

    return shape(reparsed) == shape(nodes)


def _encode_text_node(value: bytes, previous: InlineNode | None, following: InlineNode | None) -> bytes:
    """Encode text without allowing a neighboring canonical atom to change its meaning."""
    neighbors = {previous.kind if previous else "", following.kind if following else ""}
    return _encode_semantic_text(value, neighbors & {"emphasis", "strong", "code"})


def _has_nested_delimiter(node: InlineNode) -> bool:
    """Return whether an inline node contains nested emphasis or strong syntax."""
    return any(child.kind in {"emphasis", "strong"} or _has_nested_delimiter(child) for child in node.children)


def _decode_text(value: bytes) -> list[tuple[int, bool]]:
    """Decode complete source backslash runs and retain escaped-byte provenance."""
    punctuation = b'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    semantic: list[tuple[int, bool]] = []
    index = 0
    while index < len(value):
        if value[index:index + 1] != b"\\":
            semantic.append((value[index], False))
            index += 1
            continue
        end = index
        while end < len(value) and value[end:end + 1] == b"\\":
            end += 1
        count = end - index
        if end < len(value) and value[end] in punctuation:
            semantic.extend((ord("\\"), False) for _ in range(count // 2))
            if count % 2:
                semantic.append((value[end], True))
                end += 1
        else:
            semantic.extend((ord("\\"), False) for _ in range((count + 1) // 2))
        index = end
    return semantic


def _encode_semantic_text(value: bytes, protected: set[str], table: bool = False) -> bytes:
    """Encode semantic text with canonical backslashes and delimiter protection."""
    result = bytearray()
    for byte, was_escaped in _decode_text(value):
        if byte == ord("\\"):
            result.extend(b"\\\\")
        elif (was_escaped or (byte == ord("*") and protected & {"*", "emphasis", "strong"})
              or (byte == ord("_") and protected & {"_", "emphasis", "strong"})
              or (byte == ord("`") and "code" in protected) or (table and byte == ord("|"))):
            result.extend(b"\\" + bytes((byte,)))
        else:
            result.append(byte)
    return bytes(result)


def _next_atom_delimiter(previous: bytes | None) -> bytes:
    """Choose a delimiter that cannot merge with the immediately preceding atom."""
    return b"_" if previous == b"*" else b"*"


def _inline_code(node: InlineNode) -> bytes:
    """Encode an inline code node with its semantic payload."""
    semantic_payload = node.metadata.get("payload")
    has_semantic_payload = isinstance(semantic_payload, bytes)
    if isinstance(semantic_payload, bytes):
        payload = semantic_payload
    else:
        opening = len(node.source) - len(node.source.lstrip(b"`"))
        payload = node.source[opening:-opening] if opening else node.source
    payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", b" ")
    if not has_semantic_payload and len(payload) >= 2 and payload[:1] == payload[-1:] == b" " and payload.strip(b" "):
        payload = payload[1:-1]
    run = max((len(match) for match in re.findall(rb"`+", payload)), default=0) + 1
    fence = b"`" * max(3, run)
    padding = b" " if payload.startswith(b"`") or payload.endswith(b"`") else b""
    if has_semantic_payload and payload[:1] == payload[-1:] == b" " and payload.strip(b" "):
        padding = b" "
    return fence + padding + payload + padding + fence


def _canonical_link_tail(tail: bytes) -> bytes:
    """Canonicalize a link destination and title while retaining its semantics."""
    tail = _canonical_lf(tail)
    if not tail.endswith(b")"):
        return tail
    inner = tail[:-1].strip()
    if inner.startswith(b"<"):
        close = inner.find(b">")
        if close < 0:
            return tail
        destination, title = inner[1:close], inner[close + 1:].strip()
    else:
        # A destination may contain balanced parentheses and escaped bytes.  Do
        # not use a regular expression here: it cannot distinguish a title from
        # a parenthesized destination.
        destination_end = 0
        depth = 0
        while destination_end < len(inner):
            byte = inner[destination_end:destination_end + 1]
            if byte == b"\\":
                destination_end += 2
                continue
            if byte == b"(":
                depth += 1
            elif byte == b")":
                if depth == 0:
                    break
                depth -= 1
            elif byte in {b" ", b"\t", b"\n"} and depth == 0:
                break
            destination_end += 1
        if depth:
            return tail
        destination, title = inner[:destination_end], inner[destination_end:].strip()
        if not destination and title:
            return tail
    destination = _decode_destination(destination)
    if title:
        if title[:1] not in {b'"', b"'"} or title[-1:] != title[:1]:
            return tail
        title = b'"' + _decode_link_quoted_text(title[1:-1]).replace(b"\\", b"\\\\").replace(b'"', b'\\"') + b'"'
    if (not destination or any(byte in destination for byte in b" \t\n<>\\") or _unbalanced_parentheses(destination)):
        destination = b"<" + destination.replace(b"\\", b"\\\\").replace(b"<", b"\\<").replace(b">", b"\\>") + b">"
    return destination + (b" " + title if title else b"") + b")"


def _decode_link_quoted_text(value: bytes) -> bytes:
    """Decode one parser-owned link title escape layer."""
    punctuation = b'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    result = bytearray()
    index = 0
    while index < len(value):
        if value[index:index + 1] == b"\\" and index + 1 < len(value) and value[index + 1] in punctuation:
            result.append(value[index + 1])
            index += 2
        else:
            result.append(value[index])
            index += 1
    return bytes(result)


def _canonical_lf(value: bytes) -> bytes:
    """Normalize line endings in recognized Markdown source."""
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _decode_destination(value: bytes) -> bytes:
    """Decode source escapes before choosing the canonical destination form."""
    result = bytearray()
    index = 0
    punctuation = b"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    while index < len(value):
        if value[index:index + 1] == b"\\" and index + 1 < len(value) and value[index + 1] in punctuation:
            result.append(value[index + 1])
            index += 2
        else:
            result.append(value[index])
            index += 1
    return bytes(result)


def _unbalanced_parentheses(value: bytes) -> bool:
    """Return whether a decoded destination contains unbalanced parentheses."""
    depth = 0
    for byte in value:
        if byte == ord("("):
            depth += 1
        elif byte == ord(")"):
            depth -= 1
            if depth < 0:
                return True
    return depth != 0


def _list(block: BlockNode, prefix: bytes = b"") -> NormalizedList:
    """Normalize a parser-owned list recursively, retaining item and container structure."""
    ordered = block.kind == "ordered_list"
    raw_start = block.metadata.get("start", 1)
    start = int(raw_start) if isinstance(raw_start, int) else 1
    if ordered and block.source:
        marker_source = _list_paragraph_source(block.source)
        match = re.match(rb"(\d+)[.)]", marker_source)
        start = int(match.group(1)) if match else start
    items: list[NormalizedListItem] = []
    list_items = [child for child in block.children if child.kind == "list_item"]
    for index, item in enumerate(list_items):
        marker = (str(start + index) + ".") if ordered else "-"
        paragraph = item.children[0] if item.children and item.children[0].kind == "paragraph" else None
        if paragraph and paragraph.inline:
            paragraph_source = _list_paragraph_source(paragraph.source)
            paragraph_nodes = paragraph.inline
            paragraph_value = _inline(paragraph_source, paragraph_nodes).rstrip(b" \t")
        elif paragraph:
            paragraph_source = _list_paragraph_source(paragraph.source)
            paragraph_nodes = _scan_inline(paragraph_source, 0)
            paragraph_value = _inline(paragraph_source, paragraph_nodes).rstrip(b" \t")
        else:
            paragraph_source = b""
            paragraph_nodes = []
            paragraph_value = b""
        paragraph_lines = _wrap_inline(paragraph_nodes, paragraph_value) if paragraph else [b""]
        source_lines = paragraph_source.split(b"\n") if paragraph_source else []
        has_hard_break = any(node.kind == "hardbreak" for node in paragraph_nodes)
        if paragraph and len(source_lines) > 1 and not has_hard_break:
            # A lazy continuation is still a distinct physical list line. Keep
            # that structure instead of collapsing it into prose and changing
            # the item's source shape on the next parse.
            first_source = re.sub(
                rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?",
                b"",
                source_lines[0],
                count=1,
            )
            first = _inline(first_source, _scan_inline(first_source, 0))
            continuation_lines: list[bytes] = []
            for line in source_lines[1:]:
                line = line.strip(b" \t")
                if not line:
                    continue
                line_nodes = _scan_inline(line, 0)
                if not line_nodes:
                    # A standalone rescanning pass can reinterpret a lazy
                    # continuation as a new list.  Its ownership is no longer
                    # provable, so preserve the complete list block rather
                    # than silently replacing nonempty source with an empty
                    # continuation.
                    return NormalizedList(ordered, (), block.source, start, prefix)
                continuation_lines.extend(_wrap_inline(line_nodes, _inline(line, line_nodes)))
            paragraph_lines = [first, *continuation_lines]
        elif has_hard_break:
            # `_wrap_inline` keeps each hard break in the encoded stream. Split
            # its rendered newline into physical list lines without replacing
            # the canonical backslash-plus-LF marker with source whitespace.
            paragraph_lines = [part for line in paragraph_lines for part in line.split(b"\n")]
        content = paragraph_lines[0] if paragraph_lines else b""
        raw_task = item.metadata.get("task")
        task = raw_task if isinstance(raw_task, bool) else None
        task_prefix = b"[x] " if task is True else b"[ ] " if task is False else b""
        if task is not None and (content.startswith(b"[x] ") or content.startswith(b"[ ] ")):
            content = content[4:]
        continuation_lines = [line.lstrip(b" \t") for line in paragraph_lines[1:]]
        nested_children: list[object] = []
        heading_state = [0, False, False]
        for child in item.children:
            if child is paragraph:
                continue
            normalized_child = _list_child_without_marker(child)
            if child.kind in {"bullet_list", "ordered_list"}:
                nested_children.append(_list(normalized_child, prefix + b" " * (len(marker.encode()) + 1)))
                continue
            if child.kind == "paragraph":
                child_source = _list_paragraph_source(normalized_child.source)
                child_nodes = _scan_inline(child_source, 0)
                child_content = _inline(child_source, child_nodes).rstrip(b" \t")
                normalized = [NormalizedParagraph(b"\n".join(_wrap_inline(child_nodes, child_content)))]
            else:
                normalized = _normalize_blocks(
                    [normalized_child],
                    b" " * (len(marker.encode()) + 1 + len(task_prefix)),
                    heading_state,
                )
            nested_children.extend(normalized)
        column = len(marker.encode()) + 1 + len(task_prefix)
        structural_column = len(marker.encode()) + 1
        items.append(NormalizedListItem(marker, task_prefix + content, task, column, (), tuple(continuation_lines),
                                        tuple(nested_children), structural_column))
    return NormalizedList(ordered, tuple(items), b"", start, prefix)


def _list_paragraph_source(source: bytes) -> bytes:
    """Remove structural prefixes while retaining hard and soft line breaks."""
    lines = source.replace(b"\r\n", b"\n").replace(b"\r", b"\n").splitlines(keepends=True)
    if not lines:
        return b""
    lines[0] = re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", lines[0], count=1)
    while re.match(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", lines[0]):
        lines[0] = re.sub(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?", b"", lines[0], count=1)
    lines[0] = lines[0].lstrip(b" \t")
    while re.match(rb"(?:[-+*]|\d+[.)])[ \t]+", lines[0]):
        lines[0] = re.sub(rb"^(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?", b"", lines[0], count=1)
    for index in range(1, len(lines)):
        lines[index] = re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", lines[index], count=1).lstrip(b" \t")
    return b"".join(lines).rstrip(b"\n")


def _list_child_without_marker(child: BlockNode) -> BlockNode:
    """Remove an item's marker before normalizing its first block child."""
    lines = child.source.splitlines(keepends=True)
    if lines:
        lines = [_strip_container_prefix(line) for line in lines]
        while re.match(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", lines[0]):
            lines[0] = re.sub(rb"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+(?:\[[ xX]\][ \t]+)?", b"", lines[0], count=1)
        if child.kind in {"fence", "code_block"}:
            lines[1:] = [line[2:] if line.startswith(b"  ") else line for line in lines[1:]]
    descendants = [_list_child_without_marker(descendant) for descendant in child.children]
    clone = BlockNode(child.kind, b"".join(lines), descendants, list(child.inline), child.span, child.opaque,
                      dict(child.metadata))
    if child.kind in {"fence", "code_block"}:
        code = clone.metadata.get("code")
        if isinstance(code, CodePayload):
            payload = b"".join(
                line[2:] if line.startswith(b"  ") else line
                for line in code.payload.splitlines(keepends=True)
            )
            clone.metadata["code"] = CodePayload(payload, code.info, code.marker_span, code.info_span, code.payload_span)
    if child.kind.startswith("heading_"):
        heading = clone.source.splitlines()[0]
        content = re.sub(rb"^[ \t>]*#{1,6}[ \t]+", b"", heading)
        clone.inline = _scan_inline(content, 0)
    elif child.kind == "paragraph":
        content = _list_paragraph_source(clone.source)
        clone.inline = _scan_inline(content, 0)
    return clone


def _strip_container_prefix(line: bytes) -> bytes:
    """Remove all block-quote prefixes from one physical line."""
    return re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", line)


def _remove_visual_indent(line: bytes, columns: int) -> bytes:
    """Remove proven visual indentation while preserving all remaining bytes."""
    index = 0
    used = 0
    while index < len(line) and used < columns and line[index:index + 1] in {b" ", b"\t"}:
        used += 1 if line[index:index + 1] == b" " else 4 - used % 4
        index += 1
    return line[index:]


def _split_row(line: bytes) -> list[bytes]:
    """Split a table row, honoring backslash parity and code-span pipes."""
    line = line.strip(b" ")
    if line.startswith(b"|"):
        line = line[1:]
    if line.endswith(b"|"):
        backslashes = 0
        probe = len(line) - 2
        while probe >= 0 and line[probe:probe + 1] == b"\\":
            backslashes += 1
            probe -= 1
        if backslashes % 2 == 0:
            line = line[:-1]
    cells: list[bytes] = []
    begin = 0
    ticks = 0
    index = 0
    while index < len(line):
        if line[index:index + 1] == b"`":
            run = _backtick_run(line, index) if ticks else _exact_backtick_run(line, index)
            if not run:
                index += 1
                continue
            if ticks:
                if run == ticks:
                    ticks = 0
            elif _code_span_close(line, index + run, len(line), run) >= 0:
                ticks = run
            index += run
            continue
        if line[index:index + 1] == b"|" and not ticks:
            backslashes = 0
            probe = index - 1
            while probe >= 0 and line[probe:probe + 1] == b"\\":
                backslashes += 1
                probe -= 1
            if backslashes % 2 == 0:
                cells.append(line[begin:index].strip(b" "))
                begin = index + 1
        index += 1
    cells.append(line[begin:].strip(b" "))
    return cells


def _table(source: bytes) -> NormalizedTable:
    """Normalize a parser-owned table and validate its rectangular schema."""
    raw_rows = source.replace(b"\r\n", b"\n").splitlines()
    if any(_is_zero_cell_row(row) for row in raw_rows):
        raise TableError("table row has zero cells")
    rows = [_split_row(row) for row in raw_rows]
    if len(rows) < 2 or not rows[0] or not rows[1] or len(rows[1]) != len(rows[0]):
        raise TableError("table separator has the wrong number of cells")
    if any(len(row) > len(rows[0]) for row in rows[2:]):
        raise TableError("table row has too many cells")
    alignments = []
    for marker in rows[1]:
        left, right = marker.startswith(b":"), marker.endswith(b":")
        alignments.append("center" if left and right else "left" if left else "right" if right else "none")
    content_rows = [rows[0], *rows[2:]]
    content_rows = [[_canonical_cell(cell) for cell in row] for row in content_rows]
    normalized = tuple(tuple(cell for cell in row + [b""] * (len(rows[0]) - len(row))) for row in content_rows)
    widths = tuple(
        max(3 + (2 if alignment == "center" else 1 if alignment in {"left", "right"} else 0),
            *(len(cell.decode("utf-8")) for cell in column))
        for column, alignment in zip(zip(*normalized), alignments, strict=True)
    )
    return NormalizedTable(normalized, tuple(alignments), widths)


def _canonical_cell(cell: bytes) -> bytes:
    """Render a table cell's inline syntax without treating code pipes as framing."""
    return _table_inline(cell, _scan_inline(cell, 0)).strip(b" ")


def _is_zero_cell_row(row: bytes) -> bool:
    """Identify framing-only rows rather than treating them as empty cells."""
    stripped = row.strip(b" ")
    return bool(stripped) and stripped == b"|" * stripped.count(b"|")


def _table_inline(source: bytes, nodes: list[InlineNode], delimiter: bytes | None = None) -> bytes:
    """Encode table inline nodes while retaining semantic backslashes before pipes."""
    result: list[bytes] = []
    previous_atom_delimiter: bytes | None = None
    for index, node in enumerate(nodes):
        if node.kind == "text":
            value = node.source.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            protected = ({delimiter.decode()} if delimiter else set()) | {
                nodes[index - 1].kind if index else "", nodes[index + 1].kind
                if index + 1 < len(nodes) else "",
            }
            result.append(_encode_semantic_text(value, protected, table=True))
        elif node.kind == "code":
            result.append(_inline_code(node))
        elif node.kind == "emphasis":
            if _has_nested_delimiter(node):
                result.append(_canonical_lf(node.source))
            else:
                marker = _next_atom_delimiter(previous_atom_delimiter)
                result.append(marker + _table_inline(_child_source(node, b""), node.children, marker) + marker)
                previous_atom_delimiter = marker
        elif node.kind == "strong":
            if _has_nested_delimiter(node):
                result.append(_canonical_lf(node.source))
            else:
                marker = _next_atom_delimiter(previous_atom_delimiter) * 2
                result.append(marker + _table_inline(_child_source(node, b""), node.children, marker[:1]) + marker)
                previous_atom_delimiter = marker[:1]
        else:
            result.append(_inline(node.source, [node], delimiter))
    encoded = b"".join(result)
    if not _table_inline_shape_matches(encoded, nodes):
        return b"".join(node.source for node in nodes).replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return encoded


def _table_inline_shape_matches(source: bytes, nodes: list[InlineNode]) -> bool:
    """Return whether canonical table-cell bytes retain the complete inline shape."""
    reparsed = _scan_inline(source, 0)

    def shape(values: list[InlineNode]) -> tuple[tuple[str, tuple], ...]:
        return tuple((value.kind, shape(value.children)) for value in values)

    return shape(reparsed) == shape(nodes)


def _normalize_blocks(
    blocks: list[BlockNode], prefix: bytes = b"", heading_state: list[int | bool] | None = None,
) -> list[object]:
    """Normalize a block sequence with heading state local to that container."""
    output: list[object] = []
    state = heading_state if heading_state is not None else [0, False, False]
    previous_heading = int(state[0])
    preceding_body = bool(state[1])
    for index, block in enumerate(blocks):
        if block.kind == "thematic_break" and block.metadata.get("heading_transition"):
            continue
        if block.opaque is not None:
            output.append(NormalizedOpaque(block.opaque.source, block.metadata.get("unclosed_eof") is True))
            preceding_body = True
            continue
        if block.kind.startswith("heading_"):
            level = int(block.kind.rsplit("_", 1)[1])
            heading_source = block.source.splitlines()[0]
            content_source = re.sub(rb"^[ \t>]*(?:[-+*]|\d+[.)])[ \t]+", b"", heading_source)
            content_source = re.sub(rb"^[ \t>]*#{1,6}[ \t]+", b"", content_source)
            if re.fullmatch(rb"[ \t>]*#{1,6}[ \t]*", block.source.splitlines()[0].rstrip(b"\r\n")):
                content_source = b""
            content = (_inline(b"", block.inline) if block.inline else _inline(content_source.rstrip(b" \t"))).rstrip(b" \t")
            if previous_heading and level > previous_heading and (preceding_body or bool(state[2])):
                output.append(HeadingSeparator())
            blank_lines = 1 if not previous_heading or (level > previous_heading and not preceding_body) else 2
            output.append(NormalizedHeading(level, content, blank_lines))
            previous_heading = level
            preceding_body = False
            state[:] = [previous_heading, preceding_body, True]
        elif block.kind in {"fence", "code_block"}:
            lines = block.source.splitlines(keepends=True)
            lines = [_strip_quote_prefix(line) for line in lines]
            payload = block.source
            info = "text"
            fence = "```"
            if block.kind == "fence" and lines:
                # The opening line establishes the one physical indentation
                # removed by CommonMark for this fence.  Deriving it after
                # removing quote markers keeps list and quote prefixes out of
                # the payload without treating payload spaces as structure.
                opening_indent = len(lines[0]) - len(lines[0].lstrip(b" 	"))
                lines = [_strip_indent(line, opening_indent) for line in lines]
                code = block.metadata.get("code")
                info = code.info if isinstance(code, CodePayload) else "text"
                if isinstance(code, CodePayload):
                    payload = code.payload
                    marker_byte = "`"
                    marker_pattern = marker_byte.encode() + b"+"
                    longest = max((len(run) for run in re.findall(marker_pattern, payload)), default=0)
                    fence = marker_byte * max(3, longest + 1)
                    if marker_byte == "`" and "`" in info:
                        tilde_longest = max((len(run) for run in re.findall(rb"~+", payload)), default=0)
                        fence = "~" * max(3, tilde_longest + 1)
                    if not info:
                        info = "text"
                    if info in {"bash", "sh"}:
                        info = "shell"
                    output.append(NormalizedCode(payload, info, fence))
                    preceding_body = True
                    continue
                closing = len(lines) > 1 and re.match(rb"[ \t]*([`~])\1{2,}[ \t]*\r?\n?$", lines[-1]) is not None
                payload = b"".join(lines[1:-1] if closing else lines[1:])
                longest = max((len(run) for run in re.findall(rb"`+", payload)), default=0)
                fence = "`" * max(3, longest + 1)
                if "`" in info:
                    tilde_longest = max((len(run) for run in re.findall(rb"~+", payload)), default=0)
                    fence = "~" * max(3, tilde_longest + 1)
                if not info:
                    info = "text"
            elif block.kind == "code_block":
                payload = b"".join(_remove_visual_indent(line, 4) for line in lines)
            if info in {"bash", "sh"}:
                info = "shell"
            output.append(NormalizedCode(payload, info, fence))
            preceding_body = True
            state[1] = True
        elif block.kind == "table":
            output.append(_table(block.source))
            preceding_body = True
            state[1] = True
        elif block.kind in {"bullet_list", "ordered_list"}:
            normalized_list = _list(block, prefix)
            if not normalized_list.items and normalized_list.source:
                output.append(NormalizedOpaque(normalized_list.source))
            else:
                output.append(normalized_list)
            preceding_body = True
            state[1] = True
        elif block.kind == "blockquote":
            container_prefix = prefix + b"> "
            output.append(NormalizedContainer(tuple(_normalize_blocks(block.children, container_prefix)),
                                               prefix=b"> "))
            preceding_body = True
            state[1] = True
        elif block.kind == "paragraph":
            source = _canonical_lf(block.source).rstrip(b"\n")
            source = b"\n".join(_strip_container_prefix(line) for line in source.split(b"\n"))
            encoded = _inline(source, block.inline) if block.inline else _inline(source)
            output.append(b"\n".join(_wrap_inline(block.inline, encoded.rstrip(b" \t"))))
            preceding_body = True
            state[1] = True
        elif block.kind == "thematic_break":
            output.append(NormalizedOpaque(block.source))
            preceding_body = True
            state[1] = True
    return output


def normalize_document(document: DocumentAst) -> NormalizedDocument:
    """Normalize owned blocks while preserving opaque parser-delimited regions."""
    return NormalizedDocument(document.body, _normalize_blocks(document.blocks))


def _wrap_inline(nodes: list[InlineNode], encoded: bytes) -> list[bytes]:
    """Wrap prose without splitting an owned inline construct."""
    if b"\n" in encoded:
        groups: list[list[InlineNode]] = [[]]
        for node in nodes:
            if node.kind == "hardbreak":
                groups.append([])
            else:
                groups[-1].append(node)
        result: list[bytes] = []
        for index, group in enumerate(groups):
            segment = _inline(b"".join(node.source for node in group), group).rstrip(b" \t")
            wrapped = _wrap_inline_tokens(group, segment)
            if index and result and wrapped:
                result[-1] += b"\\\n" + wrapped[0]
                result.extend(wrapped[1:])
            else:
                result.extend(wrapped)
        return result
    return _wrap_inline_tokens(nodes, encoded)


def _wrap_inline_tokens(nodes: list[InlineNode], encoded: bytes) -> list[bytes]:
    """Wrap one hard-break-free inline segment."""
    if len(encoded.decode("utf-8")) <= 120:
        return [encoded]
    atoms: list[tuple[str, bool]] = []
    previous_atom_delimiter: bytes | None = None
    for index, node in enumerate(nodes):
        if node.kind == "emphasis" and not _has_nested_delimiter(node):
            marker = _next_atom_delimiter(previous_atom_delimiter)
            value = marker + _inline(_child_source(node, b""), node.children, marker) + marker
            previous_atom_delimiter = marker
        elif node.kind == "strong" and not _has_nested_delimiter(node):
            marker = _next_atom_delimiter(previous_atom_delimiter) * 2
            value = marker + _inline(_child_source(node, b""), node.children, marker[:1]) + marker
            previous_atom_delimiter = marker[:1]
        else:
            value = (_encode_text_node(
                node.source.replace(b"\r\n", b"\n").replace(b"\r", b"\n"),
                nodes[index - 1] if index else None,
                nodes[index + 1] if index + 1 < len(nodes) else None,
            ) if node.kind == "text" else _inline(node.source, [node]))
        if node.kind == "text":
            parts = re.split(r"(\s+)", value.decode("utf-8"))
            atoms.extend((part, bool(part and part.isspace())) for part in parts if part)
        else:
            atoms.append((value.decode("utf-8"), False))
    lines: list[str] = []
    current = ""
    pending_space = ""
    for atom, is_space in atoms:
        if is_space:
            pending_space += atom
            continue
        candidate = current + pending_space + atom
        if current and len(candidate) > 120 and pending_space:
            lines.append(current)
            current = atom
        else:
            current = candidate
        pending_space = ""
    if current:
        lines.append(current)
    return [line.encode("utf-8") for line in lines] or [encoded]


def _strip_indent(line: bytes, width: int) -> bytes:
    """Remove up to the fence's structural indentation from one source line."""
    index = 0
    while index < len(line) and index < width and line[index:index + 1] in {b" ", b"\t"}:
        index += 1
    return line[index:]


def _strip_quote_prefix(line: bytes) -> bytes:
    """Remove every block-quote marker before normalizing nested code content."""
    return re.sub(rb"^(?:[ \t]*>[ \t]?)+", b"", line)
