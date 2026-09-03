# Execution Review: Generic AST-based Markdown formatter

This independent iteration-23 review rechecks the current formatter against the revised plans and journal. HTML-looking
Markdown is accepted, parser-delimited HTML blocks may remain opaque, and `RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--22.md`


## Scope

**whole-plan - Iteration 23**

The review started with the current worktree diff, independently rechecked review-22 C01-C03, inspected the formatter
source and tests, and ran the whole-plan quality matrix. Only this review artifact was written.


## Issue Summary

- **Critical**: 2
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                  | Result                                                                                                                                                                      |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                         | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                |
| `uv run pytest tests/markdown_formatter --no-cov` | Passed: 362 tests.                                                                                                                                                          |
| `uv run pytest`                                   | 675 passed, 1 failed; coverage 86.24%, above the 70% threshold.                                                                                                             |
| Full pytest failure                               | Unrelated configure assertion: the OpenCode package has `@opencode-ai/plugin` `1.18.14`, while the baseline test expects `{}`.                                              |
| Focused and full Ruff                             | Passed: both documented Ruff commands report no errors.                                                                                                                     |
| Focused Ty                                        | Passed for formatter source and tests.                                                                                                                                      |
| Full Ty                                           | Failed with 74 repository-baseline diagnostics outside the formatter.                                                                                                       |
| Grouped and wrapper help                          | Passed for `markdown`, `format`, `check`, and the wrapper.                                                                                                                  |
| Wrapper temporary format/check smoke              | Passed; format then check returned success and produced `# Title\n`.                                                                                                        |
| `git diff --check`                                | Passed.                                                                                                                                                                     |
| Frontmatter matrix                                | Passed 20,011 finite IEEE-754 samples plus unsafe YAML cases.                                                                                                               |
| Parser ownership/span matrix                      | Passed LF, CRLF, astral, nested-container, table, code, EOF, and opaque-span checks.                                                                                        |
| Accepted HTML matrix                              | Passed inline-looking, escaped-angle, parser-opaque block, opaque text, and code cases without HTML rejection.                                                              |
| Review-22 C01 probe                               | Passed odd/even backslash runs before inline atoms and table pipes. Odd runs retain semantics; even table runs remain delimiters and raise the documented extra-cell error. |
| Review-22 C02 probe                               | Passed the exact adjacent emphasis/strong cases in LF and CRLF, including reparsed AST shape and three-pass stability.                                                      |
| Review-22 C03 probe                               | Passed the exact ordinary paragraph case in LF and CRLF; it remains a paragraph and does not raise.                                                                         |
| Task-bearing list child probe                     | Failed; a parser-owned block quote or fenced code child becomes a `code_block` after rendering.                                                                             |
| Whole-plan operations matrix                      | Focused tests passed for statuses, records, diagnostics, snapshots, locks, atomic replacement, cleanup, partial commits, CLI, and wrapper behavior.                         |

The full pytest failure and repository-wide Ty diagnostics are the only baselines accepted by this review. The formatter
has two independent semantic blockers below.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                           |
| ------- | ------ | -------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml`, lockfile, and passing `uv sync`. |
| 01/AC02 | ✓      | Formatter package and public models are present.   |
| 01/AC03 | ✓      | Grouped command and public contract tests pass.    |


### Task 02

| AC      | Status | Evidence                                                                   |
| ------- | ------ | -------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-140`; all three frontmatter APIs pass focused tests.    |
| 02/AC02 | ✓      | Exact delimiter, missing-close, UTF-8, and body-preservation tests pass.   |
| 02/AC03 | ✓      | Restricted tags, duplicates, unsafe values, and finite-real matrix pass.   |
| 02/AC04 | ✓      | Canonical ordering, scalar codecs, thresholds, escaping, and framing pass. |


### Task 03

