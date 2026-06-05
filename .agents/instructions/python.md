# Python Style Guide

Rules for writing Python code in any project. These rules apply unless a project's `.agents/` or `AGENTS.md`
file explicitly overrides them.


## Docstrings

### Format

Docstrings that can be written on a single line should have their triple quotes in-line:

```
# WRONG
def foo(client: Client) -> Result:
    """
    Execute a foo operation on the client and reformat the response as a Result.
    """

# RIGHT
def foo(client: Client) -> Result:
    """Execute a foo operation on the client and reformat the response as a Result."""
```

Docstring sthat require multiple lines due to their length should have triple quotes on their own lines:

```
# WRONG
def foo(client: Client) -> Result:
    """Execute a foo operation on the client and reformat the response as a Result.

    The result will be validated and missing values will be filled in with defaults.
    """

# RIGHT
def foo(client: Client) -> Result:
    """
    Execute a foo operation on the client and reformat the response as a Result.

    The result will be validated and missing values will be filled in with defaults.
    """
```

### Voice and content

The first line of a docstring should always use imperative voice and include proper punctuation. It should be a single
line followed by an empty line. Further explanation, argument documentation, return explanation, examples, callouts,
etc may be included after the empty line:

```
# WRONG
def foo(client: Client) -> Result:
    """
    Executes a foo operation on the client and reformat the response as a Result
    The result will be validated and missing values will be filled in with defaults.
    """

# RIGHT
def foo(client: Client) -> Result:
    """
    Execute a foo operation on the client and reformat the response as a Result.

    The result will be validated and missing values will be filled in with defaults.
    """
```

### Assume markdown (not Sphinx)

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
