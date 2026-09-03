# Execution Review: Generic AST-based Markdown formatter

This review independently rechecks the current formatter against the approved implementation plan, the execution
journal, and execution review 05. It starts from the current diff and uses focused semantic and contract probes in
addition to the repository checks.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--05.md`
- **Earlier reviews**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--01.md` through
  `execution-review--whole-plan--04.md`


## Scope

**whole-plan - Iteration 06**

The review covers the formatter package, parser and source spans, normalization and rendering, document orchestration,
operations, grouped CLI, compatibility wrapper, dependency and registration changes, tests, and fixtures recorded in
the journal. The plan, journal, and prior reviews were read but not modified.


## Issue Summary

- **Critical**:    6
- **Significant**: 2
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                  | Result                                                                                                                            |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                         | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                         |
| `uv run pytest tests/markdown_formatter --no-cov`                                 | Passed: 154 tests.                                                                                                                |
| `uv run pytest --no-cov`                                                          | Failed: 467 passed, 1 failed. The failure is the independently confirmed unrelated configure assertion below.                     |
| `uv run ruff check src tests`                                                     | Passed: `All checks passed!`.                                                                                                     |
| `uv run ty check`                                                                 | Failed: 74 diagnostics in existing PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears. |
| `uv run dt markdown --help`, `format --help`, `check --help`                      | Passed.                                                                                                                           |
| Inline, autolink, code, table, nested-container, wrapping, and idempotence probes | Failed as described in C01-C06.                                                                                                   |
| Operations and wrapper probes                                                     | Passed for covered cases; the cooperating-writer limitation remains as documented.                                                |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The formatter suite and Ruff pass. The repository-wide Ty run reports no formatter production or test path. These are
baseline repository failures, but the literal whole-repository Task 07 gate is not green.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                                                               |
| --------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-27`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                                                                                                                     |
| 01/AC02   | ✓      | `src/dot_tools/markdown_formatter/` contains the package and public model modules.                                                                                                                                                     |
| 01/AC03   | ⚠      | `models.py:8-66`, `cli/markdown.py:11-25`, and focused contract tests establish the names and basic result surface, but behavior fails in C01-C05.                                                                                     |
| 02/AC01   | ✓      | `frontmatter.py:87-232` exposes extraction, validation, and serialization; focused tests cover the APIs.                                                                                                                               |
| 02/AC02   | ✓      | `frontmatter.py:87-119` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                                                                                                                  |
| 02/AC03   | ✓      | `frontmatter.py:16-85,122-139` restricts events, nodes, recursive Python values, and finite reals; focused safety and numeric tests pass.                                                                                              |
| 02/AC04   | ✓      | `frontmatter.py:142-203` covers empty-root framing, nested empty containers, escaping, and tested finite-real notation.                                                                                                                |
| 03/AC01   | ✗      | Block and inline dataclasses exist, but recognized table code can claim incorrect cell spans and paragraph reconstruction can accept incomplete ownership. See C03.                                                                    |
| 03/AC02   | ✗      | CommonMark-plus-table parsing is present, but valid autolinks outside the narrow HTML-mask regex are rejected. See C02.                                                                                                                |
| 03/AC03   | ✗      | The table source association is not exact for escaped/code-pipe cells, and recognized nested tables are rewritten non-idempotently. See C03.                                                                                           |
| 03/AC04   | ⚠      | Semantic-token ownership handles many delimiter cases, but the fallback scanner and nested-link behavior still change valid semantics. See C01.                                                                                        |
| 03/AC05   | ✗      | Code masking and raw-HTML detection reject valid CommonMark URI autolinks and fail to reject a processing instruction that is then dropped. See C02 and C06.                                                                           |
| 03/AC06   | ⚠      | Top-level break policy and simple task cases pass, but nested recognized structures can be rewritten incorrectly. See C04.                                                                                                             |
| 04/AC01   | ✓      | `normalize.py:16-93` defines the requested normalized state and `test_normalize.py` asserts state directly.                                                                                                                            |
| 04/AC02   | ✗      | Paragraph wrapping exceeds 120 code points when a hard break is present, and list prose can be merged or rewrapped across structural boundaries. See C04.                                                                              |
| 04/AC03   | ✗      | Recursive list structure is not preserved for nested ordered content and continuation paragraphs. See C04.                                                                                                                             |
| 04/AC04   | ⚠      | Simple heading transitions are stable, but nested/container spacing is entangled with the malformed table and list paths.                                                                                                              |
| 04/AC05   | ✗      | Recognized tables inside block quotes acquire an extra synthetic table column on each pass. See C03.                                                                                                                                   |
| 04/AC06   | ✗      | Code-span behavior passes the small fixture table but does not preserve all parser boundaries and code-fence payload boundaries. See C05.                                                                                              |
| 05/AC01   | ✗      | Simple canonical LF/final-LF output passes, but a backtick-info fence followed by a heading is rendered with the heading inside the code payload. See C05.                                                                             |
| 05/AC02   | ✗      | Inline, nested-container, table, and code-fence outputs are not fully semantic-preserving or idempotent. See C01-C05.                                                                                                                  |
| 05/AC03   | ⚠      | `__init__.py:10-26` composes the pipeline and propagates typed errors, but canonical output is wrong for the failed paths.                                                                                                             |
| 05/AC04   | ✗      | Golden tests cover representative cases but miss the independently reproduced autolink, nested-table, wrapping, list, and fence failures. See S02.                                                                                     |
| 06/AC01   | ✓      | `operations.py:20-34` resolves CWD operands, discovers `.md` recursively, sorts, deduplicates, and reports explicit invalid paths.                                                                                                     |
| 06/AC02   | ✓      | `operations.py:178-207` prepares all files, stops at the first replacement error, preserves modes, and reports committed/untouched paths for covered failures.                                                                         |
| 06/AC03   | ⚠      | Snapshot checks, same-directory temp files, fsync, replacement, cleanup, and cooperating locks are implemented; the documented uncooperating-writer race remains.                                                                      |
| 06/AC04   | ⚠      | Representative precedence tests pass, but the final preflight failure path is recorded as `PREFLIGHT_ERROR` while the contract's write-failure mapping requires the write/partial-write contract to be verified across mixed outcomes. |
| 06/AC05   | ⚠      | Exact records and digest-only mismatch diagnostics pass covered cases; missing full status/stream combinations remain. See S02.                                                                                                        |
| 06/AC06   | ✓      | `.agents/tools/markdown-format.py:11-25` captures entry CWD, discovers the project, delegates, and passes through child streams and status.                                                                                            |
| 06/AC07   | ⚠      | Registration and smoke/help behavior pass, but the required complete semantic, operation, and wrapper matrix is not established. See S02.                                                                                              |
| 07/AC01   | ⚠      | Corpus fixtures cover the named categories at representative level, but do not protect the failures in C01-C05 or the missing contract matrix.                                                                                         |
| 07/AC02   | ⚠      | Formatter correctness fails C01-C06. The repository pytest and Ty commands also remain red on independently confirmed unrelated baseline failures.                                                                                     |


## Scope Verification

| File or path                                                            | Justification                                  | Status |
| ----------------------------------------------------------------------- | ---------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                        | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                        | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public contracts                       | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration         | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted frontmatter                 | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing and repair passes              | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repair passes        | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repair passes            | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operations and replacement safety      | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                          | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                   | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation               | ✓      |
| `tests/markdown_formatter/`                                             | Tasks 02 through 07 focused tests and fixtures | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                               | ✓      |

All modified production paths are within the approved formatter, CLI, wrapper, dependency, and registration scope. The
test path is partial because it does not establish the required edge matrix, not because it is out of scope.


## Prior Review Resolution

| Review 05 finding                                                   | Status | Current evidence                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Inline scanning and codecs change valid CommonMark semantics    | ⚠      | Intraword and several delimiter cases now pass, but `[a [b](u)](v)` formats as `[a [b](u) ](v)`, adding a label space. The compatibility scanner still changes valid nested-link semantics.                                                                          |
| C02 List-contained code and nested task state are not lossless      | ✓      | Direct probes for quoted tasks, nested list tasks, and list-contained code stayed stable across passes. `test_edge_contract.py:122-139` covers list stability; parser metadata handles nested task markers.                                                          |
| C03 Table ownership and zero-cell validation are incomplete         | ⚠      | The zero-cell repair now rejects framing-only rows in recognized tables, but `parser.py:309-327` still maps code-pipe and escaped-pipe content by raw physical-row search, and blockquoted tables grow columns on each pass.                                         |
| C04 120-code-point wrapping stops at hard breaks and lists          | ✗      | A 40-word segment on each side of a hard break yields 200 and 199 code points. List hard-break output yields 121-code-point lines.                                                                                                                                   |
| C05 Code-span normalization does not use semantic payload           | ⚠      | Padded code spans now use semantic payload and are idempotent, but parser-split backtick-info fences still absorb following blocks and malformed single-line tick runs remain outside the intended bounded ownership behavior.                                       |
| C06 Advisory locking does not prevent external post-check overwrite | ✓      | The limitation is explicit in `operations.py:66-81` and the journal. The cooperating lock serializes the complete replacement protocol; no unconditional arbitrary-writer guarantee is claimed. This remains a documented contract limitation, not a hidden failure. |
| C07 Repository-wide quality gates remain red on the known baseline  | ✓      | The full pytest failure and 74 Ty diagnostics were independently reproduced. No formatter path appears in Ty output, and the pytest failure is the OpenCode package manifest assertion; neither is treated as a formatter finding.                                   |
| S01 Empty frontmatter roots do not use approved framing             | ✓      | `frontmatter.py:201-203` emits `b"---\\n---\\n\\n"`; exact reparse coverage exists in `test_frontmatter.py:81-95`.                                                                                                                                                   |
| S02 Tests do not establish the complete approved contract           | ✗      | 154 focused tests pass, but the missing matrix remains material: valid URI autolinks, nested table/container idempotence, hard-break/list width, parser-split fence boundaries, and exact operation/status combinations are not covered.                             |


## Findings

### Summary

| Finding | Title                                                                                  | Outcome |
| ------- | -------------------------------------------------------------------------------------- | ------- |
| C01     | Nested link ownership changes the label semantics                                      |         |
| C02     | Valid CommonMark URI autolinks are rejected as raw HTML                                |         |
| C03     | Blockquoted and escaped/code-pipe tables are not source-safe or idempotent             |         |
| C04     | Prose wrapping still violates the 120-code-point and recursive-list contracts          |         |
| C05     | Backtick-info fence recovery can consume following document blocks                     |         |
| C06     | Raw HTML processing instructions are silently dropped                                  |         |
| S01     | Input errors drop trustworthy snapshots and failure-combination coverage is incomplete |         |
| S02     | Focused tests still miss reproduced formatter failures                                 |         |


### Critical

#### C01: Nested link ownership changes the label semantics


#### Where

`src/dot_tools/markdown_formatter/parser.py:485-561` and `src/dot_tools/markdown_formatter/normalize.py:109-117`


#### Issue

The parser's semantic-token pass does not own a nested link as one link node. For `[a [b](u)](v)`, `parse_document`
produces ordinary text `[a `, an inner link `[b](u)`, and ordinary text `](v)`. The fallback/normalization path then
emits `[a [b](u) ](v)`, inserting a space into the outer label. This is a source-semantic change, not a cosmetic
delimiter conversion.


#### Impact

Valid CommonMark link labels can change bytes and rendered label content. The formatter violates the plan's recursive
inline ownership and semantic preservation requirements even though the resulting output becomes stable.


#### Fix

Associate the parser-owned outer link token with its complete label and destination interval, including nested inline
content, or preserve the containing paragraph opaque when that interval cannot be proven. Add exact nested-link tests
that compare reparsed label semantics, not only output idempotence.


#### Outcome


----

### Critical

#### C02: Valid CommonMark URI autolinks are rejected as raw HTML


#### Where

`src/dot_tools/markdown_formatter/parser.py:671-702`


#### Issue

The parser delegates URI autolink recognition to `markdown-it-py`, which accepts schemes such as `ftp:`, `urn:`, and
custom schemes. Raw-HTML masking then recognizes only `https?` and `mailto` at lines 695-700. A valid CommonMark input
such as `<ftp://example.com>` therefore reaches line 701 and raises `RawHtmlError`; the same happens for
`<foo:bar>` and `<urn:isbn:1>`.


