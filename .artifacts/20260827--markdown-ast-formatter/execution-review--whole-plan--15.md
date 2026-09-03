# Execution Review: Generic AST-based Markdown formatter

This independent iteration-15 review starts from the current worktree diff, rechecks review 14, and runs plan-wide
formatter, safety, CLI, wrapper, and quality-gate checks.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--14.md`


## Scope

**whole-plan - Iteration 15**

The review covers the current formatter source and tests, frontmatter, parser ownership and masking, normalization,
rendering, document orchestration, file operations, CLI, wrapper, dependency, fixtures, and recorded execution changes.
The review started with the current diff. This review did not modify source, tests, plans, the implementation journal,
or
prior reviews.


## Issue Summary

- **Critical**:    4
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                            | Result                                                                                                                                                                                          |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `git diff --stat`, `git diff --check`                                       | Current implementation diff inspected first; whitespace check passed.                                                                                                                           |
| `uv sync`                                                                   | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                                                    |
| `uv run pytest tests/markdown_formatter --no-cov`                           | Passed: 233 tests.                                                                                                                                                                              |
| `uv run pytest`                                                             | 546 passed, 1 failed, 2 warnings; coverage 82.60%. The only failure is the unrelated configure baseline.                                                                                        |
| `uv run ruff check src tests`                                               | Passed.                                                                                                                                                                                         |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                                                                                                         |
| `uv run ty check`                                                           | Failed with 74 independently confirmed baseline diagnostics outside formatter paths.                                                                                                            |
| `uv run dt markdown --help`, grouped format/check help, wrapper `--help`    | Passed.                                                                                                                                                                                         |
| Grouped and wrapper check/format smoke on the canonical operations fixture  | Passed; each reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                                                                                                  |
| Review-14 C01 EOF matrix                                                    | Passed LF and CRLF top-level, quote, list, quote-list, and nested-quote cases. Original and reparsed `CodePayload.payload`, exact output bytes, and second and third formatting passes matched. |
| Independent escaped-HTML probe                                              | Failed: `\\<div>` raises `RawHtmlError` although MarkdownIt identifies it as ordinary escaped text. See C01.                                                                                    |
| Independent indented-tab code probe                                         | Failed: MarkdownIt payload is `b'code\\n'`, but the formatter emits and reparses `b'\\tcode\\n'`. See C02.                                                                                      |
| Independent complex table code-pipe probe                                   | Failed with `TableError: table row has too many cells` for `` ``a`b|c`` ``. See C03.                                                                                                            |
| Independent empty-list nested-fence probe                                   | Failed three-pass structural stability: the first pass keeps the fence under the list item, while the second pass makes it top-level. See C04.                                                  |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are confined to the documented PDF, clipboard/Gmail, OpenCode cost/trend,
configure, Jira, and spinner baselines. No formatter source or formatter test path appears in that output. These two
independently confirmed baselines are not formatter blockers.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                 |
| ------- | ------ | -------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, `uv.lock`; `uv sync` passed.                                                     |
| 01/AC02 | ✓      | Formatter package and public model modules exist.                                                        |
| 01/AC03 | ✓      | `tests/markdown_formatter/test_markdown_cli_contract.py:23-42`; grouped CLI tests and help smoke passed. |


### Task 02

| AC      | Status | Evidence                                                                                                              |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; extraction, validation, and serialization APIs are exercised.                                |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiter, missing-close, and body-preservation tests pass.                            |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted tags, duplicate keys, unsafe values, invalid Unicode, and finite-real tests pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical ordering, escaping, nesting, thresholds, and framing tests pass.                  |


### Task 03

