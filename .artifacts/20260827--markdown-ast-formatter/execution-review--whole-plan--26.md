# Execution Review: Generic AST-based Markdown formatter

This independent whole-plan iteration-26 review rechecks the current formatter against the revised design,
implementation
plan, journal, and iteration-25 review. HTML-looking Markdown is accepted, parser-delimited HTML blocks may remain
opaque,
and `RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--25.md`


## Scope

**whole-plan - Iteration 26**

The review started with the current worktree diff, independently rechecked review-25 C01, S01, and S02, inspected all
formatter files recorded by the journal, and ran the whole-plan quality and smoke matrix. Only this review artifact was
written. Source, tests, plans, the journal, and prior reviews were not modified.


## Issue Summary

- **Critical**: 3
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                       | Result                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `uv sync`                                                                              | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                                           |
| `uv run pytest tests/markdown_formatter --no-cov`                                      | Passed: 387 tests.                                                                                                                                                                                     |
| `uv run pytest`                                                                        | 700 passed, 1 failed; coverage 86.34%. The only failure is the accepted configure baseline below.                                                                                                      |
| Full pytest failure                                                                    | `tests/test_configure.py:651`: package contains `{'dependencies': {'@opencode-ai/plugin': '1.18.14'}}`, but the baseline expects `{}`.                                                                 |
| `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix` | Passed.                                                                                                                                                                                                |
| `uv run ruff check src tests`                                                          | Passed.                                                                                                                                                                                                |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`            | Passed.                                                                                                                                                                                                |
| `uv run ty check`                                                                      | Failed with 74 diagnostics; none reported a formatter path. These are the accepted repository Ty baseline diagnostics.                                                                                 |
| Grouped CLI help                                                                       | Passed for `markdown`, `format`, and `check`.                                                                                                                                                          |
| Wrapper help and canonical check                                                       | Passed; canonical fixture reported `UNCHANGED` and `summary check SUCCESS 1`.                                                                                                                          |
| `git diff --check`                                                                     | Passed.                                                                                                                                                                                                |
| Required C01 matrix                                                                    | LF and CRLF first-paragraph lazy continuation with secondary and nested task paragraphs passed. Bare-CR input emitted unindented first-paragraph continuation and required a second pass to repair it. |
| Required S01 matrix                                                                    | Top-level and nested long secondary paragraphs wrapped at 120 code points after structural indentation and converged in three passes.                                                                  |
| Required S02 matrix                                                                    | Nested emphasis/strong and multiline link titles canonicalized LF for LF, CRLF, and bare-CR inputs; recursive spans and three-pass output passed.                                                      |
| Code and opaque exception matrix                                                       | Code payload bytes and parser-delimited opaque bytes passed for LF, CRLF, and bare-CR cases exercised. A separate bare-CR fenced-code normalization defect is C03.                                     |
| Prior semantic matrix                                                                  | 56 LF/CRLF backslash, adjacent delimiter, table-pipe, and false-table-boundary cases passed with semantic shape and three-pass checks.                                                                 |
| Frontmatter matrix                                                                     | 20,011 finite-real samples and unsafe YAML cases passed.                                                                                                                                               |
| Parser ownership/span matrix                                                           | LF, CRLF, astral, repeated, nested-container, table, code, and opaque fixtures passed exact source-slice checks.                                                                                       |
| Table matrix                                                                           | 15 LF/CRLF/bare-CR framing, alignment, escaped-pipe, code-pipe, and short-row cases passed with three-pass checks.                                                                                     |
| Operations and failure injection                                                       | Focused operations, CLI, and wrapper tests passed: 33 tests, including preflight, races, cleanup, replacement failure, partial commits, and status mapping.                                            |
| Accepted HTML matrix                                                                   | Inline-looking, escaped-angle, parser-opaque block, opaque text, and code cases passed without HTML rejection or a `RawHtmlError` path.                                                                |

The configure pytest failure and repository-wide Ty diagnostics are the only unrelated baselines accepted by this
review.
The three findings below are formatter-specific.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                               |
| ------- | ------ | ---------------------------------------------------------------------- |
| 01/AC01 | ✓      | Dependency and lockfile are present; `uv sync` passed.                 |
| 01/AC02 | ✓      | Formatter package and public models are present.                       |
| 01/AC03 | ✓      | `models.py`, grouped CLI registration, and public contract tests pass. |


### Task 02

| AC      | Status | Evidence                                                                                    |
| ------- | ------ | ------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-140` exposes extraction, validation, and serialization APIs.             |
| 02/AC02 | ✓      | `frontmatter.py:90-100` passes exact delimiter, missing-close, body, and UTF-8 checks.      |
| 02/AC03 | ✓      | `frontmatter.py:52-137` passes unsafe YAML, duplicate-key, finite-real, and Unicode checks. |
| 02/AC04 | ✓      | `frontmatter.py:140-235` passes ordering, nesting, scalar, escaping, and framing checks.    |


### Task 03