#### Impact

The bounded parser rejects owned syntax it explicitly promises to support. This is a correctness failure in parser
ownership and raw-HTML policy, not an intentional unsupported-extension failure.


#### Fix

Use the parser-owned autolink intervals or the complete CommonMark URI scheme rule when masking autolinks. Keep actual
HTML tags, comments, and declarations rejected, and add URI-scheme, email, astral-prefix, and adjacent-HTML tests.


#### Outcome


----

### Critical

#### C03: Blockquoted and escaped/code-pipe tables are not source-safe or idempotent


#### Where

`src/dot_tools/markdown_formatter/parser.py:309-327`, `src/dot_tools/markdown_formatter/normalize.py:265-350`, and
`src/dot_tools/markdown_formatter/render.py:27-80`


#### Issue

The table parser associates each inline token by `line.find(token.content, cursor)`, but `token.content` is semantic
content while the physical row may contain escaped pipes, container prefixes, or code spans. Direct probes show
incomplete ownership for `| a\|b | c |`, and code-span rows can associate only the text before the code span. More
visibly,
a valid blockquoted table is rendered as a table with an extra `> ` cell:

Observed bytes: input `> | a |` / `> | --- |` / `> | x |`; pass 1 adds a `> ` cell and pass 2 adds another.

The output is not idempotent and changes table column structure. Whole all-pipe rows such as `|||` can instead be
parsed as ordinary paragraphs, bypassing the required recognized-table zero-cell failure.


