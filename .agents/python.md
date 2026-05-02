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
