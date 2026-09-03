# Execution Review: Generic AST-based Markdown formatter

This review independently checks the formatter against the approved implementation plan, execution journal, and
execution review 07. The focused suite and quality tools pass for the formatter paths, but adversarial probes still
find formatter-specific correctness and safety defects.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--07.md`


## Scope

**whole-plan - Iteration 08**

The review covers the formatter package, parser and source spans, normalization and rendering, document orchestration,
operations, grouped CLI, compatibility wrapper, dependency and registration changes, tests, and fixtures recorded in
the journal. The plan, journal, and prior review were read but not modified.


## Issue Summary

- **Critical**:    6
- **Significant**: 2
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                                   | Result                                                                                                        |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                          | Passed. The environment resolves the pinned formatter dependency.                                             |
| `uv run pytest tests/markdown_formatter --no-cov`                                                  | Passed: 185 tests. The suite does not cover the failures below.                                               |
| `uv run pytest --no-cov`                                                                           | Failed: 498 passed, 1 failed. The failure is the independently confirmed unrelated configure assertion below. |
| `uv run ruff check src tests`                                                                      | Passed: `All checks passed!`.                                                                                 |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`                        | Passed.                                                                                                       |
| `uv run ty check`                                                                                  | Failed: 74 diagnostics in existing non-formatter paths. No formatter path appears.                            |
| `git diff --check`                                                                                 | Passed.                                                                                                       |
| Grouped CLI and wrapper help/smoke probes                                                          | Passed. Help succeeds; wrapper check and second-pass format report `UNCHANGED` and `summary ... SUCCESS 1`.   |
| Empty-list, body-delimiter, opaque-code, hard-break-list, center-table, and fence probes           | Failed. These reproduce C01-C05 and S01 below.                                                                |
| Lexical alias, frontmatter comment, table/code span, recursive-container, and common corpus probes | Passed where covered by existing tests and direct probes; they do not cover the failures listed below.        |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The test expects `.config/opencode/package.json` to be empty. That existing repository policy failure is unrelated to
the
formatter and is excluded from the formatter findings. The repository-wide Ty diagnostics likewise contain no
`markdown_formatter` or `cli/markdown.py` path.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                             |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 01/AC01 | ✓      | `pyproject.toml`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                         |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/` contains the package and public model modules.                                                   |
| 01/AC03 | ⚠      | `models.py:8-66`, `cli/markdown.py`, and focused contract tests establish the public surface, but C01-C06 remain in formatter paths. |


### Task 02

| AC      | Status | Evidence                                                                                                                              |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-143` exposes extraction, validation, and serialization; frontmatter tests exercise the APIs.                       |
| 02/AC02 | ✓      | `frontmatter.py:87-99` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                  |
| 02/AC03 | ✓      | `frontmatter.py:52-119` enforces the restricted node and scalar envelope, including duplicate, alias, tag, and comment-only handling. |
| 02/AC04 | ✓      | `frontmatter.py:142-203` implements deterministic framing and scalar escaping; exact frontmatter tests pass.                          |


### Task 03

| AC      | Status | Evidence                                                                                                                                            |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:35-111,393-548` provides byte-addressed AST models and table/fence spans, but C04 shows nested fence metadata still misattributes bytes. |
| 03/AC02 | ⚠      | `parser.py:112-128,170-299` owns the requested basic structures, but opaque code-first masking fails for C03.                                       |
| 03/AC03 | ✗      | `parser.py:922-955` does not collect code ranges from opaque blocks before HTML scanning, so C03 violates the required fail-closed ownership rule.  |
| 03/AC04 | ⚠      | The semantic-token pass and opaque fallback cover many inline cases, but C04 demonstrates incorrect nested fence payload/span ownership on reparse. |
| 03/AC05 | ✗      | The required code-first scan includes opaque ranges, but `_reject_raw_html` only masks recognized code ranges. See C03.                             |
| 03/AC06 | ⚠      | Task metadata and heading-break policy work in covered cases, but C01 and C04 show recursive recognized structures are not fully safe.              |


### Task 04

| AC      | Status | Evidence                                                                                                                                           |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-93` defines the normalized state and `test_normalize.py` asserts state directly.                                                  |
| 04/AC02 | ✗      | `normalize.py:235-248` replaces hard-break list content with physical source lines after wrapping; C05 produces a 151-codepoint continuation line. |
| 04/AC03 | ✗      | `normalize.py:222-236` references `paragraph_source` without initializing it for empty list items, causing C01's uncaught crash.                   |
| 04/AC04 | ⚠      | Heading transitions and ordinary containers are stable, but C04 shows nested recognized container metadata remains inconsistent.                   |
| 04/AC05 | ✗      | `normalize.py:346` uses `3 + (1 if alignment != "none" else 0)` rather than `3 + marker count`; S01 renders a center marker one dash short.        |
| 04/AC06 | ⚠      | Direct code normalization and collision-safe fences pass, but nested fence payload metadata remains wrong under C04.                               |