#### Impact

AST consumers cannot trust table spans, code-pipe ownership is not proven, escaped cell semantics are vulnerable, and
recognized tables inside containers are rewritten destructively on every pass. This violates Tasks 03, 04, and 05.


#### Fix

Represent rows and cells explicitly from parser token positions after removing only proven container prefixes. Associate
each cell's physical interval and recursively verify its inline reconstruction. Mark the whole table opaque when proof
fails, reject every framing-only row in a recognized table, and render nested tables with the active prefix exactly
once.
Add exact tests for escaped/code pipes, repeated cells, blockquoted tables, all-pipe paragraphs, and three-pass output.


#### Outcome


----

### Critical

#### C04: Prose wrapping still violates the 120-code-point and recursive-list contracts


#### Where

`src/dot_tools/markdown_formatter/normalize.py:140-145,209-262,426-464`


#### Issue

The hard-break branch splits an encoded paragraph on `b"\\\\n"` and calls `_wrap_inline_tokens([], segment)`. With no
inline nodes, that helper returns the entire segment unchanged, so a 40-word segment on either side of a hard break
produces lines of 200 and 199 Unicode code points. A long list with a hard break produces 121-code-point lines because
the structural prefix is not excluded consistently. Separately, continuation paragraphs inside a list item are flattened
into the first paragraph on one pass and then into the same item text on the next, for example:

