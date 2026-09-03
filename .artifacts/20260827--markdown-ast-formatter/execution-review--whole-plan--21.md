# Execution Review: Generic AST-based Markdown formatter

This independent iteration-21 review rechecks review 20 against the revised plans and current journal. HTML-looking
Markdown is accepted, parser-delimited HTML blocks may remain opaque, and `RawHtmlError` is not a contract.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--20.md`


## Scope

**whole-plan - Iteration 21**

The review started with the current worktree diff, then inspected the revised plans, journal, review 20, formatter
source, focused tests, and fixtures. It independently re-tested review-20 C01, C02, and S01, then ran the whole-plan
quality matrix. It did not modify source, tests, plans, the journal, or prior reviews. This artifact is the only
authored
file.


## Issue Summary

- **Critical**: 3
- **Significant**: 2
- **Trivial**: 1


## Verification Evidence

| Command or probe                                  | Result                                                                                                           |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                         | Passed; `markdown-it-py==4.2.0` is resolved.                                                                     |
| `uv run pytest tests/markdown_formatter --no-cov` | Passed: 299 tests.                                                                                               |
| `uv run pytest`                                   | 612 passed, 1 failed; coverage 83.14%, above the 70% threshold.                                                  |
| Focused Ruff                                      | Passed for formatter source and tests.                                                                           |
| `uv run ruff check src tests`                     | Passed.                                                                                                          |
| Focused Ty                                        | Passed for formatter source and tests.                                                                           |
| `uv run ty check`                                 | Failed with 74 repository-baseline diagnostics; no formatter path appeared.                                      |
| Grouped command help                              | Passed for `markdown`, `format`, and `check`.                                                                    |
| Wrapper help and canonical smoke                  | Passed; check and format reported `UNCHANGED` and `SUCCESS 1`.                                                   |
| `git diff --check`                                | Passed.                                                                                                          |
| Review-20 C01 re-test                             | Passed for LF and CRLF lazy continuation; text was retained and output converged.                                |
| Review-20 C02 re-test                             | Passed for LF and CRLF code closers and table extra-cell errors.                                                 |
| Review-20 S01 re-test                             | Passed; siblings use three LF bytes, while separator cases retain one blank line on each side.                   |
| Frontmatter finite-real matrix                    | Passed 19,993 finite IEEE-754 samples plus adversarial non-finite inputs.                                        |
| HTML policy matrix                                | Passed accepted inline, block, escaped-angle, code, and opaque cases with LF and CRLF.                           |
| Parser and span matrix                            | Passed recursive inline, table, code, LF/CRLF, and EOF ownership probes except S02.                              |
| Structure and wrapping matrix                     | Passed covered prose, paragraph, list, container, heading, separator, table, and code cases; C01-C03/S01 remain. |
| Active rejection scan                             | No `RawHtmlError` or embedded-HTML rejection path exists in formatter source or tests.                           |
| Operations and failure-injection matrix           | Passed statuses, records, digests, snapshots, locks, replacement, cleanup, and CLI probes.                       |
| Independent formatter probes                      | Found C01, C02, C03, S01, and S02 below.                                                                         |

The full pytest failure is the unrelated configure assertion:

```text
tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics are the existing diagnostics in the PDF, clipboard/Gmail, OpenCode cost/trend,
configure, Jira, and spinner paths. They do not reference formatter code. These two results are baselines, not formatter
findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                    |
| ------- | ------ | ----------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml`, resolved lockfile, and passing `uv sync`. |
| 01/AC02 | ✓      | `models.py:8-66` and formatter package modules exist.       |
| 01/AC03 | ✓      | `cli/markdown.py:11-36`; public contract tests pass.        |


### Task 02

| AC      | Status | Evidence                                                                  |
| ------- | ------ | ------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-142`; all three APIs pass focused tests.               |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters and body preservation pass.     |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; unsafe YAML and finite-real probes pass.         |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; ordering, codecs, thresholds, and framing pass. |