| AC      | Status | Evidence                                                                                                                           |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:35-110`; byte-addressed AST models and source-span tests pass.                                                          |
| 03/AC02 | ⚠      | CommonMark blocks and inline forms pass focused tests, but indented code with a tab changes the semantic payload; see C02.         |
| 03/AC03 | ✓      | `parser.py:469-491,1019-1030`; exact span, recursive reconstruction, CRLF, astral, and opaque tests pass.                          |
| 03/AC04 | ✓      | `parser.py:658-826`; token-driven inline precedence and exact ownership tests pass for the exercised inline corpus.                |
| 03/AC05 | ✗      | `parser.py:1039-1085` scans the original text without excluding escaped `<`; valid escaped HTML-looking text is rejected; see C01. |
| 03/AC06 | ✓      | `parser.py:1104-1115`; task metadata and thematic-break transition tests pass.                                                     |


### Task 04

| AC      | Status | Evidence                                                                                                                        |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-95`; normalized state models and state-only tests pass.                                                        |
| 04/AC02 | ✓      | `normalize.py:564-613`; direct Unicode wrapping and inline/code-span tests pass for the exercised cases.                        |
| 04/AC03 | ✗      | `normalize.py:243-324` plus `render.py:97-129` lose an empty list item's nested code child on reparsing; see C04.               |
| 04/AC04 | ✓      | `normalize.py:468-489`; heading state and separator fixtures pass, including nested containers.                                 |
| 04/AC05 | ✗      | `normalize.py:378-423` does not match code-span fence lengths when splitting table cells; see C03.                              |
| 04/AC06 | ✗      | `normalize.py:491-535` preserves only four literal leading spaces for indented code, not a CommonMark tab indentation; see C02. |


### Task 05

| AC      | Status | Evidence                                                                                                                            |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✗      | `render.py:149-152` receives the incorrect tab-indented code payload and emits changed code semantics; see C02.                     |
| 05/AC02 | ✗      | Exact code/table/list rendering passes the existing fixtures, but the complex code-pipe and empty-list cases fail; see C03 and C04. |
| 05/AC03 | ✓      | `__init__.py:10-24`; document pipeline and typed-error tests pass.                                                                  |
| 05/AC04 | ⚠      | Golden and idempotence fixtures pass, but the uncovered C02-C04 boundaries fail independent exact-byte or reparse probes.           |


### Task 06

| AC      | Status | Evidence                                                                                                                                                                                                               |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:21-40`; recursive discovery, explicit errors, lexical deduplication, and zero-discovery tests pass.                                                                                                     |
| 06/AC02 | ✓      | `operations.py:151-224`; preflight-all-before-write, sorted commits, partial writes, and cleanup tests pass.                                                                                                           |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshot identity/content checks, advisory locking, atomic replacement, mode preservation, symlink rejection, and collision cleanup tests pass; an independent mode/cleanup probe also passed. |
| 06/AC04 | ✓      | `operations.py:123-136,195-230`; status precedence and format/check mappings pass.                                                                                                                                     |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-24`; records, streams, diagnostics, digests, and exit mappings pass.                                                                                                      |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, repository discovery, delegation, and passthrough smoke passed.                                                                                                 |
| 06/AC07 | ✓      | `cli/main.py:31-39` and grouped/wrapper contract tests pass.                                                                                                                                                           |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus fixtures cover the listed broad categories, but omit escaped HTML text, tab-indented code, mismatched code-span runs in table cells, and empty-list nested code. |
| 07/AC02 | ✗      | Formatter-focused pytest and Ruff pass, but C01-C04 remain. Full pytest and repository Ty have only the separately confirmed unrelated baselines described above.       |


## Scope Verification

| File or path                                                            | Justification                               | Status |
| ----------------------------------------------------------------------- | ------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency                          | ✓      |
| `uv.lock`                                                               | Task 01 dependency lock                     | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public result models                | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document pipeline           | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML                     | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, policy, and repairs | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repairs           | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repairs               | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 safe operations                     | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                       | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility wrapper               | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 coverage                | ✓      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                            | ✓      |

The implementation remains within the approved formatter, dependency, CLI, wrapper, registration, test, fixture, and
journal scope. No unrelated production subsystem was changed.


## Prior Review Resolution

| Prior finding                                                      | Status           | Current evidence                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Review 14 C01: unclosed EOF fences gain a semantic payload newline | ✓ Fully resolved | `parser.py:354-358` marks a fence ending at EOF without LF as opaque; `normalize.py:476-478` preserves it; `render.py:201-209` preserves terminal EOF. `test_edge_contract.py:89-120` and the independent LF/CRLF container matrix compare original and reparsed payloads, exact bytes, and three passes. |


## Findings

### Summary

| Finding | Title                                            | Outcome         |
| ------- | ------------------------------------------------ | --------------- |
| C01     | Escaped HTML-looking text is rejected            | Blocks approval |
| C02     | Tab-indented code payload gains a structural tab | Blocks approval |
| C03     | Mismatched code-span runs split table pipes      | Blocks approval |
| C04     | Empty list items lose nested code structure      | Blocks approval |


