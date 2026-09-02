"""Markdown parser data contracts."""

from dataclasses import dataclass, field


class ParseError(Exception):
    """Report a Markdown parser failure."""


class RawHtmlError(ValueError):
    """Report raw HTML outside code."""


class StructureError(ValueError):
    """Report invalid document structure."""


class UnsupportedSyntaxError(ValueError):
    """Report unsupported syntax that cannot be safely normalized."""


class TableError(ValueError):
    """Report an invalid recognized table."""


@dataclass(frozen=True)
class SourceSpan:
    """Represent a byte interval in the source."""

    start: int
    end: int


@dataclass(frozen=True)
class CodePayload:
    """Represent code payload bytes and optional info string."""

    payload: bytes
    info: str = ""


@dataclass(frozen=True)
class OpaqueBlock:
    """Represent a parser-delimited source region preserved byte-for-byte."""

    source: bytes
    span: SourceSpan | None = None


@dataclass
class InlineNode:
    """Represent an inline AST node."""

    kind: str
    source: bytes = b""
    children: list["InlineNode"] = field(default_factory=list)
    span: SourceSpan | None = None


@dataclass
class BlockNode:
    """Represent a block AST node."""

    kind: str
    source: bytes = b""
    children: list["BlockNode"] = field(default_factory=list)
    inline: list[InlineNode] = field(default_factory=list)
    span: SourceSpan | None = None
    opaque: OpaqueBlock | None = None


@dataclass
class DocumentAst:
    """Represent the parsed Markdown document."""

    blocks: list[BlockNode] = field(default_factory=list)
    frontmatter: object | None = None
    body: bytes = b""


def parse_document(body: bytes) -> DocumentAst:
    """Parse a Markdown body into the formatter AST."""
    try:
        body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ParseError(str(error)) from error
    return DocumentAst(body=body)