| AC      | Status | Evidence                                                                                                              |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | Byte-addressed AST models and parser-owned code metadata pass the LF/CRLF/EOF span matrix.                            |
| 03/AC02 | ⚠      | Core parser ownership passes, but an owned list tree can render into a different child AST. See C02.                  |
| 03/AC03 | ✓      | Exact spans and opaque fallback pass the independent LF/CRLF/EOF, astral, repeated-text, and nested-container checks. |
| 03/AC04 | ✓      | Source-order inline scanning, code spans, links, images, escapes, emphasis, strong, and hard breaks pass.             |
| 03/AC05 | ✓      | HTML-looking Markdown is accepted; parser-delimited HTML blocks remain opaque; no `RawHtmlError` path remains.        |
| 03/AC06 | ✓      | Task metadata and thematic-break policy pass focused and direct checks.                                               |


### Task 04

| AC      | Status | Evidence                                                                                                          |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | Normalized-state models and state-only tests pass.                                                                |
| 04/AC02 | ⚠      | Wrapping and inline codecs pass covered cases, but generated adjacent delimiters can change a valid AST. See C01. |
| 04/AC03 | ⚠      | Lists and containers pass covered cases, but task-bearing block children reparse as code. See C02.                |
| 04/AC04 | ✓      | Heading spacing, descent separators, source-break reuse, and idempotence pass.                                    |
| 04/AC05 | ✓      | Table geometry, parity, code-span pipes, cell spans, and invalid-row handling pass.                               |
| 04/AC06 | ✓      | LF/CRLF/EOF code payload and collision-safe fence tests pass under parser semantic payload ownership.             |


### Task 05

| AC      | Status | Evidence                                                                                          |
| ------- | ------ | ------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | Canonical composition passes covered cases, but C01 and C02 change reparsed structure.            |
| 05/AC02 | ⚠      | Inline and code rendering pass the existing matrix, but C01 changes adjacent delimiter semantics. |
| 05/AC03 | ✓      | Public orchestration propagates documented typed errors and accepts HTML-looking Markdown.        |
| 05/AC04 | ⚠      | Existing golden and idempotence fixtures pass, but independent C01 and C02 semantic probes fail.  |


### Task 06

| AC      | Status | Evidence                                                                                            |
| ------- | ------ | --------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | Collection, recursive discovery, lexical deduplication, and explicit path errors pass.              |
| 06/AC02 | ✓      | Preflight-all-before-write, atomic replacement, stop-on-first-write-error, modes, and cleanup pass. |
| 06/AC03 | ✓      | Snapshots, identity checks, locks, destination safety, fsync, and replacement pass.                 |
| 06/AC04 | ✓      | Status precedence and complete result records pass.                                                 |
| 06/AC05 | ✓      | Streams, sorted records, diagnostics, digest-only mismatches, and exit mapping pass.                |
| 06/AC06 | ✓      | The wrapper captures CWD, delegates through `uv`, and propagates status in temporary smoke.         |
| 06/AC07 | ✓      | Grouped registration, help, CLI contract, and wrapper tests pass.                                   |


### Task 07

| AC      | Status | Evidence                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories pass, but independent mixed-delimiter and task-bearing-child cases are missing and fail. |
| 07/AC02 | ⚠      | Focused Ruff, Ty, and pytest pass; full failures are only the accepted baselines, but C01-C02 remain.      |


## Scope Verification

