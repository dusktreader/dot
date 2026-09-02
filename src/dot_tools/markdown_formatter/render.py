"""Markdown rendering contracts."""

from .normalize import NormalizedDocument


def render_document(document: NormalizedDocument) -> bytes:
    """Render normalized Markdown document bytes."""
    return document.source
