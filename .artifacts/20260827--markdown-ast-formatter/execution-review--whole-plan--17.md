# Execution Review: Generic AST-based Markdown formatter

This independent iteration-17 review starts from the current worktree diff and checks the revised plans and current
journal. HTML-looking Markdown is accepted, parser-delimited HTML blocks remain opaque, and `RawHtmlError` is not a
contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--16.md`


## Scope

**whole-plan - Iteration 17**

The review began with `git diff`, then inspected the formatter source, focused tests, fixtures, plans, journal, and
review 16. It did not modify source, tests, plans, the journal, or prior reviews. The only authored file is this
artifact.


## Issue Summary

- **Critical**: 4
- **Significant**: 3
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                                                     | Result                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                            | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                                                                                |
| `uv run pytest tests/markdown_formatter --no-cov`                                                                    | Passed: 258 tests.                                                                                                                                                                                                                          |
| `uv run pytest`                                                                                                      | 571 passed, 1 failed; coverage 82.84%. The failure is the unrelated configure baseline below.                                                                                                                                               |
| `uv run ruff check src/dot_tools/markdown_formatter src/dot_tools/cli/markdown.py tests/markdown_formatter --no-fix` | Passed.                                                                                                                                                                                                                                     |
| `uv run ruff check src tests`                                                                                        | Passed.                                                                                                                                                                                                                                     |
| `uv run ty check src/dot_tools/markdown_formatter src/dot_tools/cli/markdown.py tests/markdown_formatter`            | Passed.                                                                                                                                                                                                                                     |
| `uv run ty check`                                                                                                    | Failed with 74 diagnostics, all outside formatter source and tests in the documented repository baseline.                                                                                                                                   |
| Grouped command help and wrapper `--help`                                                                            | Passed.                                                                                                                                                                                                                                     |
| Grouped and wrapper `check` smoke on the canonical operations fixture                                                | Passed: `UNCHANGED`, `summary check SUCCESS 1`.                                                                                                                                                                                             |
| `git diff --check`                                                                                                   | Passed.                                                                                                                                                                                                                                     |
| Review-16 C01-C05/S01 direct matrix                                                                                  | Passed independently for LF and CRLF where applicable, including exact bytes, AST shape, spans, codecs, and three-pass convergence.                                                                                                         |
| Revised HTML matrix                                                                                                  | Passed for inline, block, escaped-angle, code, and opaque HTML-looking input with LF/CRLF coverage. No active formatter source or test defines `RawHtmlError`.                                                                              |
| Independent whole-plan probes                                                                                        | Frontmatter, parser ownership, wrapping, containers, separators, tables, code, operations, statuses, diagnostics, snapshots, locks, atomic replacement, cleanup, CLI, and wrapper paths were exercised. The concrete failures below remain. |

The full pytest failure is:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are confined to the existing PDF, clipboard/Gmail, OpenCode cost/trend, configure,
Jira, and spinner paths. No formatter path appears in that output. These two results are accepted baselines, not
formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, resolved lockfile, and passing `uv sync`.                                                          |
| 01/AC02 | ✓      | Formatter package and public models exist.                                                                                 |
| 01/AC03 | ✓      | `models.py:8-66`, `cli/markdown.py:15-24`, and passing contract tests cover the public status, signature, and CLI surface. |


### Task 02

| AC      | Status | Evidence                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all three APIs and focused tests pass.                                            |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters, missing close, and body preservation pass.                      |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted tags, duplicates, unsafe values, Unicode, and finite-real probes pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, nesting, scalar codecs, thresholds, escaping, and framing pass.        |


### Task 03

| AC      | Status | Evidence                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | Byte-addressed AST and normal source spans pass, but indented-code payload bytes lose CRLF line endings; see C04.                               |
| 03/AC02 | ✓      | `parser.py:108-123,542-618`; CommonMark-plus-table parsing, table ownership, and focused parser tests pass.                                     |
| 03/AC03 | ⚠      | Opaque fallback and ordinary ownership pass for tested cases, but code payload preservation is incomplete; see C04.                             |
| 03/AC04 | ✓      | `parser.py:716-884`; semantic token association, recursive reconstruction, and direct ownership probes pass.                                    |
| 03/AC05 | ✓      | `parser.py:291-292,830`; HTML-looking inline text is accepted, parser-delimited HTML blocks are opaque, and no `RawHtmlError` contract remains. |
| 03/AC06 | ✓      | `parser.py:304-307,1107-1118`; task metadata and source-break policy pass focused and direct tests.                                             |


### Task 04

| AC      | Status | Evidence                                                                                                                 |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| 04/AC01 | ✓      | `normalize.py:18-97`; normalized-state tests pass.                                                                       |
| 04/AC02 | ✗      | Inline delimiter conversion can change semantic content, and link codecs have canonical gaps; see C01, C03, and S03.     |
| 04/AC03 | ✗      | Same-marker nested ordered lists lose their nested AST structure after rendering; see C02.                               |
| 04/AC04 | ⚠      | Downward separator insertion and reuse pass, but ordinary heading spacing after body blocks is short by one LF; see S01. |
| 04/AC05 | ✓      | Table geometry, framing, parity, code-span pipes, invalid rows, source spans, and three-pass output pass.                |


### Task 05

| AC      | Status | Evidence                                                                                                                                                 |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | Canonical rendering and final-newline behavior pass, but indented code changes payload line-ending bytes; see C04.                                       |
| 05/AC02 | ✗      | Inline canonicalization and same-marker nested-list rendering fail semantic preservation; see C01 and C02.                                               |
| 05/AC03 | ✓      | `__init__.py:10-24`; frontmatter, parser, normalizer, renderer, and typed error propagation pass.                                                        |
| 05/AC04 | ⚠      | Golden and idempotence fixtures pass, but they omit the newly exposed delimiter, nested-list, spacing, destination, empty-item, and indented-code cases. |


### Task 06

| AC      | Status | Evidence                                                                                                              |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-40`; direct path resolution, recursive discovery, sorting, deduplication, and explicit errors pass. |
| 06/AC02 | ✓      | `operations.py:90-117,195-230`; preflight, atomic replacement, stop-on-write-error, and cleanup probes pass.          |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshots, identity/mode/type checks, cooperating locks, fsync, and symlink rejection pass.   |
| 06/AC04 | ✓      | `operations.py:123-136,195-230`; status precedence and format/check mappings pass.                                    |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-24`; records, streams, diagnostics, digests, and exits pass.             |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, delegation, passthrough, and discovery failure pass.           |
| 06/AC07 | ✓      | `cli/main.py:35-39`; grouped help and CLI contract tests pass.                                                        |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                         |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories exist, but the fixtures omit the failing delimiter, same-marker nested-list, ordinary-heading-spacing, angle-destination, empty-item, and indented-CRLF cases. |
| 07/AC02 | ✗      | Focused pytest and both Ruff gates pass; formatter-specific findings remain. Full pytest and repository-wide Ty have only the two unrelated baselines recorded above.            |


## Scope Verification

| File or path                                                                                         | Justification                            | Status |
| ---------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py`                            | Task 01 dependency and public contract   | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                                                       | Tasks 01 and 05 orchestration            | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py` and frontmatter fixtures/tests                     | Task 02 restricted YAML                  | ✓      |
| `src/dot_tools/markdown_formatter/parser.py` and parser fixtures/tests                               | Task 03 parsing, spans, and policy       | ⚠      |
| `src/dot_tools/markdown_formatter/normalize.py` and normalization tests                              | Task 04 normalization                    | ⚠      |
| `src/dot_tools/markdown_formatter/render.py` and render/document tests                               | Task 05 rendering                        | ⚠      |
| `src/dot_tools/markdown_formatter/operations.py` and operation tests                                 | Task 06 safe operations                  | ✓      |
| `src/dot_tools/cli/markdown.py`, `src/dot_tools/cli/main.py`, and `.agents/tools/markdown-format.py` | Task 06 CLI, registration, and wrapper   | ✓      |
| `tests/markdown_formatter/` and fixtures                                                             | Tasks 02 through 07 coverage             | ⚠      |
| Revised design and implementation plans                                                              | Human-directed HTML requirement revision | ✓      |
| Implementation journal                                                                               | Execution record                         | ✓      |

The implementation remains within the formatter, dependency, CLI, wrapper, registration, test, fixture, and artifact
scope. The plan and journal changes predate this review and were not edited during it.


## Prior Review Resolution

| Review-16 finding                                        | Status       | Current evidence                                                                                                                                                 |
| -------------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 empty-list fenced code rewrites CRLF payload bytes   | ✓            | `parser.py:349-393`, `render.py:122-132`; independent LF/CRLF payload, AST, and three-pass probes pass.                                                          |
| C02 escaped backticks hide an extra table cell           | ✓            | `parser.py:184-193,597-614`; independent exact-run valid case and escaped-backtick extra-cell rejection pass for LF/CRLF.                                        |
| C03 list-item heading transitions omit the separator     | ✓            | `normalize.py:307-328`, `render.py:113-120`; active-prefix LF/CRLF separator and normalized-state probes pass.                                                   |
| C04 empty link labels bypass destination/title codecs    | ✓            | `normalize.py:113-121`; empty link/image and table-cell codec probes pass and converge.                                                                          |
| C05 task-bearing nested lists lose their child structure | ✓            | `render.py:113-120`; LF/CRLF task-bearing nested-list AST and three-pass probes pass.                                                                            |
| S01 recognized headings retain trailing whitespace       | ✓            | `normalize.py:494-502`; top-level and container trailing-space probes pass.                                                                                      |
| Review-15 embedded-HTML rejection                        | ✓ Superseded | The revised requirement removes rejection. Active source contains parser ownership for `html_block` and `html_inline`, not a rejection policy or `RawHtmlError`. |


## Findings

### Summary

| Finding | Title                                                    | Outcome         |
| ------- | -------------------------------------------------------- | --------------- |
| C01     | Canonical delimiter conversion changes inline semantics  | Blocks approval |
| C02     | Same-marker nested lists collapse after rendering        | Blocks approval |
| C03     | Angle destinations do not escape decoded less-than bytes | Blocks approval |
| C04     | Indented code loses CRLF payload bytes                   | Blocks approval |
| S01     | Ordinary heading spacing is one blank line short         | Blocks approval |
| S02     | Empty list items emit trailing whitespace                | Blocks approval |
| S03     | Link title codec retains noncanonical backslash escapes  | Blocks approval |


### Critical

#### C01: Canonical delimiter conversion changes inline semantics


#### Where

`src/dot_tools/markdown_formatter/normalize.py:99-110,462-473`


#### Issue

The inline codec changes `__` to `**` and `_` to `*` without escaping literal target delimiters in descendant text. An
independent probe formats `b"# T\\n\\n__a**b__\\n"` as `b"# T\\n\\n**a**b**\\n"`. The input has one strong node whose
content is `a**b`; the output reparses as strong content `a` followed by
plain `b**`. The output is stable, but its Markdown meaning is not.


#### Impact

Formatting valid emphasis or strong content changes document semantics. This violates Task 04 AC02 and Task 05 AC02.


#### Fix

Use a delimiter-aware recursive inline encoder. When converting a container delimiter, escape literal target delimiter
characters and backslashes in descendant text, and use the same codec for table cells and link/image labels. Add
semantic-reparse tests for literal `*`, `**`, `_`, and `__` inside emphasis and strong nodes.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C02: Same-marker nested lists collapse after rendering


#### Where

`src/dot_tools/markdown_formatter/normalize.py:306-328` and `src/dot_tools/markdown_formatter/render.py:113-120`


#### Issue

The normalizer retains a nested list, but the renderer emits it immediately below the parent item without the blank
line required when both lists use the same marker family. An independent probe formats:

`b"# T\\n\\n1. parent\\n\\n   2. child\\n"`

as:

`b"# T\\n\\n1. parent\\n   2. child\\n"`

The input reparses as an ordered list containing a nested ordered list. The output reparses as one list item whose
paragraph contains `2. child`; the nested list node is gone. Two formatting passes cannot reveal this because the first
pass has already flattened the tree.


#### Impact

Formatting changes recursive list structure and can discard nested task or ordered-list state. This violates Task 04
AC03
and Task 05 AC02.


#### Fix

Render a structurally safe boundary for same-family nested lists, preserving the active marker column and any task
state.
Add LF/CRLF AST-shape tests for nested bullet, ordered, and task-bearing lists, including multi-digit parent markers.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C03: Angle destinations do not escape decoded less-than bytes


#### Where

`src/dot_tools/markdown_formatter/normalize.py:172-214`


#### Issue

The angle-destination path escapes backslashes and `>`, but not `<`. An independent probe formats
`b"# T\\n\\n[x](<a\\\\<b>)\\n"` as `b"# T\\n\\n[x](<a<b>)\\n"`. The input parser owns a link; the output parser sees
plain text because the unescaped `<` terminates the
angle destination.


#### Impact

Formatting changes a valid link into text and violates the destination codec in Task 04 AC02.


#### Fix

Encode the decoded destination, escaping every backslash, `<`, and `>` required by the angle form. Test links, images,
table cells, escaped destinations, and semantic reparsing.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C04: Indented code loses CRLF payload bytes


#### Where

`src/dot_tools/markdown_formatter/parser.py:293-299` and `src/dot_tools/markdown_formatter/normalize.py:546-554`


#### Issue

Indented code stores `markdown-it-py`'s `token.content`, which has already normalized CRLF to LF. An independent probe
formats `b"# T\\r\\n\\r\\n    x  \\r\\n    y\\r\\n"` as `b"# T\\n\\n```text\\nx  \\ny\\n```\\n"`; the recognized code
payload changes from physical `b"x  \\r\\ny\\r\\n"` to `b"x  \\ny\\n"`. Fenced code preserves this payload distinction,
so the defect is specific to the indented-code path.


#### Impact

Formatting changes bytes inside a recognized code payload, violating the explicit payload-preservation rule in Task 03
AC03 and Task 05 AC01/AC02.


#### Fix

Derive indented-code payload bytes from the original physical source while removing only the proven visual indentation.
Retain LF/CRLF endings and trailing spaces, use an optional span only when the resulting bytes are contiguous, and fall
back to opaque preservation when ownership cannot be proven. Add LF/CRLF and mixed space/tab tests.


#### Outcome

Blocks approval until resolved.


----

### Significant

#### S01: Ordinary heading spacing is one blank line short


#### Where

`src/dot_tools/markdown_formatter/normalize.py:479-505` and `src/dot_tools/markdown_formatter/render.py:237-249`


#### Issue

The normalizer tracks whether a body block precedes a heading, but the renderer always joins adjacent normalized blocks
with `b"\\n\\n"`. An independent probe formats:

`b"# T\\n\\n## A\\nbody\\n## B\\n"`

as:

`b"# T\\n\\n---\\n\\n## A\\n\\nbody\\n\\n## B\\n"`

The `## B` heading has one blank line before it. The revised design requires two blank lines when a non-H1 heading
follows
a body block; the no-body sibling case still requires one.


