import pytest

from dot_tools.markdown_format import format_contents, wrap_prose_line


@pytest.mark.parametrize(
    ("prefix", "continuation"),
    [("", ""), ("- ", "  "), ("> ", "> ")],
)
def test_wrap_prose_rebalances_single_word_final_line(prefix: str, continuation: str):
    content = " ".join(["word"] * 25)

    wrapped = wrap_prose_line(f"{prefix}{content}")

    assert len(wrapped) > 1
    assert len(wrapped[-1][len(continuation) :].split()) > 1
    assert all(len(line) <= 120 for line in wrapped)
    assert all(line.startswith(prefix if index == 0 else continuation) for index, line in enumerate(wrapped))
    reconstructed = " ".join(
        line[len(prefix if index == 0 else continuation) :] for index, line in enumerate(wrapped)
    )
    assert reconstructed == content


def test_wrap_prose_rebalances_short_final_line_from_task_plan_example():
    content = (
        "Revise the `run-feature` plan-review cadence to stop dispatching adversarial agent reviews after every "
        "human-directed edit. Preserve an initial agent review, allow an uninterrupted human feedback loop, then run a "
        "final consolidated review before requesting approval. Apply the same gates to design and implementation plans "
        "without weakening unknown-resolution or explicit-approval requirements."
    )

    wrapped = wrap_prose_line(content)

    assert wrapped[-1].startswith("plans without weakening")
    assert all(len(line) <= 120 for line in wrapped)
    assert " ".join(wrapped) == content


@pytest.mark.parametrize(
    ("prefix", "continuation"),
    [("- ", "  "), ("> ", "> ")],
)
def test_format_contents_reflows_soft_wrapped_marked_paragraph(prefix: str, continuation: str):
    words = ["word"] * 25
    contents = f"# Example\n\n{prefix}{' '.join(words[:-1])}\n{continuation}{words[-1]}"

    formatted = format_contents(contents)
    paragraph = formatted.split("\n\n")[1].splitlines()

    assert paragraph[0].startswith(prefix)
    assert all(line.startswith(continuation) for line in paragraph[1:])
    reconstructed = " ".join(
        line[len(prefix if index == 0 else continuation) :] for index, line in enumerate(paragraph)
    )
    assert reconstructed == " ".join(words)
    assert len(paragraph[-1][len(continuation) :].split()) > 1


def test_format_contents_reflows_soft_wrapped_paragraph_and_preserves_fenced_code():
    words = ["word"] * 25
    prose = " ".join(words)
    code = "x" * 130
    contents = f"# Example\n\n{' '.join(words[:-1])}\n{words[-1]}\n\n```text\n{code}\n```\n\n## Next\n\nDone."

    formatted = format_contents(contents)

    blocks = formatted.split("\n\n")

    assert blocks[0] == "# Example"
    assert " ".join(blocks[1].splitlines()) == prose
    assert len(blocks[1].splitlines()[-1].split()) > 1
    assert blocks[2] == f"```text\n{code}\n```"
    assert formatted.endswith("\n\n\n## Next\n\nDone.")
