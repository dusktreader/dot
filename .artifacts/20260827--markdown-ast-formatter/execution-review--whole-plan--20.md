# Execution Review: Generic AST-based Markdown formatter

This independent iteration-20 review rechecks review 19 against the revised plans and current journal. The HTML policy
remains accepted: HTML-looking Markdown is ordinary input, parser-delimited HTML blocks may remain opaque, and
`RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--19.md`


## Scope

**whole-plan - Iteration 20**

The review started with the current worktree diff, then inspected the implementation, focused tests, fixtures, plans,
journal, and review 19. It independently re-tested review-19 cleanup blockers and the whole formatter matrix. It did not
modify source, tests, plans, the journal, or prior reviews. This artifact is the only authored file.


## Issue Summary

- **Critical**: 2
- **Significant**: 1
- **Trivial**: 0


## Verification Evidence

| Command or probe                                  | Result                                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `uv sync`                                         | Passed; `markdown-it-py==4.2.0` is resolved.                                                                 |
| `uv run pytest tests/markdown_formatter --no-cov` | Passed: 291 tests.                                                                                           |
| `uv run pytest`                                   | 604 passed, 1 failed; coverage was 83.04% and the threshold was reached.                                     |
| Focused Ruff                                      | Passed for formatter source and tests.                                                                       |
| `uv run ruff check src tests`                     | Passed.                                                                                                      |
| Focused Ty                                        | Passed for formatter source and tests.                                                                       |
| `uv run ty check`                                 | Failed with 74 diagnostics in the existing non-formatter baseline only.                                      |
| Grouped command help                              | Passed for `markdown`, `format`, and `check`.                                                                |
| Wrapper help and canonical smoke                  | Passed; check and format both reported `UNCHANGED` and `SUCCESS 1`.                                          |
| `git diff --check`                                | Passed.                                                                                                      |
| Review-19 cleanup re-test                         | Passed: committed replacement survives cleanup `lstat` failure; fstat failure leaves a substituted sentinel. |
| Independent whole-plan matrix                     | 83 assertions passed; 3 formatter-specific failures are listed below.                                        |
| Revised HTML matrix                               | Passed for inline, block, escaped-angle, code, and opaque HTML-looking input with LF and CRLF.               |
| Rejection scan                                    | No active `RawHtmlError` or embedded-HTML rejection logic exists in formatter source or tests.               |

The full pytest failure is the unrelated configure assertion:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are the existing diagnostics in the PDF, clipboard/Gmail, OpenCode cost/trend,
configure, Jira, and spinner paths. No formatter path appears in that output. These two results are baselines, not
formatter findings.

The independent matrix exercised adversarial finite reals, parser spans and recursive children, accepted HTML forms,
120-code-point prose wrapping, paragraph structure, recursive lists and containers, headings and separators, LF/CRLF/EOF
tables and code, operation records and diagnostics, snapshots, locks, atomic replacement, cleanup, grouped CLI, wrapper,
and help. The operation failure injections independently confirmed both review-19 fixes.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                     |
| ------- | ------ | ---------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml`, resolved lockfile, and passing `uv sync`.                  |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and package modules exist. |
| 01/AC03 | ✓      | `models.py`, `cli/markdown.py:11-36`, and passing contract tests.            |


### Task 02

| AC      | Status | Evidence                                                                         |
| ------- | ------ | -------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all public APIs pass focused tests.                     |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters and body preservation pass.            |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; unsafe YAML and adversarial finite-real probes pass.    |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, scalar codecs, thresholds, and framing pass. |


### Task 03

| AC      | Status | Evidence                                                                                                              |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:31-123`; byte-addressed models and parser spans are present.                                               |
| 03/AC02 | ⚠      | `parser.py:732-900` owns the exercised inline forms, but a parser-owned escaped code closer falls back to opaque.     |
| 03/AC03 | ⚠      | Recursive span probes pass for covered forms; the escaped code-span case is not owned despite a safe parser boundary. |
| 03/AC04 | ✗      | `parser.py:1013-1027` treats a backslash before a code closer as an escape, contrary to CommonMark code-span rules.   |
| 03/AC05 | ✓      | `parser.py:291-292,846-900`; HTML-looking input is accepted and HTML blocks remain opaque.                            |
| 03/AC06 | ✓      | `parser.py:300-307,1134-1143`; task metadata and source-break policy pass.                                            |


