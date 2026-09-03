# Execution Review: Generic AST-based Markdown formatter

This review independently checks the current formatter against the approved implementation plan, execution journal, and
execution review 06. It starts from the current diff and supplements the focused suite with adversarial semantic,
source-span, recursive-container, frontmatter, operation, and three-pass probes.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--06.md`


## Scope

**whole-plan - Iteration 07**

The review covers the formatter package, parser and source spans, normalization and rendering, document orchestration,
operations, grouped CLI, compatibility wrapper, dependency and registration changes, tests, and fixtures recorded in
the journal. The plan, journal, and prior review were read but not modified.


## Issue Summary

- **Critical**:    4
- **Significant**: 3
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                  | Result                                                                                                                                               |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                         | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                                            |
| `uv run pytest tests/markdown_formatter --no-cov`                                 | Passed: 162 tests. This does not cover the failing probes below.                                                                                     |
| `uv run pytest`                                                                   | Failed: 475 passed, 1 failed. The failure is the independently confirmed unrelated configure assertion below.                                        |
| `uv run ruff check src tests`                                                     | Passed: `All checks passed!`.                                                                                                                        |
| `uv run ty check`                                                                 | Failed: 74 diagnostics in existing PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears.                    |
| `uv run dt markdown --help`, `format --help`, `check --help`                      | Passed.                                                                                                                                              |
| Compatibility wrapper help, canonical `check`, and canonical second-pass `format` | Passed. Both operations reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                                            |
| `git diff --check`                                                                | Passed.                                                                                                                                              |
| Recursive list/blockquote three-pass probes                                       | Failed. Nested list child paragraphs acquire an extra blockquote and nested code fences grow quote prefixes and fence lengths on each pass. See C01. |
| List hard-break and lazy-continuation probes                                      | Failed. `- first  \n  second` becomes `- first second`; lazy list lines such as `3. parent\n   9. child` are flattened. See C02.                     |
| CRLF table source-span probe                                                      | Failed. Separator and data-cell spans point one or more bytes before their claimed source slices. See C03.                                           |
| CRLF fenced-code payload probe                                                    | Failed. `CodePayload.payload` and `payload_span` omit the LF from a CRLF payload line. See C04.                                                      |
| Comment-only frontmatter probe                                                    | Failed. `---\n# comment\n---\n# T\n` raises `FrontmatterError` instead of representing the empty YAML mapping. See S01.                              |
| Path alias deduplication probe                                                    | Failed. `x.md` and `a/../x.md` produce two records when `a` exists. See S02.                                                                         |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The failing test reads `.config/opencode/package.json` and asserts an OpenCode dependency policy unrelated to the
formatter. The repository-wide Ty diagnostics likewise contain no `markdown_formatter` or `cli/markdown.py` path, so
both baseline failures are excluded from formatter findings. The formatter-specific recursive and source-span failures
remain blockers.


## Acceptance Criteria Verification

### Task 01

