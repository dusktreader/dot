"""Normalization data contracts."""

from dataclasses import dataclass, field

from .parser import DocumentAst


@dataclass(frozen=True)
class HeadingSeparator:
    """Represent a canonical heading separator."""


@dataclass(frozen=True)
class NormalizedHeading:
    """Represent a normalized heading."""

    level: int
    content: bytes = b""


@dataclass(frozen=True)
class NormalizedList:
    """Represent a normalized list."""

    ordered: bool = False
    items: tuple[object, ...] = ()


@dataclass(frozen=True)
class NormalizedTable:
    """Represent a normalized table."""

    rows: tuple[tuple[bytes, ...], ...] = ()


@dataclass(frozen=True)
class NormalizedCode:
    """Represent a normalized code block."""

    payload: bytes = b""
    info: str = "text"


@dataclass
class NormalizedDocument:
    """Represent normalized document state."""

    source: bytes = b""
    blocks: list[object] = field(default_factory=list)


def normalize_document(document: DocumentAst) -> NormalizedDocument:
    """Normalize a parsed document."""
    return NormalizedDocument(source=document.body, blocks=list(document.blocks))
