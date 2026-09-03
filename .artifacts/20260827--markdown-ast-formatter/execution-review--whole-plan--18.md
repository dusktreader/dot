# Execution Review: Generic AST-based Markdown formatter

This independent iteration-18 review rechecks review 17 against the revised plans and journal. HTML-looking Markdown is
accepted, parser-delimited HTML blocks may remain opaque, and `RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--17.md`


## Scope

**whole-plan - Iteration 18**

The review began with the current diff, then inspected the implementation, focused tests, fixtures, plans, journal, and
review 17. It did not modify source, tests, plans, the journal, or prior reviews. The only authored file is this
artifact.


## Issue Summary

- **Critical**: 2
- **Significant**: 4
- **Trivial**: 0


## Verification Evidence

| Command or probe                                  | Result                                                                                                                                                                  |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                         | Passed; `markdown-it-py==4.2.0` is resolved.                                                                                                                            |
| `uv run pytest tests/markdown_formatter --no-cov` | Passed: 271 tests.                                                                                                                                                      |
| `uv run pytest`                                   | 584 passed, 1 failed; only the documented configure baseline failed. Coverage was 83.14%.                                                                               |
| `uv run ruff check src tests`                     | Passed.                                                                                                                                                                 |
| `uv run ty check`                                 | Failed with 74 diagnostics, all outside formatter source and tests in the documented baseline.                                                                          |
| Grouped command help                              | Passed for `markdown`, `format`, and `check`.                                                                                                                           |
| Wrapper help and canonical fixture smoke          | Passed: `UNCHANGED` and `summary ... SUCCESS 1`.                                                                                                                        |
| `git diff --check`                                | Passed.                                                                                                                                                                 |
| Review-17 C01-C04/S01-S03 matrix                  | Passed 33 of 33 direct assertions for exact bytes, ownership, semantic reparses, and three passes.                                                                      |
| Revised HTML matrix                               | Passed for inline, escaped-angle, code, and parser-delimited block cases with LF and CRLF.                                                                              |
| Whole-plan probes                                 | Frontmatter, parser, containers, separators, tables, code, operations, CLI, and wrapper paths passed their covered cases. The formatter-specific failures below remain. |

The full pytest failure is the unrelated configure assertion:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are confined to the existing PDF, clipboard/Gmail, OpenCode cost/trend, configure,
Jira, and spinner paths. No formatter path appears in that output. These two results are accepted baselines, not review
findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, resolved lockfile, and passing `uv sync`.                               |
| 01/AC02 | ✓      | Formatter package and public models exist.                                                      |
| 01/AC03 | ✓      | `models.py:8-66`, `cli/markdown.py:15-24`, and passing contract tests cover the public surface. |


### Task 02

| AC      | Status | Evidence                                                                                             |
| ------- | ------ | ---------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all three APIs and focused tests pass.                                      |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters, missing close, and body preservation pass.                |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted tags, duplicates, unsafe values, Unicode, and finite reals pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, nesting, scalar codecs, thresholds, and framing pass.            |


### Task 03

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | Byte spans and physical LF/CRLF code payloads pass; valid link titles containing `)` fall back opaque in C03. |
| 03/AC02 | ✓      | `parser.py:108-123,542-618`; CommonMark-plus-table parsing and covered owned kinds pass.                      |
| 03/AC03 | ⚠      | Opaque fallback works, but the parser fails to own a parser-mapped link title containing an unescaped `)`.    |
| 03/AC04 | ⚠      | Delimiter and recursive ownership cases pass; quote-aware link-tail ownership is incomplete in C03.           |
| 03/AC05 | ✓      | HTML-looking inline text is accepted, HTML blocks remain opaque, and no `RawHtmlError` logic exists.          |
| 03/AC06 | ✓      | `parser.py:304-307,1123-1134`; task metadata and source-break policy pass covered cases.                      |