### Task 04

| AC      | Status | Evidence                                                                                                           |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| 04/AC01 | ✓      | `normalize.py:18-98`; normalized-state tests pass.                                                                 |
| 04/AC02 | ⚠      | 120-code-point wrapping and ordinary code spans pass, but the escaped closer bypasses required code normalization. |
| 04/AC03 | ✗      | `normalize.py:320-337`; a lazy continuation beginning `11. [ ] two` is rendered as an empty line and loses text.   |
| 04/AC04 | ✗      | `normalize.py:562-565` and `render.py:248-249`; equal-level sibling headings receive one, not two, blank lines.    |
| 04/AC05 | ⚠      | Normal table geometry and source ownership pass, but the escaped closer can hide a required extra-cell error.      |
| 04/AC06 | ✓      | `normalize.py:568-614`; LF/CRLF/EOF payload, info, and collision-safe fence probes pass.                           |


### Task 05

| AC      | Status | Evidence                                                                                                             |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | Canonical composition and opaque/code preservation pass for exercised cases; the owned escaped code case is opaque.  |
| 05/AC02 | ⚠      | Inline, list, separator, table, and code rendering pass the suite, but the two edge cases above remain.              |
| 05/AC03 | ⚠      | Typed orchestration and error propagation pass generally; the recognized table edge does not reach `TableError`.     |
| 05/AC04 | ✗      | Focused golden tests are green, but the independent CommonMark edge matrix found non-canonical output and data loss. |


### Task 06

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:21-41`; collection, sorting, lexical deduplication, and no-op discovery pass.                  |
| 06/AC02 | ✓      | `operations.py:91-126,205-240`; preflight, commit ordering, cleanup, and both injected cleanup blockers pass. |
| 06/AC03 | ✓      | `operations.py:44-126`; snapshots, locks, identity checks, replacement, and sentinel preservation pass.       |
| 06/AC04 | ✓      | `operations.py:133-147`; status precedence and exit mappings pass.                                            |
| 06/AC05 | ✓      | `operations.py:149-158`, `cli/markdown.py:15-25`; records, streams, diagnostics, and digests pass.            |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, delegation, and passthrough pass.                      |
| 06/AC07 | ✓      | `cli/main.py:35-39` and grouped CLI contract tests pass.                                                      |


### Task 07

| AC      | Status | Evidence                                                                                                                                                 |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus fixtures cover the requested categories, but the independent list and code-span probes found regressions.                                         |
| 07/AC02 | ⚠      | Focused Ruff, focused Ty, and the formatter suite pass; the full repository retains only the stated baselines, while formatter-specific blockers remain. |


## Scope Verification

| File or path                                    | Justification                                 | Status                                       |
| ----------------------------------------------- | --------------------------------------------- | -------------------------------------------- |
| `pyproject.toml`, `uv.lock`, `models.py`        | Task 01 dependency and public contract        | ✓                                            |
| `markdown_formatter/__init__.py`                | Tasks 01 and 05 orchestration                 | ✓                                            |
| `frontmatter.py` and frontmatter fixtures/tests | Task 02 restricted YAML                       | ✓                                            |
| `parser.py` and parser fixtures/tests           | Task 03 parsing, spans, and policy boundaries | ✓                                            |
| `normalize.py` and normalization tests          | Task 04 normalization                         | ⚠, findings C01 and S01                      |
| `render.py` and render/document tests           | Task 05 rendering                             | ⚠, findings C02 and S01                      |
| `operations.py` and operation tests             | Task 06 safe operations                       | ✓                                            |
| `cli/markdown.py`, `cli/main.py`, and wrapper   | Task 06 CLI and delegation                    | ✓                                            |
| `tests/markdown_formatter/` and fixtures        | Tasks 02 through 07 contract coverage         | ⚠, findings C01 and C02 expose missing cases |
| Revised design and implementation plans         | Human-directed HTML requirement revision      | ✓, unchanged during review                   |
| Implementation journal                          | Execution record                              | ✓, unchanged during review                   |

The implementation remains within formatter, dependency, CLI, wrapper, test, fixture, and artifact scope. No unrelated
configure or repository-wide Ty baseline is attributed to this formatter review.


## Prior Review Resolution

| Review-19 finding                                          | Status | Current evidence                                                                                                                                       |
| ---------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C01 cleanup `lstat` can hide a successful replacement      | ✓      | `operations.py:108-111` clears temporary cleanup state after `os.replace`; independent injection reports `SUCCESS`, committed output, and `FORMATTED`. |
| C02 unknown fstat identity permits unsafe temporary unlink | ✓      | `operations.py:102-103,116-126` unlinks only with descriptor identity; independent pathname substitution leaves the sentinel untouched.                |


## Findings

### Summary

| Finding | Title                                                   | Outcome         |
| ------- | ------------------------------------------------------- | --------------- |
| C01     | Lazy list continuation can be silently dropped          | Blocks approval |
| C02     | Code-span closer parity is wrong and hides table errors | Blocks approval |
| S01     | Equal-level sibling headings get insufficient spacing   | Blocks approval |


### Critical

#### C01 Lazy list continuation can be silently dropped


#### Where

`src/dot_tools/markdown_formatter/normalize.py:320-337`, with list-paragraph opacity bypass in
`src/dot_tools/markdown_formatter/parser.py:259-262`


#### Issue

For this parser-owned list paragraph:

```text
# T

