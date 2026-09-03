"""Test the restricted YAML frontmatter envelope."""

from pathlib import Path

import pytest

from dot_tools.markdown_formatter.frontmatter import (
    FrontmatterError,
    extract_frontmatter,
    serialize_frontmatter,
    validate_frontmatter,
)


FIXTURES = Path(__file__).parent / "fixtures" / "frontmatter"


def test_extracts_mapping_and_preserves_body_bytes() -> None:
    source = (FIXTURES / "valid.md").read_bytes()

    value, body = extract_frontmatter(source)

    assert value == {"active": True, "nested": {"items": [None, 2]}, "title": "quoted: value"}
    assert body == b"# Title\r\n\r\nBody\n"


def test_body_delimiters_do_not_create_multiple_yaml_documents() -> None:
    source = b"---\na: 1\n---\n# T\n\n---\n\n```text\n---\n---\n```\n"
    value, body = extract_frontmatter(source)
    assert value == {"a": 1}
    assert body == b"# T\n\n---\n\n```text\n---\n---\n```\n"


def test_fenced_delimiters_after_frontmatter_remain_body_material() -> None:
    source = b"---\na: 1\n---\n# T\n\n```text\n---\n---\n```\n"
    value, body = extract_frontmatter(source)

    assert value == {"a": 1}
    assert body == b"# T\n\n```text\n---\n---\n```\n"


def test_requires_byte_zero_delimiter_and_exact_closing_line() -> None:
    assert extract_frontmatter(b"text\n---\nafter\n") == (None, b"text\n---\nafter\n")
    with pytest.raises(FrontmatterError):
        extract_frontmatter(b"---\ntitle: value\n")
    with pytest.raises(FrontmatterError):
        extract_frontmatter(b"---\ntitle: value\n--- extra\n# H1\n")


@pytest.mark.parametrize(
    "document",
    [
        b"a: 1\na: 2\n",
        b"a: &value 1\nb: *value\n",
        b"a: !!str 1\n",
        b"a: 2026-01-01\n",
        b"a: !!binary YQ==\n",
        b"a: !!set {x: null}\n",
        b"- not a mapping\n",
        b"a: .nan\n",
    ],
)
def test_rejects_unsafe_yaml(document: bytes) -> None:
    with pytest.raises(FrontmatterError):
        extract_frontmatter(b"---\n" + document + b"---\nbody\n")


def test_rejects_invalid_utf8() -> None:
    with pytest.raises(UnicodeError):
        extract_frontmatter(b"---\nvalue: \xff\n---\nbody\n")


def test_validates_python_values() -> None:
    assert validate_frontmatter({"z": [None, False, 1, 1.25, "text"]}) == {
        "z": [None, False, 1, 1.25, "text"]
    }
    with pytest.raises(FrontmatterError):
        validate_frontmatter({1: "not a string key"})
    with pytest.raises(FrontmatterError):
        validate_frontmatter({"value": float("inf")})
    with pytest.raises(FrontmatterError):
        validate_frontmatter({"value": "\ud800"})


def test_serializes_canonical_mapping() -> None:
    value = {"z": [], "nested": {"b": "line\n\tvalue", "a": -0.0}, "items": [True, None, {"x": 2}]}

    assert serialize_frontmatter(value) == (
        b'---\n"items":\n  - true\n  - null\n  -\n    "x": 2\n'
        b'"nested":\n  "a": 0\n  "b": "line\\n\\tvalue"\n'
        b'"z": []\n---\n\n'
    )


def test_serializes_empty_root_as_delimiter_only_document_and_reparses() -> None:
    encoded = serialize_frontmatter({})

    assert encoded == b"---\n---\n\n"
    value, body = extract_frontmatter(encoded + b"# Body\n")
    assert value == {}
    assert body == b"\n# Body\n"


def test_comment_only_root_is_empty_mapping_and_reparses_canonical_bytes() -> None:
    value, body = extract_frontmatter(b"---\n# comment\n\n---\n# Body\n")
    assert value == {}
    assert value is not None
    assert body == b"# Body\n"
    encoded = serialize_frontmatter(value)
    assert encoded == b"---\n---\n\n"
    reparsed, reparsed_body = extract_frontmatter(encoded + body)
    assert reparsed == {}
    assert reparsed_body == b"\n# Body\n"


def test_serializes_empty_nested_containers_as_flow_values() -> None:
    encoded = serialize_frontmatter({"mapping": {}, "sequence": []})

    assert encoded == b'---\n"mapping": {}\n"sequence": []\n---\n\n'
    value, _ = extract_frontmatter(encoded)
    assert value == {"mapping": {}, "sequence": []}


@pytest.mark.parametrize("value", [{"value": float("nan")}, {"value": "\udfff"}])
def test_rejects_unserializable_values(value: dict[str, object]) -> None:
    with pytest.raises(FrontmatterError):
        serialize_frontmatter(value)


@pytest.mark.parametrize("value", [1e-6, 1.2345678, 1e20, 1e21, 1e-7, 5e-324, -0.0])
def test_serializes_finite_reals_losslessly(value: float) -> None:
    encoded = serialize_frontmatter({"value": value})
    parsed, _ = extract_frontmatter(encoded)
    assert parsed == {"value": value}


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1e-6, b"value: 0.000001"), (1.2345678, b"value: 1.2345678"), (1e21, b"value: 1.0e21"), (1e-7, b"value: 1.0e-7")],
)
def test_serializes_finite_reals_in_canonical_notation(value: float, expected: bytes) -> None:
    assert expected.replace(b"value:", b'"value":') in serialize_frontmatter({"value": value})


@pytest.mark.parametrize("key", ["a: b", "true", "", "line\nbreak", "😀"])
def test_serializes_string_keys_as_round_trippable_yaml_strings(key: str) -> None:
    encoded = serialize_frontmatter({key: 1})

    parsed, _ = extract_frontmatter(encoded)

    assert parsed == {key: 1}


def test_rejects_unhashable_yaml_mapping_key_as_frontmatter_error() -> None:
    with pytest.raises(FrontmatterError, match="hashable"):
        extract_frontmatter(b"---\n? [a]\n: b\n---\n")
