# Execution Review: Generic AST-based Markdown formatter

This independent iteration-22 review rechecks the current formatter against the revised plans, journal, and iteration-21
review. HTML-looking Markdown is accepted, parser-delimited HTML blocks may remain opaque, and `RawHtmlError` is not a
contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--21.md`


## Scope

**whole-plan - Iteration 22**

The review started with the current worktree diff. It independently inspected the current formatter source and tests,
rechecked every iteration-21 finding, re-ran the whole-plan quality matrix, and added no changes outside this artifact.
The revised HTML requirement was applied throughout.


## Issue Summary

- **Critical**: 3
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                       | Result                                                                                                                                                |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                              | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                          |
| `uv run pytest tests/markdown_formatter --no-cov`                                      | Passed: 306 tests.                                                                                                                                    |
| `uv run pytest`                                                                        | 619 passed, 1 failed; coverage 86.23%, above the 70% threshold. The failure is the unrelated configure assertion recorded below.                      |
| `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix` | Passed.                                                                                                                                               |
| `uv run ruff check src tests`                                                          | Passed.                                                                                                                                               |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`            | Passed.                                                                                                                                               |
| `uv run ty check`                                                                      | Failed with 74 repository-baseline diagnostics; no formatter path appeared.                                                                           |
| Grouped command help                                                                   | Passed for `markdown`, `format`, and `check`.                                                                                                         |
| Wrapper help and canonical smoke                                                       | Passed; wrapper `check` and `format` reported `UNCHANGED` and `SUCCESS 1`.                                                                            |
| `git diff --check`                                                                     | Passed.                                                                                                                                               |
| Frontmatter finite-real matrix                                                         | Passed 20,011 finite IEEE-754 samples plus adversarial non-finite inputs.                                                                             |
| HTML policy matrix                                                                     | Passed 10 LF/CRLF cases covering accepted HTML-looking text, parser-opaque blocks, escaped angles, code, and unknown opaque text.                     |
| Parser and span matrix                                                                 | Passed owned inline, table, code, LF/CRLF, EOF, astral, and recursive span checks. The compatibility false-positive in C03 was reproduced.            |
| Review-20 regression matrix                                                            | Passed lazy list continuation, code-span closer parity, table extra-cell rejection, heading relationships, and empty-heading checks.                  |
| Operations and failure-injection matrix                                                | Passed statuses, records, diagnostics, digests, snapshots, locks, replacement, cleanup, partial commits, CLI, and wrapper tests in the focused suite. |
| Dead-helper scan                                                                       | Passed; no uncalled private production helpers remain among the iteration-21 candidates.                                                              |

The full pytest failure is:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are the existing PDF, clipboard/Gmail, OpenCode cost/trend, configure, Jira, and
spinner diagnostics. They do not reference formatter code and remain baseline results, not formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                           |
| ------- | ------ | ------------------------------------------------------------------ |
| 01/AC01 | ✓      | `pyproject.toml`, resolved lockfile, and passing `uv sync`.        |
| 01/AC02 | ✓      | Formatter package modules and public models exist.                 |
| 01/AC03 | ✓      | `src/dot_tools/cli/markdown.py:11-36`; public contract tests pass. |


### Task 02

| AC      | Status | Evidence                                                                         |
| ------- | ------ | -------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-140`; all three APIs pass focused tests.                      |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiter and body-preservation tests pass.       |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; unsafe YAML and finite-real probes pass.                |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, scalar codecs, thresholds, and framing pass. |


### Task 03

| AC      | Status | Evidence                                                                                                                |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123`; byte-addressed AST models and spans pass owned-source checks.                                       |
| 03/AC02 | ⚠      | `parser.py:243-247,669-675`; the compatibility fallback invents a table for the non-table paragraph in C03.             |
| 03/AC03 | ⚠      | `parser.py:243-247`; the false promotion rejects a parser-unowned paragraph instead of preserving its safe boundary.    |
| 03/AC04 | ✓      | `parser.py:715-996`; inline ownership, closer parity, recursive reconstruction, and opaque fallback pass covered cases. |
| 03/AC05 | ✓      | `parser.py:301-303`; accepted HTML matrix passes and parser-delimited blocks remain opaque.                             |
| 03/AC06 | ✓      | `parser.py:999-1023`; task metadata and source-break policy pass.                                                       |


### Task 04

