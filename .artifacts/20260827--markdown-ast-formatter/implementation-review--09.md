# Implementation Plan Review: Generic AST-based Markdown formatter

This narrow re-review checks whether review 08 findings were resolved without regressions in the approved generic
formatter plan.


**Iteration 09**


## Source artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The review found:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior review resolution

- **S01** ✓: Task 06 AC06 and its steps now state the exact mode-to-command mappings: wrapper `format` invokes
  `uv run --project <repo> dt markdown format <absolute paths>`, and wrapper `check` invokes
  `uv run --project <repo> dt markdown check <absolute paths>`. The wrapper tests are assigned the same exact contract.
- **T01** ✓: `test_markdown_cli_contract.py` is assigned to Task 06 and included in both the red and green commands.
  Task 01's only verification remains `uv sync`.


## Findings

### Summary

| Finding ID | Title                 | Outcome  |
| ---------- | --------------------- | -------- |
| None       | No remaining findings | Approved |


## Approval

The plan is approved. The wrapper format and check commands map exactly to the grouped `dt markdown format` and
`dt markdown check` commands with `uv run --project <repo>` and absolute paths; no shorthand or old command remains.
The grouped CLI contract test is owned by Task 06 and appears in its exact red/green command, while Task 01 runs only
`uv sync`.


## Regression checks

- Package ownership remains consistent: document orchestration and operations stay in `dot_tools.markdown_formatter`,
  while Typer adaptation and command registration stay in the CLI modules; the wrapper remains a thin delegate.
- The command group remains `dt markdown` with separate `format` and `check` subcommands, with no stale top-level
  command or shorthand.
- The scope remains generic and fail-closed, with no profile-specific or Zensical behavior introduced.
- Previously approved models, status and error precedence, formatting and opaque-byte preservation, and safe operation
  ordering remain represented in the plan.
- Task ordering remains coherent: dependency and contracts, frontmatter, parsing, normalization, rendering,
  operations/CLI/wrapper, then the corpus and quality gate.

No findings remain from review 08, and no new regression is identified in this narrow re-review.
