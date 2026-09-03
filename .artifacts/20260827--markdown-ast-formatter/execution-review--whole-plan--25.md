# Execution Review: Generic AST-based Markdown formatter

This independent whole-plan iteration-25 review rechecks the current formatter against the revised plans, journal, and
iteration-24 review. HTML-looking Markdown is accepted, parser-delimited HTML blocks may remain opaque, and
`RawHtmlError`
is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--24.md`


## Scope

**whole-plan - Iteration 25**

The review started with the current worktree diff, independently rechecked review-24 C01, inspected the formatter source
and focused tests, and ran the documented quality and smoke matrix. Only this review artifact was written.


## Issue Summary

- **Critical**:    1
- **Significant**: 2
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                       | Result                                                                                                                                                                                                |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                              | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                                          |
| `uv run pytest tests/markdown_formatter --no-cov`                                      | Passed: 376 tests.                                                                                                                                                                                    |
| `uv run pytest`                                                                        | 689 passed, 1 failed; coverage 86.33%, above the 70% threshold.                                                                                                                                       |
| Full pytest failure                                                                    | Unrelated configure assertion: `@opencode-ai/plugin` is present while the baseline expects `{}`.                                                                                                      |
| `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix` | Passed.                                                                                                                                                                                               |
| `uv run ruff check src tests`                                                          | Passed.                                                                                                                                                                                               |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`            | Passed.                                                                                                                                                                                               |
| `uv run ty check`                                                                      | Failed with 74 diagnostics outside formatter scope; no formatter path was reported.                                                                                                                   |
| Review-24 C01 secondary-only probe                                                     | Passed for LF and CRLF: exact output, two paragraph nodes, task state, and three-pass stability.                                                                                                      |
| Task continuation extension                                                            | Failed for LF and CRLF when a first-paragraph lazy continuation is followed by a secondary paragraph. The continuation loses its active column; nested task items lose their nested active column.    |
| Frontmatter adversarial probe                                                          | Passed finite-real threshold, exponent, non-finite, unsafe-tag, duplicate-key, and lossless round-trip cases.                                                                                         |
| Parser and HTML probe                                                                  | Passed byte spans for repeated, astral, CRLF, table, and nested-container cases. Accepted inline, escaped, block, code, and opaque HTML-looking cases without a rejection path.                       |
| Wrapping, tables, code, and headings probe                                             | Passed exercised code-span, table geometry, LF/CRLF payload, EOF-fence, separator, and idempotence cases. Secondary paragraph wrapping and recognized nested-inline CRLF failures are recorded below. |
| Operations, CLI, and wrapper probe                                                     | Passed focused status, records, snapshots, digests, preflight, lock, atomic replacement, cleanup, partial-commit, grouped-help, and wrapper smoke cases.                                              |
| `git diff --check`                                                                     | Passed.                                                                                                                                                                                               |

The configure pytest failure and repository-wide Ty diagnostics are the only unrelated baselines accepted by this
review.
The findings below are formatter-specific.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                    |
| ------- | ------ | --------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:15`, lockfile, and passing `uv sync`.                       |
| 01/AC02 | ✓      | Formatter package and public models are present.                            |
| 01/AC03 | ✓      | `src/dot_tools/cli/main.py:35-39`, grouped help, and public contract tests. |


### Task 02

| AC      | Status | Evidence                                                                                         |
| ------- | ------ | ------------------------------------------------------------------------------------------------ |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all three APIs and focused tests pass.                                  |
| 02/AC02 | ✓      | `frontmatter.py:90-100`; exact delimiter, missing-close, body, and UTF-8 cases pass.             |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; unsafe YAML, duplicate-key, finite-real, and Unicode cases pass.        |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical ordering, nesting, scalar, escaping, and framing cases pass. |


### Task 03

| AC      | Status | Evidence                                                                                                          |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123`; byte-addressed AST models and entry point pass ownership probes.                              |
| 03/AC02 | ✓      | `parser.py:115-123`; CommonMark-plus-table block and inline cases pass.                                           |
| 03/AC03 | ✓      | `test_parser.py` and direct LF/CRLF, astral, repeated-text, nested-container, and opaque-span probes pass.        |
| 03/AC04 | ✓      | `parser.py:718-999`; scanner, reconstruction, and independent delimiter cases pass.                               |
| 03/AC05 | ✓      | `parser.py:301-303`; HTML-looking text is accepted, HTML blocks may be opaque, and no `RawHtmlError` path exists. |
| 03/AC06 | ✓      | `parser.py:126-140,315-319,1015-1025`; task metadata and thematic-break policy cases pass.                        |


