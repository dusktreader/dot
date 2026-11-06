from dot_tools.markdown_format import format_contents


def test_format_contents_applies_heading_spacing_only():
    contents = "# Intro\n## Section\n### Subsection\n### Peer\nLong  prose.   \n"

    formatted = format_contents(contents)

    assert formatted == "# Intro\n\n## Section\n\n### Subsection\n\n\n### Peer\nLong  prose.   \n"


def test_format_contents_does_not_apply_frontmatter_spacing():
    contents = "---\ntitle: Guide\n---\n# Guide\nText\n## Section\n"

    formatted = format_contents(contents)

    assert formatted == "---\ntitle: Guide\n---\n# Guide\nText\n\n\n## Section\n"


def test_format_contents_preserves_fenced_code_and_ignores_headings_inside():
    contents = "# Intro\n```text\n## Backtick heading\n```\n~~~text\n### Tilde heading\n~~~\n## Section\n"

    formatted = format_contents(contents)

    assert formatted == "# Intro\n```text\n## Backtick heading\n```\n~~~text\n### Tilde heading\n~~~\n\n\n## Section\n"


def test_format_contents_uses_one_blank_line_after_horizontal_rule():
    contents = "# Intro\n----\n## Section\n"

    assert format_contents(contents) == "# Intro\n----\n\n## Section\n"
