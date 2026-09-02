"""Restricted YAML frontmatter handling."""

from collections.abc import Mapping
import math
import yaml


class FrontmatterError(ValueError):
    """Report frontmatter that falls outside the formatter's safe subset."""


def extract_frontmatter(source: bytes) -> tuple[dict[str, object] | None, bytes]:
    """Extract frontmatter from source.

    The complete restricted loader is implemented in the frontmatter task. This contract-level placeholder deliberately
    rejects frontmatter rather than interpreting it incorrectly.
    """
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError:
        raise
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None, source
    closing = next((index for index, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"), None)
    if closing is None:
        raise FrontmatterError("frontmatter closing delimiter is missing")
    raw = "".join(lines[1:closing])
    try:
        value = yaml.safe_load(raw) if raw.strip() else {}
    except yaml.YAMLError as error:
        raise FrontmatterError(str(error)) from error
    return dict(validate_frontmatter(value)), source[len("".join(lines[: closing + 1]).encode()):]


def validate_frontmatter(value: object) -> Mapping[str, object]:
    """Validate and return a restricted frontmatter mapping."""
    def valid(item: object) -> bool:
        if item is None or isinstance(item, (str, bool, int)):
            return True
        if isinstance(item, float):
            return math.isfinite(item)
        if isinstance(item, Mapping):
            return all(isinstance(key, str) and valid(child) for key, child in item.items())
        if isinstance(item, (list, tuple)):
            return all(valid(child) for child in item)
        return False

    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value) or not valid(value):
        raise FrontmatterError("frontmatter root must be a mapping with string keys")
    return value


def serialize_frontmatter(value: Mapping[str, object]) -> bytes:
    """Serialize a restricted frontmatter mapping."""
    validate_frontmatter(value)

    def scalar(item: object) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if isinstance(item, str):
            return '"' + item.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
        return str(item)

    def emit(item: object, indent: int) -> list[str]:
        prefix = " " * indent
        if isinstance(item, Mapping):
            if not item:
                return [prefix + "{}"]
            lines: list[str] = []
            for key in sorted(item):
                child = item[key]
                if isinstance(child, (Mapping, list, tuple)) and child:
                    lines.append(f'{prefix}{key}:')
                    lines.extend(emit(child, indent + 2))
                else:
                    lines.append(f'{prefix}{key}: {scalar(child)}')
            return lines
        if isinstance(item, (list, tuple)):
            if not item:
                return [prefix + "[]"]
            lines = []
            for child in item:
                if isinstance(child, (Mapping, list, tuple)) and child:
                    lines.append(prefix + "-")
                    lines.extend(emit(child, indent + 2))
                else:
                    lines.append(prefix + "- " + scalar(child))
            return lines
        return [prefix + scalar(item)]

    return ("---\n" + "\n".join(emit(value, 0)) + "\n---\n\n").encode()