### Task 04

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:18-97`; normalized-state tests pass.                                                            |
| 04/AC02 | ✗      | C02 changes nested emphasis semantics during canonical delimiter conversion; C03 misses the title codec edge. |
| 04/AC03 | ⚠      | Nested list AST shape survives, but C04 leaves whitespace-only lines in canonical list output.                |
| 04/AC04 | ✓      | Review-17 heading spacing and separator probes pass exactly and converge in three passes.                     |
| 04/AC05 | ✓      | Table geometry, framing, parity, code-span pipes, invalid rows, spans, and three-pass output pass.            |


### Task 05

| AC      | Status | Evidence                                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------------------------ |
| 05/AC01 | ✗      | C01 emits wrapped prose lines as separate blocks joined by two LF bytes, changing paragraph structure. |
| 05/AC02 | ✗      | C02 changes nested inline semantics; C04 violates canonical list whitespace.                           |
| 05/AC03 | ✓      | `__init__.py:10-24`; pipeline and typed error propagation pass covered cases.                          |
| 05/AC04 | ⚠      | Golden and idempotence tests pass, but they do not catch the C01-C04 whole-plan failures.              |


### Task 06

| AC      | Status | Evidence                                                                                                                |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ⚠      | Discovery and valid-path deduplication pass; duplicate explicit invalid paths are emitted twice in `check_paths`.       |
| 06/AC02 | ⚠      | Preflight, atomic replacement, stop-on-error, and normal cleanup pass; C06 leaks a temp file after `fstat` failure.     |
| 06/AC03 | ⚠      | Snapshot, lock, mode, type, symlink, and cooperating-writer checks pass; cleanup is incomplete on one filesystem error. |
| 06/AC04 | ✓      | Status precedence and format/check mappings pass the focused and direct operation probes.                               |
| 06/AC05 | ✓      | Records, streams, diagnostics, digests, and exits pass covered cases.                                                   |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, delegation, passthrough, and discovery failure pass.             |
| 06/AC07 | ✓      | `cli/main.py:35-39`; grouped help and CLI contract tests pass.                                                          |


### Task 07

| AC      | Status | Evidence                                                                                                                         |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories exist, but no fixture catches C01-C04.                                                                         |
| 07/AC02 | ✗      | Focused pytest and Ruff pass; six formatter-specific findings remain. Full pytest and Ty have only the accepted baselines above. |


## Scope Verification

| File or path                                                              | Justification                            | Status |
| ------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| `pyproject.toml`, `uv.lock`, `src/dot_tools/markdown_formatter/models.py` | Task 01 dependency and public contract   | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                            | Tasks 01 and 05 orchestration            | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py` and its tests/fixtures  | Task 02 restricted YAML                  | ✓      |
| `src/dot_tools/markdown_formatter/parser.py` and its tests/fixtures       | Task 03 parsing, spans, and policy       | ⚠      |
| `src/dot_tools/markdown_formatter/normalize.py` and normalization tests   | Task 04 normalization                    | ⚠      |
| `src/dot_tools/markdown_formatter/render.py` and render/document tests    | Task 05 rendering                        | ⚠      |
| `src/dot_tools/markdown_formatter/operations.py` and operation tests      | Task 06 safe operations                  | ⚠      |
| `src/dot_tools/cli/markdown.py`, `src/dot_tools/cli/main.py`, and wrapper | Task 06 CLI and delegation               | ✓      |
| `tests/markdown_formatter/` and fixtures                                  | Tasks 02 through 07 coverage             | ⚠      |
| Revised design and implementation plans                                   | Human-directed HTML requirement revision | ✓      |
| Implementation journal                                                    | Execution record                         | ✓      |

The implementation remains within formatter, dependency, CLI, wrapper, test, fixture, and artifact scope. The plans,
journal, and prior reviews were not edited during this review.


## Prior Review Resolution

| Review-17 finding                                     | Status | Current evidence                                                                                                                      |
| ----------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| C01 delimiter conversion changes inline semantics     | ✓      | `normalize.py:148-160`; literal target delimiters and backslashes preserve the tested semantic content.                               |
| C02 same-marker nested lists collapse                 | ✓      | `render.py:119-122`; bullet, ordered, task-bearing, LF, CRLF, and three-pass AST probes pass.                                         |
| C03 angle destinations omit decoded less-than escapes | ✓      | `normalize.py:226-233`; `<` is escaped and links reparse with the same destination.                                                   |
| C04 indented code loses CRLF payload bytes            | ✓      | `parser.py:373-391,493-502`; physical LF/CRLF payloads and optional spans pass.                                                       |
| S01 ordinary heading spacing is short                 | ✓      | `normalize.py:545-547`, `render.py:248-249`; exact spacing and three-pass probes pass.                                                |
| S02 empty list items emit trailing whitespace         | ✓      | `render.py:109-112`; empty unordered and ordered markers pass. C04 is a distinct deep-nesting whitespace case.                        |
| S03 title codec retains noncanonical escapes          | ✓      | `normalize.py:226-248`; tested quote and backslash escapes produce stable semantic titles. C03 is a distinct parenthesis parsing gap. |


## Findings

### Summary

| Finding | Title                                                            | Outcome         |
| ------- | ---------------------------------------------------------------- | --------------- |
| C01     | Wrapped prose becomes multiple paragraphs                        | Blocks approval |
| C02     | Canonical delimiter conversion changes nested emphasis semantics | Blocks approval |
| S01     | Parser-mapped link titles containing `)` remain opaque           | Blocks approval |
| S02     | Deep nested lists render whitespace-only lines                   | Blocks approval |
| S03     | Duplicate explicit invalid paths bypass final deduplication      | Blocks approval |
| S04     | `fstat` failure leaks the newly created temporary file           | Blocks approval |


### Critical

#### C01 Wrapped prose becomes multiple paragraphs


#### Where

`src/dot_tools/markdown_formatter/normalize.py:612-617` and `src/dot_tools/markdown_formatter/render.py:239-255`


#### Issue

The paragraph normalizer extends the block list with one bytes object per wrapped line. The renderer treats every bytes
object as a separate block and joins adjacent blocks with two LF bytes. An independent probe with 40 `word` atoms emits
blank lines between wrapped lines. The output is stable only because the second pass repeats the same wrong structure.