### Task 04

| AC      | Status | Evidence                                                                                                                             |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 04/AC01 | ✓      | Normalized state models and focused normalization tests pass.                                                                        |
| 04/AC02 | ⚠      | Code, table, and ordinary inline cases pass, but recognized nested inline content can retain CRLF; see S02.                          |
| 04/AC03 | ⚠      | Review-24 secondary-only task cases pass, but first-paragraph continuation columns fail when a secondary paragraph follows; see C01. |
| 04/AC04 | ✓      | Heading spacing, descent separators, source-break reuse, and idempotence cases pass.                                                 |
| 04/AC05 | ✓      | Table geometry, framing, parity, code-span pipes, spans, invalid rows, and idempotence cases pass.                                   |
| 04/AC06 | ✓      | Fence collision, info normalization, payload, LF/CRLF, EOF, and semantic-code cases pass.                                            |


### Task 05

| AC      | Status | Evidence                                                                                                                      |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:101-141` emits task continuation content without the required active prefix; see C01.                              |
| 05/AC02 | ⚠      | Inline, table, and code cases pass, but the valid task-list block is rendered with the wrong continuation structure; see C01. |
| 05/AC03 | ✓      | `__init__.py:10-24`; typed errors propagate and HTML-looking Markdown is accepted.                                            |
| 05/AC04 | ⚠      | Existing golden and idempotence tests pass, but the independent task-continuation and nested-inline CRLF cases fail.          |


### Task 06

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-41`; collection, recursive discovery, lexical deduplication, and explicit path errors pass. |
| 06/AC02 | ✓      | `operations.py:91-126,205-234`; preflight, atomic replacement, stop-on-error, mode, and cleanup cases pass.   |
| 06/AC03 | ✓      | `operations.py:44-88`; snapshots, identity, destination safety, locks, fsync, and replacement cases pass.     |
| 06/AC04 | ✓      | `operations.py:133-146`; precedence and complete result records pass.                                         |
| 06/AC05 | ✓      | `operations.py:149-158`; streams, records, diagnostics, digest-only mismatches, and mappings pass.            |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:12-25`; CWD, discovery, delegation, passthrough, and smoke cases pass.      |
| 06/AC07 | ✓      | Grouped registration, help, CLI contract, wrapper tests, and smoke commands pass.                             |


### Task 07

| AC      | Status | Evidence                                                                                                        |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus fixtures pass but omit the failing first-continuation/secondary-paragraph and nested-inline CRLF cases.  |
| 07/AC02 | ⚠      | Focused pytest, Ruff, and formatter Ty pass; accepted baselines remain, but formatter-specific findings remain. |


## Scope Verification

| File or path                                                 | Justification                                           | Status                                      |
| ------------------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------- |
| `pyproject.toml`, `uv.lock`                                  | Task 01 dependency and public contract                  | ✓                                           |
| `src/dot_tools/markdown_formatter/models.py`                 | Task 01 public result models                            | ✓                                           |
| `src/dot_tools/markdown_formatter/__init__.py`               | Tasks 01 and 05 public document pipeline                | ✓                                           |
| `src/dot_tools/markdown_formatter/frontmatter.py`            | Task 02 restricted YAML envelope                        | ✓                                           |
| `src/dot_tools/markdown_formatter/parser.py`                 | Task 03 parsing, spans, ownership, and policy           | ✓                                           |
| `src/dot_tools/markdown_formatter/normalize.py`              | Task 04 normalization, lists, tables, and inline codecs | ⚠ C01, S01, S02                             |
| `src/dot_tools/markdown_formatter/render.py`                 | Task 05 rendering and recursive containers              | ⚠ C01                                       |
| `src/dot_tools/markdown_formatter/operations.py`             | Task 06 operations and replacement safety               | ✓                                           |
| `src/dot_tools/cli/main.py`, `src/dot_tools/cli/markdown.py` | Task 06 grouped CLI                                     | ✓                                           |
| `.agents/tools/markdown-format.py`                           | Task 06 compatibility wrapper                           | ✓                                           |
| `tests/markdown_formatter/` and fixtures                     | Tasks 02 through 07 contract and corpus coverage        | ⚠ Missing regressions for C01, S01, and S02 |
| Revised plans, journal, and prior reviews                    | Review context                                          | ✓ Reviewed, not modified by this review     |


## Prior Review Resolution

| Review-24 finding                                                            | Status | Current evidence                                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01: task-bearing secondary paragraphs use the paragraph continuation column | ✓      | `test_edge_contract.py:1039-1076` and independent LF/CRLF probes pass for top-level and nested secondary paragraphs. Output uses the structural child column, preserves exact secondary text, retains task states, and is stable for three passes. |

The review-24 extension exposed the remaining first-paragraph continuation case. It is recorded as C01 in this review,
not treated as a regression of the resolved secondary-only path.


## Findings

### Summary

| Finding | Title                                                                                        | Outcome         |
| ------- | -------------------------------------------------------------------------------------------- | --------------- |
| C01     | Task-list first-paragraph continuations lose their active column beside secondary paragraphs | Blocks approval |
| S01     | Secondary list paragraphs bypass the 120-code-point wrapper                                  | Blocks approval |
| S02     | Recognized nested inline and link-title content leaks CRLF                                   | Blocks approval |


### Critical

#### C01 Task-list first-paragraph continuations lose their active column beside secondary paragraphs


#### Where

`src/dot_tools/markdown_formatter/normalize.py:361-424` and `src/dot_tools/markdown_formatter/render.py:101-141`


#### Issue

`_list` only separates lazy first-paragraph continuation lines when `len(paragraphs) == 1`. When a first paragraph has a
soft continuation and a later secondary paragraph, the condition is false. The normalized item therefore stores an
embedded newline in `content`, and `_list_item` emits that newline from `item.content` without applying
`continuation_column`.

For the following valid source, the task-aware continuation column is six spaces, but the formatter emits the
continuation
at column zero:

```text
# T

