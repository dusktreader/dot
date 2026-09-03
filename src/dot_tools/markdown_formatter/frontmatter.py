"""Extract, validate, and serialize the formatter's restricted YAML envelope."""

from collections.abc import Mapping, Sequence
import math
import re
from decimal import Decimal
from typing import Any, cast

import yaml


class FrontmatterError(ValueError):
    """Report frontmatter outside the formatter's safe YAML subset."""


_SCALAR_TAGS = {
    "tag:yaml.org,2002:null",
    "tag:yaml.org,2002:bool",
    "tag:yaml.org,2002:int",
    "tag:yaml.org,2002:float",
    "tag:yaml.org,2002:str",
}
_CONTAINER_TAGS = {"tag:yaml.org,2002:map", "tag:yaml.org,2002:seq"}


class _RestrictedLoader(yaml.SafeLoader):
    """Construct mappings while rejecting duplicate keys."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in result:
                    raise FrontmatterError(f"duplicate frontmatter key: {key}")
                result[key] = self.construct_object(value_node, deep=deep)
            except TypeError as error:
                raise FrontmatterError("frontmatter mapping keys must be hashable") from error
        return result


_RestrictedLoader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(r"^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+]?[0-9]+)?|[-+]?[0-9][0-9_]*[eE][-+]?[0-9]+)$"),
    list("-+0123456789"),
)
for _initial_character in "-+0123456789":
    _resolvers = _RestrictedLoader.yaml_implicit_resolvers[_initial_character]
    _resolvers.insert(0, _resolvers.pop())


def _check_events(text: str) -> None:
    """Reject YAML events that use aliases, anchors, or explicit tags."""
    try:
        events = yaml.parse(text)
        for event in events:
            if getattr(event, "anchor", None) is not None:
                raise FrontmatterError("YAML anchors and aliases are not permitted")
            if getattr(event, "tag", None) is not None:
                raise FrontmatterError("explicit YAML tags are not permitted")
            if isinstance(event, yaml.events.AliasEvent):
                raise FrontmatterError("YAML anchors and aliases are not permitted")
    except yaml.YAMLError as error:
        raise FrontmatterError(str(error)) from error


def _check_node(node: yaml.Node) -> None:
    """Reject node tags outside the implicit restricted YAML type set."""
    if isinstance(node, yaml.MappingNode):
        if node.tag not in _CONTAINER_TAGS:
            raise FrontmatterError("unsupported YAML mapping")
        for key, value in node.value:
            _check_node(key)
            _check_node(value)
    elif isinstance(node, yaml.SequenceNode):
        if node.tag not in _CONTAINER_TAGS:
            raise FrontmatterError("unsupported YAML sequence")
        for child in node.value:
            _check_node(child)
    elif isinstance(node, yaml.ScalarNode):
        if node.tag not in _SCALAR_TAGS:
            raise FrontmatterError("unsupported YAML scalar")
    else:
        raise FrontmatterError("unsupported YAML node")


def extract_frontmatter(source: bytes) -> tuple[dict[str, object] | None, bytes]:
    """Extract byte-zero frontmatter and return its validated mapping and body bytes."""
    source.decode("utf-8")
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].removesuffix(b"\n").removesuffix(b"\r") != b"---":
        return None, source
    closing = next(
        (index for index, line in enumerate(lines[1:], 1) if line.removesuffix(b"\n").removesuffix(b"\r") == b"---"),
        None,
    )
    if closing is None:
        raise FrontmatterError("frontmatter closing delimiter is missing")
    body = b"".join(lines[closing + 1 :])
    raw = b"".join(lines[1:closing]).decode("utf-8")
    _check_events(raw)
    try:
        documents = list(yaml.compose_all(raw, Loader=_RestrictedLoader))
    except yaml.YAMLError as error:
        raise FrontmatterError(str(error)) from error
    if not documents:
        return {}, body
    if len(documents) != 1:
        raise FrontmatterError("multiple YAML documents are not permitted")
    node = documents[0]
    try:
        value: object = {} if node is None else _RestrictedLoader(raw).get_single_data()
    except (yaml.YAMLError, FrontmatterError) as error:
        raise FrontmatterError(str(error)) from error
    if node is not None:
        _check_node(node)
    return dict(validate_frontmatter(value)), body


def validate_frontmatter(value: object) -> Mapping[str, object]:
    """Validate and return a restricted frontmatter mapping."""
    def valid(item: object) -> bool:
        if item is None or isinstance(item, (str, bool, int)):
            if isinstance(item, str) and any(0xD800 <= ord(char) <= 0xDFFF for char in item):
                return False
            return True
        if isinstance(item, float):
            return math.isfinite(item)
        if isinstance(item, Mapping):
            return all(isinstance(key, str) and valid(key) and valid(child) for key, child in item.items())
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            return all(valid(child) for child in item)
        return False

    if not isinstance(value, Mapping) or not valid(value):
        raise FrontmatterError("frontmatter root must be a mapping with string keys")
    return cast(Mapping[str, object], value)


def serialize_frontmatter(value: Mapping[str, object]) -> bytes:
    """Serialize a validated mapping using deterministic restricted YAML."""
    validate_frontmatter(value)

    def scalar(item: object) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if isinstance(item, str):
            escaped = []
            for char in item:
                code = ord(char)
                escaped.append({"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}.get(
                    char, f"\\u00{code:02x}" if code < 0x20 or code == 0x7F else char
                ))
            return '"' + "".join(escaped) + '"'
        if isinstance(item, int):
            return str(item)
        if isinstance(item, float):
            return _float_text(item)
        raise FrontmatterError("unsupported scalar")

    def emit(item: object, indent: int) -> list[str]:
        prefix = " " * indent
        if isinstance(item, Mapping):
            if not item:
                return [prefix + "{}"]
            lines: list[str] = []
            for key in sorted(item):
                child = item[key]
                encoded_key = scalar(key)
                if isinstance(child, Mapping) or isinstance(child, Sequence) and not isinstance(child, (str, bytes)):
                    if child:
                        lines.append(f"{prefix}{encoded_key}:")
                        lines.extend(emit(child, indent + 2))
                    else:
                        lines.append(f"{prefix}{encoded_key}: {scalar(child) if isinstance(child, str) else '{}' if isinstance(child, Mapping) else '[]'}")
                else:
                    lines.append(f"{prefix}{encoded_key}: {scalar(child)}")
            return lines
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            if not item:
                return [prefix + "[]"]
            lines = []
            for child in item:
                if isinstance(child, Mapping) or isinstance(child, Sequence) and not isinstance(child, (str, bytes)):
                    if child:
                        lines.append(prefix + "-")
                        lines.extend(emit(child, indent + 2))
                    else:
                        lines.append(prefix + "- {}" if isinstance(child, Mapping) else prefix + "- []")
                else:
                    lines.append(prefix + "- " + scalar(child))
            return lines
        return [prefix + scalar(item)]

    if not value:
        return b"---\n---\n\n"
    return ("---\n" + "\n".join(emit(value, 0)) + "\n---\n\n").encode("utf-8")


def _float_text(value: float) -> str:
    """Render a finite real with the approved threshold and normalized exponent."""
    if not math.isfinite(value):
        raise FrontmatterError("non-finite real")
    if value == 0:
        return "0"
    text = repr(value).lower()
    if 1e-6 <= abs(value) < 1e21:
        text = format(Decimal(text), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if "." not in text:
            text += ".0"
    elif "e" not in text:
        text = format(value, ".17e")
    if "e" in text:
        mantissa, exponent = re.split("e", text)
        mantissa = mantissa.rstrip("0").rstrip(".")
        if "." not in mantissa:
            mantissa += ".0"
        normalized_exponent = int(exponent)
        exponent_text = str(normalized_exponent)
        text = mantissa + "e" + exponent_text
    try:
        reparsed = _RestrictedLoader(text).get_single_data()
        if not isinstance(reparsed, float) or reparsed != value or (
            value == 0 and math.copysign(1.0, reparsed) != math.copysign(1.0, value)
        ):
            raise FrontmatterError("real cannot be represented without loss")
    except (ValueError, yaml.YAMLError) as error:
        raise FrontmatterError("real cannot be represented without loss") from error
    return text
