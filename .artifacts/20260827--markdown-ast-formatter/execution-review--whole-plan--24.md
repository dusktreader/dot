# Execution Review: Generic AST-based Markdown formatter

This independent whole-plan iteration-24 review rechecks the current formatter against the revised design,
implementation
plan, journal, and review 23. HTML-looking Markdown is accepted, parser-delimited HTML blocks may remain opaque, and
`RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--23.md`


## Scope

**whole-plan - Iteration 24**

The review started with the current worktree diff, independently rechecked review-23 C01 and C02, inspected the current
formatter source and tests, and ran the whole-plan quality matrix. Only this review artifact was written.


## Issue Summary

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                       | Result                                                                                                                                                                                                     |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                              | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                                               |
| `uv run pytest tests/markdown_formatter --no-cov`                                      | Passed: 372 tests.                                                                                                                                                                                         |
| `uv run pytest`                                                                        | 685 passed, 1 failed; coverage 86.31%, above the 70% threshold.                                                                                                                                            |
| Full pytest failure                                                                    | Unrelated configure assertion: `@opencode-ai/plugin` is present in the OpenCode package while the baseline test expects `{}`.                                                                              |
| `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix` | Passed.                                                                                                                                                                                                    |
| `uv run ruff check src tests`                                                          | Passed.                                                                                                                                                                                                    |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`            | Passed.                                                                                                                                                                                                    |
| `uv run ty check`                                                                      | Failed with 74 diagnostics outside formatter scope; no formatter path was reported.                                                                                                                        |
| Direct C01 probe                                                                       | Passed 1,096 mixed emphasis/strong paragraph and table cases across LF and CRLF. Complete recursive inline shapes and three-pass output matched.                                                           |
| Direct C02 probe                                                                       | Passed 8 task-bearing secondary quote, fence, heading, and nested-child cases across LF and CRLF for AST shape, task state, code payload, and three-pass output.                                           |
| Direct C02 extension                                                                   | Failed for a task-bearing secondary paragraph in both LF and CRLF. The first pass emits a `code_block`; the second emits a fence, so output is not stable. See C01.                                        |
| Frontmatter, parser/span, wrapping, code, table, and HTML probes                       | Passed. Exact source spans, CRLF and astral ownership, finite and unsafe YAML cases, semantic code payloads, table geometry, accepted HTML-looking text, opaque HTML blocks, and idempotence were checked. |
| Operations probe                                                                       | Passed status, record, digest, snapshot, preflight, symlink, partial-commit, and untouched-file checks. Focused tests also cover locks, atomic replacement, cleanup, and races.                            |
| CLI and wrapper smoke                                                                  | Passed grouped help, wrapper help, grouped check/format, and wrapper check/format. Canonical input reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                       |
| `git diff --check`                                                                     | Passed.                                                                                                                                                                                                    |

The configure pytest failure and repository-wide Ty diagnostics are the only unrelated baselines accepted by this
review.
The formatter-specific C02 extension failure remains a blocker.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                                 |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:15`, lockfile, and passing `uv sync`.                                                                                    |
| 01/AC02 | ✓      | Formatter package and public models are present; `test_markdown_cli_contract.py::test_public_models_and_callable_signatures_are_stable`. |
| 01/AC03 | ✓      | `src/dot_tools/cli/main.py:35-39`, grouped help, and public CLI contract tests.                                                          |


### Task 02

| AC      | Status | Evidence                                                                                         |
| ------- | ------ | ------------------------------------------------------------------------------------------------ |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; extraction, validation, and serialization tests pass.                   |
| 02/AC02 | ✓      | `frontmatter.py:90-100`; exact delimiter, missing-close, body, and UTF-8 tests pass.             |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; unsafe YAML, duplicate-key, Unicode, and finite-real tests pass.        |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical ordering, nesting, scalar, escaping, and framing tests pass. |


### Task 03