| AC      | Status | Evidence                                                                                                       |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:18-98`; normalized-state tests pass.                                                             |
| 04/AC02 | ⚠      | `normalize.py:100-161`; C01 and C02 show semantic loss in the inline codec.                                    |
| 04/AC03 | ✓      | `normalize.py:292-382`; lazy continuation, task state, nested lists, and container columns pass covered cases. |
| 04/AC04 | ✓      | `normalize.py:559-664`; sibling, child, ancestor, separator, and empty-heading checks pass.                    |
| 04/AC05 | ⚠      | `normalize.py:490-512`; recognized table geometry passes, but C01 also affects trailing-backslash table cells. |
| 04/AC06 | ✓      | `normalize.py:589-633`; code payload, info, fence, LF/CRLF, and EOF checks pass.                               |


### Task 05

| AC      | Status | Evidence                                                                                                                  |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:181-211`; document composition is correct for covered cases but renders C01 and C02's unsafe normalized state. |
| 05/AC02 | ⚠      | `render.py:19-84` and `normalize.py:100-201`; delimiter collision cases are not semantically preserved.                   |
| 05/AC03 | ✓      | `src/dot_tools/markdown_formatter/__init__.py:10-24`; orchestration and typed-error tests pass.                           |
| 05/AC04 | ⚠      | Existing golden and idempotence fixtures pass, but the independent semantic probes found C01 and C02.                     |


### Task 06

| AC      | Status | Evidence                                                                                              |
| ------- | ------ | ----------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:21-42`; collection, discovery, sorting, and deduplication tests pass.                  |
| 06/AC02 | ✓      | `operations.py:91-126,205-240`; preflight, replacement, stop, and cleanup tests pass.                 |
| 06/AC03 | ✓      | `operations.py:44-126`; snapshots, identity, mode, type, lock, and replacement tests pass.            |
| 06/AC04 | ✓      | `operations.py:133-147`; status precedence tests pass.                                                |
| 06/AC05 | ✓      | `operations.py:149-158` and `cli/markdown.py:15-25`; streams, records, diagnostics, and digests pass. |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD, delegation, passthrough, and project discovery pass.   |
| 06/AC07 | ✓      | `src/dot_tools/cli/main.py:35-39`; grouped CLI and wrapper contract tests pass.                       |


### Task 07

| AC      | Status | Evidence                                                                                                                            |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories pass, but the independent trailing-backslash, adjacent-atom, and false-table cases are not covered.               |
| 07/AC02 | ⚠      | Focused formatter gates pass; formatter-specific C01-C03 remain. The only full pytest and Ty failures are the documented baselines. |


## Scope Verification

| File or path                                                                                    | Justification                            | Status                         |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------ |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py`                       | Task 01 dependency and public contract   | ✓                              |
| `src/dot_tools/markdown_formatter/{__init__,frontmatter,parser,normalize,render,operations}.py` | Tasks 01-06 formatter pipeline           | ⚠, C01-C03                     |
| `src/dot_tools/cli/{main,markdown}.py`                                                          | Task 06 grouped CLI                      | ✓                              |
| `.agents/tools/markdown-format.py`                                                              | Task 06 compatibility wrapper            | ✓                              |
| `tests/markdown_formatter/` and fixtures                                                        | Tasks 02-07 contract and corpus coverage | ⚠, missing C01-C03 regressions |
| Revised design and implementation plans                                                         | Human-directed HTML requirement revision | ✓, not edited in this review   |
| Implementation journal and prior reviews                                                        | Execution record                         | ✓, not edited in this review   |

The implementation remains within formatter, dependency, CLI, wrapper, test, fixture, and artifact scope. This review
did not attribute the configure pytest failure or repository-wide Ty diagnostics to the formatter.


## Prior Review Resolution

| Review-21 finding                                             | Status | Current evidence                                                                                                                                              |
| ------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01: canonical emphasis delimiters collide with adjacent text | ✓      | `normalize.py:141-161`; LF/CRLF `test_adjacent_canonical_emphasis_preserves_literal_delimiters` preserves the literal delimiters.                             |
| C02: canonical code delimiters change adjacent code semantics | ✓      | `normalize.py:141-161,184-201`; LF/CRLF `test_adjacent_canonical_code_preserves_literal_backticks` preserves the code payload and node shape.                 |
| C03: hard-break ownership falls through on trailing spaces    | ✓      | `parser.py:829-836`; `test_hard_break_owns_its_trailing_source_spaces` owns the complete delimiter and converges.                                             |
| S01: ancestor headings receive child spacing                  | ✓      | `normalize.py:582-585`; direct ancestor, sibling, child, and separator spacing checks pass.                                                                   |
| S02: empty ATX headings are not parser-semantically owned     | ✓      | `parser.py:450-479`; LF/CRLF empty-heading checks produce empty owned content and stable output.                                                              |
| T01: dead formatter helpers remain in production modules      | ✓      | The named helpers and their dependent legacy scanner are absent; an AST call scan finds no uncalled private production helpers among the reviewed candidates. |