Observed bytes: pass 1 is `- a` followed by an indented `b`; pass 2 becomes `- a b`.

Nested ordered content can likewise be flattened into a single paragraph. Idempotence alone does not establish the
required recursive structure.


#### Impact

The central wrapping limit is violated, unbreakable inline atoms are not the only wrapping unit, and valid nested list
and continuation structure is lost. This fails the core prose/list behavior in Tasks 04 and 05.


#### Fix

Wrap from the owned inline token stream for each hard-break segment while retaining atom boundaries. Measure only prose
content, then apply the active structural prefix in rendering. Keep each parser-owned list child block structured and
preserve lazy continuation as normalized continuation lines; use opaque fallback when structure cannot be proven.
Add exact width assertions for ordinary, hard-break, list, nested-list, and multi-digit-marker cases.


#### Outcome


----

### Critical

#### C05: Backtick-info fence recovery can consume following document blocks


#### Where

`src/dot_tools/markdown_formatter/parser.py:233-250` and `src/dot_tools/markdown_formatter/normalize.py:375-398`


#### Issue

For a backtick-bearing info string, `markdown-it-py` emits a paragraph for the opening line and a fence beginning at the
next line. `_join_split_backtick_fences` blindly joins adjacent paragraph/fence nodes and extends the fence span to the
second node's end. With ` ```foo\`bar\nabc\n```\n\n## h\n`, the fence source becomes ` ```foo\`bar\nabc\n```\n\n## h\n`,
its payload includes the heading, and rendering emits:

Observed output: `~~~foo\`bar\nabc\n```\n\n## h\n~~~`.

That is a code block containing the heading rather than a code block followed by a heading. The output can be stable
only
after the parser has already changed the document structure.


#### Impact

Valid fenced code followed by ordinary blocks is consumed and rewritten as code payload. This violates parser block
spans, untouched code payloads, document orchestration, and idempotent rendering.


#### Fix

Recover split fences only when the second parser fence's source span ends at the actual closing fence for the recovered
opening line. Preserve the following token sequence outside the fence, and verify the reconstructed node's source span
and
payload against the original bytes before accepting it. Add backtick-info fence tests with following paragraphs,
headings, separators, containers, CRLF, and EOF boundaries.


