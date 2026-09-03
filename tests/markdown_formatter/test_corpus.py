"""Exercise the generic formatter against representative whole-document corpora."""

from pathlib import Path

import pytest

from dot_tools.markdown_formatter import format_document
from dot_tools.markdown_formatter.models import FileStatus, OperationStatus
from dot_tools.markdown_formatter.operations import check_paths, format_paths
from dot_tools.markdown_formatter.parser import StructureError, UnsupportedSyntaxError


CORPUS = Path(__file__).parent / "fixtures" / "corpus"


def _fixture(name: str) -> tuple[bytes, bytes]:
    """Read an input and its exact canonical companion."""
    return ((CORPUS / f"{name}.md").read_bytes(), (CORPUS / f"{name}.expected.md").read_bytes())


@pytest.mark.parametrize("name", ["frontmatter", "boundaries", "headings", "lists", "tables", "code", "opaque"])
def test_generic_corpus_has_exact_canonical_bytes_and_is_idempotent(name: str) -> None:
    source, expected = _fixture(name)

    actual = format_document(source)

    assert actual == expected
    assert format_document(actual) == expected


def test_prose_wraps_without_altering_unicode_or_unbreakable_tokens() -> None:
    source, expected = _fixture("prose")

    assert format_document(source) == expected


def test_raw_html_is_accepted_even_when_surrounded_by_owned_markdown() -> None:
    source = (CORPUS / "raw-html.md").read_bytes()
    assert format_document(source) == source + (b"\n" if not source.endswith(b"\n") else b"")


def test_h1_scope_rejects_a_body_without_a_top_level_h1() -> None:
    with pytest.raises(StructureError):
        format_document((CORPUS / "invalid-h1.md").read_bytes())


def test_source_breaks_are_rejected_outside_downward_heading_transitions() -> None:
    with pytest.raises(UnsupportedSyntaxError):
        format_document((CORPUS / "invalid-break.md").read_bytes())


def test_multi_file_format_preflights_every_document_before_writing(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_bytes((CORPUS / "headings.md").read_bytes())
    bad.write_bytes((CORPUS / "invalid-h1.md").read_bytes())

    result = format_paths([good, bad])

    assert result.status is OperationStatus.INPUT_ERROR
    assert result.committed == ()
    assert result.files[0].status is FileStatus.INPUT_ERROR
    assert good.read_bytes() == (CORPUS / "headings.md").read_bytes()


def test_multi_file_check_reports_only_mismatching_files(tmp_path: Path) -> None:
    canonical = tmp_path / "canonical.md"
    mismatch = tmp_path / "mismatch.md"
    canonical.write_bytes((CORPUS / "frontmatter.expected.md").read_bytes())
    mismatch.write_bytes((CORPUS / "frontmatter.md").read_bytes())

    result = check_paths([tmp_path])

    assert result.status is OperationStatus.MISMATCH
    assert [item.status for item in result.files] == [FileStatus.UNCHANGED, FileStatus.MISMATCH]
    assert len(result.diagnostics) == 1
    assert "SHA-256" in result.diagnostics[0]
