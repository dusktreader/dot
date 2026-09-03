# Execution Review: Generic AST-based Markdown formatter

This independent iteration-19 review rechecks review 18 against the revised plans and current journal. HTML-looking
Markdown is accepted, parser-delimited HTML blocks may remain opaque, and `RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--18.md`


## Scope

**whole-plan - Iteration 19**

The review started with the current worktree diff, then inspected the implementation, tests, fixtures, plans, journal,
and review 18. It independently re-tested every review-18 finding and the whole-plan formatter surface. It did not
modify
source, tests, plans, the journal, or prior reviews. This artifact is the only authored file.


## Issue Summary

- **Critical**: 2
- **Significant**: 0
- **Trivial**: 0


## Verification Evidence

| Command or probe                                  | Result                                                                                                           |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                         | Passed; `markdown-it-py==4.2.0` is resolved.                                                                     |
| `uv run pytest tests/markdown_formatter --no-cov` | Passed: 288 tests.                                                                                               |
| `uv run pytest`                                   | 601 passed, 1 failed; only the documented configure baseline failed. Coverage was 83.06%.                        |
| Focused Ruff                                      | Passed for formatter source and tests.                                                                           |
| `uv run ruff check src tests`                     | Passed.                                                                                                          |
| Focused Ty                                        | Passed for formatter source and tests.                                                                           |
| `uv run ty check`                                 | Failed with 74 diagnostics, all outside formatter source and tests in the documented baseline.                   |
| Grouped command help                              | Passed for `markdown`, `format`, and `check`.                                                                    |
| Wrapper help and canonical check smoke            | Passed: `UNCHANGED` and `summary check SUCCESS 1`.                                                               |
| `git diff --check`                                | Passed.                                                                                                          |
| Review-18 C01/C02/S01-S04 matrix                  | Passed all direct assertions for bytes, semantic reparses, spans, three passes, deduplication, and cleanup.      |
| Revised HTML matrix                               | Passed for inline, block, escaped-angle, code, and opaque HTML-looking cases with LF and CRLF.                   |
| Whole-plan probes                                 | Passed for frontmatter, ownership, wrapping, containers, separators, tables, code, operations, CLI, and wrapper. |
| Cleanup failure probes                            | Failed: cleanup `lstat` can mask a successful replacement, and unknown fstat identity permits unsafe unlink.     |
| Rejection scan                                    | No `RawHtmlError` or HTML rejection logic remains in formatter source or tests.                                  |

The full pytest failure is the unrelated configure assertion:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are confined to the existing PDF, clipboard/Gmail, OpenCode cost/trend, configure,
Jira, and spinner paths. No formatter path appears in that output. These two results are accepted baselines, not
findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                     |
| ------- | ------ | ---------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, resolved lockfile, and passing `uv sync`.            |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and package modules exist. |
| 01/AC03 | ✓      | `models.py:8-66`, `cli/markdown.py:11-36`, and passing contract tests.       |


### Task 02

| AC      | Status | Evidence                                                                                             |
| ------- | ------ | ---------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all three APIs and focused tests pass.                                      |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiter and body-preservation tests pass.                           |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted tags, duplicates, unsafe values, Unicode, and finite reals pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, nesting, scalar codecs, thresholds, and framing pass.            |


### Task 03

| AC      | Status | Evidence                                                                                                         |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123,204-211`; byte spans, code metadata, and focused ownership tests pass.                         |
| 03/AC02 | ✓      | `parser.py:108-123,214-315,732-900`; CommonMark-plus-table owned cases pass.                                     |
| 03/AC03 | ✓      | `parser.py:533-555,1107-1118`; recursive reconstruction and opaque fallback pass.                                |
| 03/AC04 | ✓      | `parser.py:732-900`; delimiter, nesting, escape, code, link, image, and hard-break cases pass.                   |
| 03/AC05 | ✓      | `parser.py:291-292,846-900`; HTML-looking text is accepted and HTML blocks remain opaque without a policy error. |
| 03/AC06 | ✓      | `parser.py:300-307,1121-1145`; task metadata and source-break policy pass.                                       |


### Task 04

| AC      | Status | Evidence                                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------------------------ |
| 04/AC01 | ✓      | `normalize.py:18-98`; normalized-state tests pass.                                                     |
| 04/AC02 | ✓      | `normalize.py:100-199,647-696`; wrapping, recursive inline codecs, and code-span cases pass.           |
| 04/AC03 | ✓      | `normalize.py:290-373`; recursive list state and direct deep-list probes pass.                         |
| 04/AC04 | ✓      | `normalize.py:541-645`; local heading spacing and separator state pass.                                |
| 04/AC05 | ✓      | `normalize.py:437-538`; table geometry, ownership, escaping, invalid rows, and three-pass output pass. |


### Task 05

| AC      | Status | Evidence                                                                                  |
| ------- | ------ | ----------------------------------------------------------------------------------------- |
| 05/AC01 | ✓      | `render.py:190-220,223-231`; canonical LF composition and opaque/code preservation pass.  |
| 05/AC02 | ✓      | `render.py:28-93,96-187`; inline, list, separator, table, and code rendering probes pass. |
| 05/AC03 | ✓      | `__init__.py:10-26`; document orchestration and typed error propagation pass.             |
| 05/AC04 | ✓      | Render/document golden and idempotence tests pass.                                        |


### Task 06

| AC      | Status | Evidence                                                                                                       |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-42`; discovery, path resolution, sorting, deduplication, and zero-discovery pass.            |
| 06/AC02 | ⚠      | `operations.py:91-119,199-234`; normal cleanup passes, but injected cleanup failure corrupts commit reporting. |
| 06/AC03 | ✗      | `operations.py:44-119`; snapshots and locks pass, but unknown fstat identity permits unsafe pathname cleanup.  |
| 06/AC04 | ✓      | `operations.py:127-140`; status precedence and format/check mappings pass.                                     |
| 06/AC05 | ✓      | `operations.py:143-152`, `cli/markdown.py:15-25`; records, streams, diagnostics, digests, and exits pass.      |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, discovery, delegation, and passthrough pass.            |
| 06/AC07 | ✓      | `cli/main.py:35-39` and grouped CLI contract tests pass.                                                       |