10. [x] one
    11. [ ] two
        > quote
        > line
```

the normalizer rescans each continuation line independently. `_scan_inline(b"11. [ ] two", 0)` returns no nodes because
markdown-it parses that standalone line as an ordered list. `_wrap_inline` then emits an empty continuation instead of
preserving the source text. The independent output was:

```text
b'# T\n\n10. [x] one\n        \n        quote\n        line\n'
```


#### Impact

The formatter loses user content and fails the recursive-list and lazy-continuation contract. A successful formatting
operation can silently commit the corrupted document.


#### Fix

Use the parser-owned inline token stream and exact source intervals for continuation content. If a continuation cannot
be
proven owned, preserve the complete containing list item or list as opaque. Never turn a nonempty source line into an
empty rendered line after an ownership failure.


#### Outcome


#### C02 Code-span closer parity is wrong and hides table errors


#### Where

`src/dot_tools/markdown_formatter/parser.py:1006-1027`, especially the escaped-closer check at line 1019; the same
helper drives table splitting at `parser.py:623-630`.


#### Issue

`_code_span_close` rejects a matching closer when an odd backslash run precedes it. CommonMark treats backslashes as
literal inside code spans, so markdown-it proves this source is a code span followed by text:

```text
# T

`a\`b`
```

The implementation instead marks the complete paragraph opaque and leaves the valid parser-owned code unnormalized.
For a recognized one-column table containing `` `a\`b|c` ``, the same mistake leaves the table opaque instead of
allowing
the extra physical cell to reach the required `TableError` path.


#### Impact

The formatter fails to own a required inline-code form despite a safe parser boundary and can accept a recognized table
that violates the contract's non-droppable extra-cell rule. This bypasses canonical rendering and required validation.


#### Fix

Do not apply backslash escaping to a code-span closer. Keep backslash parity for code-span openers and table delimiters
where Markdown syntax requires it, but match a closer solely by exact run length and adjacent backticks.


#### Outcome


### Significant

#### S01 Equal-level sibling headings get insufficient spacing


#### Where

`src/dot_tools/markdown_formatter/normalize.py:562-565` and `src/dot_tools/markdown_formatter/render.py:248-249`


#### Issue

When no body block precedes a heading, normalization always stores `blank_lines_before=1`. Rendering converts that to
two
LF bytes, one blank line. The independent probe:

```text
# T
## A
## B
```

produced:

```text
b'# T\n\n---\n\n## A\n\n## B\n'
```

AC05 requires two blank lines before an equal-level sibling, which means three LF bytes between `## A` and `## B`.


#### Impact

Canonical heading spacing is wrong for adjacent siblings, so the formatter does not implement repository heading style
for
a valid heading sequence.


#### Fix

Track the previous heading level and relationship when assigning `blank_lines_before`. Give equal-level siblings the
normal
two-blank-line spacing; retain the one-blank-line child rule and separator override for downward transitions.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global fallback
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, and S01 are formatter-specific findings. The two review-19 cleanup blockers are resolved, the revised HTML
requirement is respected, and the configure pytest failure plus repository-wide Ty diagnostics are unrelated baselines.
Resolve all three findings before approval.