### Task 03

| AC      | Status | Evidence                                                                                     |
| ------- | ------ | -------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:31-123` provides byte-addressed models, but empty ATX heading ownership is wrong. |
| 03/AC02 | ✓      | `parser.py:224-325,742-910`; exercised CommonMark blocks and inline forms are parsed.        |
| 03/AC03 | ⚠      | Exact spans pass covered cases, but empty headings are not mapped to parser semantic text.   |
| 03/AC04 | ✓      | `parser.py:184-203,836-910`; review-20 code closer and ownership cases pass.                 |
| 03/AC05 | ✓      | `parser.py:301-302,856-900`; accepted HTML matrix passes with opaque HTML blocks.            |
| 03/AC06 | ✓      | `parser.py:1128-1152`; task metadata and source-break policy pass.                           |


### Task 04

| AC      | Status | Evidence                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:19-98`; normalized-state tests pass.                                              |
| 04/AC02 | ⚠      | `normalize.py:130-149,525-546,660-709`; canonical delimiter collisions and hard-break C03 fail. |
| 04/AC03 | ✓      | `normalize.py:318-380`; ambiguous lazy continuation is preserved and converges.                 |
| 04/AC04 | ⚠      | `normalize.py:570-573`; ancestor headings receive child spacing, as S01 documents.              |
| 04/AC05 | ✓      | `normalize.py:489-511`; LF/CRLF table geometry and extra-cell checks pass.                      |
| 04/AC06 | ✓      | `normalize.py:577-622`; code payload, info, fence, LF/CRLF, and EOF probes pass.                |


### Task 05

| AC      | Status | Evidence                                                                                |
| ------- | ------ | --------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:190-220,239-303`; composition passes except affected inline cases.           |
| 05/AC02 | ⚠      | `normalize.py:101-200`; emphasis, code-boundary, and hard-break canonical output fails. |
| 05/AC03 | ✓      | `__init__.py:10-24`; document orchestration and typed error tests pass.                 |
| 05/AC04 | ⚠      | Golden fixtures pass, but independent semantic and idempotence probes found C01-C03.    |


### Task 06

| AC      | Status | Evidence                                                                                           |
| ------- | ------ | -------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:21-42`; collection, sorting, lexical deduplication, and discovery errors pass.      |
| 06/AC02 | ✓      | `operations.py:91-126,205-240`; preflight, replacement, stop, and cleanup probes pass.             |
| 06/AC03 | ✓      | `operations.py:44-126`; snapshots, locks, identity, mode, type, and replacement pass.              |
| 06/AC04 | ✓      | `operations.py:133-147`; total status precedence passes.                                           |
| 06/AC05 | ✓      | `operations.py:149-158`, `cli/markdown.py:15-25`; streams, records, diagnostics, and digests pass. |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD, discovery, delegation, and passthrough pass.        |
| 06/AC07 | ✓      | `cli/main.py:35-39`; grouped CLI and wrapper contract tests pass.                                  |


### Task 07

| AC      | Status | Evidence                                                                            |
| ------- | ------ | ----------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus categories pass, but the independent inline and heading cases are uncovered. |
| 07/AC02 | ⚠      | Focused formatter gates pass; formatter-specific C01-C03 and S01-S02 remain.        |


## Scope Verification

