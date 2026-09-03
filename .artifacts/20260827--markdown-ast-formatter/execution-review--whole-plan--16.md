# Execution Review: Generic AST-based Markdown formatter

This independent iteration-16 review starts from the current worktree diff and checks the revised approved plans and
journal. The embedded-HTML rejection requirement is not used: HTML-looking Markdown is expected to be accepted.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--15.md`


## Scope

**whole-plan - Iteration 16**

The review began with the current diff, then expanded to the complete formatter implementation, tests, fixtures, and
execution record. It did not modify source, tests, plans, the journal, or prior reviews. Review-15's HTML finding is
superseded by the 2026-09-03 requirement revision.


## Issue Summary

- **Critical**:    5
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                                                     | Result                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                            | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                        |
| `uv run pytest tests/markdown_formatter --no-cov`                                                                    | Passed: 247 tests.                                                                                                                                                  |
| `uv run pytest`                                                                                                      | 560 passed, 1 failed; coverage 82.82%. The failure is the unrelated configure baseline below.                                                                       |
| `uv run ruff check src/dot_tools/markdown_formatter src/dot_tools/cli/markdown.py tests/markdown_formatter --no-fix` | Passed.                                                                                                                                                             |
| `uv run ruff check src tests`                                                                                        | Passed.                                                                                                                                                             |
| `uv run ty check src/dot_tools/markdown_formatter src/dot_tools/cli/markdown.py tests/markdown_formatter`            | Passed.                                                                                                                                                             |
| `uv run ty check`                                                                                                    | Failed with 74 diagnostics confined to the documented repository baseline outside formatter paths.                                                                  |
| Grouped command help and wrapper `--help`                                                                            | Passed.                                                                                                                                                             |
| Wrapper `check` smoke on a canonical fixture                                                                         | Passed: `UNCHANGED`, `summary check SUCCESS 1`.                                                                                                                     |
| `git diff --check`                                                                                                   | Passed.                                                                                                                                                             |
| Independent frontmatter probe                                                                                        | Passed thresholds, subnormal, maximum finite, signed-zero, scientific, and invalid-value cases.                                                                     |
| Independent HTML and former C02-C04 probes                                                                           | HTML-looking LF/CRLF, escaped-angle, code, and opaque cases passed. Former tab-indented code, mismatched code-span table, and LF empty-list structure cases passed. |
| Independent three-pass probe                                                                                         | Covered canonical cases converge. The findings below expose semantic or byte-preservation failures that existing three-pass tests do not cover.                     |

The full pytest failure is:

```text
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty run reports only the existing PDF, clipboard/Gmail, OpenCode cost/trend, configure, Jira, and
spinner diagnostics. No formatter source or formatter test path appears in that output. These two baselines are not
formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, `uv.lock`, and the passing `uv sync` run.                                          |
| 01/AC02 | ✓      | Formatter package and public models exist.                                                                 |
| 01/AC03 | ✓      | `models.py:8-66`, `cli/markdown.py:15-24`, and contract tests cover statuses, signatures, and CLI mapping. |


### Task 02

| AC      | Status | Evidence                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; extraction, validation, and serialization tests pass.                             |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters, missing close, and body preservation pass.                      |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted tags, duplicates, unsafe values, Unicode, and finite-real probes pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, nesting, scalar codecs, thresholds, escaping, and framing pass.        |


### Task 03

| AC      | Status | Evidence                                                                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123`; byte-addressed AST models and span tests pass for normal cases.                                                                        |
| 03/AC02 | ⚠      | CommonMark blocks and inline ownership pass, but escaped backticks make the table cell splitter disagree with parser semantics; see C02.                   |
| 03/AC03 | ⚠      | Exact ownership and opaque fallback pass for covered cases, but the escaped-backtick table boundary is not proven; see C02.                                |
| 03/AC04 | ✓      | `parser.py:697-865`; token-driven inline precedence and recursive reconstruction pass for the exercised corpus.                                            |
| 03/AC05 | ✓      | `parser.py:274-276,811-865`; HTML-looking inline text is accepted, parser-delimited HTML blocks are opaque, and no `RawHtmlError` remains in the contract. |
| 03/AC06 | ✓      | `parser.py:1072-1096`; task metadata and thematic-break policy tests pass.                                                                                 |


### Task 04

| AC      | Status | Evidence                                                                                                                          |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94`; normalized-state tests pass.                                                                                |
| 04/AC02 | ⚠      | 120-codepoint wrapping and code-span cases pass, but empty links bypass canonical destination and title encoding; see C04.        |
| 04/AC03 | ⚠      | Basic list order and tasks pass, but a task-bearing parent loses a nested child after reparsing; see C05.                         |
| 04/AC04 | ⚠      | Heading spacing works in block quotes, but downward transitions between list-item headings omit the generated separator; see C03. |
| 04/AC05 | ✗      | Table geometry and normal code-span pipes pass, but escaped backticks hide an extra physical cell; see C02.                       |