| Task / AC | Status | Evidence                                                                                                                                                  |
| --------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-16`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                                        |
| 01/AC02   | ✓      | `src/dot_tools/markdown_formatter/` contains the package and public model modules.                                                                        |
| 01/AC03   | ⚠      | `models.py:8-66`, `cli/markdown.py:11-25`, and focused contract tests establish the public surface, but recursive and source-span behavior fails C01-C04. |


### Task 02

| Task / AC | Status | Evidence                                                                                                                                                                 |
| --------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 02/AC01   | ✓      | `frontmatter.py:87-143` exposes extraction, validation, and serialization; `test_frontmatter.py` exercises all three APIs.                                               |
| 02/AC02   | ✓      | `frontmatter.py:87-119` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                                                    |
| 02/AC03   | ⚠      | `frontmatter.py:52-85,122-139` rejects the tested unsafe YAML constructs, but comment-only empty documents fail instead of taking the approved empty-root path. See S01. |
| 02/AC04   | ⚠      | `frontmatter.py:142-203` implements deterministic framing and scalar escaping, but the focused tests do not establish every exact empty/comment and scalar-tag case.     |


### Task 03

| Task / AC | Status | Evidence                                                                                                                                                                                                          |
| --------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01   | ⚠      | `parser.py:35-111,170-177` provides byte-addressed models and token maps, but `parser.py:393-427` produces incorrect CRLF table cell spans. See C03.                                                              |
| 03/AC02   | ⚠      | `parser.py:95-111,180-299` uses CommonMark-plus-table parsing and owns the simple requested nodes, but unprovable list inline regions are flattened by normalization rather than kept structurally safe. See C02. |
| 03/AC03   | ✗      | Exact ownership fails for CRLF table rows, and parser-unproven list continuation/hard-break regions are not made opaque. See C02 and C03.                                                                         |
| 03/AC04   | ⚠      | The semantic-token pass and opaque nested-link fallback cover many inline cases (`parser.py:525-666`), but source ownership is not complete for the listed CRLF/table boundaries.                                 |
| 03/AC05   | ✓      | Code ranges are collected before raw-HTML scanning in `parser.py:875-908`; URI autolinks and processing instructions are covered by `test_parser.py:147-174`.                                                     |
| 03/AC06   | ⚠      | Simple task metadata and downward-break policy work (`parser.py:257-267,927-938`), but recursive list continuation and container composition fail C01-C02.                                                        |


### Task 04

| Task / AC | Status | Evidence                                                                                                                                                                                  |
| --------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01   | ✓      | `normalize.py:16-93` defines the requested normalized state and `test_normalize.py` asserts state directly.                                                                               |
| 04/AC02   | ⚠      | Ordinary token-aware wrapping and hard-break prose pass focused cases (`normalize.py:439-483`, `test_edge_contract.py:208-217`), but list hard breaks are lost in `normalize.py:223-236`. |
| 04/AC03   | ✗      | `normalize.py:209-275` flattens parser-lazy continuation into item prose and does not preserve recursive list/block child structure in all valid cases. See C01-C02.                      |
| 04/AC04   | ⚠      | Heading transitions and separators are stable for simple containers (`normalize.py:366-431`), but recursive list/blockquote composition does not remain stable across three passes.       |
| 04/AC05   | ⚠      | Table alignment, padding, and code-pipe preservation work in representative cases (`normalize.py:315-363`), but exact source ownership for CRLF tables is false, as shown by C03.         |
| 04/AC06   | ⚠      | Code info normalization and collision-safe fence selection work for direct blocks (`normalize.py:388-411`), but nested container code payloads grow on repeated passes. See C01 and C04.  |


### Task 05

| Task / AC | Status | Evidence                                                                                                                                                                          |
| --------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01   | ⚠      | `render.py:136-164` provides canonical LF and final-newline rendering for simple nodes, but nested container rendering applies structural prefixes inconsistently. See C01.       |
| 05/AC02   | ✗      | Direct outputs are not semantic-preserving or idempotent for list-contained blockquotes and fences. `render.py:91-120,152-154` compounds prefixes and code payloads. See C01-C02. |
| 05/AC03   | ⚠      | `__init__.py:10-26` composes frontmatter, parsing, normalization, and rendering and propagates typed errors, but the canonical output is wrong for the failed structures.         |
| 05/AC04   | ✗      | The 162 focused tests pass, but they do not cover the current failing recursive, CRLF span, and comment-only frontmatter cases. See S03.                                          |


### Task 06

| Task / AC | Status | Evidence                                                                                                                                                                                                      |
| --------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01   | ⚠      | `operations.py:15-34` resolves CWD operands, recursively discovers `.md`, and sorts results, but lexical aliases are not deduplicated. See S02.                                                               |
| 06/AC02   | ✓      | `operations.py:135-207` prepares all outputs before replacement, preserves modes, uses same-directory temporary files, stops after the first replacement error, and reports committed/untouched paths.        |
| 06/AC03   | ✓      | `operations.py:37-101` captures content, digest, identity, mode, and type; performs locked final validation; fsyncs and atomically replaces. The documented uncooperating-writer limitation remains explicit. |
| 06/AC04   | ⚠      | `operations.py:107-120,178-213` implements the documented precedence and representative mappings, but the complete mixed status matrix is not established by tests.                                           |
| 06/AC05   | ⚠      | `cli/markdown.py:15-25` and operations diagnostics provide exact records and digest-only mismatch output for covered cases, but the full stream/status/no-write matrix remains incomplete.                    |
| 06/AC06   | ✓      | `.agents/tools/markdown-format.py:11-25` captures entry CWD, discovers the repository, delegates through `uv run --project`, and passes child streams and status through.                                     |
| 06/AC07   | ⚠      | `main.py:20-40` registers the group and help/smoke tests pass, but required recursive semantic and complete operation/wrapper matrix coverage is missing.                                                     |


### Task 07

| Task / AC | Status | Evidence                                                                                                                                                                            |
| --------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01   | ⚠      | `tests/markdown_formatter/fixtures/corpus/` and `test_corpus.py` cover representative categories, but the current recursive/container and CRLF failures are absent from the corpus. |
| 07/AC02   | ✗      | Ruff passes and the formatter suite passes, but formatter-specific probes fail C01-C04. Repository pytest and Ty are also red on independently confirmed unrelated baseline issues. |


## Scope Verification

| File or path                                                            | Justification                                | Status |
| ----------------------------------------------------------------------- | -------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                      | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                      | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public contracts                     | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration       | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted frontmatter               | ⚠      |
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
The ⚠ statuses identify implementation or coverage gaps within those justified paths, not scope creep.


## Prior Review Resolution

| Review 06 finding                                                         | Status | Current evidence                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 nested link ownership changes label semantics                         | ✓      | `parser.py:218-224` makes nested link-like labels opaque; `test_parser.py:157-163` verifies complete source preservation.                                                                                                                                                                 |
| C02 valid URI autolinks are rejected as raw HTML                          | ✓      | `parser.py:640-647` accepts the parser-owned scheme form; `test_parser.py:165-170` covers FTP, URN, and custom schemes.                                                                                                                                                                   |
| C03 blockquoted and escaped/code-pipe tables are unsafe or non-idempotent | ⚠      | Blockquoted tables now fail closed and code-pipe tables are stable in LF probes, but CRLF table spans still point at the wrong bytes. See C03.                                                                                                                                            |
| C04 wrapping and recursive-list behavior are incomplete                   | ⚠      | Ordinary hard-break wrapping passes, but list hard breaks and lazy continuation still flatten in `normalize.py:223-236`. See C02.                                                                                                                                                         |
| C05 backtick-info fence recovery can consume following blocks             | ⚠      | `_join_split_backtick_fences` now falls back to opaque source when the closing boundary cannot be proven (`parser.py:302-326`), avoiding destructive absorption, but valid split fences with following blocks are not recovered as owned code and nested container code remains unstable. |
| C06 raw-HTML processing instructions are silently dropped                 | ✓      | `parser.py:875-879` rejects parser-identified HTML blocks; `test_parser.py:172-175` verifies processing-instruction failure.                                                                                                                                                              |
| S01 input errors lose snapshots and operation coverage is incomplete      | ⚠      | Successful-read input errors retain snapshots (`operations.py:142-150`, `test_operations.py:47-58`), but comment-only frontmatter and the full operation matrix remain untested or incorrect.                                                                                             |
| S02 focused tests miss reproduced formatter failures                      | ⚠      | The suite grew to 162 tests, but none assert the current recursive list/blockquote failures, CRLF table spans, CRLF payload span, comment-only root, or lexical path alias.                                                                                                               |


## Findings

### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| C01     | Recursive list and blockquote rendering is not idempotent       |         |
| C02     | List hard breaks and lazy continuation are flattened            |         |
| C03     | CRLF table cell spans do not slice the claimed source           |         |
| C04     | CRLF fenced-code payload spans omit the line-feed byte          |         |
| S01     | Comment-only YAML frontmatter is rejected as multiple documents |         |
| S02     | Path aliases are not deduplicated before processing             |         |
| S03     | Focused coverage still omits independently reproduced failures  |         |


### Critical

#### C01: Recursive list and blockquote rendering is not idempotent


#### Where

`src/dot_tools/markdown_formatter/normalize.py:209-275,366-423` and
`src/dot_tools/markdown_formatter/render.py:91-120,152-154`


#### Issue

Valid nested list/container blocks are normalized with incompatible prefix ownership. For
`# T\n\n> - a\n>\n>   paragraph\n`, pass one emits `>   >   paragraph` and pass two emits `>   > paragraph`, so the
first canonical result is not stable. For
`# T\n\n> - a\n>\n>   ```text\n>   x\n>   ```\n`, every pass adds another quote prefix to the code payload and increases
the fence length.

