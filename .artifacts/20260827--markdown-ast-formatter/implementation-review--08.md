# Implementation Plan Review: Generic AST-based Markdown formatter

This targeted re-review checks the CLI/package reorganization against the previously approved generic formatter
behavior. It does not review implementation code or run tests, builds, or linters.


**Iteration 08**


## Source Artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The review surfaced findings:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 1


## Prior Review Resolution

- **S06** ✓: Task 04 and Task 05 now specify the exact code-span boundary algorithm, table serialization order,
  escaped-width calculation, boundary fixtures, reparsing, and second-pass idempotence.


## Findings

### Summary

| Finding ID | Title                                                     | Outcome |
| ---------- | --------------------------------------------------------- | ------- |
| S01        | Wrapper delegation uses a non-command `format/check` path |         |
| T01        | Grouped CLI contract tests lack a focused red/green path  |         |


### Significant

#### S01: Wrapper delegation uses a non-command `format/check` path


#### Where

Execution — Task 06 — AC06 and Steps, approximately lines 361–397


#### Issue

The wrapper contract says to invoke `uv run --project <repo> dt markdown format/check <absolute paths>` and the
steps refer to delegation to `dt markdown format/check`. `format/check` is not an executable subcommand; the plan
defines two separate paths, `dt markdown format PATH...` and `dt markdown check PATH...`, everywhere else. The wrapper
contract does not state the exact mode-to-command mapping in this normative delegation text.


#### Impact

An executor can implement the literal `format/check` operand, making both wrapper modes fail instead of preserving the
standalone tool and the unchanged TypeScript caller. The ambiguity also weakens the required verification of both
delegation paths.


#### Suggestion

Replace the shorthand with two explicit statements: wrapper `format` invokes `uv run --project <repo> dt markdown
format <absolute paths>`, and wrapper `check` invokes `uv run --project <repo> dt markdown check <absolute paths>.
Use those exact forms in the Task 06 steps and wrapper tests.


#### Outcome


### Trivial

#### T01: Grouped CLI contract tests lack a focused red/green path


#### Where

Execution — Task 01 — Steps, approximately lines 151–157; Task 06 — Steps, approximately lines 389–397


#### Issue

Task 01 creates `tests/markdown_formatter/test_markdown_cli_contract.py` for the grouped command surface, but its
only verification is `uv sync`. Task 06's focused red and green commands omit that module and cover only
`test_markdown_cli.py` for the grouped CLI. The plan also says to create the CLI group in Task 01 while assigning
implementation of `src/dot_tools/cli/markdown.py` to Task 06, without distinguishing the tested skeleton from the
final commands.


#### Impact

The newly changed command-shape contract has no task-local red/green verification and can remain inconsistent with
the implementation until the final full suite. The executor also has no clear point at which the Task 01 contract
test is expected to pass.


#### Suggestion

Either move `test_markdown_cli_contract.py` to Task 06 and include it in that task's exact red and green commands, or
assign a minimal grouped-command skeleton to Task 01 and add explicit red/green commands for the contract test.


#### Outcome


## Notes

The package boundary is otherwise consistent: core document orchestration and operations belong under
`src/dot_tools/markdown_formatter`, while Typer adaptation belongs in `src/dot_tools/cli/markdown.py`. Task 01 names
the grouped public contract, Task 05 keeps the document pipeline out of the CLI module, and Task 06 assigns command
registration in the existing `src/dot_tools/cli/main.py`.

The Project Commands section uses the exact grouped paths for help. No stale `dt format` or `dt check` command is
documented, and the plan adds no profile or Zensical scope. The wrapper retains entry-CWD path resolution,
repository discovery, child stream passthrough, and return-code propagation; the TypeScript caller remains unchanged
and still supplies `format` or `check` plus paths. The previously approved public models, error/status precedence,
formatting and opaque-byte behavior, and safe write ordering remain represented in Tasks 01, 04, 05, and 06. Task
ordering and the existing red/green commands for frontmatter, parsing, normalization, rendering, and operations have
no other regression.