The requested earlier regression checks also pass independently: ambiguous lazy list continuations retain nonempty
content and converge for LF/CRLF; code-span closer matching ignores internal backslash parity; physical table extra
cells, including empty cells, raise `TableError`; heading relationship spacing and empty headings converge; and the
review-21 dead-helper cleanup is present.


## Findings

### Summary

| Finding | Title                                                         | Outcome         |
| ------- | ------------------------------------------------------------- | --------------- |
| C01     | Even trailing backslash runs gain an extra semantic backslash | Blocks approval |
| C02     | Adjacent canonical emphasis atoms merge into a different AST  | Blocks approval |
| C03     | Compatibility table fallback rejects an ordinary paragraph    | Blocks approval |


### Critical

#### C01 Even trailing backslash runs gain an extra semantic backslash


#### Where

`src/dot_tools/markdown_formatter/normalize.py:141-145,169-181,526-556`


#### Issue

`_encode_text_node` appends one backslash whenever a text node ends in a backslash, without accounting for the source
run's CommonMark semantic parity. For the exact source `b"# T\\n\\na\\\\\\n"`, where the body has two backslash bytes,
formatting emits `b"# T\\n\\na\\\\\\\\\\n"`, with three backslash bytes. The parser changes the text payload from one
semantic backslash to two. The same branch runs for table cells and for text immediately before a link or image.


#### Impact

The formatter changes valid Markdown meaning while producing stable bytes. This violates the inline codec and lossless
table-cell contracts, and a two-byte backslash run before a link can turn the link into ordinary text.


#### Fix

Decode the complete source backslash run to its semantic value, then emit the canonical escaped run for that value.
Apply the same proof to table cells and inline-node boundaries, or preserve the containing block opaque when canonical
ownership cannot be proven. Add LF/CRLF semantic reparse tests for odd and even runs at EOF and before links, images,
emphasis, code, and table pipes.


#### Outcome

Blocks approval.


#### C02 Adjacent canonical emphasis atoms merge into a different AST


#### Where

`src/dot_tools/markdown_formatter/normalize.py:105-128`


#### Issue

The inline renderer canonicalizes each emphasis node independently and does not check delimiter interaction between
adjacent non-text atoms. Formatting `b"# T\\n\\n*a*_a_\\n"` emits `b"# T\\n\\n*a**a*\\n"`. The input parser owns two
sibling emphasis nodes; the output parser owns one emphasis node whose content is `a**a`. The same defect occurs for
adjacent strong nodes, for example `**a**__a__`.


#### Impact

Valid Markdown changes its AST semantics even though the output is idempotent. The current focused tests cover literal
punctuation adjacent to an emphasis or code node, but not canonical emphasis or strong atoms adjacent to each other.


#### Fix

Make delimiter encoding context-aware across all adjacent inline atoms, not only text neighbors. Escape or otherwise
separate generated delimiter runs, preserve the containing paragraph or table cell opaque when no safe canonical form
exists, and compare the reparsed semantic shape before accepting the normalized output.


#### Outcome

Blocks approval.


#### C03 Compatibility table fallback rejects an ordinary paragraph


#### Where

`src/dot_tools/markdown_formatter/parser.py:243-247,669-675`


#### Issue

The `parent.kind == "paragraph"` compatibility path promotes any paragraph whose second physical line resembles a
separator. For `b"# T\\n\\na\\n--- | ---\\n"`, `MarkdownIt("commonmark").enable("table")` returns one paragraph token,
not a table token. The formatter nevertheless promotes it, then `_table` sees one header cell and two separator cells
and raises `TableError`.


#### Impact

The formatter rejects ordinary parser-owned Markdown instead of preserving or normalizing the paragraph. This violates
the parser-identified-table boundary and the requirement that unrecognized pipe text remain unchanged. It is a false
policy error, not a fail-closed opaque fallback.


#### Fix

Remove the paragraph-to-table invention, or constrain it to a parser-established table boundary with independently
proven header and separator ownership. Add LF/CRLF negative tests for paragraphs whose second line contains
separator-like pipes, and assert that they remain ordinary paragraph or opaque output rather than raising `TableError`.


#### Outcome

Blocks approval.


----

## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global fallback
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, and C03 are formatter-specific semantic or parser-boundary blockers. The iteration-21 findings are
independently resolved. The configure pytest failure and repository-wide Ty diagnostics remain unrelated baselines under
the revised requirement.