`_render_block` applies `NormalizedContainer.prefix` at `render.py:114-116`, while its callers add the active list or
outer-container prefix again at `render.py:104` and `render.py:153-154`. Normalization also sends nested code through
`_normalize_blocks` with only a space prefix, leaving quote syntax in the payload.


#### Impact

The formatter changes recognized recursive structure and fails the required three-pass idempotence contract. Code
payloads and fence boundaries are rewritten on each invocation. This fails Tasks 04 and 05 even though the focused suite
passes.


#### Fix

Define one owner for each active structural prefix. Normalize nested blocks against a composed container context, strip
each parser-proven prefix exactly once, and render a container either with its own prefix or through its caller, never
both. Add exact recursive list/blockquote/code fixtures that assert semantic reparsing and `format(format(format(x))) ==
format(x)`.


#### Outcome


----

### Critical

#### C02: List hard breaks and lazy continuation are flattened


#### Where

`src/dot_tools/markdown_formatter/parser.py:215-228` and
`src/dot_tools/markdown_formatter/normalize.py:221-236,240-274`


#### Issue

When a list paragraph spans physical lines, the parser cannot prove one contiguous inline source interval and leaves
`paragraph.inline` empty. The normalizer then removes the marker, joins all physical lines with ordinary spaces, and
rescans that lossy string. The direct input `- first  \n  second` becomes `- first second`, deleting the required hard
break. A lazy continuation such as `3. parent\n   9. child` becomes `3. parent 9. child`, and an indented task/nested
marker can become literal prose in the parent item.