| AC      | Status | Evidence                                                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | Byte-addressed AST and spans pass the direct matrix, but bare-CR fenced code enters the wrong compatibility path; see C03. |
| 03/AC02 | ⚠      | CommonMark-plus-table ownership passes covered cases, but a valid bare-CR fence is converted to a paragraph; see C03.      |
| 03/AC03 | ⚠      | Exact ownership passes covered cases, but the bare-CR fence boundary is not retained as a code node; see C03.              |
| 03/AC04 | ✓      | Source-order scanner, recursive reconstruction, and inline semantic matrix pass.                                           |
| 03/AC05 | ✓      | HTML-looking Markdown is accepted, HTML blocks may be opaque, and no `RawHtmlError` path exists.                           |
| 03/AC06 | ✓      | Task metadata and thematic-break policy pass focused and direct checks.                                                    |


### Task 04

| AC      | Status | Evidence                                                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | Normalized state models and state-focused tests pass.                                                                      |
| 04/AC02 | ✓      | 120-code-point wrapping, nested inline LF normalization, code, and table matrices pass.                                    |
| 04/AC03 | ⚠      | Bare-CR list continuations lose their active column, and bare-CR container paragraphs duplicate prefixes; see C01 and C02. |
| 04/AC04 | ✓      | Heading spacing, descent separators, source-break reuse, and idempotence pass.                                             |
| 04/AC05 | ✓      | Table framing, alignment, escaped/code pipes, ownership, invalid rows, and idempotence pass.                               |
| 04/AC06 | ⚠      | Fenced and indented code cases pass except bare-CR fence normalization through the compatibility path; see C03.            |


### Task 05

| AC      | Status | Evidence                                                                                                                      |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | Canonical rendering exposes the list and container continuation defects in C01 and C02 and the fence defect in C03.           |
| 05/AC02 | ⚠      | Inline, table, and ordinary code renderers pass; valid bare-CR list/container/code output is not canonical on the first pass. |
| 05/AC03 | ✓      | `__init__.py:10-24` composes the pipeline and propagates typed errors while accepting HTML-looking Markdown.                  |
| 05/AC04 | ⚠      | Existing goldens pass, but direct bare-CR structure probes fail first-pass canonicality or three-pass stability.              |


### Task 06

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-41` passes collection, discovery, sorting, deduplication, and explicit path checks.         |
| 06/AC02 | ✓      | `operations.py:91-126,205-234` passes preflight, atomic replacement, stop-on-error, mode, and cleanup checks. |
| 06/AC03 | ✓      | `operations.py:44-88` passes snapshots, identity, destination safety, locks, fsync, and replacement checks.   |
| 06/AC04 | ✓      | `operations.py:133-146` passes status precedence and complete result-record checks.                           |
| 06/AC05 | ✓      | `operations.py:149-158` passes streams, diagnostics, digest-only mismatches, and exit mappings.               |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:12-25` passes CWD, discovery, delegation, passthrough, and smoke checks.    |
| 06/AC07 | ✓      | Grouped registration, help, CLI contract, wrapper, and failure-injection tests pass.                          |


### Task 07

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus fixtures pass, but they omit the bare-CR list, container, and fence cases that fail the direct matrix. |
| 07/AC02 | ⚠      | Focused pytest, Ruff, and Ty pass; accepted baselines remain, but formatter-specific findings remain.         |


## Scope Verification

| File or path                                                              | Justification                                           | Status                                    |
| ------------------------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py` | Task 01 dependency and public contract                  | ✓                                         |
| `src/dot_tools/markdown_formatter/__init__.py`                            | Tasks 01 and 05 document pipeline                       | ✓                                         |
| `src/dot_tools/markdown_formatter/frontmatter.py`                         | Task 02 restricted YAML envelope                        | ✓                                         |
| `src/dot_tools/markdown_formatter/parser.py`                              | Task 03 parsing, spans, ownership, and policy           | ⚠ C03                                     |
| `src/dot_tools/markdown_formatter/normalize.py`                           | Task 04 normalization, lists, tables, and inline codecs | ⚠ C01, C02                                |
| `src/dot_tools/markdown_formatter/render.py`                              | Task 05 rendering and recursive containers              | ⚠ C01, C02                                |
| `src/dot_tools/markdown_formatter/operations.py`                          | Task 06 operations and replacement safety               | ✓                                         |
| `src/dot_tools/cli/main.py`, `src/dot_tools/cli/markdown.py`              | Task 06 grouped CLI                                     | ✓                                         |
| `.agents/tools/markdown-format.py`                                        | Task 06 compatibility wrapper                           | ✓                                         |
| `tests/markdown_formatter/` and fixtures                                  | Tasks 02 through 07 contract and corpus coverage        | ⚠ Missing bare-CR regressions for C01-C03 |
| Revised plans, journal, and prior reviews                                 | Review context                                          | ✓ Reviewed, not modified by this review   |


## Prior Review Resolution

| Review-25 finding                                                                                 | Status | Current evidence                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01: task-list first-paragraph continuations lose their active column beside secondary paragraphs | ⚠      | Fully passes for LF and CRLF, including nested task items. Bare-CR top-level and nested cases still emit the continuation without the required active indentation; see C01.              |
| S01: secondary list paragraphs bypass the 120-code-point wrapper                                  | ✓      | The direct top-level and nested 50-word cases wrap after structural indentation and converge in three passes; `test_edge_contract.py:1125-1144` covers the nested case.                  |
| S02: recognized nested inline and link-title content leaks CRLF                                   | ✓      | Nested emphasis/strong and multiline link titles pass LF, CRLF, and bare-CR canonical-LF, recursive-span, and three-pass checks; `test_edge_contract.py:1146-1178` covers the new cases. |


## Findings

### Summary

| Finding | Title                                                             | Outcome         |
| ------- | ----------------------------------------------------------------- | --------------- |
| C01     | Bare-CR task continuations lose their required active indentation | Blocks approval |
| C02     | Bare-CR container continuations duplicate structural prefixes     | Blocks approval |
| C03     | Bare-CR fenced code bypasses code normalization                   | Blocks approval |


### Critical

#### C01 Bare-CR task continuations lose their required active indentation


#### Where

`src/dot_tools/markdown_formatter/normalize.py:369-394` and `src/dot_tools/markdown_formatter/render.py:101-105`


#### Issue

`_list_paragraph_source` converts bare CR to LF and produces multiple `source_lines`, but the lazy-continuation branch
is
gated by `b"\\n" in paragraph.source`. For bare-CR input that condition is false. The first continuation remains
embedded
in `item.content`, so the renderer emits it without `continuation_column`.

For the valid source `b"# T\\r\\r- [x] first\\rcontinuation\\r\\r  second paragraph\\r"`, the first pass emits:

```text
# T