### Task 05

| AC      | Status | Evidence                                                                                                                  |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✗      | `render.py:117-125`; empty-list fenced code converts CRLF payload line endings to LF; see C01.                            |
| 05/AC02 | ✗      | Canonical inline, table, list, separator, and fence fixtures pass, but C01-C05 expose untested boundary failures.         |
| 05/AC03 | ✓      | `__init__.py:10-24`; extraction, parse, normalize, render, and typed document errors compose correctly.                   |
| 05/AC04 | ⚠      | Golden and idempotence tests pass for the covered corpus, but they omit the failing semantic and byte-preservation cases. |


### Task 06

| AC      | Status | Evidence                                                                                                         |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-40`; path resolution, recursive discovery, sorting, deduplication, and explicit errors pass.   |
| 06/AC02 | ✓      | `operations.py:90-117,195-230`; preflight, atomic replacement, stop-on-write-error, and cleanup tests pass.      |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshots, identity checks, locks, fsync, mode preservation, and symlink rejection pass. |
| 06/AC04 | ✓      | `operations.py:123-136,195-230`; status precedence and format/check mapping tests pass.                          |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-24`; records, streams, diagnostics, digests, and exits pass.        |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, discovery, delegation, and passthrough smoke pass.        |
| 06/AC07 | ✓      | `cli/main.py:35-39` and grouped/wrapper contract tests pass.                                                     |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                      |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories exist, but the corpus omits escaped-backtick tables, empty-link codecs, task-bearing nested lists, list-item heading transitions, and CRLF empty-list code. |
| 07/AC02 | ✗      | Focused pytest and both Ruff gates pass, but formatter-specific C01-C05 remain. Full pytest and repository Ty have only the two unrelated baselines recorded above.           |


## Scope Verification

| File or path                                                            | Justification                      | Status |
| ----------------------------------------------------------------------- | ---------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency                 | ✓      |
| `uv.lock`                                                               | Task 01 dependency lock            | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public models              | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 orchestration      | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML            | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, and policy | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization              | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering                  | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 safe operations            | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter              | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration       | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility wrapper      | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 coverage       | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                   | ✓      |

The implementation stays within the formatter, dependency, CLI, wrapper, registration, test, fixture, and journal
scope. The design and implementation plan changes are the human-directed revised review inputs, not scope creep.


## Prior Review Resolution

| Prior finding                                              | Status                 | Current evidence                                                                                                                                           |
| ---------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Review 15 C01: escaped HTML-looking text is rejected       | ✓ Superseded           | The revised design removes this rejection. `parser.py` has no `RawHtmlError`; accepted HTML-looking LF/CRLF probes pass.                                   |
| Review 15 C02: tab-indented code gains a structural tab    | ✓ Resolved             | `parser.py:277-283,358-366` uses semantic code content; `test_edge_contract.py:54-70` passes LF and CRLF.                                                  |
| Review 15 C03: mismatched code-span runs split table pipes | ✓ Resolved             | `parser.py:153-166,581-590` requires matching runs; `test_edge_contract.py:74-89` passes exact output and three passes.                                    |
| Review 15 C04: empty list items lose nested code structure | ✓ Resolved as reported | `render.py:117-125` keeps the fence under the item for LF; `test_edge_contract.py:93-104` passes the former structural case. New CRLF payload loss is C01. |


## Findings

### Summary

| Finding | Title                                                     | Outcome         |
| ------- | --------------------------------------------------------- | --------------- |
| C01     | Empty-list fenced code rewrites CRLF payload bytes        | Blocks approval |
| C02     | Escaped backticks hide an extra table cell                | Blocks approval |
| C03     | List-item heading transitions omit the required separator | Blocks approval |
| C04     | Empty link labels bypass the canonical destination codec  | Blocks approval |
| C05     | Task-bearing nested lists lose their child structure      | Blocks approval |
| S01     | Recognized headings retain trailing whitespace            | Blocks approval |


### Critical

#### C01 Empty-list fenced code rewrites CRLF payload bytes


#### Where

`src/dot_tools/markdown_formatter/render.py:117-125`


#### Issue

For an empty list item whose first child is fenced code, `_list_item` calls `.splitlines()` on the rendered code and
then
joins the resulting list with LF separators. The input
`b'# T\r\n\r\n-\r\n  ```text\r\n  x  \r\n  ```\r\n'` has parser payload `b'x  \r\n'`, but the first output reparses with
payload `b'x  \n'`.


#### Impact

This changes code payload bytes in a recognized node. It violates the explicit LF/CRLF code-payload preservation
contract even though the output reaches a stable byte fixed point.


#### Fix

Inline the opening fence without splitting and rejoining the rendered payload, or carry physical line endings through
the
empty-item path. Add an exact CRLF payload assertion alongside the existing structural idempotence test.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C02 Escaped backticks hide an extra table cell