| AC      | Status | Evidence                                                                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123`; byte-addressed models and parser entry point pass ownership tests.                                                                     |
| 03/AC02 | ✓      | `parser.py:115-123`; CommonMark-plus-table block and inline ownership tests pass. The rendering defect is tracked under Task 04.                           |
| 03/AC03 | ✓      | `test_parser.py` and direct LF/CRLF, astral, repeated-text, nested-container, and opaque-span probes pass.                                                 |
| 03/AC04 | ✓      | `parser.py:719-903`; source-order inline scanning and reconstruction tests pass, including the independent C01 matrix.                                     |
| 03/AC05 | ✓      | `parser.py:301-303`; HTML-looking inline text is accepted and parser-delimited HTML blocks remain opaque. No `RawHtmlError` or HTML rejection path exists. |
| 03/AC06 | ✓      | `parser.py:126-140,916-1026`; task metadata and thematic-break policy tests pass.                                                                          |


### Task 04

| AC      | Status | Evidence                                                                                                  |
| ------- | ------ | --------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | Normalized state models and `test_normalize.py` pass.                                                     |
| 04/AC02 | ✓      | Independent C01 matrix passed complete inline shape and three-pass checks for paragraphs and table cells. |
| 04/AC03 | ⚠      | `normalize.py:397-417` and `render.py:134-139` misindent task-bearing secondary paragraphs, causing C01.  |
| 04/AC04 | ✓      | Heading spacing, descent separators, source-break reuse, and idempotence tests pass.                      |
| 04/AC05 | ✓      | Table geometry, framing, parity, code-span pipes, source spans, invalid rows, and idempotence tests pass. |
| 04/AC06 | ✓      | Fence collision, info normalization, payload, LF/CRLF, EOF, and semantic code tests pass.                 |


### Task 05

| AC      | Status | Evidence                                                                                                           |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| 05/AC01 | ⚠      | `render.py:97-139` renders the task-bearing secondary paragraph at a column that reparses as code.                 |
| 05/AC02 | ⚠      | Inline, table, and code rendering pass their matrices, but the C02 extension changes a valid block AST.            |
| 05/AC03 | ✓      | `__init__.py:10-24`; orchestration propagates the documented typed errors and accepts HTML-looking Markdown.       |
| 05/AC04 | ⚠      | Existing golden tests pass, but the independent task-bearing secondary-paragraph probe fails three-pass stability. |


### Task 06

| AC      | Status | Evidence                                                                                                          |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-41`; collection, recursive discovery, lexical deduplication, and explicit path errors pass.     |
| 06/AC02 | ✓      | `operations.py:91-126,205-234`; preflight, atomic replacement, stop-on-write-error, mode, and cleanup tests pass. |
| 06/AC03 | ✓      | `operations.py:44-88`; snapshots, identity, destination safety, lock, fsync, and replacement tests pass.          |
| 06/AC04 | ✓      | `operations.py:133-146`; status precedence and complete result records pass focused and direct checks.            |
| 06/AC05 | ✓      | `operations.py:149-158`; streams, sorted records, diagnostics, digest-only mismatches, and exit mapping pass.     |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:12-29`; CWD, project discovery, delegation, passthrough, and smoke tests pass.  |
| 06/AC07 | ✓      | Grouped registration, help, CLI contract, wrapper tests, and smoke commands pass.                                 |


### Task 07

| AC      | Status | Evidence                                                                                                                                 |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Generic corpus tests pass, but the corpus omits the independent task-bearing secondary-paragraph case that fails C01.                    |
| 07/AC02 | ⚠      | Focused pytest, Ruff, and Ty pass; full pytest and Ty retain only accepted baselines, but a formatter-specific semantic blocker remains. |


## Scope Verification

| File or path                                                              | Justification                                          | Status                                  |
| ------------------------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------- |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py` | Task 01 dependency and public contract                 | ✓                                       |
| `src/dot_tools/markdown_formatter/{__init__,frontmatter}.py`              | Tasks 01, 02, and 05 document/frontmatter pipeline     | ✓                                       |
| `src/dot_tools/markdown_formatter/parser.py`                              | Task 03 parsing, source spans, ownership, and policy   | ✓                                       |
| `src/dot_tools/markdown_formatter/normalize.py`                           | Task 04 normalization, list columns, and inline codecs | ⚠ C01                                   |
| `src/dot_tools/markdown_formatter/render.py`                              | Task 05 rendering and recursive containers             | ⚠ C01                                   |
| `src/dot_tools/markdown_formatter/operations.py`                          | Task 06 operations and replacement safety              | ✓                                       |
| `src/dot_tools/cli/{main,markdown}.py`                                    | Task 06 grouped CLI                                    | ✓                                       |
| `.agents/tools/markdown-format.py`                                        | Task 06 compatibility wrapper                          | ✓                                       |
| `tests/markdown_formatter/` and fixtures                                  | Tasks 02 through 07 contract and corpus coverage       | ⚠ Missing C01 extension regression      |
| Revised plans, journal, and prior reviews                                 | Review context                                         | ✓ Reviewed, not modified by this review |

