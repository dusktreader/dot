"""Test the public byte-oriented Markdown document pipeline."""

import pytest

from dot_tools.markdown_formatter import check_document, format_document
from dot_tools.markdown_formatter.parser import StructureError


def test_format_document_reassembles_frontmatter_and_is_idempotent() -> None:
    source = b'---\nz: true\na: "value"\n---\n\n# Title\n\ntext\n'
    expected = b'---\n"a": "value"\n"z": true\n---\n\n# Title\n\ntext\n'

    assert format_document(source) == expected
    assert format_document(expected) == expected
    assert check_document(source) == expected


def test_format_document_requires_utf8_and_accepts_embedded_html() -> None:
    with pytest.raises(UnicodeError):
        format_document(b"# title\n\xff")
    assert format_document(b"# title\n\n<div>bad</div>\n") == b"# title\n\n<div>bad</div>\n"


def test_format_document_preserves_opaque_source() -> None:
    source = b"# title\n\n\x00extension\r\ntrailing  \r\n"
    assert format_document(source) == source


def test_format_document_preserves_typed_structure_errors() -> None:
    with pytest.raises(StructureError):
        format_document(b"paragraph\n")


def test_empty_document_has_no_synthetic_body() -> None:
    with pytest.raises(StructureError):
        format_document(b"")