### Critical

#### C01 Escaped HTML-looking text is rejected


#### Where

`src/dot_tools/markdown_formatter/parser.py:1039-1085`


#### Issue

The raw-HTML scan operates on the original decoded body after masking code ranges, then rejects any `<` followed by an
HTML-looking character. It does not account for a backslash escape. MarkdownIt identifies `\\<div>` as an ordinary text
token with an escaped `<`, but `parse_document(b"# T\\n\\n\\\\<div>\\n")` raises `RawHtmlError`.


#### Impact

Valid CommonMark text containing an escaped angle bracket cannot be formatted. This violates the parser's escape
ownership and raw-HTML policy boundary.


#### Fix

Exclude parser-proven escaped punctuation from the raw-HTML scan, or mask escaped `<` bytes using the same exact source
ownership map before applying the HTML-looking check. Add exact LF/CRLF tests for escaped `<div>` beside genuinely raw
HTML.


#### Outcome

Blocks approval until resolved.


----

### C02 Tab-indented code payload gains a structural tab

#### Where

`src/dot_tools/markdown_formatter/parser.py:293-353` and `src/dot_tools/markdown_formatter/normalize.py:491-535`


#### Issue

For `code_block` nodes, parser metadata falls through to `node.source` rather than the CommonMark semantic code payload.
The normalizer then removes only a literal four-space prefix. A source of `# T\\n\\n\\tcode\\n` has MarkdownIt payload
`b"code\\n"`, but formatting emits `b"# T\\n\\n```text\\n\\tcode\\n```\\n"` and reparsing returns `b"\\tcode\\n"`.


#### Impact

Formatting changes the content of valid indented code blocks and makes structural indentation part of the code payload.
The output is stable only because it has already adopted the wrong payload.


#### Fix

Build `CodePayload.payload` for indented code from the parser's semantic `code_block` content, or remove CommonMark
structural indentation by visual columns, including tabs, before normalization. Add exact LF/CRLF tests for tabs and
mixed space/tab indentation, including reparsed payload equality.


#### Outcome

Blocks approval until resolved.


----

### C03 Mismatched code-span runs split table pipes

#### Where

`src/dot_tools/markdown_formatter/normalize.py:378-423`


#### Issue

The table splitter treats any backtick run as a state toggle instead of requiring a closing run with the opener's exact
length. In the valid inline code span `` ``a`b|c`` ``, the single backtick is payload because the opener and closer use
two ticks. The splitter nevertheless closes at that single tick and treats `|` as a cell delimiter, producing
`TableError: table row has too many cells`.


#### Impact

A recognized table containing a valid code-span pipe is rejected rather than rendered losslessly. This violates the
table
cell ownership and code-span pipe requirements.


#### Fix

Track the active code-span opener length while splitting physical cells and ignore pipes until a matching run closes it.
Use the same exact-run helper for parser ownership, normalization, and rendering. Add tests for mismatched inner runs
and
pipes, exact bytes, semantic reparsing, and three-pass stability.


#### Outcome

Blocks approval until resolved.


----

### C04 Empty list items lose nested code structure

#### Where

`src/dot_tools/markdown_formatter/render.py:97-124`


#### Issue

When an empty list item has a nested `NormalizedCode` child, `_list_item` emits `- `, a blank line, and a fence prefixed
with only the continuation column. For `# T\\n\\n-\\n  ```text\\n  x\\n  ```\\n`, the first output is
`b"# T\\n\\n- \\n\\n  ```text\\n  x\\n  ```\\n"`. Reparsing makes the fence top-level, and the second output is
`b"# T\\n\\n- \\n\\n```text\\nx\\n```\\n"`.


#### Impact

Formatting changes the recognized list/container tree and fails the required idempotence and nested-list preservation
contract.


#### Fix

Render a nested code child of an empty item in a CommonMark form that remains inside the item after reparsing, while
preserving the active continuation column and code payload. Add a regression asserting the reparsed AST shape, exact
bytes, and three formatting passes.


#### Outcome

Blocks approval until resolved.


### Significant

None.


### Trivial

None.


## Skills Applied

- `review-implementation-execution`: project-local
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

New formatter-specific findings C01, C02, C03, and C04 must be resolved before approval. Review-14 C01 is fully
resolved. The unrelated configure pytest failure and the 74 repository-wide Ty baseline diagnostics remain documented
and are not formatter blockers.