### Task 05

| AC      | Status | Evidence                                                                                                                                     |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:138-166` supplies canonical separators and final-newline behavior, but it renders the incorrect normalized center width from S01. |
| 05/AC02 | ✗      | `render.py:27-70` repeats the same incorrect marker-width minimum, and C04's reparsed nested fence payload is not semantic-preserving.       |
| 05/AC03 | ⚠      | `__init__.py` composes typed stages and error propagation, but C01-C03 expose unsafe stage behavior.                                         |
| 05/AC04 | ⚠      | Golden and idempotence tests pass for covered inputs, but S02 identifies missing regressions for the failed boundary cases.                  |


### Task 06

| AC      | Status | Evidence                                                                                                                                          |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:21-35` resolves, sorts, lexically normalizes, deduplicates, and recursively discovers Markdown paths.                              |
| 06/AC02 | ⚠      | `operations.py:85-101,136-213` preflights and cleans normal writes, but C06 shows collision cleanup can delete an unrelated file.                 |
| 06/AC03 | ✗      | `operations.py:85-101` unconditionally unlinks a predetermined temp pathname after `open("xb")` fails, violating safe cleanup.                    |
| 06/AC04 | ✓      | `operations.py:107-120,178-213` implements the documented status precedence and mappings for covered outcomes.                                    |
| 06/AC05 | ⚠      | CLI and diagnostics tests cover representative records and streams, but the temp collision safety case is missing from the contract matrix.       |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py` captures entry CWD, discovers the repository, delegates through `uv run --project`, and passes streams/status. |
| 06/AC07 | ⚠      | `cli/main.py`, grouped help, wrapper smoke, and focused tests pass, but the full operation safety matrix is incomplete.                           |


### Task 07

| AC      | Status | Evidence                                                                                                                                      |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | `tests/markdown_formatter/fixtures/corpus/` covers the requested broad categories, but it omits the independently reproduced failures in S02. |
| 07/AC02 | ✗      | Formatter-focused tests, Ruff, and focused Ty pass, but C01-C06/S01 remain. Full pytest and repository Ty are also red on baseline issues.    |


## Scope Verification

| File or path                                                            | Justification                                | Status |
| ----------------------------------------------------------------------- | -------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                      | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                      | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public contracts                     | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration       | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted frontmatter               | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing and repair passes            | ⚠      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repair passes      | ⚠      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repair passes          | ⚠      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operations and replacement safety    | ⚠      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                        | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                 | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation             | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 focused tests and corpus | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                             | ✓      |

All modified production paths remain within the approved formatter, CLI, wrapper, dependency, and registration scope.
The warning statuses identify implementation or coverage gaps within those justified paths, not scope creep.


## Prior Review Resolution

| Review 07 finding | Status | Current evidence                                                                                                                                   |
| ----------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01               | ⚠      | Basic recursive list/blockquote output now converges in covered cases, but C04 still fails direct reparsed nested fence metadata.                  |
| C02               | ⚠      | Basic hard-break and lazy-continuation cases pass, but C05 shows hard-break list continuations bypass the 120-codepoint limit.                     |
| C03               | ✓      | `parser.py:486-548` and parser regressions establish LF/CRLF table row and cell spans in covered table cases.                                      |
| C04               | ⚠      | Direct fenced payload span repairs pass for direct fences, but C04 remains for nested quoted/list fence metadata.                                  |
| S01               | ✓      | `frontmatter.py:108-119` and `test_frontmatter.py::test_comment_only_root_is_empty_mapping_and_reparses_canonical_bytes` cover comment-only roots. |
| S02               | ✓      | `operations.py:15-35` and `test_operations.py::test_deduplicates_lexical_path_aliases_without_resolving_symlinks` cover lexical aliases.           |
| S03               | ✗      | The focused suite is larger, but S02 remains because the new independently reproduced C01-C06/S01 cases are still not all covered.                 |


## Findings

### Summary

| Finding | Title                                                       | Outcome |
| ------- | ----------------------------------------------------------- | ------- |
| C01     | Empty list items crash during normalization                 |         |
| C02     | Body code delimiters trigger false multiple-YAML rejection  |         |
| C03     | Opaque code-like HTML is not masked before policy scanning  |         |
| C04     | Nested quoted/list fence metadata includes structural bytes |         |
| C05     | List hard-break continuations bypass the prose width limit  |         |
| C06     | Temp-file collision cleanup deletes an unrelated file       |         |
| S01     | Center-table minimum width is one dash too short            |         |
| S02     | Regression coverage omits the reproduced formatter failures |         |


### Critical

#### C01: Empty list items crash during normalization


#### Where

`src/dot_tools/markdown_formatter/normalize.py:222-236`


#### Issue

When a list item has no paragraph, the `else` branch initializes `paragraph_nodes` and `paragraph_value` but not
`paragraph_source`. The unconditional read at line 236 then raises `UnboundLocalError`. Inputs including
`b"# T\\n\\n-\\n"`, `b"# T\\n\\n1.\\n"`, and whitespace-only or nested-child empty items all crash instead of rendering
a safe empty item or preserving an
opaque parser-owned block.


#### Impact

Valid Markdown input causes an uncaught implementation exception. The formatter violates its fail-closed behavior and
cannot process empty list items.


#### Fix

Initialize `paragraph_source = b""` in the no-paragraph branch, then add explicit empty-item and empty-item-with-nested-
children tests that assert semantic output, idempotence, and the intended opaque fallback where ownership is not proven.


#### Outcome


----

### Critical

#### C02: Body code delimiters trigger false multiple-YAML rejection


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:99-101`


