# Execution Review: Generic AST-based Markdown formatter

This independent whole-plan iteration-27 review rechecks the current formatter against the revised plans, journal, and
iteration-26 review. HTML-looking Markdown is accepted, parser-delimited HTML blocks may remain opaque, and
`RawHtmlError`
is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--26.md`


## Scope

**whole-plan - Iteration 27**

The review started with the current worktree diff, independently rechecked iteration-26 C01-C03 across LF, CRLF, and
bare CR, reran the whole-plan semantic and quality matrices, and inspected the formatter implementation and tests. Only
this review artifact was written.


## Issue Summary

- **Critical**: 3
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                    | Result                                                                                                      |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                           | Passed; `markdown-it-py==4.2.0` is resolved.                                                                |
| `uv run pytest tests/markdown_formatter --no-cov`                                   | Passed: 401 tests.                                                                                          |
| `uv run pytest tests/markdown_formatter/test_edge_contract.py --no-cov`             | Passed: 238 tests.                                                                                          |
| Parser, normalization, rendering, and document tests                                | Passed: 117 tests.                                                                                          |
| Operations, CLI, and wrapper tests                                                  | Passed: 33 tests.                                                                                           |
| Whole-plan keyword matrix                                                           | Passed: 185 selected tests, 216 deselected.                                                                 |
| C01-C03 direct matrix                                                               | Passed for task/list continuations, containers, and fenced code across LF, CRLF, and bare CR.               |
| Prior semantic matrices                                                             | Passed for inline, list, heading, separator, table, code, and opaque cases covered by the focused suite.    |
| Frontmatter matrix                                                                  | Passed: 20,011 finite-real round trips and 9 unsafe YAML cases.                                             |
| Accepted HTML matrix                                                                | Passed: 15 inline, escaped, block, opaque, and code cases across LF, CRLF, and bare CR.                     |
| Operations and failure injection                                                    | Passed: preflight, race, replacement failure, partial commit, cleanup, and status mappings.                 |
| `uv run pytest`                                                                     | 714 passed, 1 failed. The only failure is the accepted configure baseline at `tests/test_configure.py:651`. |
| Full pytest failure                                                                 | The baseline expects an empty OpenCode dependency mapping, but `@opencode-ai/plugin` `1.18.14` is present.  |
| `uv run ruff check src tests`                                                       | Passed.                                                                                                     |
| Focused `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                     |
| `uv run ty check`                                                                   | Failed with 74 repository diagnostics; none reference formatter paths.                                      |
| Grouped CLI help                                                                    | Passed for `markdown`, `format`, and `check`.                                                               |
| Wrapper help and canonical fixture check                                            | Passed; wrapper check reported `UNCHANGED` and `summary check SUCCESS 1`.                                   |
| `git diff --check`                                                                  | Passed.                                                                                                     |
| Adversarial direct probes                                                           | Found C04, C05, and C06 below.                                                                              |

The configure pytest failure and repository-wide Ty diagnostics are the only unrelated baselines accepted by this
review.
The three findings below are formatter-specific.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                          |
| ------- | ------ | --------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:15`, `uv.lock`, and the successful `uv sync` run.                 |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/` contains the package and public models.       |
| 01/AC03 | ✓      | `models.py`, grouped CLI registration, and `test_markdown_cli_contract.py:23-42`. |


### Task 02

| AC      | Status | Evidence                                                                              |
| ------- | ------ | ------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-140` exposes extraction, validation, and serialization APIs.       |
| 02/AC02 | ✓      | `frontmatter.py:89-117` and `test_frontmatter.py` exact delimiter and UTF-8 coverage. |
| 02/AC03 | ✓      | `frontmatter.py:52-137` and the finite-real and unsafe-YAML matrices.                 |
| 02/AC04 | ✓      | `frontmatter.py:140-235` and exact ordering, nesting, scalar, and escaping tests.     |


### Task 03

| AC      | Status | Evidence                                                                                                    |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:31-105` provides the AST and byte spans; C05 exposes a missed bare-CR hard-break ownership case. |
| 03/AC02 | ⚠      | CommonMark-plus-table parsing is present at `parser.py:117`, but C05 is not normalized on the first pass.   |
| 03/AC03 | ⚠      | Exact ownership passes covered cases, but bare-CR hard-break ownership is incomplete in C05.                |
| 03/AC04 | ✓      | `parser.py:719-1000` source-order scanning and recursive reconstruction pass the semantic matrix.           |
| 03/AC05 | ✓      | HTML-looking text is accepted, HTML blocks may be opaque, and no `RawHtmlError` path exists.                |
| 03/AC06 | ✓      | `parser.py:1016-1027` and thematic-break tests pass.                                                        |