#### Impact

Formatting changes one owned paragraph into multiple paragraphs. This violates the 120-column wrapping contract and
changes the Markdown block AST on semantic reparse.


#### Fix

Store wrapped lines as one paragraph value joined by a single LF. Keep hard-break groups joined by the canonical
backslash-plus-LF marker, then add a semantic-reparse test asserting one paragraph before and after formatting.


### Critical

#### C02 Canonical delimiter conversion changes nested emphasis semantics


#### Where

`src/dot_tools/markdown_formatter/normalize.py:100-112`


#### Issue

The recursive codec emits `*children*` for every emphasis node. For the parser-owned input
`b"# T\\n\\n*_a_*\\n"`, it emits `b"# T\\n\\n**a**\\n"`. The input reparses as emphasis containing emphasis; the output
reparses as strong. The
paragraph is not opaque, and the output remains stable, so the existing idempotence assertion does not detect the
semantic change.


#### Impact

Formatting changes an owned inline construct's Markdown meaning. The same collision affects nested strong/emphasis
combinations and violates Task 04 AC02 and Task 05 AC02.


#### Fix

Add a delimiter-aware semantic reparse check for nested emphasis and strong nodes. Either emit an unambiguous
semantics-preserving representation or mark the containing block opaque when the required canonical delimiter policy
cannot represent the nested structure safely.


### Significant

#### S01 Parser-mapped link titles containing `)` remain opaque


#### Where

`src/dot_tools/markdown_formatter/parser.py:813-819,1030-1044`


#### Issue

`_balanced_destination` stops at the first unescaped `)` without tracking whether it is inside a quoted title. For
`b"# T\\n\\n[x](u 'a)b')\\n"`, `markdown-it-py` owns a link with title `a)b`, but the formatter's inline scanner cannot
associate the
complete token and marks the paragraph opaque. The formatter therefore leaves the single-quoted title unchanged.


#### Impact

Valid parser-owned links and images do not receive the required double-quoted semantic title codec or source-span
ownership. The same gap can make a recognized table opaque.


#### Fix

Consume the parser-owned link token's complete source interval or make the destination/title scanner quote-aware. Add
link, image, and table-cell cases with literal and escaped parentheses, then assert canonical title bytes and semantic
reparses.


### Significant

#### S02 Deep nested lists render whitespace-only lines


#### Where

`src/dot_tools/markdown_formatter/render.py:119-122,147-150`


#### Issue

When a same-family nested list itself contains a same-family child, the renderer creates an empty separator line and
then
prefixes it with the parent continuation indentation. Formatting
`b"# T\\n\\n- a\\n  - b\\n    - c\\n"` emits `b"  \\n"` between the nested lists.


#### Impact

The canonical output contains trailing whitespace outside opaque spans and code payloads. This violates the output
policy
and is absent from the current list fixture coverage.


#### Fix

Keep structural blank separator lines empty when applying list prefixes. Add exact LF/CRLF tests for three nested
same-family lists and assert no non-code output line ends in horizontal whitespace.


### Significant

#### S03 Duplicate explicit invalid paths bypass final deduplication


#### Where

`src/dot_tools/markdown_formatter/operations.py:21-40,227-230`


#### Issue

`_collect` deduplicates discovered paths but appends every explicit invalid operand to `errors`. `check_paths` returns
those errors directly instead of passing them through `_complete_results`. For two operands resolving to the same
missing
path, it returns two identical file records and two identical diagnostics.


#### Impact

The public operation and CLI contract promises one sorted record per final deduplicated path. Duplicate invalid operands
break deterministic record and diagnostic counts.


#### Fix

Deduplicate normalized error paths before returning from `_collect`, or complete check results through the same
path-keyed
assembly used by format. Add duplicate missing and duplicate non-Markdown operand tests for records and diagnostics.


### Significant

#### S04 `fstat` failure leaks the newly created temporary file


#### Where

`src/dot_tools/markdown_formatter/operations.py:90-115`


#### Issue

`_replace` sets `created = True` after opening the temporary file, but it only records `temporary_identity` after
`os.fstat`. If `os.fstat` raises, the `finally` block has no identity and skips cleanup. An independent
failure-injection
probe returns `WRITE_ERROR` and leaves `.<name>.dt-tmp-<pid>` in the destination directory.


#### Impact

A filesystem failure leaves an orphan temporary file. A later invocation can fail with a collision on the fixed
temporary
pathname, and the implementation does not satisfy the cleanup guarantee in Task 06 AC02/AC03.


#### Fix

Keep cleanup under the destination lock and make the cleanup state safe when identity capture fails. Remove only a file
created by the current invocation, with a test that injects `fstat` failure and verifies the destination and directory
are
clean.


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global skill
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

Resolve C01 and C02 before approval. Resolve S01 through S04 in the same pass. Review-17 C01-C04/S01-S03 are resolved
for
their reported cases, and the revised HTML requirement is respected. The unrelated configure pytest failure and
repository-wide Ty diagnostics remain accepted baselines only.