#### Impact

The implementation changes inline semantics and list structure exactly where the plan requires either source-proven
recursive ownership or opaque fallback. Task state, hard-break behavior, nested ordered content, and continuation
columns
cannot be trusted.


#### Fix

Keep parser-owned inline token groups aligned to their physical list lines, including hard-break nodes, and render them
from the token stream. If a lazy continuation or nested marker cannot be classified with a proven source interval, mark
the
containing list item/list block opaque instead of joining its bytes into prose. Add exact hard-break, task, lazy,
multi-digit ordered, and nested-list semantic tests.


#### Outcome


----

### Critical

#### C03: CRLF table cell spans do not slice the claimed source


#### Where

`src/dot_tools/markdown_formatter/parser.py:393-427`


#### Issue

The table compatibility path splits a mapped table region on `b"\\n"` and advances its row offset with `len(row) + 1`
at `parser.py:405-412`. For CRLF rows, `row` still contains `b"\\r"`, so each subsequent row starts one byte later than
the computed offset. The direct source
`b"# T\\r\\n\\r\\n| `a|b` | c |\\r\\n| --- | --- |\\r\\n| x | y |\\r\\n"` produces separator and data nodes whose
`span` slices `b" --"` and `b"|"`, not the node's claimed `b"---"` and `b"x"`/`b"y"`.


#### Impact

The AST's byte-addressed ownership contract is false for a required CRLF boundary. Downstream normalization can only
look
correct by ignoring the bad spans, and any consumer relying on source slices can rewrite or attribute the wrong bytes.


#### Fix

Build row starts from the shared UTF-8 byte line index or advance by the actual `len(row) + len(line_ending)` for each
physical row. Represent table rows/cells explicitly and assert for every owned node that
`source[node.span.start:node.span.end] == node.source` under LF, CRLF, astral, escaped-pipe, and code-pipe inputs.


#### Outcome


----

### Critical