- [x] first
continuation

  second paragraph
```

The required task continuation has six spaces. The second pass repairs the line to six spaces, so the first pass is not
canonical and the three-pass check fails. The nested task case similarly emits two spaces instead of the required eight.


#### Impact

Valid recognized list structure is rendered with the wrong active column. This violates design AC04 and
implementation-plan
Task 04 AC03 and Task 05 AC01, AC02, and AC04.


#### Fix

Detect lazy continuation from the normalized `source_lines`, not the raw `paragraph.source`, and apply the same
task-aware
column recursively to nested items. Add exact LF, CRLF, and bare-CR tests asserting output bytes, paragraph shape, task
state, source spans, and three-pass stability.


#### Outcome

Blocks approval.


----

### Critical

#### C02 Bare-CR container continuations duplicate structural prefixes


#### Where

`src/dot_tools/markdown_formatter/normalize.py:717-720` and `src/dot_tools/markdown_formatter/render.py:286-300`


#### Issue

Paragraph normalization strips terminal CR and then splits only on `b"\\n"`. A bare-CR blockquote paragraph therefore
stays
one source line while still containing an embedded `\r> ...` prefix. `_inline` canonicalizes that CR to LF, and
`_prefix_lines` adds the blockquote prefix again to the second logical line.

For `b"# T\\r\\r> quote\\r> continuation\\r"`, the first pass emits
`b"# T\\n\\n> quote\\n> > continuation\\n"`; the second emits
`b"# T\\n\\n> quote\\n> \\n> > continuation\\n"`. The valid recognized container is neither canonical nor
stable. Bare-CR nested list/container continuations show the same boundary failure.


#### Impact

Formatting changes recognized container structure and adds a spurious nested blockquote. This violates design AC03 and
AC04
and implementation-plan Task 04 AC03 and Task 05 AC01, AC02, and AC04.


#### Fix

Normalize CRLF and bare CR to LF before splitting recognized paragraph source, or split with a line-ending-aware routine
that
retains the owned content. Add exact bare-CR blockquote and nested-container AST, byte, and three-pass regressions.


#### Outcome

Blocks approval.


----

### Critical

#### C03 Bare-CR fenced code bypasses code normalization


#### Where

`src/dot_tools/markdown_formatter/parser.py:284-300`


#### Issue

The single-line fence recovery path checks only for the absence of `b"\\n"`. A valid multiline bare-CR fence therefore
enters
that path, and its `.*` compatibility regex spans the CR separators. For
`b"# T\\r\\r~~~bash\\rvalue\\r~~~\\r"`, `markdown-it-py` produces a fence token, but `_blocks` replaces it with a
paragraph. The first output remains `b"# T\\n\\n~~~bash\\nvalue\\n~~~\\n"`; the second output becomes
`b"# T\\n\\n```shell\\nvalue\\n```\\n"`.


#### Impact

The first pass does not apply unconditional code normalization, does not preserve the code AST boundary, and is not
idempotent. This violates design AC08 and implementation-plan Task 03 AC02-AC03, Task 04 AC06, and Task 05 AC01-AC04.


#### Fix

Enter the one-line compatibility path only when the source contains no physical line ending of any supported form. Keep
CR,
LF, and CRLF multiline fences on the normal fence-token path, and add bare-CR tests for marker selection, language
normalization, payload bytes, ownership, and three-pass output.


#### Outcome

Blocks approval.


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, and C03 must be resolved before approval. Review-25 S01 and S02 are independently resolved. Review-25 C01 is
resolved for LF and CRLF but remains open for bare-CR list continuations. The configure pytest failure and
repository-wide Ty
diagnostics remain unrelated baselines under the revised HTML requirement.