| File or path                                  | Justification                                 | Status                         |
| --------------------------------------------- | --------------------------------------------- | ------------------------------ |
| `pyproject.toml`, `uv.lock`, `models.py`      | Task 01 dependency and public contract        | ✓                              |
| `markdown_formatter/__init__.py`              | Tasks 01 and 05 orchestration                 | ✓                              |
| `frontmatter.py` and frontmatter tests        | Task 02 restricted YAML                       | ✓                              |
| `parser.py` and parser tests                  | Task 03 parsing, spans, and policy boundaries | ⚠, S02                         |
| `normalize.py` and normalization tests        | Task 04 normalization                         | ⚠, C01, C03, and S01           |
| `render.py` and render/document tests         | Task 05 rendering                             | ⚠, C01 and C02                 |
| `operations.py` and operation tests           | Task 06 safe operations                       | ✓                              |
| `cli/markdown.py`, `cli/main.py`, and wrapper | Task 06 CLI and delegation                    | ✓                              |
| `tests/markdown_formatter/` and fixtures      | Tasks 02 through 07 contract coverage         | ⚠, missing regression coverage |
| Revised design and implementation plans       | Human-directed HTML requirement revision      | ✓, not edited in this review   |
| Implementation journal                        | Execution record                              | ✓, not edited in this review   |

The implementation remains within formatter, dependency, CLI, wrapper, test, fixture, and artifact scope. The review
did not attribute the configure pytest failure or repository-wide Ty diagnostics to this feature.


## Prior Review Resolution

| Review-20 finding                                         | Status | Current evidence                                                                        |
| --------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| C01 Lazy list continuation can be silently dropped        | ✓      | `normalize.py:337-345`; LF/CRLF re-test retains `11. [ ] two` and converges.            |
| C02 Code closer parity hides table errors                 | ✓      | `parser.py:1016-1034`; LF/CRLF code and extra-cell re-tests pass.                       |
| S01 Equal-level sibling headings get insufficient spacing | ✓      | `normalize.py:570-573`; sibling re-test yields exactly three LF bytes between headings. |

The review-19 cleanup fixes remain confirmed by the operation test suite and independent replacement failure probes.


## Findings

### Summary

| Finding | Title                                                    | Outcome         |
| ------- | -------------------------------------------------------- | --------------- |
| C01     | Canonical emphasis delimiters collide with adjacent text | Blocks approval |
| C02     | Canonical code delimiters change adjacent code semantics | Blocks approval |
| C03     | Hard-break ownership falls through on trailing spaces    | Blocks approval |
| S01     | Ancestor headings receive child spacing                  | Blocks approval |
| S02     | Empty ATX headings are not parser-semantically owned     | Blocks approval |
| T01     | Dead formatter helpers remain in production modules      | Blocks approval |


### Critical

#### C01 Canonical emphasis delimiters collide with adjacent text


#### Where

`src/dot_tools/markdown_formatter/normalize.py:130-149` and `525-546`


#### Issue

The ordinary text codec leaves literal `*` and `_` bytes in place while neighboring emphasis or strong nodes are
canonicalized to `*` and `**`. Independent formatting of `b"# T\\n\\na*_g_*\\n"` returns `b"# T\\n\\na**g**\\n"`; the
parser changes from text plus emphasis plus text to a strong node. A table cell containing
`*a*_b_` first renders as `*a**b*` and changes again on the second pass to an escaped form.


#### Impact

Valid Markdown changes meaning or fails idempotence. The formatter can commit a document whose inline structure differs
from the input.


#### Fix

Make inline encoding context-aware across adjacent atoms. Escape literal delimiter bytes when canonical neighboring
nodes would otherwise create a new delimiter run, and apply the same proof to table cells. Reparse the result and assert
semantic shape before returning it.


#### Outcome


----

#### C02 Canonical code delimiters change adjacent code semantics


#### Where

`src/dot_tools/markdown_formatter/normalize.py:130-149,183-200`


#### Issue

The text codec leaves literal backticks next to a canonical inline-code fence. The independent probe was:

````text
source: b"# T\n\n```a`x`\n"
first:  b"# T\n\n```a```x```\n"
````

Before formatting, the parser owns literal text followed by code payload `x`; afterward it owns code payload `a`
followed
by text. A CommonMark render confirms the semantic change.


#### Impact

The required code-span normalization is not lossless at an inline-atom boundary. Stable bytes do not make the changed
code payload safe.


#### Fix