#### Impact

Canonical heading spacing is wrong for ordinary same-level and upward heading transitions, including container-local
sequences. This violates Task 04 AC04 and Task 05 AC01.


#### Fix

Carry the normalized heading-spacing decision into renderable state, or make block joining consume the container-local
heading state. Emit three LF bytes before a non-H1 heading after body content and two LF bytes for the no-body case,
without
inventing edge blanks.


#### Outcome

Blocks approval until resolved.


----

### Significant

#### S02: Empty list items emit trailing whitespace


#### Where

`src/dot_tools/markdown_formatter/render.py:106-112`


#### Issue

`_list_item` always constructs the first line as `marker + b" " + item.content`. An empty source item `b"# T\\n\\n-\\n"`
therefore formats as `b"# T\\n\\n- \\n"`.


#### Impact

The output contains trailing whitespace in a recognized non-code node, contrary to the canonical-output rule. The same
defect appears on an empty ordered item and an empty parent with nested children.


#### Fix

Emit the marker alone when the item has no task marker or content, then render nested children from that line. Add exact
byte tests for empty unordered, ordered, nested, and LF/CRLF cases.


#### Outcome

Blocks approval until resolved.


----

### Significant

#### S03: Link title codec retains noncanonical backslash escapes


#### Where

`src/dot_tools/markdown_formatter/normalize.py:207-214`


#### Issue

The title path copies source escapes after changing single quotes to double quotes. For example, an independent probe
leaves a literal title backslash in `b"[x](u \\\"a\\\\b\\\")"` as one backslash rather than encoding it as a double
backslash, and changes a single-quoted escaped apostrophe to a double-quoted title containing the unnecessary `\\'`
escape. The output remains parseable but does not implement the specified canonical double-quoted title codec.


#### Impact

`check` can accept a title that is semantically valid but not in the required canonical representation. This leaves the
link/image codec incomplete under Task 04 AC02.


#### Fix

Use parser-owned semantic title text, decode source quote/backslash escapes once, then emit double quotes while escaping
every literal backslash and double quote. Add empty and nonempty link/image tests with both quote styles and escaped
punctuation.


#### Outcome

Blocks approval until resolved.


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global skill
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

Resolve C01, C02, C03, C04, S01, S02, and S03 before approval. Review-16 C01-C05/S01 are independently resolved. The
revised HTML requirement is respected, and the unrelated configure pytest failure plus repository-wide Ty diagnostics
are
accepted baselines only.