| File or path                                                                                    | Justification                            | Status                                  |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------- |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py`                       | Task 01 dependency and public contract   | ✓                                       |
| `src/dot_tools/markdown_formatter/{__init__,frontmatter,parser,normalize,render,operations}.py` | Tasks 01-06 formatter pipeline           | ⚠ C01-C02                               |
| `src/dot_tools/cli/{main,markdown}.py`                                                          | Task 06 grouped CLI                      | ✓                                       |
| `.agents/tools/markdown-format.py`                                                              | Task 06 compatibility wrapper            | ✓                                       |
| `tests/markdown_formatter/` and fixtures                                                        | Tasks 02-07 contract and corpus coverage | ⚠ Missing C01-C02 regressions           |
| Revised design and implementation plans                                                         | Human-directed HTML requirement revision | ✓ Reviewed, not modified by this review |
| Implementation journal and prior reviews                                                        | Execution record                         | ✓ Reviewed, not modified by this review |

The worktree already contains the executor's source, test, plan, journal, and prior-review changes shown by the initial
diff. This review added no changes outside this artifact.


## Prior Review Resolution

| Review-22 finding                                                  | Status | Current evidence                                                                                                                                                                                |
| ------------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01: even trailing backslash runs gain an extra semantic backslash | ✓      | LF/CRLF direct runs 1-4 before links, images, emphasis, code, and EOF text preserve reparsed node shape and stable output. Odd table runs remain literal; even runs remain delimiters.          |
| C02: adjacent canonical emphasis atoms merge into a different AST  | ✓      | Exact review-22 cases `*a*_a_`, `**a**__a__`, `*a***b**`, and `**a***b*` preserve sibling kinds in LF and CRLF and converge in three passes. A broader mixed-delimiter case remains as new C01. |
| C03: compatibility table fallback rejects an ordinary paragraph    | ✓      | `a\n--- | ---\n` remains a paragraph without error in LF and CRLF.                                                                                                                              |


## Findings

### Summary

| Finding | Title                                                                | Outcome         |
| ------- | -------------------------------------------------------------------- | --------------- |
| C01     | Generated delimiter context still changes valid sibling emphasis AST | Blocks approval |
| C02     | Task-bearing list children are emitted as code blocks                | Blocks approval |


### Critical

#### C01 Generated delimiter context still changes valid sibling emphasis AST


#### Where

`src/dot_tools/markdown_formatter/normalize.py:105-121,197-200`


#### Issue

The canonical emphasis and strong renderers choose the next marker from only the preceding generated atom. They do not
account for literal text between atoms or the resulting CommonMark flanking context. The independently reproduced valid
input `b"# T\\n\\n*a*a*a*\\n"` is parsed as emphasis, text, emphasis. Formatting emits `b"# T\\n\\n*a*a_a_\\n"`, which
reparses as emphasis, text, with the final `a_a_` left as text. The same boundary defect occurs in table cells.


#### Impact

Formatting changes a valid Markdown AST while remaining idempotent. It can silently remove a later emphasis or strong
atom, violating the inline codec and table-cell semantic-preservation requirements.


#### Fix

Make delimiter selection account for both neighboring source atoms and CommonMark flanking rules, then reparse and
compare
the complete inline shape before accepting canonical bytes. If no safe canonical spelling exists, retain the proven
paragraph or table-cell source unchanged rather than emitting a different AST. Add LF/CRLF regressions for mixed text
and
adjacent emphasis/strong atoms in paragraphs and table cells.


#### Outcome

Blocks approval.


----

### Critical

#### C02 Task-bearing list children are emitted as code blocks


#### Where

`src/dot_tools/markdown_formatter/normalize.py:383-399` and
`src/dot_tools/markdown_formatter/render.py:97-137`


#### Issue

For the parser-owned source `b"# T\\n\\n- [x] task\\n  > quote\\n"`, the list item contains a paragraph and a block
quote. The
normalizer computes the continuation column as six spaces because it includes the task prefix, then the renderer
prefixes
that column to every secondary block child. It emits `b"# T\\n\\n- [x] task\\n\\n      > quote\\n"`; six leading spaces
make the child a
`code_block` on the next parse. The same defect turns a task-bearing secondary fenced-code child into a `code_block`.


#### Impact

Formatting changes a valid list-child AST and changes the rendered meaning of block quotes and fenced code. Task state
is
preserved only while the child structure is lost, violating recursive list and container handling.


#### Fix

Carry the list item's structural child indentation separately from the text continuation column. Render secondary block
quotes, fences, headings, and other block children at the structural list-child column that reparses as the original
container, while keeping ordinary paragraph continuation lines at the task-aware content column. Add LF/CRLF regressions
for task-bearing block quote and fenced-code children with reparsed AST-shape and three-pass assertions.


#### Outcome

Blocks approval.


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction
- `write-docs`: global fallback


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 and C02 are formatter-specific semantic blockers. Review-22 C01-C03 were independently rechecked; the exact prior
cases pass, but the broader whole-plan matrix does not. The configure pytest assertion and repository-wide Ty
diagnostics
remain unrelated baselines under the revised requirement.