### Task 04

| AC      | Status | Evidence                                                                                                         |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | Normalized state models and `test_normalize.py` pass.                                                            |
| 04/AC02 | ⚠      | Wrapping and ordinary hard breaks pass, but bare-CR hard breaks fail first-pass canonicalization in C05.         |
| 04/AC03 | ⚠      | Task continuations pass all three line endings, but adjacent normalized unordered lists fail idempotence in C04. |
| 04/AC04 | ⚠      | Heading and separator matrices pass except the bare-CR opaque boundary in C06.                                   |
| 04/AC05 | ✓      | Table framing, alignment, escaping, ownership, invalid rows, and idempotence pass.                               |
| 04/AC06 | ✓      | Fenced and indented code normalization, including the prior bare-CR fence case, passes.                          |


### Task 05

| AC      | Status | Evidence                                                                                           |
| ------- | ------ | -------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | Canonical rendering is not stable for the list and opaque-boundary cases in C04 and C06.           |
| 05/AC02 | ⚠      | Inline, table, and ordinary code matrices pass; C04-C06 remain first-pass or idempotence failures. |
| 05/AC03 | ✓      | `__init__.py:10-24` composes the pipeline and propagates the revised typed error contract.         |
| 05/AC04 | ⚠      | Existing goldens pass, but the adversarial C04-C06 cases are not canonical.                        |


### Task 06

| AC      | Status | Evidence                                                                                                     |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------ |
| 06/AC01 | ✓      | `operations.py:21-41` and the collection and discovery tests pass.                                           |
| 06/AC02 | ✓      | `operations.py:91-126,205-234` and failure-injection tests pass.                                             |
| 06/AC03 | ✓      | `operations.py:44-88` covers snapshots, safety, locks, fsync, and replacement.                               |
| 06/AC04 | ✓      | `operations.py:133-146` and complete result-record tests pass.                                               |
| 06/AC05 | ✓      | `operations.py:149-158`, CLI streams, digest diagnostics, and exit mappings pass.                            |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25` passes wrapper CWD, delegation, help, and canonical-fixture checks. |
| 06/AC07 | ✓      | Grouped registration, CLI contracts, wrapper tests, and help smoke pass.                                     |


### Task 07

| AC      | Status | Evidence                                                                                                     |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------ |
| 07/AC01 | ⚠      | Corpus fixtures pass, but they omit the mixed-marker, bare-CR hard-break, and opaque-boundary regressions.   |
| 07/AC02 | ⚠      | Focused pytest, Ruff, and Ty pass; formatter-specific findings remain despite accepted repository baselines. |


## Scope Verification

| File or path                                                              | Justification                                           | Status |
| ------------------------------------------------------------------------- | ------------------------------------------------------- | ------ |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py` | Task 01 dependency and public contract                  | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                            | Tasks 01 and 05 document pipeline                       | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                         | Task 02 restricted YAML envelope                        | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                              | Task 03 parsing, spans, ownership, and policy           | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                           | Task 04 normalization, lists, tables, and inline codecs | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                              | Task 05 rendering and recursive containers              | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                          | Task 06 operations and replacement safety               | ✓      |
| `src/dot_tools/cli/main.py`, `src/dot_tools/cli/markdown.py`              | Task 06 grouped CLI                                     | ✓      |
| `.agents/tools/markdown-format.py`                                        | Task 06 compatibility wrapper                           | ✓      |
| `tests/markdown_formatter/` and fixtures                                  | Tasks 02 through 07 contract and corpus coverage        | ✓      |
| Revised plans, journal, and prior reviews                                 | Review context only                                     | ✓      |


## Prior Review Resolution

| Review-26 finding                                                  | Status | Current evidence                                                                                                                     |
| ------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| C01: bare-CR task continuations lose active indentation            | ✓      | `normalize.py:369-394` now splits normalized source lines; top-level and nested task probes pass for LF, CRLF, and bare CR.          |
| C02: bare-CR container continuations duplicate structural prefixes | ✓      | `parser.py:697-710`, `render.py:286-300`, and container probes pass all three line endings without `> >` duplication.                |
| C03: bare-CR fenced code bypasses normalization                    | ✓      | `parser.py:290-404` keeps the valid multiline fence on the normal path; marker, info, payload, ownership, and stability probes pass. |


## Findings

### Summary

