"""Generic, fail-closed Markdown formatting pipeline."""

from .models import FileResult, FileSnapshot, FileStatus, Operation, OperationResult, OperationStatus
from .frontmatter import extract_frontmatter
from .parser import parse_document
from .normalize import normalize_document
from .render import render_document


def format_document(source: bytes) -> bytes:
    """Format one Markdown document."""
    frontmatter, body = extract_frontmatter(source)
    rendered = render_document(normalize_document(parse_document(body)))
    if frontmatter is not None:
        from .frontmatter import serialize_frontmatter

        rendered = serialize_frontmatter(frontmatter) + rendered.lstrip(b"\n")
    if rendered and not rendered.endswith(b"\n"):
        rendered += b"\n"
    return rendered


def check_document(source: bytes) -> bytes:
    """Return the canonical bytes for one Markdown document."""
    return format_document(source)

__all__ = ["FileResult", "FileSnapshot", "FileStatus", "Operation", "OperationResult", "OperationStatus", "format_document", "check_document"]