#### Issue

After extracting the frontmatter envelope, the implementation scans the Markdown body for `---` patterns and raises a
multiple-document error. This treats body thematic breaks or code-fence content as YAML documents. For
`b"---\\na: 1\\n---\\n# T\\n\\n```text\\n---\\n---\\n```\\n"`, the body is valid Markdown but `extract_frontmatter`
raises
`FrontmatterError("multiple YAML documents are not permitted")`.


#### Impact

Valid body Markdown cannot follow valid frontmatter when it contains common delimiter-like content. Envelope validation
is not isolated from body parsing, so the formatter rejects documents outside the approved YAML boundary.


#### Fix

Remove the body-wide delimiter heuristic. Detect multiple YAML documents only from the extracted frontmatter slice using
the YAML event/node stream, while preserving all body bytes for Markdown parsing. Add a regression with delimiter lines
in
fenced code and a body thematic break.


#### Outcome


----

### Critical

#### C03: Opaque code-like HTML is not masked before policy scanning


#### Where

`src/dot_tools/markdown_formatter/parser.py:922-955`


#### Issue

The raw-HTML pass masks recognized fences and inline code spans, but it never masks a parser-delimited opaque block. For
`b"# T\\n\\n\\x00 `<span>`\\n"`, the NUL forces an opaque fallback, yet the code-like `<span>` remains in the scan and
raises `RawHtmlError`.


#### Impact

The implementation violates the required code-first ordering and rejects an opaque region based on text that must remain
outside the raw-HTML policy scan. It also makes opaque preservation dependent on incidental inline recognition.


#### Fix

Collect code intervals and opaque-block intervals from the complete parser tree before scanning. Mask only code content
within opaque regions, not arbitrary opaque text, and ensure raw HTML outside those code ranges still raises. Add tests
for
code-like HTML in opaque inline, fenced, indented, and nested-container regions.


#### Outcome


----

### Critical

#### C04: Nested quoted/list fence metadata includes structural bytes


#### Where

`src/dot_tools/markdown_formatter/parser.py` fence metadata construction and nested structural-prefix handling


#### Issue

For `b"# T\\n\\n> - a\\n>   ```text\\n>   x\\n>   ```\\n"`, the first rendered output is visually stable, but reparsing
it stores the nested `CodePayload.payload` as
`b">   x\\n>   \\` rather than `b"x\\n"`. Its payload span also covers quote prefixes and closing-fence bytes. The
nested fence therefore does not satisfy the
byte-addressed semantic payload contract even though the focused normalized-payload test passes.