#### C04: CRLF fenced-code payload spans omit the line-feed byte


#### Where

`src/dot_tools/markdown_formatter/parser.py:282-297`


#### Issue

For a fenced block with CRLF payload, the closing match begins at `b"\\r\\n"` and `parser.py:288-290` sets
`payload_end = closing.start() + 1`. The resulting `CodePayload` for `b"```text\\r\\nx\\r\\n```\\r\\n"` is
`payload=b"x\\r"`
with a span covering only `b"x\\r"`, while the payload line's source bytes are `b"x\\r\\n"`. The LF is silently excluded
from the parser model even though LF is retained by the normalizer's separate `splitlines` path.


#### Impact

The parser tree does not preserve the exact code payload or source span under CRLF. This violates the code payload,
source-span, and CRLF requirements and can cause later code consumers to lose a byte while rendering appears
superficially
stable.


#### Fix

Set the payload end at the beginning of the closing line, including the complete preceding line ending, and derive
`payload_span` from that exact boundary. Add LF, CRLF, missing-final-LF, empty-payload, trailing-space, fence-marker,
and
info-string assertions against both `CodePayload.payload` and its source slice.


#### Outcome


----

### Significant

#### S01: Comment-only YAML frontmatter is rejected as multiple documents


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:105-119`


#### Issue

`yaml.compose_all` returns no node for a comment-only YAML document. The implementation only treats that condition as an
empty mapping when `not raw.strip()` at `frontmatter.py:108`; a comment makes `raw.strip()` nonempty, so the code falls
through to `len(documents) != 1` and raises `FrontmatterError("multiple YAML documents are not permitted")`.


#### Impact

An empty YAML root with comments is rejected even though the approved envelope defines an empty root and deterministic
empty-root serialization. The exact frontmatter safety/serialization contract is incomplete.


#### Fix

Treat a zero-node, comment-only YAML stream as the empty mapping, while continuing to reject an actual second document.
Add
exact extraction, serialization, and reparse tests for empty, whitespace-only, and comment-only roots.


#### Outcome


----

### Significant

#### S02: Path aliases are not deduplicated before processing


#### Where

`src/dot_tools/markdown_formatter/operations.py:15-34`


#### Issue

`_absolute` uses `Path.absolute()` without lexical normalization. With an existing `a` directory, operands `x.md` and
`a/../x.md` produce two distinct `Path` keys and two records for the same destination instead of one sorted,
deduplicated file.


#### Impact

The operation contract is not deterministic for equivalent direct operands. A file can be read, rendered, and committed
twice, and the output record count depends on operand spelling.


#### Fix

Normalize `.` and `..` components without resolving symlink targets, then deduplicate the final absolute path set before
reading. Add equivalent-path, repeated-path, recursive-discovery, symlink, and outside-repository tests.


#### Outcome


----

### Significant

#### S03: Focused coverage still omits independently reproduced failures


#### Where

`tests/markdown_formatter/` and the Task 03 through Task 07 fixture requirements in
`implementation-plan.md:194-418`


#### Issue

The focused suite passes 162 tests, but no test asserts the current failures in C01-C04 or S01-S02. Existing idempotence
tests cover simpler containers, existing table tests mostly assert output stability rather than every recursive span,
and
the operation contract tests do not include lexical path aliases. The passing count therefore does not establish the
approved recursive, CRLF, frontmatter, and complete contract matrix.


#### Impact

Focused green tests provide false confidence while the formatter violates core semantic-preservation and source-span
requirements. The journal's formatter-scoped completion claim is unsupported by the independent probes.


#### Fix

Add exact-byte and semantic-reparse regressions for every current failure, including recursive list/blockquote/code
composition, list hard breaks/lazy markers, CRLF table and code spans, comment-only frontmatter, and path aliases. Make
three-pass equality and recursive source-slice assertions explicit rather than relying on representative idempotence.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C04 must be resolved before approval. S01-S03 must be addressed in the same pass because the exact frontmatter,
path, and coverage contracts remain incomplete. The unrelated configure pytest failure and baseline Ty diagnostics are
independently confirmed and excluded from formatter findings.