Protect literal backtick runs in ordinary text from adjacent generated code delimiters, or preserve the containing
paragraph opaque when a safe canonical encoding cannot be proven. Reparse canonical spans and compare payloads.


#### Outcome


----

#### C03 Hard-break ownership falls through on trailing spaces


#### Where

`src/dot_tools/markdown_formatter/parser.py:757-764,848-934` and `normalize.py:660-679`


#### Issue

For `b"# T\\n\\na  \\nb \\n"`, MarkdownIt emits a hard-break token. The source scanner consumes the final text token
only through `b`, leaves its trailing space unowned, and returns `None`. The conservative fallback then treats the
entire paragraph as ordinary text. The first output is `b"# T\\n\\na  \\nb\\n"`; the second is
`b"# T\\n\\na\\\\\\nb\\n"` with the hard break canonicalized only on pass two.


#### Impact

Formatting a valid paragraph produces noncanonical, non-idempotent output and leaves source hard-break syntax subject to
the fallback text codec.


#### Fix

Map the parser hard-break token and its source delimiter as one exact interval, while handling insignificant trailing
spaces in the following text token. If the interval cannot be proven, preserve the complete paragraph opaque instead of
downgrading a recognized hard break to ordinary text.


#### Outcome


### Significant

#### S01 Ancestor headings receive child spacing


#### Where

`src/dot_tools/markdown_formatter/normalize.py:570-573`


#### Issue

The blank-line calculation assigns one blank line whenever no body block precedes a heading and the previous heading
level
differs. In `# T`, `## A`, `### B`, `## C`, the final ancestor heading receives `b"### B\\n\\n## C"` instead of the
required two blank lines.


#### Impact

Heading spacing is wrong for a valid upward transition. The sibling repair did not cover this distinct relationship.


#### Fix

Classify child, sibling, and ancestor relationships explicitly. Use the one-blank child rule only for a true child
without
body, use two blanks for ancestors and siblings, and let a generated separator override both sides of a downward
transition.


#### Outcome


----

#### S02 Empty ATX headings are not parser-semantically owned


#### Where

`src/dot_tools/markdown_formatter/parser.py:449-474,259-272`


#### Issue

The heading source extractor only removes an opening marker when whitespace follows it. For the valid empty heading
`b"#\\n"`, it passes `b"#"` to the inline scanner, which records a text node instead of the parser's empty inline token.
The
first formatting pass returns `b"# #\\n"`; the parser then sees a different source shape. The same defect affects empty
H2 and
empty headings nested in recognized containers.


#### Impact

The AST does not reflect parser-owned heading semantics, violating the source-span and normalized-state contract for a
valid boundary case. The accidental closing-marker spelling hides the defect from a byte-only idempotence check.


#### Fix

Use the parser inline token content for an empty heading, or explicitly map the marker-only source to an empty owned
inline
interval. Render an intentional empty heading spelling and add LF/CRLF recursive ownership tests.


#### Outcome


### Trivial

#### T01 Dead formatter helpers remain in production modules


#### Where

`parser.py:647,691,937`, `normalize.py:175,712`, and `render.py:19`


#### Issue

The production formatter contains unused `_has_even_escape_pipe`, `_semantic_cell_matches`, `_scan_inline_legacy`,
`_paragraph`, `_strip_prefix`, and `_fence` helpers. The active implementation has separate code paths for the same
concerns, while Ruff and Ty do not report unused private functions.


#### Impact

Dead compatibility code increases review and maintenance surface and leaves stale behavior available for accidental
future
use.


#### Fix

Delete the unused helpers, or wire each one into a covered production path and add behavior tests.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback
- `engineer-reviewer`: global agent definition
- `write-docs`: global fallback
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, and C03 are formatter-specific semantic and idempotence blockers. S01 and S02 violate the revised heading and
parser contracts. T01 should be cleaned up before approval. The configure pytest failure and repository-wide Ty
diagnostics
remain unrelated baselines.