#### Where

`src/dot_tools/markdown_formatter/parser.py:143-167,569-599` and `src/dot_tools/markdown_formatter/normalize.py:378-416`


#### Issue

The physical table splitters treat every backtick run as a possible code-span opener without checking whether the opener
backtick is escaped. For
`b'| h | z |\n| --- | --- |\n| \\`a|b\\` | c |\n'`, the unescaped pipe creates an extra physical data cell, but
the formatter considers `\\`a|b\\`` one cell and accepts the row. It emits
`b'| \\`a|b\\` | c   |\n'` instead of raising the required extra-cell error.


#### Impact

The formatter's physical ownership model disagrees with CommonMark table parsing and fails the rule that an extra,
including empty, data cell is never dropped. The emitted Markdown has different table-cell boundaries under the parser.


#### Fix

Make the shared physical splitter recognize code spans only from unescaped backticks and matching opener lengths. Use
that
same rule in parser ownership, normalization, and rendering, then add escaped-backtick and unescaped-pipe LF/CRLF tests.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C03 List-item heading transitions omit the required separator


#### Where

`src/dot_tools/markdown_formatter/normalize.py:305-320`


#### Issue

Each non-list child of a list item is passed to `_normalize_blocks` as a one-element list. Heading state therefore
resets
between siblings. For `b'# T\n\n- # H1\n  ## H2\n'`, the formatter emits
`b'# T\n\n- # H1\n\n  ## H2\n'` with no generated `---` transition.


#### Impact

This violates the separator rule for a downward heading transition in the same recognized container. The output is
idempotent but does not represent the required normalized AST state.


#### Fix

Normalize all list-item block children in source order with shared heading state, including the active continuation
prefix,
or explicitly carry heading state across the per-child normalization calls. Add a nested-list-item heading fixture that
asserts the separator bytes and three-pass output.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C04 Empty link labels bypass the canonical destination codec


#### Where

`src/dot_tools/markdown_formatter/normalize.py:111-119`


#### Issue

The link/image codec treats `not child_source` as an inability to prove ownership. An owned empty link has
`child_source == b''`, so `[](foo\\bar 'title')` is emitted unchanged instead of using the required angle destination,
escaped backslash, and double-quoted title form.


#### Impact

The formatter accepts a parser-owned link but does not produce canonical output. `check` can report this noncanonical
input
as unchanged, and the destination/title contract is incomplete for a valid empty label.


#### Fix

Distinguish an absent ownership proof from a proven empty label. Run the destination and title codec for the empty-label
case, and add empty-link and empty-image tests where parser ownership is available.


#### Outcome

Blocks approval until resolved.


----

### Critical

#### C05 Task-bearing nested lists lose their child structure


#### Where

`src/dot_tools/markdown_formatter/normalize.py:298-323` and `src/dot_tools/markdown_formatter/render.py:109-116,138-142`


#### Issue

The renderer places a nested list below a task-bearing parent at the calculated six-column continuation offset. For
`b'# T\n\n- [x] first\n  - [ ] nested\n'`, the first output is
`b'# T\n\n- [x] first\n      - [ ] nested\n'`. CommonMark reparses that marker as lazy paragraph text rather than a
nested list; the third formatting pass
then emits only the blank continuation line and loses the child.


#### Impact

Formatting changes a valid recursive list tree and drops a nested task item on repeated formatting. This violates list
order/task-state preservation and the three-pass semantic idempotence requirement.


#### Fix

Choose a canonical representation that both preserves the approved task-aware content column and reparses as the same
nested list, or preserve the containing list opaque when that representation cannot be proven. Add LF/CRLF tests that
compare nested task AST shape, task state, exact output, and three formatting passes.


#### Outcome

Blocks approval until resolved.


### Significant

#### S01 Recognized headings retain trailing whitespace


#### Where

`src/dot_tools/markdown_formatter/parser.py:420-445` and `src/dot_tools/markdown_formatter/normalize.py:484-492`


#### Issue

Heading normalization derives content from the raw first source line and does not remove trailing structural whitespace.
`format_document(b'# H   \n')` returns `b'# H   \n'`.


#### Impact

The result violates the revised plan's canonical-output rule that trailing whitespace is absent outside opaque spans and
code payloads. The parser-owned semantic heading content is not the source used by the normalizer.


#### Fix

Use the parser-owned heading inline content when normalizing, or remove only heading structural trailing whitespace
before
encoding the heading. Add ATX and container-local trailing-whitespace tests.


#### Outcome

Blocks approval until resolved.


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction
- `write-docs`: global skill


## Decision

**BLOCKED - CHANGES REQUIRED**

Resolve C01, C02, C03, C04, C05, and S01 before approval. The revised HTML requirement is correctly implemented and
Review-15
C01 is superseded. The unrelated configure pytest failure and repository-wide Ty baseline are documented only and do not
replace the formatter-specific blockers.