The worktree already contained the implementation, tests, revised plans, journal, and review artifacts shown by the
initial diff. This review added no changes outside this artifact.


## Prior Review Resolution

| Review-23 finding                                                     | Status | Current evidence                                                                                                                                                                                                                       |
| --------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01: generated delimiter context changes a valid sibling emphasis AST | ✓      | Independent 1,096-case LF/CRLF paragraph and table matrix preserves recursive inline shape and converges in three passes.                                                                                                              |
| C02: task-bearing list children are emitted as code blocks            | ⚠      | The exact quote, fence, heading, and nested-child cases pass for task state, AST shape, payload, and three-pass output. A secondary paragraph child still receives the task continuation column and reparses as `code_block`; see C01. |


## Findings

### Summary

| Finding | Title                                                                   | Outcome         |
| ------- | ----------------------------------------------------------------------- | --------------- |
| C01     | Task-bearing secondary paragraphs use the paragraph continuation column | Blocks approval |


### Critical

#### C01 Task-bearing secondary paragraphs use the paragraph continuation column


#### Where

`src/dot_tools/markdown_formatter/normalize.py:397-417` and `src/dot_tools/markdown_formatter/render.py:134-139`


#### Issue

The list normalizer correctly separates the first item's paragraph continuation column from the structural child column
for
containers, headings, fences, and nested lists. It does not preserve that distinction for a secondary paragraph. The
secondary paragraph becomes a plain `bytes` child, and the renderer sends every such child through `continuation`, which
includes the task prefix width.

For the valid source `b"# T\\n\\n- [x] task\\n\\n  second paragraph\\n"`, the first pass emits
`b"# T\\n\\n- [x] task\\n\\n      second paragraph\\n"`. Six spaces are the task-aware paragraph continuation column,
but after a blank line they are an indented code
block. The second pass therefore emits a fenced code block, and the third pass changes its payload indentation again.
The
same failure occurs with CRLF input.


#### Impact

Formatting changes a recognized secondary paragraph into a `code_block`, then into a fence. It changes the block AST,
violates recursive list/container preservation, and breaks three-pass idempotence. This violates Task 04 AC03 and Task
05
AC01, AC02, and AC04 under the revised design.


#### Fix

Keep secondary paragraphs as a typed normalized block or mark them distinctly from physical continuation lines. Render a
secondary paragraph at the structural child column, reserving the task-aware `continuation_column` for continuation
lines
of the first paragraph. Add LF and CRLF regressions for task-bearing secondary paragraphs and nested task-item secondary
paragraphs that assert exact block kinds, preserved text, task state, and three formatting passes.


#### Outcome

Blocks approval.


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global fallback
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 must be resolved before approval. Review-23 C01 is independently resolved. Its exact C02 cases are resolved, but the
broader task-bearing secondary-paragraph path remains a formatter-specific semantic blocker. The configure pytest
failure
and repository-wide Ty diagnostics remain unrelated baselines under the revised requirement.