#### Impact

Consumers of the AST receive incorrect payload and source spans. A later normalization pass can preserve a visually
stable
document while silently attributing structural syntax to code content.


#### Fix

Build nested fence marker, info, and payload spans from the parser's physical line maps after removing each proven quote
and
list indentation prefix exactly once. Derive payload end at the start of the closing fence line and assert
`source[payload_span.start:payload_span.end] == payload` for nested LF and CRLF fences, including trailing spaces.


#### Outcome


----

### Critical

#### C05: List hard-break continuations bypass the prose width limit


#### Where

`src/dot_tools/markdown_formatter/normalize.py:235-248`


#### Issue

The hard-break repair replaces wrapped segments with raw physical source lines. That bypasses `_wrap_inline` for the
continuation segment. A list beginning `- first  ` followed by 30 `word` tokens emits a continuation line of 151 code
points, including indentation, rather than wrapping the prose segment at 120 code points excluding structural
indentation.


#### Impact

The formatter violates the explicit 120-codepoint wrapping contract for a common list structure. Output width and
idempotence behavior depend on whether the source happened to contain a hard break.


#### Fix

Retain hard-break token groups and wrap each segment independently through the same token-aware wrapper used for
ordinary
paragraphs. Apply the active list/container prefix only after wrapping, and add a long continuation regression asserting
the content width and three-pass equality.


#### Outcome


----

### Critical

#### C06: Temp-file collision cleanup deletes an unrelated file


#### Where

`src/dot_tools/markdown_formatter/operations.py:85-101`


#### Issue

The replacement code chooses a deterministic pathname before opening it with `xb`. If that pathname already exists,
`open("xb")` raises, but the `finally` block still unlinks the same pathname. A pre-existing unrelated temp file is
therefore deleted by a failed formatting attempt.


#### Impact

A write failure can destroy an unrelated file in the destination directory. This violates the atomic-operation safety
contract and makes cleanup actively unsafe under PID/path collisions.


#### Fix

Track whether this invocation successfully created the temporary file, and unlink only that created file. Prefer a
unique
same-directory temporary file created with exclusive semantics, retaining its path only after successful creation. Add a
collision regression that verifies the pre-existing file survives and no formatter temp file remains.


#### Outcome


----

### Significant

#### S01: Center-table minimum width is one dash too short


#### Where

`src/dot_tools/markdown_formatter/normalize.py:346` and `src/dot_tools/markdown_formatter/render.py:60,64-70`


#### Issue

Both width calculations use a one-bit aligned-column adjustment instead of counting alignment markers. For a
center-aligned
column, the required minimum is `3 + 2 = 5`, but the implementation chooses 4 and renders `:--:` instead of `:---:` for
`| a |\\n| :---: |\\n| x |\\n`.


#### Impact

Canonical table output diverges from the approved serialization algorithm. Center marker geometry is not preserved and
the
normalizer and renderer disagree with the required minimum-width rule.


#### Fix

Compute marker count as two for center, one for left/right, and zero for unaligned, then use
`max(content_width, 3 + marker_count)` in both normalization and rendering. Add exact center-width and three-pass table
tests.


#### Outcome


----

### Significant

#### S02: Regression coverage omits the reproduced formatter failures


#### Where

`tests/markdown_formatter/` and the Task 03 through Task 07 fixture requirements in `implementation-plan.md:194-418`


#### Issue

The focused suite passes 185 tests, but it has no regression for empty list items, body delimiter false positives,
opaque code-like HTML masking, direct nested `CodePayload` spans, long list hard-break continuation wrapping, center
marker
width, or temp-file collision cleanup. Existing nested-fence coverage inspects normalized payload state but does not
inspect
the parser metadata and source slice after reparsing.


#### Impact

The green focused suite gives false confidence while six critical formatter defects and one serialization defect remain.
Future repair passes can regress these boundaries without detection.


#### Fix

Add exact-byte and semantic-reparse regressions for C01-C06 and S01. Assert every nested code payload's bytes and span
slice,
test physical-width limits after list prefix application, and verify collision files survive failed replacement. Make
the
three-pass and source-ownership assertions explicit in the corpus or edge-contract suite.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C06 must be resolved before approval. S01 and S02 must be addressed in the same pass. The unrelated configure pytest
failure and repository-wide Ty diagnostics are independently confirmed baseline issues and are excluded from formatter
findings.