#### Outcome


----

### Critical

#### C06: Raw HTML processing instructions are silently dropped


#### Where

`src/dot_tools/markdown_formatter/parser.py:671-702` and `src/dot_tools/markdown_formatter/normalize.py:353-418`


#### Issue

The parser's raw-HTML detector only rejects an angle construct beginning with `A-Z`, `a-z`, `!`, or `/` at line 701.
Markdown-it identifies a processing instruction such as `<?xml?>` as an HTML block, but that construct reaches the
normalizer without a supported branch and is silently omitted. A direct probe with `# T\n\n<?xml?>\n` returns only
`# T\n`, rather than raising `RawHtmlError` or preserving an opaque block.


#### Impact

Raw HTML is neither rejected nor preserved. Formatting therefore deletes source bytes from a body region that the plan
requires the raw-HTML policy to fail closed on.


#### Fix

Recognize the complete parser-owned HTML block range, including processing instructions and declarations, before
normalization. Raise `RawHtmlError` for every raw-HTML form outside code and add tests that cover processing
instructions,
declarations, comments, tags, opaque regions, and code masking.


#### Outcome


----

### Significant

#### S01: Input errors lose successful-read snapshots and failure-combination coverage is incomplete


#### Where

`src/dot_tools/markdown_formatter/operations.py:123-213` and `tests/markdown_formatter/test_operations.py:12-208`


#### Issue

The operation implementation has representative happy-path and write-failure tests, but it drops the snapshot even when
the file was read successfully and formatting then raised an input/policy error. In `_prepare`, `snapshot` is captured
at
line 144, but the `except (UnicodeError, ValueError)` branch at lines 148-149 constructs a `FileResult` without it. The
plan requires `snapshot` after every successful read; a parser/frontmatter/raw-HTML error therefore returns a
trustworthy-read result with `snapshot=None`.

The plan also requires every `FileResult` field and every mixed precedence combination. There is no direct contract
coverage for read errors with trustworthy versus absent snapshots, preflight errors mixed with input/read errors,
zero-file
CLI output, read/write diagnostic ordering, mode/type mutation, or the no-write guarantee for every check path.
`test_markdown_cli_contract.py:97-102`
is still explicitly named `test_zero_file_operation_is_success_with_empty_records` while supplying a missing operand and
asserting `INPUT_ERROR`; it is not a zero-discovery contract test.


#### Impact

The result contract is observably wrong for successful reads followed by input errors, and the passing operation count
does
not prove the total status, diagnostic, stream, and no-write contracts. Regressions in mixed failures can report the
wrong
operation status or incomplete records while focused tests remain green.


#### Fix

Carry the successfully captured snapshot into parser/frontmatter/policy error results. Add parameterized contract tests
for
all status combinations and precedence, explicit zero-discovery CLI streams, read and replacement errors, snapshot
presence rules, mode/type/symlink mutations, temp cleanup, partial commits, and check's unchanged filesystem bytes and
metadata.


#### Outcome


----

### Significant

#### S02: Focused tests still miss reproduced formatter failures


#### Where

`tests/markdown_formatter/` and the Task 03 through Task 07 fixture requirements in `implementation-plan.md:194-418`


#### Issue

The 154-test focused suite passes, but it does not assert the directly reproduced failures in C01-C06. It lacks semantic
assertions for URI autolinks, nested-link-like labels, physical table spans
for
escaped/code-pipe cells, blockquoted table three-pass idempotence, hard-break/list width, continuation paragraph
structure,
and backtick-info fences followed by another block. Representative corpus fixtures and a second-pass equality assertion
allow malformed output to appear complete once it stabilizes.


#### Impact

Focused test counts provide false confidence and do not cover the exact edge and contract surface demanded by the
approved
plan. The journal's formatter-scoped completion claim is unsupported by the independent probes.


#### Fix

Add exact-byte plus semantic-reparse tests for each reproduced failure, assert recursive source spans and block
boundaries,
and use three-pass tests for nested containers and fence/table/list composition. Add processing-instruction raw-HTML
tests,
snapshot-presence assertions for input errors, and the operation stream/status matrix before claiming whole-plan
completion.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C06 must be resolved before approval. S01 and S02 must be addressed in the same pass because the current focused
suite does not establish the exact formatter-specific contract. The repository-wide pytest and Ty failures are recorded
as independently confirmed unrelated baseline results and are not counted as formatter findings.