### Task 07

| AC      | Status | Evidence                                                                                                       |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ✓      | Corpus fixtures cover frontmatter, boundaries, headings, lists, tables, code, HTML-looking text, opaque spans, |
|         |        | source-break policy, idempotence, and multi-file failure behavior.                                             |
| 07/AC02 | ✗      | Formatter tests and lint/type checks pass, but two formatter-specific cleanup failures remain below.           |


## Scope Verification

| File or path                                    | Justification                                 | Status |
| ----------------------------------------------- | --------------------------------------------- | ------ |
| `pyproject.toml`, `uv.lock`, `models.py`        | Task 01 dependency and public contract        | ✓      |
| `markdown_formatter/__init__.py`                | Tasks 01 and 05 orchestration                 | ✓      |
| `frontmatter.py` and frontmatter tests/fixtures | Task 02 restricted YAML                       | ✓      |
| `parser.py` and parser tests/fixtures           | Task 03 parsing, spans, and policy boundaries | ✓      |
| `normalize.py` and normalization tests          | Task 04 normalization                         | ✓      |
| `render.py` and render/document tests           | Task 05 rendering                             | ✓      |
| `operations.py` and operation tests             | Task 06 safe operations                       | ⚠      |
| `cli/markdown.py`, `cli/main.py`, and wrapper   | Task 06 CLI and delegation                    | ✓      |
| `tests/markdown_formatter/` and fixtures        | Tasks 02 through 07 contract coverage         | ✓      |
| Revised design and implementation plans         | Human-directed HTML requirement revision      | ✓      |
| Implementation journal                          | Execution record                              | ✓      |

The implementation remains within formatter, dependency, CLI, wrapper, test, fixture, and artifact scope. This review
did
not modify the plans, journal, source, tests, or prior reviews.


## Prior Review Resolution

| Review-18 finding                                          | Status | Current evidence                                                                                     |
| ---------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------- |
| C01 wrapped prose becomes multiple paragraphs              | ✓      | `normalize.py:647-696`; direct parse confirms one paragraph after wrapping and three-pass stability. |
| C02 delimiter conversion changes nested emphasis semantics | ✓      | `normalize.py:108-117,154-156`; nested inline shapes match before and after formatting.              |
| S01 link titles containing `)` remain opaque               | ✓      | `parser.py:1030-1055`; link, image, and table-title cases remain owned and canonical.                |
| S02 deep lists render whitespace-only lines                | ✓      | `render.py:113-123`; four-level same-family lists contain no whitespace-only output lines.           |
| S03 duplicate invalid paths bypass deduplication           | ✓      | `operations.py:40-41`; duplicate missing and non-Markdown operands yield one record and diagnostic.  |
| S04 fstat failure leaks the temporary file                 | ✓      | `operations.py:110-119`; injected fstat failure returns `WRITE_ERROR` and leaves no temporary file.  |


## Findings

### Summary

| Finding | Title                                                  | Outcome         |
| ------- | ------------------------------------------------------ | --------------- |
| C01     | Cleanup `lstat` can hide a successful replacement      | Blocks approval |
| C02     | Unknown fstat identity permits unsafe temporary unlink | Blocks approval |

Two critical formatter-specific findings remain.


### Critical

#### C01 Cleanup `lstat` can hide a successful replacement


#### Where

`src/dot_tools/markdown_formatter/operations.py:109-119`


#### Issue

After `os.replace` succeeds, `_replace` leaves `temporary` set and calls `temporary.lstat()` in `finally`. An injected
`OSError` from that cleanup `lstat` escapes after the destination already contains the canonical output. The direct
probe
returned `WRITE_ERROR` with `committed=()` and `untouched=(path,)`, even though the destination had been replaced.


#### Impact

The operation reports failure and incorrect commit sets after a successful atomic write. A caller can retry or alert on
a
write failure while the file has already changed, violating the status and atomic-operation contract.


#### Fix

Clear the temporary cleanup state immediately after `os.replace` succeeds. Ensure cleanup errors before replacement
never
mask the primary replacement error, and preserve accurate committed/untouched reporting for every failure path.


#### Outcome


#### C02 Unknown fstat identity permits unsafe temporary unlink


#### Where

`src/dot_tools/markdown_formatter/operations.py:99-119`


#### Issue

When `os.fstat` raises, `created` is true but `temporary_identity` is still `None`; the `finally` block unconditionally
unlinks the temporary pathname. A direct failure-injection probe replaced that pathname with an unrelated sentinel
before
raising fstat, and the formatter deleted the sentinel.


#### Impact

An fstat failure combined with a pathname race can delete a file not created by this invocation. This violates the
cleanup
and destination-safety guarantees and is a data-integrity failure.


#### Fix

Never unlink a temporary pathname when ownership cannot be proven. Redesign temporary creation or cleanup to retain a
descriptor-verifiable identity, and otherwise report the cleanup failure without deleting an unverified file.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global fallback
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 and C02 must be resolved before approval. The original review-18 cases pass, and the only nonzero repository-wide
quality results remain the independently confirmed unrelated configure pytest assertion and the 74 documented
repository-wide Ty baseline diagnostics. The revised HTML requirement is respected, but the formatter's cleanup failure
paths still violate the atomic-operation contract.