| Finding | Title                                                                     | Outcome         |
| ------- | ------------------------------------------------------------------------- | --------------- |
| C04     | Adjacent unordered lists become non-idempotent after marker normalization | Blocks approval |
| C05     | Bare-CR hard breaks are not recognized on the first pass                  | Blocks approval |
| C06     | Bare-CR opaque boundaries collapse before generated separators            | Blocks approval |


### Critical

#### C04 Adjacent unordered lists become non-idempotent after marker normalization


#### Where

`src/dot_tools/markdown_formatter/normalize.py:703-710` and `src/dot_tools/markdown_formatter/render.py:236-253`


#### Issue

For the valid source `b"# T\n\n* a\n+ b\n"`, the parser produces adjacent bullet-list blocks because the source uses
different
unordered markers. Normalization correctly changes both markers to `-`, but rendering joins the two normalized blocks
with a blank line. The first pass is `b"# T\n\n- a\n\n- b\n"`; reparsing merges the now same-family lists and the second
pass is
`b"# T\n\n- a\n- b\n"`. The same failure occurs for LF, CRLF, and bare CR input.


#### Impact

The formatter violates the required idempotence of canonical output and changes the structural list boundary between
passes. This fails design AC04 and implementation-plan Task 04 AC03 plus Task 05 AC01, AC02, and AC04.


#### Fix

Coalesce adjacent normalized unordered lists that become the same canonical list, or emit a boundary that reparses as
the
same structure. Add exact LF, CRLF, and bare-CR tests for mixed `-`, `*`, and `+` markers and assert identical first,
second, and third passes.


#### Outcome

Blocks approval.


----

### Critical

#### C05 Bare-CR hard breaks are not recognized on the first pass


#### Where

`src/dot_tools/markdown_formatter/parser.py:833-840`


#### Issue

The hard-break scanner accepts backslash-plus-LF, two spaces plus LF, and the CRLF variants through `\r?\n`, but it does
not accept a bare CR. For the valid source `b"# T\r\ra  \rb\r"`, `markdown-it-py` recognizes the paragraph, but the
scanner
records one text node rather than a hard-break node. The first pass emits `b"# T\n\na  \nb\n"`; the second pass
recognizes
the two-space LF break and emits `b"# T\n\na\\\nb\n"`.


#### Impact

The first pass leaves trailing spaces in recognized Markdown and fails the required canonical hard-break spelling. This
violates design AC03 and AC04 and implementation-plan Task 04 AC02 plus Task 05 AC01, AC02, and AC04.


#### Fix

Make the exact hard-break matcher accept bare CR as a physical line ending, preserve its source span, and normalize it
to
one backslash plus LF. Add LF, CRLF, and bare-CR tests for both hard-break spellings and three-pass stability.


#### Outcome

Blocks approval.


----

### Critical

#### C06 Bare-CR opaque boundaries collapse before generated separators


#### Where

`src/dot_tools/markdown_formatter/render.py:247-251,256-268`


#### Issue

For `b"# T\r\r\x00 ext\r## H\r"`, the unknown paragraph is correctly preserved as opaque and the heading transition
correctly
gets a generated separator. The join logic counts the terminal bare CR as one line break and adds only one LF. That
turns
the opaque ending plus the added byte into CRLF, not a blank-line boundary, producing the first output
`b"# T\n\n\x00 ext\r\n---\n\n## H\n"`. On reparse, `\x00 ext\r\n---` is interpreted as a setext H2, so the second pass
adds another separator:
`b"# T\n\n\x00 ext\r\n---\n\n---\n\n## H\n"`.


#### Impact

The generated separator changes the parser boundary around preserved opaque bytes and canonical output is not
idempotent.
This violates design AC03 and AC06 and implementation-plan Task 04 AC04 plus Task 05 AC01, AC02, and AC04.


#### Fix

Make separator insertion line-ending-aware without rewriting opaque bytes. When an opaque block ends in bare CR, add
enough
LF bytes after that preserved span to create a real blank line before the generated separator. Add bare-CR
opaque-to-heading
tests that assert source preservation, AST boundaries, and three-pass stability.


#### Outcome

Blocks approval.


## Skills Applied

- `review-implementation-execution`: global skill
- `write-docs`: global skill
- `engineer-reviewer`: global agent definition
- `editing`, `markdown`, and `git-safety`: global instructions


## Decision

**BLOCKED - CHANGES REQUIRED**

C04, C05, and C06 must be resolved before approval. Review-26 C01-C03 pass independently for LF, CRLF, and bare CR.
The configure pytest failure and repository-wide Ty diagnostics remain unrelated baselines under the revised HTML
requirement.