- [x] first
continuation

  second paragraph
```

The nested task case emits `  continuation` instead of the nested active column of eight spaces. Both LF and CRLF inputs
retain the words, task states, paragraph count, and three-pass bytes, but the required structural indentation is wrong.


#### Impact

Formatting changes recognized list structure at the physical source boundary. It violates Task 04 AC03 and Task 05 AC01,
AC02, and AC04. A stable second pass does not make the first pass structurally correct.


#### Fix

Split first-paragraph lazy continuation lines independently of the presence of secondary children. Store them separately
from
`content`, and render them at the active container prefix plus marker and task-prefix width. Apply the same calculation
recursively to nested task items. Add LF and CRLF tests asserting exact bytes, first-paragraph and secondary paragraph
indentation, nested AST shape, task state, text, and three passes.


#### Outcome

Blocks approval.


----

### Significant

#### S01 Secondary list paragraphs bypass the 120-code-point wrapper


#### Where

`src/dot_tools/markdown_formatter/normalize.py:411-413`


#### Issue

Secondary paragraphs are converted directly to `NormalizedParagraph(_inline(...))` without passing through
`_wrap_inline`. A 40-word secondary paragraph produces one 201-code-point content line, while ordinary prose wrapping is
otherwise enabled.


#### Impact

Valid list prose violates Task 04 AC02 and design AC04. The structural two-space prefix does not account for the
failure:
the content itself is 199 code points and exceeds the 120-code-point limit.


#### Fix

Retain the secondary paragraph's owned inline nodes or wrapped lines in normalized state and run the same token-aware
120-code-point wrapper used for other prose before rendering each structural continuation line. Add a long secondary
list
paragraph regression, including a nested-list case and an idempotence assertion.


#### Outcome

Blocks approval.


----

#### S02 Recognized nested inline and link-title content leaks CRLF


#### Where

`src/dot_tools/markdown_formatter/normalize.py:116-120` and `src/dot_tools/markdown_formatter/normalize.py:246-288`


#### Issue

The nested-delimiter fallback appends `node.source` without line-ending normalization. The link-tail codec likewise
carries
source CRLF through a recognized link title. These paragraphs are not opaque, so the preserved CRLF is not protected
opaque
source.

For `# T\r\n\r\n***a\r\nb***\r\n`, parsing reports a recognized paragraph and formatting emits
`# T\n\n***a\r\nb***\n`. A multiline link title shows the same leak.


#### Impact

Recognized nodes violate the design and Task 03/04 canonical-LF contract. The output can be idempotent while still
failing
the required line-ending normalization.


#### Fix

Normalize CRLF and bare CR in every recognized inline fallback and link-tail path, or preserve the complete containing
block
opaque when canonicalization cannot be proven safe. Add LF/CRLF exact-output and ownership tests for nested
emphasis/strong
and multiline link titles.


#### Outcome

Blocks approval.


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, S01, and S02 must be resolved before approval. The review-24 secondary-only finding is resolved. The configure
pytest
failure and repository-wide Ty diagnostics remain unrelated baselines under the revised HTML requirement.
