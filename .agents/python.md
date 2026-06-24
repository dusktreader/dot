# Python Style Guide

Rules for writing Python code in any project. These rules apply unless a project's `.agents/` or `AGENTS.md`
file explicitly overrides them.


## Docstrings

Docstrings render as Markdown. Do not use reStructuredText markup.

Specifically:

- No Sphinx interpreted-text roles. Never write `:class:`, `:func:`, `:mod:`, `:meth:`, `:attr:`, `:exc:`, or
  `:obj:` prefixes before a backtick-wrapped name.
- No double backticks for inline code. Use a single backtick.

```python
# WRONG
def foo(client: Client) -> Result:
    """
    Run the request using :class:`Client` and return a :class:`Result`.

    The ``timeout`` argument is passed straight through to ``httpx``.
    """

# RIGHT
def foo(client: Client) -> Result:
    """
    Run the request using `Client` and return a `Result`.

    The `timeout` argument is passed straight through to `httpx`.
    """
```

The only project where rST docstring markup is acceptable is one explicitly using Sphinx, and that project
will say so in its own `.agents/` or `AGENTS.md`. If you don't see an explicit opt-in, assume Markdown.


## Why this matters

Most modern Python documentation tooling (mkdocstrings, pdoc, zensical) renders docstrings as Markdown. Sphinx
markup in those toolchains shows up as literal noise in the rendered output: `:class:` appears as plain text,
and double backticks render as visible backticks wrapped around the word.


## Args alignment

In `Args:` sections, pad parameter names to the same column width so all descriptions line up:

```python
# WRONG — descriptions start at different columns
def foo(x: int, long_param: str, y: float = 0.0) -> None:
    """
    Do the thing.

    Args:
        x: The first value.
        long_param: A longer parameter name.
        y: An optional float.
    """

# RIGHT — descriptions aligned
def foo(x: int, long_param: str, y: float = 0.0) -> None:
    """
    Do the thing.

    Args:
        x:          The first value.
        long_param: A longer parameter name.
        y:          An optional float.
    """
```

Continuation lines for a single argument wrap to align with the start of the description on the line above, not
with the parameter name.


## Inline comments

Only add comments when they provide clarity that the code itself cannot. A comment should explain *why*
something non-obvious is done — not restate what the code already says.

Never write comments that:

- Label what the next function or block is named (`# Authentication` above `def authenticate`)
- Divide a class into sections with banners (`# ---`, `# ===`)
- Describe what a well-named variable or call already makes obvious (`# hash the password` above `pswd_ctx.hash(password)`)

If a class feels like it needs section signposting, that is a signal to split it up instead.
