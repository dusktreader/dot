# Implementation Journal: Generic AST-based Markdown formatter

This journal records execution of the approved generic Markdown formatter implementation plan.


## Execution-review 22 blocker repairs 2026-09-03

Repaired C01 by decoding complete source backslash runs to semantic values before canonical encoding. The same codec now
applies to ordinary prose, inline boundaries, and table cells, including literal pipes. Canonical delimiter selection is
context-aware across adjacent emphasis and strong atoms, including table cells, and preserves the reparsed inline shape.

Removed the unconstrained paragraph-to-table promotion. The remaining compatibility path requires matching physical
header
and separator schemas, so separator-like ordinary paragraphs remain parser-owned paragraphs instead of raising
`TableError`.

Added exact LF/CRLF regressions for backslash runs at EOF and before links, images, emphasis, code, and table pipes,
plus
adjacent mixed delimiter atoms and false table boundaries. Tests assert source ownership, semantic reparsing, exact
output,
and three-pass stability. Accepted HTML behavior remains unchanged.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 362 tests.
- Focused Ruff and Ty checks passed.
- Direct C01-C03 and accepted-HTML probes passed.
- `git diff --check` passed.

No plans or execution-review artifacts were edited and no commit was created.


## Human-directed HTML policy change 2026-09-03

The human changed the requirement: embedded-HTML detection and rejection are removed from the formatter. HTML-looking
Markdown body text is accepted by ordinary parser and formatter handling. Parser-delimited HTML blocks remain opaque so
the formatter preserves bytes when ownership cannot be proven. Code remains code through parser ownership, without a
separate HTML scan or masking policy.

Removed `RawHtmlError` from the parser and document/CLI error contract. Rewrote formatter tests for accepted inline,
block, escaped-angle, code, and opaque HTML-looking cases with LF and CRLF coverage. Updated the design and
implementation plans. Review 15 was not edited.


### Verification

- HTML-focused formatter tests passed, including inline-looking tags, block HTML, escaped angle text, opaque text, and
  LF/CRLF preservation.
- The full focused formatter suite had 233 passing tests and 14 failures in the pre-existing review-15 C02-C04 cases.
- Focused Ruff passed. Focused Ty retained four diagnostics in the pre-existing C02 case and an existing metadata typing
  assertion. Direct accepted-HTML and idempotence probes passed. `git diff --check` passed.
- Review 15 findings C02-C04 remain separate and are not claimed as fixed here.


## Execution-review 15 formatter blocker repairs 2026-09-03

Indented code now uses MarkdownIt's semantic `code_block` payload, so structural indentation is removed by the parser's
visual-column rules rather than by a literal four-space fallback. Fenced code nested directly under an empty list item
also uses the parser semantic payload, preserving the active continuation column and list-item ownership after
reparsing.

Table physical splitting now tracks the exact backtick opener run and ignores pipes until that run closes. The
regression
covers repeated cells, escaped/code pipes, line endings, source ownership, canonical output, and three-pass stability.

Added exact C02-C04 regressions for LF and CRLF inputs, semantic payload and AST preservation, and accepted HTML
idempotence. No execution-review artifact was edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 247 tests.
- Focused Ruff passed. Focused Ty passed after narrowing metadata values with runtime type checks and a typed table-row
  assertion.
- Direct C02-C04 and accepted-HTML/idempotence probes passed.
- `git diff --check`: passed.


## Execution-review 14 C01 repair 2026-09-03

Unclosed fenced blocks ending at EOF without a terminal line ending are now marked as opaque, preserving their exact
source bytes instead of synthesizing a payload newline and closer. Propagated container ownership retains the same EOF
marker, while closed and newline-terminated unclosed fences retain their existing canonical behavior.

Added LF and CRLF regressions comparing the original and reparsed `CodePayload` values, exact output bytes, and three
formatting passes. No plans or review artifacts were edited. No commit was created.


## Execution-review 11 C01 repair 2026-09-03

Repaired the remaining blockquote-list heading ownership defect. The parser now removes a proven list marker before
building a heading's owned inline source, and list-child normalization strips proven blockquote prefixes before removing
the marker. This keeps heading text as `H` instead of treating structural `- #` bytes as content while preserving source
order and active container prefixes.

Added LF and CRLF regressions covering exact parser-owned heading slices, semantic reparsing, and identical first,
second,
and third formatting passes. Related nested list child coverage remains in the focused edge-contract suite.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 206 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct LF/CRLF probes passed for parser-owned heading slices, semantic reparsing, exact output, and three-pass
  convergence. Related nested list child probes also passed.
- `git diff --check`: passed. Plans and execution reviews were not edited. No commit was created.


## Execution-review 10 formatter-specific repair 2026-09-03

Repaired fence closer validation so recovered and ordinary fences require the opener character and length, preserved
mismatched and short marker lines as payload, and retained empty closed payloads without synthesizing a newline. Owned
prose text and table inline nodes now canonicalize CRLF and recurse through the ordinary inline codec, including links.
Finite real serialization now validates the restricted-loader result and scalar type. Mixed list normalization keeps the
first block's ownership and nested blocks in source order.


### Verification

- Focused formatter tests: 204 collected, 203 passed; one pre-existing nested-list fence expectation remains sensitive
  to
  the mixed-child ordering repair and requires follow-up before claiming the full focused gate.
- Direct probes passed for mismatched/short fences, empty fences, CRLF prose, mixed lists, large finite reals, and table
  link title canonicalization. Ruff and Ty were not reached after the remaining focused test failure.
- Plans and review artifacts were not edited. No commit was created.


## Nested list fence repair 2026-09-03

The remaining failure came from the renderer treating every normalized list child as a secondary block. A nested list is
already in source order as a structural child of its list item, so the renderer now emits it at the active continuation
column without a paragraph separator. Secondary paragraphs and code blocks retain their canonical blank-line separator.
This preserves the nested list hierarchy while retaining the blank line before the nested fence.


### Verification

- The focused nested-list test passes after the production renderer change.
- `uv run pytest tests/markdown_formatter --no-cov` passed with 204 tests.
- Focused Ruff and Ty checks passed.
- The direct nested-list probe passed, including exact bytes, three-pass idempotence, and `b"x  \\n"` code payload.
- `git diff --check` passed.
- No plans or review artifacts were edited. No commit was created.


## Execution-review 09 final formatter-specific repair 2026-09-03

Repaired the remaining formatter-specific table ownership gap found during the direct review-09 probes. Table rows no
longer become opaque merely because a pipe follows an even backslash run. The physical splitter owns that pipe as a
delimiter, so malformed column counts reach the documented table error path rather than passing through unchanged.

Added an exact regression for even-parity table delimiters. The direct probe matrix still has a known formatter-specific
limitation: canonical output intentionally uses backtick fences, so source tilde fences are not preserved as tilde
fences. This remains consistent with the existing canonical fence tests and was not changed in this pass. No plans or
reviews were edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 204 tests.
- Focused Ruff and Ty checks passed. Full Ruff and `git diff --check` passed.
- `uv run pytest --no-cov`: 517 passed and one known unrelated configure assertion failed because the OpenCode package
  manifest contains `@opencode-ai/plugin` while the baseline test expects an empty dependency mapping.
- Grouped and wrapper help smoke passed. Repository-wide `ty check` retains the documented 74 baseline diagnostics
  outside formatter scope.


## Execution-review 09 repair: C08, C11, and S03 2026-09-03

Repaired parser ownership for recognized table rows containing escaped literal pipes and code-span pipes. Physical cell
boundaries now provide the ownership proof, while parser semantic truncation no longer incorrectly forces the complete
table opaque. Added exact LF/CRLF output, row and cell byte-span, non-opaque, semantic reparse, and three-pass
assertions.
Recursive discovery now catches `OSError` from traversal and returns a complete `READ_ERROR` operation result. Added
direct
operation and grouped CLI coverage for the diagnostic, record, status, and exit contract. Even-parity delimiter pipes
remain fail-closed rather than being guessed as escaped content.


### Verification

- `uv run pytest tests/markdown_formatter/test_edge_contract.py tests/markdown_formatter/test_operations.py
  tests/markdown_formatter/test_markdown_cli.py --no-cov`: passed after correcting exact expected table bytes.
- `uv run pytest tests/markdown_formatter --no-cov`: 202 tests passed before this repair; the focused repair subset
  passed after the repair.
- Focused Ruff and Ty checks passed for the changed formatter source and tests.

No plans or reviews were edited. No commit was created.


## Execution-review 18 formatter blocker repairs 2026-09-03

Repaired C01-C02 and S01-S04 without restoring embedded-HTML policy logic. Wrapped prose now remains one paragraph with
single-LF soft breaks, while hard breaks remain explicit. Nested emphasis and strong constructs whose canonical
delimiter
conversion is unsafe preserve their proven source bytes, including table cells. Link destination scanning now ignores
parentheses inside quoted titles, so links and images remain parser-owned and titles receive canonical encoding.

Same-family nested list rendering no longer prefixes structural blank lines with whitespace. Invalid explicit operands
are
deduplicated by final normalized path for both operations. Temporary cleanup runs under the destination lock and removes
a
newly created temporary file even when `fstat` cannot capture its identity.

Added exact-byte, parser source-span, semantic-reparse, and three-pass regressions for prose, nested delimiters,
link/image
and table titles, nested lists, duplicate invalid paths, temporary cleanup, and accepted HTML.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 288 tests.
- Focused Ruff and Ty checks passed for formatter source and tests.
- Direct C01/C02/S01-S04 and accepted-HTML probes passed.
- `git diff --check`: passed.

No plans or execution-review artifacts were edited. No commit was created.


## Execution-review 19 formatter blocker repairs 2026-09-03

Repaired both remaining formatter operation blockers without restoring embedded-HTML policy logic. Successful atomic
replacement now clears temporary cleanup state before the cleanup phase, so a later temporary `lstat` failure cannot
change a committed result into a write error. Cleanup errors that occur before replacement no longer mask the primary
replacement error.

Temporary cleanup now requires the descriptor-captured device and inode identity. If `fstat` cannot capture that
identity, the temporary pathname remains untouched, including when a failure-injection pathname substitution replaces it
with an unrelated sentinel.

Added regressions for successful replacement with cleanup `lstat` failure, replacement-error precedence, and `fstat`
failure with pathname substitution. No execution-review artifact was edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 291 tests.
- `uv run pytest tests/markdown_formatter/test_operations.py tests/markdown_formatter/test_markdown_cli.py
  tests/markdown_formatter/test_markdown_cli_contract.py tests/markdown_formatter/test_wrapper.py --no-cov`: passed,
  33 tests.
- Focused Ruff and Ty checks passed for formatter source and tests.
- Direct C01/C02 failure-injection probes passed, including committed reporting and pathname-substitution preservation.
- Grouped and wrapper help plus wrapper canonical check smoke passed.
- `git diff --check`: passed.


## Source plan

`.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`


## Status

**Incomplete**: Tasks 02 through 07 remain incomplete. The prior scaffolding was repaired in several areas, but the
approved source-span AST, normalization, rendering, operation, fixture, and contract-test surface is not complete.


## Tasks

### Task 01: Establish dependency and public contracts

#### Status

**Incomplete**: Dependency synchronization and initial package contracts were completed, but the planned contract tests
were not added.


#### Overview

Added the pinned `markdown-it-py` dependency, formatter package modules, public result models, and initial grouped CLI
surface. The implementations are scaffolding only and do not satisfy the complete formatter contract.


#### Steps taken

- Added `markdown-it-py==4.2.0` to project dependencies.
- Ran `uv sync`, which refreshed `uv.lock` and installed `markdown-it-py==4.2.0`.
- Added formatter model and stage modules with the public names from the plan.
- Added and registered the `dt markdown format` and `dt markdown check` command group.
- Ran the grouped command help smoke commands successfully.
- Ran Ruff on the new and modified Python modules and found style errors, then corrected those errors.


#### Files modified

- UPDATED: `pyproject.toml`
- UPDATED: `uv.lock`
- CREATED: `src/dot_tools/markdown_formatter/__init__.py`
- CREATED: `src/dot_tools/markdown_formatter/models.py`
- CREATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- CREATED: `src/dot_tools/markdown_formatter/parser.py`
- CREATED: `src/dot_tools/markdown_formatter/normalize.py`
- CREATED: `src/dot_tools/markdown_formatter/render.py`
- CREATED: `src/dot_tools/markdown_formatter/operations.py`
- CREATED: `src/dot_tools/cli/markdown.py`
- UPDATED: `src/dot_tools/cli/main.py`
- UPDATED: `.agents/tools/markdown-format.py`
- CREATED: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`


#### Acceptance criteria validation


#### Unsatisfied AC01: Add the dependency and refresh the lockfile

`uv sync` completed successfully and installed `markdown-it-py==4.2.0`; the planned contract tests and complete package
implementation remain unfinished.


#### Unsatisfied AC02: Create complete formatter modules and CLI group

The named modules and CLI group exist, but most modules contain contract scaffolding rather than the required behavior.


#### Unsatisfied AC03: Implement public models, statuses, signatures, and CLI contract

The public model names, enums, and signatures were added. File operations, diagnostics, exit mapping, and document
behavior are incomplete, and no contract tests were added.


#### Additional notes

The requested implementation is substantially larger than the available execution window. No commit was created and no
files outside the requested feature worktree were modified.


### Task 02: Implement restricted frontmatter

#### Status

**Incomplete**: No task-level fixtures or complete restricted YAML implementation were completed.


#### Overview

Added a provisional frontmatter module, but it does not satisfy the approved safe YAML envelope, duplicate and tag
rejection, scalar canonicalization, or exact byte serialization requirements.


#### Steps taken

- Added provisional extraction, validation, and serialization functions.


#### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`


#### Acceptance criteria validation


#### Unsatisfied AC01: Expose frontmatter APIs

The functions exist, but behavior is incomplete.


#### Unsatisfied AC02: Enforce exact delimiters and missing-close behavior

The provisional extractor does not implement all exact byte rules.


#### Unsatisfied AC03: Enforce the restricted YAML type and safety envelope

The implementation relies on permissive `yaml.safe_load` and does not reject all prohibited constructs.


#### Unsatisfied AC04: Serialize canonical YAML and exact document framing

Scalar formatting and exact framing are incomplete.


### Tasks 03 through 07: Parser, normalization, rendering, operations, and quality gate

#### Status

**Incomplete**: These tasks were not executed to completion.


#### Overview

Only minimal placeholder stage APIs and basic path processing were added. The AST span association, opaque preservation,
normalization, rendering, atomic operations, complete CLI output/error contracts, wrapper behavior, fixtures, and
quality
gate remain unfinished.


#### Steps taken

- Added placeholder parser, normalization, and rendering contracts.
- Added provisional document orchestration and basic file processing.
- Replaced the legacy wrapper with a provisional delegation wrapper.


#### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `src/dot_tools/markdown_formatter/operations.py`
- UPDATED: `src/dot_tools/markdown_formatter/__init__.py`
- UPDATED: `.agents/tools/markdown-format.py`


#### Acceptance criteria validation


#### Unsatisfied AC01 through AC07

The planned parser, normalization, rendering, safe operations, wrapper, fixtures, and full quality gates were not
completed.


#### Additional notes

No focused task tests existed in the worktree at the start of execution, and the planned tests were not authored before
the execution window ended.


## Continuation execution

### Task 02

**Status:** Incomplete.

The restricted frontmatter loader was expanded with duplicate-key checks, YAML node checks, scalar validation, and
canonical serialization. The required exact fixtures and tests were not added, and the implementation still requires
additional validation for explicit tags, aliases, scalar losslessness, and exact framing.


### Task 03

**Status:** Incomplete.

The parser now invokes `markdown-it-py`, creates basic block spans, applies an H1 policy, and performs a preliminary
code-first raw-HTML scan. The required recursive inline source scanner, token-map proof, opaque whole-block fallback,
task markers, table ownership, and heading-break policy are not complete.


### Task 04

**Status:** Incomplete.

Basic heading, code, and table normalization scaffolding was added. Wrapping, inline codecs, list columns, heading
spacing, separator reuse, exact table geometry, and opaque propagation are not complete. No planned state fixtures or
tests were added.


### Task 05

**Status:** Incomplete.

Basic rendering for headings, separators, code, tables, and text was added. The exact CommonMark code-span algorithm,
lossless code payload rules, inline rendering, table serialization, and golden/idempotence tests are not complete.


### Task 06

**Status:** Incomplete.

The operations layer now collects explicit path errors, captures snapshots, prepares outputs before replacement, uses
temporary files with flush/fsync, and reports basic result statuses. The exact preflight, atomic replacement,
diagnostic,
precedence, digest, race, cleanup, and wrapper contracts remain incomplete. The CLI help commands pass, but the planned
operation, CLI, and wrapper tests were not added.


### Task 07

**Status:** Incomplete.

No generic corpus fixtures or corpus tests were added. Focused Ruff validation passed. `ty check` remains non-zero due
to
existing repository diagnostics and new formatter diagnostics. The full pytest quality gate was not green: 313 tests
passed and one pre-existing configure test failed because `.config/opencode/package.json` contains a plugin dependency.


### Continuation verification

- `uv run ruff check src tests`: passed.
- `uv run python -m compileall -q src/dot_tools`: passed.
- `uv run dt markdown --help`: passed.
- `uv run dt markdown format --help`: passed.
- `uv run dt markdown check --help`: passed.
- `uv run pytest tests --no-cov`: failed, 313 passed and 1 failed in the configure test for the
  OpenCode npm dependency manifest.
- `uv run ty check`: failed with existing repository diagnostics and formatter type diagnostics.


## Task 02 execution update

**Status:** Complete.

Implemented restricted YAML frontmatter extraction, validation, and deterministic serialization. Added exact-byte tests
and fixtures, ran the required red command against the provisional implementation, then ran the required green command
with all 16 tests passing.


### Steps taken

- Added a valid exact-byte fixture covering quoted strings, booleans, nested mappings, sequences, CRLF, and body bytes.
- Added tests for delimiters, missing closes, body preservation, invalid UTF-8, unsafe YAML constructs, duplicate keys,
  recursive value validation, canonical ordering, nesting, scalar spelling, and string escaping.
- Implemented YAML event and node restrictions, duplicate-key construction, recursive validation, strict UTF-8 handling,
  and canonical mapping, sequence, scalar, and document framing serialization.
- Ran focused Ruff and Ty checks on the changed source and tests successfully.


### Files modified

- CREATED: `tests/markdown_formatter/test_frontmatter.py`
- CREATED: `tests/markdown_formatter/fixtures/frontmatter/valid.md`
- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- UPDATED: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`


### Acceptance criteria validation

- **AC01 Satisfied**: The three planned frontmatter APIs are implemented and covered by focused tests.
- **AC02 Satisfied**: Extraction is byte-oriented, opens only at byte 0, closes at the first later exact `---` line, and
  raises `FrontmatterError` when no close exists. Body bytes are returned unchanged.
- **AC03 Satisfied**: Anchors, aliases, explicit tags, unsupported scalar tags, duplicates, multiple documents,
  timestamps, binary/set values, invalid Unicode, non-finite values, and non-mapping roots are rejected. Accepted values
  are restricted recursively to the approved mappings, sequences, and scalar types.
- **AC04 Satisfied**: Mappings sort Unicode keys, nested values use two-space indentation, empty containers use `{}` and
  `[]`, and scalar output follows the approved canonical forms and escaping rules. Delimiters, LF framing, and the
  required blank line are emitted deterministically.


### Verification

- `uv run pytest tests/markdown_formatter/test_frontmatter.py`: passed, 16 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/frontmatter.py tests/markdown_formatter/test_frontmatter.py`:
  passed.
- `uv run ty check src/dot_tools/markdown_formatter/frontmatter.py`: passed.


## Final continuation attempt

### Task 03

**Status:** Incomplete. Extended parser block extraction, code-range masking, thematic-break checks, and basic source
span handling. Full recursive inline ownership and opaque-block semantics remain unimplemented.


### Task 04

**Status:** Incomplete. Extended heading, prose, list, and table normalization scaffolding. The approved inline codecs,
list continuation columns, heading-parent spacing, and exact table algorithm remain unimplemented.


### Task 05

**Status:** Incomplete. Corrected final-newline and frontmatter composition behavior and retained basic renderers. Exact
code-span, payload, inline, and idempotent rendering rules remain unimplemented.


### Task 06

**Status:** Incomplete. Added basic mismatch diagnostics and destination write-bit checking. Full operation precedence,
preflight, digest diagnostics, atomic replacement, and wrapper contract tests remain unimplemented.


### Task 07

**Status:** Incomplete. No generic corpus was added and the full quality gate was not reached.


### Verification

- `uv run pytest tests/markdown_formatter/test_frontmatter.py --no-cov`: passed, 16 tests.
- `uv run ruff check src/dot_tools/markdown_formatter src/dot_tools/cli/markdown.py`: passed.
- Grouped `dt markdown` help commands: passed.
- `uv run dt markdown check .artifacts/20260827--markdown-ast-formatter/design-plan.md`: returned a mismatch record for
  the currently noncanonical design document.

The implementation remains incomplete because the requested feature scope requires the planned parser, normalization,
rendering, operations, fixture, and contract-test surfaces, which were not present and could not be completed in this
execution window. No planning or review artifact was modified and no commit was created.


## Task 03 execution update

**Status:** Complete.

Implemented the parser task in the assigned worktree. The parser now exposes byte-addressed AST dataclasses and typed
parser errors, parses CommonMark with the table rule, associates parser block maps with UTF-8 byte spans, scans owned
inline constructs from exact source slices, preserves unowned blocks as opaque, masks parser-owned code before raw HTML
detection, enforces top-level H1 and thematic-break policy, and records task state.


### Steps taken

- Added parser fixtures and `test_parser.py` covering block ownership, inline precedence, opaque fallback, raw HTML,
  code-looking HTML, H1 and thematic-break policy, CRLF, astral Unicode, and missing final LF.
- Ran the required red command, `uv run pytest tests/markdown_formatter/test_parser.py`; initial collection failed on a
  non-ASCII bytes literal before implementation.
- Implemented the parser models, UTF-8 line-start indexing, token-map block extraction, recursive inline scanner,
  reconstruction checks, code-first masking, policy checks, and typed UTF-8/parser errors.
- Corrected fixture and implementation issues found by the green tests and quality checks.


### Files modified

- **CREATED:** `tests/markdown_formatter/test_parser.py`
- **CREATED:** `tests/markdown_formatter/fixtures/parser/basic.md`
- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`


### Acceptance criteria validation

- **AC01 Satisfied:** `parse_document` and the requested AST dataclasses are present; source spans are UTF-8 byte
  intervals.
- **AC02 Satisfied:** CommonMark plus table parsing and the requested owned block/inline kinds are covered by focused
  tests.
- **AC03 Satisfied:** Line-start byte indexing, sequential inline scanning, reconstruction, and opaque fallback are
  implemented and tested for CRLF, astral text, repeated source, and missing final LF.
- **AC04 Satisfied:** The scanner applies code, image/link, emphasis, hard-break, escape, and text precedence and uses
  sequential cursor spans.
- **AC05 Satisfied:** Code ranges are masked before raw HTML scanning; raw HTML raises `RawHtmlError`, code-looking HTML
  is accepted, and top-level H1 policy raises `StructureError`.
- **AC06 Satisfied:** Task state is recorded separately and thematic breaks outside downward heading transitions raise
  `UnsupportedSyntaxError`.


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py --no-cov`: passed, 7 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py`: passed.


### Additional notes

No normalization, renderer, operations, CLI, wrapper, or unrelated modules were changed. No commit was created.


## Continued execution: Tasks 04 through 07

### Task 04

**Status:** Complete for the implemented focused normalization surface. Added normalization state tests and repaired the
owned-AST normalization models for prose wrapping, headings, list markers and task state, table geometry, code info and
fences, and opaque propagation. The broader parser and renderer limitations remain outside this task.

**Files modified:** `src/dot_tools/markdown_formatter/normalize.py`, `src/dot_tools/markdown_formatter/parser.py`, and
`tests/markdown_formatter/test_normalize.py`.

**Verification:** The required red command, `uv run pytest tests/markdown_formatter/test_normalize.py`, initially
collected six tests with four failures against the scaffolding. After implementation, the same exact command collected
six tests and all six passed; pytest still returned nonzero because repository-wide coverage enforcement applies to this
focused invocation. Focused Ruff and Ty both passed for the changed normalization/parser source and tests.


#### Acceptance criteria validation

- **AC01 Satisfied:** The requested normalization entry point and state dataclasses are present, and tests assert state
  without importing rendering or orchestration.
- **AC02 Partially satisfied:** Unicode-aware prose wrapping, owned heading inline content, and code non-wrapping state
  are covered. The complete inline codec and every specified code-span semantic case require later renderer/parser work.
- **AC03 Partially satisfied:** Ordered start, sequential marker state, task state, and continuation columns are
  covered.
  Recursive nested and quote columns are constrained by the existing parser tree and remain incomplete.
- **AC04 Partially satisfied:** Heading descent state and generated separators are covered. Exact parent-body spacing
  and
  source-break consumption require broader AST boundary support.
- **AC05 Partially satisfied:** Recognized table alignment, padding, and widths are normalized. The complete lossless
  escaping/parity and all invalid-row cases remain dependent on parser/render integration.
- **AC06 Satisfied:** Code payload remains unwrapped, missing language defaults to `text`, `bash`/`sh` metadata maps to
  `shell`, and fence state is collision-aware for payload markers.


### Task 05

**Status:** Complete for the focused render and document pipeline surface.

**Overview:** Added render/document golden and idempotence tests, repaired canonical inline code-span encoding, list and
table rendering, opaque/code byte composition, strict UTF-8 orchestration, and frontmatter reattachment.

**Files modified:** Created `tests/markdown_formatter/test_render.py`, `tests/markdown_formatter/test_document.py`, and
`tests/markdown_formatter/fixtures/render/code-spans.txt`. Updated `src/dot_tools/markdown_formatter/render.py`,
`src/dot_tools/markdown_formatter/normalize.py`, `src/dot_tools/markdown_formatter/__init__.py`, and this journal.

**Acceptance criteria validation:** AC01 through AC04 satisfied for the focused renderer/document contract. Tests cover
exact code-span bytes, headings, lists, tables, opaque/code composition, frontmatter, typed errors, and idempotence.

**TDD and verification:** The exact red command was run first and failed with renderer/scaffolding assertions. The exact
green command was then run with `--no-cov` because the focused invocation's repository coverage threshold otherwise
masks
test results; it passed with 13 tests. Focused Ruff and Ty commands both passed.


### Task 06

**Status:** Complete for the Task 06 implementation surface. Added focused operation, grouped CLI, and wrapper tests;
implemented deterministic collection, result precedence, preflight-all-before-write behavior, snapshot validation,
atomic replacement, diagnostics, CLI exit mapping, and PEP 723 wrapper delegation.

**Files modified:** Created `tests/markdown_formatter/test_operations.py`,
`tests/markdown_formatter/test_markdown_cli.py`,
`tests/markdown_formatter/test_wrapper.py`, and `tests/markdown_formatter/fixtures/operations/canonical.md`. Updated
`src/dot_tools/markdown_formatter/operations.py`, `src/dot_tools/cli/markdown.py`, and
`.agents/tools/markdown-format.py`.

**Acceptance criteria validation:** AC01 through AC07 are satisfied by the focused tests and implementation. Path
collection resolves CWD operands, recursively discovers `.md`, sorts and deduplicates, and reports explicit invalid
paths. Formatting computes all outputs before commits, validates snapshots and destination safety, preserves modes,
cleans temporary files, stops on write failure, and reports committed/untouched paths. Check is write-free and emits
digest-only mismatch diagnostics. The grouped CLI and wrapper delegate and map statuses according to the plan.

**TDD and verification:** The exact red command was run first; five focused tests passed and the wrapper assertion
failed
against the initial command-index expectation. After implementation and test correction, the exact command collected six
tests and all six passed. The configured repository coverage threshold still returns nonzero for this focused invocation
(35% total versus 70%), because unrelated package modules are excluded from the focused test set. `uv run ruff check
src tests` passed. `uv run ty check` remains nonzero on pre-existing unrelated repository diagnostics; no new formatter
diagnostic was reported. No commit was created and Task 07 corpus files were not changed.


### Task 07

**Status:** Incomplete. No generic corpus fixtures or corpus tests were added. `uv run ruff check src tests` passed.
`uv run ty check` remains non-zero on pre-existing repository diagnostics in `md-to-pdf.py`, clipboard/Gmail tools,
opencode cost/trend modules, configure tests, Jira tests, and spinner tests. No formatter-specific Ty diagnostic
remains.

**Final verification:** `uv run pytest --no-cov` passed 336 tests and failed one unrelated configure assertion;
`uv run ruff check src tests` passed; `uv run ty check` failed with the pre-existing diagnostics listed above. No commit
was created. Planning and review artifacts were not edited.


## Task 07 execution update

**Status:** Complete for the generic corpus and quality-gate scope. Added exact corpus fixtures and tests for
frontmatter, parser boundaries, headings and separators, prose, lists and tasks, tables, code, opaque preservation, raw
HTML, source-break policy, idempotence, and multi-file operations. Repaired only formatter behavior exposed by the
corpus: block-token nesting, heading inline spans, paragraph line preservation, generated separator reuse, and stable
corpus expectations.


### Acceptance criteria validation

- **AC01 Satisfied:** `tests/markdown_formatter/fixtures/corpus/` and `test_corpus.py` cover the requested generic
  behaviors and multi-file failure paths.
- **AC02 Satisfied for formatter scope:** Focused corpus tests, full pytest except the documented unrelated configure
  assertion, Ruff, and formatter behavior all pass.


### Files modified

- **CREATED:** `tests/markdown_formatter/test_corpus.py` and generic corpus fixtures/expected companions.
- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`, `normalize.py`, and `render.py`.
- **UPDATED:** This journal.


### Verification

- `uv run pytest tests/markdown_formatter/test_corpus.py --no-cov`: passed, 13 tests.
- `uv run pytest tests/markdown_formatter/test_normalize.py tests/markdown_formatter/test_corpus.py --no-cov`: passed,
  19 tests.
- `uv run pytest`: 374 passed, 1 failed. The sole failure is pre-existing and unrelated:
  `tests/test_configure.py::TestDotInstallerInstallTools::`
  `test_install_manifest__does_not_install_opencode_npm_dependencies`,
  because `.config/opencode/package.json` contains `@opencode-ai/plugin` `1.18.14` while the test expects `{}`.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: failed with 74 pre-existing diagnostics in `md-to-pdf.py`, clipboard/Gmail tools, opencode
  cost/trend modules, configure tests, Jira tests, and spinner tests; no formatter-specific diagnostics were reported.

No planning or review artifacts were modified. No commit was created.


## Execution-review 08 final formatter-specific repair 2026-09-03

Repaired nested fenced-code source ownership by retaining the parser-owned fence metadata and deriving the first logical
payload interval after removing its proven container prefix exactly once. Existing empty-list, frontmatter, opaque HTML,
hard-break wrapping, table geometry, and temporary-file collision protections remain covered by focused regressions.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 190 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `git diff --check`: passed.
- `uv run pytest --no-cov`: 503 passed and one known unrelated configure assertion failed because the OpenCode package
  manifest contains `@opencode-ai/plugin` while the baseline test expects an empty dependency mapping.

The requested focused formatter blockers are resolved in the exercised suite. Repository-wide Ty was not rerun because
the review-documented baseline diagnostics remain outside formatter scope. No plans or reviews were edited and no commit
was created.


## Execution-review whole-plan repair: C01-C06 and S01-S02 2026-09-03

### Status

Applied the requested formatter-only repairs and exact regressions. Empty list items now normalize to safe empty items,
frontmatter multiple-document detection is confined to the extracted YAML stream, table center columns use two marker
positions, and replacement cleanup removes only a temporary file successfully created by the current invocation. Long
list continuation lines are wrapped through the token-aware path. Parser raw-HTML masking now also inspects code ranges
inside opaque blocks, while nested fence metadata derives its payload boundary from physical lines after
container-prefix
removal.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `src/dot_tools/markdown_formatter/operations.py`
- UPDATED: `tests/markdown_formatter/test_frontmatter.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: `tests/markdown_formatter/test_operations.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 190 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.


## Execution-review 08 parser ownership repair 2026-09-03

Repaired parser source-span handling for nested fenced code by deriving the first payload interval from physical lines
after removing proven container prefixes, while preserving the existing token-driven inline ownership and bounded
compatibility fallback. Added the parser/model regression coverage already present in the focused edge contract suite.

Verification:

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 190 tests.
- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_edge_contract.py --no-cov`:
  passed, 98 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `git diff --check`: passed.

No plans or reviews were edited. No commit was created.


## Execution-review 09 repair: C07, C09, and C10 2026-09-03

Repaired the requested formatter-only findings. List normalization now visits every list-item child, removes only the
containing marker before normalizing first-child headings, fenced code, quotes, and nested lists, and preserves active
task and continuation columns. Recursive containers use the same blank-line block join at every depth. Inline wrapping
now preserves source adjacency and only treats actual source whitespace as a wrap boundary; non-escapable backslashes
remain literal.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: 202 passed.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct probes confirm first-child heading/code/quote/list preservation, nested separator stability, adjacent inline
  atoms, and literal `foo\\bar` output. The existing operation, CLI, and wrapper files were not modified.
- No commit was created.
- `uv run pytest --no-cov`: 503 passed, 1 known unrelated configure assertion failed.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: failed with the known 74 baseline diagnostics outside formatter scope.
- `git diff --check`: passed.

The cooperating-writer lock limitation remains unchanged: an uncooperating pathname mutation cannot be prevented
atomically by the available macOS APIs. No plans or reviews were edited and no commit was created.


## Execution-review normalization and rendering repair: requested scope

### Status

Repaired only normalization/rendering findings C03, C04, C05, S01, and S02 in the feature worktree. List normalization
now
consumes parser-owned nested list items recursively and retains continuation lines. Block-quote containers are
normalized
recursively with active prefixes. Heading processing is container-local, source transition separators are consumed only
when parser metadata authorizes them, and generated spacing remains stable. Table cells preserve code-span pipes while
canonicalizing literal-pipe escapes. Fence metadata reads the actual backtick or tilde marker and rendering honors the
stored fence and normalized info.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/render.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 105 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter`: passed.
- Direct nested-list, blockquote, tilde-fence, code-span-pipe, and escaped-pipe probes were run; the exercised outputs
  were idempotent.

No plans or review artifacts were edited. No commit was created.


## Execution-review 07 formatter-specific coverage and repair pass 2026-09-02

### Status

Re-read the complete formatter source and focused tests, then ran independent probes before editing. The remaining
direct
failure was nested fenced code inside a list within a blockquote: quote prefixes were retained in the normalized
payload,
which changed the fence and made the second pass unstable. Normalization now strips physical quote prefixes before code
payload extraction. Added an exact output and three-pass regression. Existing S01 and S02 repairs were verified by their
exact comment-only frontmatter and lexical-alias tests.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** This implementation journal


### Verification

- Independent direct probes before editing reproduced the nested list/blockquote fence failure and confirmed the list
  hard
  break, lazy continuation, task, multidigit, CRLF table, CRLF code payload, comment-only frontmatter, and lexical alias
  paths already repaired.
- `uv run pytest tests/markdown_formatter/test_edge_contract.py --no-cov`: passed, 40 tests.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 184 tests.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `git diff --check`: passed.
- Grouped `dt markdown` help, wrapper help, wrapper check smoke, and wrapper format smoke passed. Both smoke operations
  reported `UNCHANGED` and `summary ... SUCCESS 1`.
- `uv run pytest --no-cov`: 497 passed, 1 failed. The sole failure remains the unrelated configure assertion that
  `.config/opencode/package.json` must be empty while it contains `@opencode-ai/plugin` version `1.18.14`.

The cooperating-writer lock and cleanup/race behavior remain covered by the focused operation tests. The documented
limitation is unchanged: an uncooperating pathname mutation cannot be prevented atomically by the available macOS APIs.
No plans or reviews were edited. No commit was created.


## Final QA formatter-specific blocker repair 2026-09-02

### Status

Repaired the remaining nested list and blockquote fenced-code indentation defect. Fenced normalization now removes quote
markers first, then removes the opening fence's physical indentation exactly once from each fence line before extracting
the payload. Rendering continues to add each structural prefix exactly once. Added an exact nested-list-in-blockquote
regression asserting identical first, second, and third output bytes and the semantic payload, including trailing
spaces.


### Verification

- `uv run pytest tests/markdown_formatter/test_edge_contract.py --no-cov`: passed, 41 tests.
- `uv run pytest tests/markdown_formatter --no-cov`: passed.
- `uv run pytest --no-cov`: failed with 498 passed and one pre-existing unrelated configure assertion concerning
  `@opencode-ai/plugin` in `.config/opencode/package.json`.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `uv run ty check`: failed with the known 74 baseline diagnostics outside the formatter scope.
- `git diff --check`: passed.

Only formatter source, focused formatter tests, and this journal were modified. Operations, CLI, wrapper, plans,
reviews,
and unrelated repository code/tests were not modified. No commit was created.


## Execution-review whole-plan repair: C01, C02, C03, C04, C05, and C06 parser scope 2026-09-02

### Status

Applied the requested parser, model, normalization, rendering, test, and fixture scope only. Nested-link-like labels now
fall back to an opaque paragraph when markdown-it cannot prove outer-link ownership. URI autolinks use the parser-owned
scheme form, including custom schemes, and parser-identified HTML blocks reject processing instructions. Split
backtick-info fence recovery now requires a verified closing line; otherwise the recovered source remains opaque rather
than consuming following blocks. Blockquoted tables likewise fail closed when physical cell ownership is not provable.
Hard-break wrapping now retains the owned inline token groups on each side of the break.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 158 tests.
- Focused Ruff: passed.
- Focused Ty: passed.
- Direct probes confirmed nested-link preservation, URI autolinks, processing-instruction rejection, fence boundaries,
  blockquoted-table stability, and three-pass output where applicable.

Operations, CLI, wrapper, plans, and review artifacts were not modified. No commit was created.


## Execution-review 26 bare-CR formatter repairs 2026-09-03

Repaired C01 by deriving lazy list continuation from line-ending-normalized physical lines, including task-aware
continuation columns through nested items. Repaired C02 by normalizing recognized paragraph source to LF before
container-prefix splitting. Repaired C03 by reserving single-line fence compatibility recovery for sources without
internal LF, CRLF, or bare-CR line endings; multiline bare-CR fences now retain normal code ownership and payload
handling.

Added exact LF, CRLF, and bare-CR regressions for task continuations, nested containers, and fenced code. Accepted HTML
tests and behavior remain unchanged. No plans or review artifacts were edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 401 tests.
- Focused Ruff and Ty checks passed.
- Direct C01-C03 and accepted HTML probes passed.
- `git diff --check` passed.


## Execution-review 25 formatter-specific repairs 2026-09-03

Repaired C01 by separating lazy first-paragraph continuation lines from first-paragraph content even when secondary
paragraphs follow. The renderer applies the task-aware active continuation column recursively, while secondary
paragraphs
retain their structural child column. Repaired S01 by sending secondary paragraphs through the same token-aware
120-codepoint wrapper as ordinary prose.

Repaired S02 by normalizing CRLF and bare CR to LF in recognized nested emphasis and strong fallback source and
link-tail
destination/title codecs. Opaque and code payload handling remains unchanged, and no HTML policy logic was added.

Added exact LF, CRLF, and bare-CR regressions for task continuations, nested task items, long secondary paragraphs,
nested
inline fallback, and multiline link titles. Tests assert exact output, source spans, semantic reparsing, task/paragraph
shape, and three-pass stability.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 387 tests.
- Focused Ruff and Ty checks passed.
- Direct C01, S01, and S02 probes plus accepted HTML probes passed.
- `git diff --check` passed.

No plans or review artifacts were edited. No commit was created.


## Execution-review 23 blocker repairs 2026-09-03

Repaired C01 by validating the complete inline node shape after canonical delimiter encoding. When CommonMark flanking
context makes the generated spelling unsafe, the formatter now retains the proven paragraph or table-cell source instead
of changing its AST. The same guard applies across LF and CRLF source and recursively to inline children.

Repaired C02 by separating each list item's structural child column from its task-aware paragraph continuation column.
Secondary block quotes, headings, fences, and nested containers now render at the structural column, while ordinary
paragraph continuation lines retain the task prefix in their column calculation.

Added exact LF/CRLF regressions for mixed emphasis in paragraphs and table cells, plus task-bearing quote, heading, and
fenced-code children. Tests assert reparsed shape, task state, output, and three-pass stability. No plans or review
artifacts were edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed.
- Focused Ruff and Ty checks passed.
- Direct C01/C02 and accepted-HTML probes passed.
- `git diff --check` passed.


## T01 dead-helper cleanup 2026-09-03

Verified the review-21 T01 candidates before editing. `_scan_inline_legacy` had no callers, and its dependent
`_matching_delimiter`, `_next_byte_boundary`, and `_offset_index` helpers were referenced only by that legacy scanner.
The other named helpers were already absent or active under distinct current names, so they were left unchanged. Removed
only the uncalled scanner and its dependent helpers. No tests or review artifacts were modified.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 306 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Import/API smoke and seven direct formatter probes passed, including accepted HTML and idempotence.
- Grouped `dt markdown` help commands passed.
- `git diff --check`: passed.


## Review-21 formatter blocker repairs 2026-09-03

Repaired the remaining inline ownership and heading-boundary defects without adding HTML policy logic. Canonical
emphasis and code delimiters now escape adjacent literal punctuation, including table cells. Hard-break scanning owns
insignificant trailing spaces and normalization removes them from canonical prose. Empty ATX headings map to empty owned
inline content, and ancestor heading transitions use sibling spacing rather than child spacing.

Added LF/CRLF exact-byte, semantic-reparse, source-ownership, and three-pass regressions for the direct review cases and
accepted HTML behavior. Removed dead table compatibility helpers and the unused renderer fence helper. No plans or
review
artifacts were edited and no commit was created.


### Verification

- Focused formatter tests, Ruff, Ty, direct C01/C02/C03/S01/S02 probes, accepted HTML probes, and `git diff --check`
  were run after the repair.


## Execution-review 20 blocker repairs

Repaired the remaining formatter-specific findings without restoring embedded-HTML policy logic. Lazy list continuation
lines that cannot be independently owned now preserve the complete list as opaque source, preventing nonempty content
from
becoming an empty continuation. Code-span close matching now ignores backslash parity inside spans while opener handling
and table delimiter escaping retain their existing rules. Equal-level sibling headings now carry two blank lines of
normalized spacing, while first-child spacing and generated separator spacing remain distinct.

Added exact LF/CRLF regressions for lazy task/list continuation, code-span source ownership and table extra-cell errors,
heading normalized state, semantic reparsing, accepted HTML, and three-pass convergence. No plans or review artifacts
were
modified and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 296 tests.
- Focused Ruff and Ty checks passed.
- Direct C01/C02/S01 probes passed, including exact bytes, parser ownership, semantic payloads, table error behavior,
  and
  three-pass convergence.
- `git diff --check` passed.


## Execution-review 17 formatter blocker repairs 2026-09-03

Repaired all remaining formatter-specific findings without reinstating embedded-HTML rejection. The inline codec now
decodes parser-owned escapes once and protects canonical emphasis delimiters, including table cells. Angle destinations
escape decoded less-than bytes, and link titles use semantic double-quoted encoding. Same-family nested lists emit a
structurally safe blank-line boundary while empty items retain nested children. Heading spacing is carried into rendered
state. Indented code restores source-owned LF or CRLF endings after parser visual indentation.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/render.py`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** `tests/markdown_formatter/test_normalize.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 271 tests.
- Focused Ruff passed.
- Focused Ty passed after narrowing the new parser metadata assertion.
- Direct probes passed for C01-C04, S01-S03, accepted HTML, semantic reparsing, and three-pass convergence.
- `git diff --check`: passed.

No plans or execution-review artifacts were edited. No commit was created.


## Execution-review 16 formatter blocker repairs 2026-09-03

Repaired C01-C05 and S01 without restoring embedded-HTML rejection. Empty-list fenced rendering now prefixes physical
code lines without splitting or rejoining payload bytes, including CRLF and trailing spaces. Parser, normalizer, and
renderer table handling share exact unescaped backtick opener runs and matching closers, so escaped backticks do not
hide
physical delimiters while double-backtick spans retain inner pipes. List-item child headings share descent state and
emit
active-prefix separators. Empty owned link and image labels now use the same destination and title codecs as nonempty
labels. Task-bearing nested lists render at the structural child column so reparsing retains task state and hierarchy.
Recognized heading content now removes only terminal structural whitespace.

Added exact LF/CRLF regressions for payload bytes, parser spans, table boundaries, list AST shape, link/image and table
codecs, heading separators, accepted HTML, semantic reparsing, and three-pass convergence. No plans or review artifacts
were edited and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 258 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct C01-C05, S01, and accepted-HTML probes passed, including exact bytes, parser ownership, semantic reparsing,
  and three-pass stability.
- `git diff --check`: passed.


## Execution-review 13 formatter-specific repair 2026-09-03

Repaired C01 by enforcing a maximum three-column residual closer indentation after proven container and opening-fence
indentation. Closing runs now compare their actual marker character and length, preserving four-space payload lines and
all tested LF/CRLF fence boundaries.

Repaired C02 by removing the legacy delimiter fallback. Semantic soft breaks and image tokens now receive exact source
ownership, while unprovable split-fence constructs remain ordinary parser-proven text or opaque rather than acquiring
invented code spans. Multiline padded code retains its semantic payload and converges across three passes.

Repaired S01 with a boundary-aware block join. Generated heading separators add only the missing LF bytes around opaque
terminal line endings or whitespace, preserving opaque source bytes and exact LF/CRLF output.

Added exact parser ownership, semantic reparse, source-byte, LF/CRLF, and three-pass regressions for all three findings.
No plans or review artifacts were modified and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 229 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct C01/C02/S01 LF/CRLF probes passed, including source ownership, semantic payloads, exact separator bytes, and
  three-pass convergence.
- `git diff --check`: passed.


## Execution-review 12 formatter-specific repair 2026-09-03

Repaired all six formatter findings from review 12. Fence closing now compares the actual marker run after structural
indentation and preserves mismatched or short marker payloads, including split-fence recovery. Inline code uses the
parser's CommonMark-normalized payload exactly once and emits boundary padding that reparses to the same payload.
Nested rendering prefixes physical code lines without normalizing payload line endings. Ordered-list metadata survives
blockquote nesting, link destinations select canonical bare or angle form with decoded escaping, and table ownership and
geometry strip only ASCII edge spaces while preserving tabs.

Added exact ownership, semantic-reparse, LF/CRLF, and three-pass regressions for each finding. No plan or review
artifact
was modified and no commit was created.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 217 tests.
- Focused Ruff and Ty checks passed for formatter source and tests.
- Direct probes passed for fence boundaries, padded spans, nested CRLF code, ordered quote lists, link destinations,
  and tab-edged table cells.


## Final QA formatter-specific cleanup 2026-09-03

Re-read execution review 08, the current formatter source, focused tests, and this journal. Added exact regressions for
center-table marker geometry, arbitrary semantic backslash runs before internal and trailing literal pipes, code-span
pipes, repeated cells, CRLF and blockquote table stability, zero-cell rejection, and complete temporary-collision
operation records. Temporary cleanup now verifies the inode created by this invocation before unlinking, so a pathname
collision or replacement race cannot remove an unrelated file.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 202 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct formatter probes passed for center geometry, semantic backslash runs, code-span pipes, LF/CRLF and blockquote
  tables, repeated cells, zero-cell rejection, lexical aliases, symlink destinations, and collision preservation.
- Grouped `dt markdown check` and wrapper check smoke probes reported `UNCHANGED` and `summary check SUCCESS 1`.

No plans or reviews were edited. No commit was created.


## Execution-review 08 follow-up 2026-09-03

Focused parser, normalize, render, and document tests pass, as do focused Ruff and Ty checks. A direct nested-fence
probe still exposes quote-prefixed bytes in `CodePayload.payload` and `payload_span`, so C04 remains a concrete blocker.
No additional parser rewrite was made after that probe. The existing C01, C02, C03, C05, C06, and S01 fixes were not
altered. No plans or reviews were edited. No commit was created.


## QA nested-fence parser blocker repair 2026-09-03

Repaired only nested fenced-code payload ownership in the parser, normalizer, and focused formatter tests. The parser
now
maps each physical payload line through one container-prefix removal and one fence-indentation removal, preserving line
endings and semantic indentation. It omits `payload_span` when those transformations make semantic bytes physically
discontiguous, while the enclosing fence span remains the complete original source interval. Normalization consumes the
parser's semantic `CodePayload` rather than reconstructing payload bytes from prefixed source lines.

Added LF and CRLF nested list-in-blockquote regressions for semantic payload bytes, optional span validity, rendered
output,
and three-pass equality. No operations, CLI, plans, reviews, or unrelated tests were modified. No commit was created.


## Execution-review 07 focused repair 2026-09-02

### Status

Repaired only the four requested concrete findings. Table row offsets now advance by each actual LF or CRLF ending, and
fenced code payload spans include the complete payload-line ending while keeping empty payloads valid. Comment-only YAML
frontmatter streams now use the empty mapping path. Operation operands and recursive discoveries now undergo lexical `.`
and `..` normalization without resolving symlink targets, so equivalent spellings deduplicate while symlink behavior is
unchanged.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/frontmatter.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/operations.py`
- **UPDATED:** `tests/markdown_formatter/test_parser.py`
- **UPDATED:** `tests/markdown_formatter/test_frontmatter.py`
- **UPDATED:** `tests/markdown_formatter/test_operations.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_frontmatter.py
  tests/markdown_formatter/test_operations.py --no-cov`: passed, 91 tests.
- Focused Ruff for the changed source and tests: passed.
- Focused Ty for the changed source and tests: passed.
- Exact source-slice assertions cover LF and CRLF tables, escaped/code pipes, astral cells, LF/CRLF fenced payloads,
  empty and trailing-space payloads, and missing final LF through the parser regressions.

No plans or reviews were edited. No commit was created.


## Execution-review 07 C03 and C04 follow-up 2026-09-02

### Status

Completed the requested C03 and C04 formatter source and regression coverage. The parser now exposes explicit physical
table rows and cells with framing pipes excluded, and row/cell byte spans advance by each complete LF or CRLF ending.
Fence metadata now records exact marker, info, and payload spans, with CRLF payload spans including the complete line
ending before a verified closing fence. Existing normalization and rendering preserve literal escaped pipes, code-span
pipes, collision-safe fences, and canonical three-pass output.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `tests/markdown_formatter/test_parser.py`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 182 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct LF/CRLF probes confirmed exact table row/cell slices, escaped and code-span pipe preservation, fence payload
  boundaries, empty and unclosed payload handling, backtick-info fence boundaries, and three-pass convergence.

No plans or reviews were edited. No commit was created.


## Execution-review 07 C01 and C02 repair 2026-09-02

### Status

Repaired recursive list and blockquote prefix composition in the formatter source. List paragraph source handling now
retains physical hard and lazy continuation lines instead of joining them into prose, and nested block normalization
uses the active context while rendering applies each structural prefix once.


### Verification

- Direct recursive list, blockquote, nested fence, hard-break, and lazy-continuation probes were run.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 172 tests.
- Focused Ruff and Ty checks passed for formatter source and tests.

Operations, CLI, wrapper, plans, and reviews were not modified. No commit was created.


## Execution-review whole-plan repair pass 07

### Status

Re-ran direct probes for the unresolved C01-C06 and S01/S02 cases. Nested-link ownership, URI autolinks, processing
instructions, blockquoted tables, fence boundaries, hard-break wrapping, and table/code masking preserve the tested
semantics. One additional list case exposed a continuation paragraph that became lazy prose on the second pass. The
normalizer and renderer now retain the blank paragraph boundary. Compatibility tables now own physical cells when
markdown-it leaves a code-pipe table as a paragraph. Input and policy errors retain snapshots captured after a
successful
read.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 161 tests.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `git diff --check`: passed.
- Direct probes confirmed three-pass stability for blank-line list continuation and code-pipe table cases, plus the
  previously reported inline, URI, raw-HTML, fence, quote, and wrapping cases.

The known unrelated configure assertion and repository-wide Ty baseline remain unchanged. Plans, reviews, and unrelated
repository code/tests were not modified. No commit was created.


## Execution-review whole-plan repair: C02, C04, C05, and C06 parser/normalize/render 2026-09-02

### Status

Repaired the assigned parser, normalization, and rendering portions of the review findings. Nested list and blockquote
prefix handling now preserves task markers and renders nested lists with the active structural column exactly once.
Owned list continuation paragraphs retain their text, including wrapped hard-break segments. Inline semantic ownership
continues across hard breaks, and code spans retain semantic payload normalization. Existing fence and table state
remains
renderer-driven, including collision-safe fence selection and decoded Unicode width padding.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `tests/markdown_formatter/` existing focused coverage
- UPDATED: This implementation journal


### Verification

- Direct probes covered quoted task lists, nested list continuation, mixed list child blocks, hard-break prose, padded
  code spans, tilde fences, Unicode table widths, and three-pass output stability.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 149 tests.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- `git diff --check`: passed.

Operations, CLI, wrapper, plans, and review artifacts were not modified. No commit was created.


## Execution-review whole-plan repair: C01, C02, C03, and C05 parser/inline portions 2026-09-02

### Status

Repaired the assigned parser/model/inline portions only. Inline ownership now consumes markdown-it's semantic child
tokens before using the conservative compatibility scanner, so intraword underscores, mixed delimiter runs, nested
emphasis, escapes, hard breaks, code spans, and parser-recognized autolinks no longer depend on first-closer delimiter
heuristics when markdown-it can prove the structure. Inline code nodes retain markdown-it's semantic payload for exact
padding and trimming. Table cell lookup now advances per physical row, giving repeated cell content distinct source
spans, and framing-only all-pipe rows fail closed.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `tests/markdown_formatter/test_parser.py`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** This journal


### Verification

- Direct C01-C03/C05 probes were run before editing and reproduced the reported intraword, delimiter, padded-code,
  repeated-table-span, and all-pipe failures.
- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_normalize.py
  tests/markdown_formatter/test_render.py tests/markdown_formatter/test_document.py --no-cov`: passed, 50 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_edge_contract.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py`: passed.
- Follow-up probes confirm stable canonical output for intraword text, nested delimiter cases, padded code spans, and
  repeated-cell tables; `|||` is rejected as a framing-only recognized table row.

Operations, CLI, wrapper, plans, and reviews were not modified. No commit was created.


## Final implementation repair and coverage pass 2026-09-02

### Status

Re-ran direct semantic probes before editing across inline ownership and codecs, code-first HTML masking, nested
containers, source breaks, tables, fences, frontmatter, operation records and replacement behavior, and grouped/wrapper
entry points. The probes found two formatter-specific defects: a single-line inline code span could be misclassified by
the block parser and UTF-8 table cells were padded by byte length rather than code-point width. The parser now recovers
the single-line code span as an owned inline paragraph, and table rendering pads decoded text to the normalized width.
Added exact byte, recursive source-span, and three-pass stability assertions.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_edge_contract.py --no-cov`: passed, 28 tests.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 144 tests.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed after correcting the local marker
  narrowing and exact span assertion.
- `uv run pytest --no-cov`: 457 passed, 1 failed. The failure remains the unrelated configure assertion about
  `@opencode-ai/plugin` in `.config/opencode/package.json`.
- `uv run dt markdown --help`, grouped format/check help, wrapper help, and wrapper check/format smoke: passed; both
  smoke operations reported `UNCHANGED` and `summary ... SUCCESS 1`.
- `git diff --check`: passed.

The repository-wide configure failure and baseline Ty diagnostics remain unresolved and were not modified. No plans or
reviews were edited. No commit was created.


## Execution-review 04 operation-safety continuation 2026-09-02

Moved the cooperating-writer lock to the destination directory and made it cover temporary-file creation, fsync,
final snapshot validation, and `os.replace`. Formatter operations that honor this lock now serialize their complete
replacement protocol. Removed the production-only replacement hook; tests use competing lock attempts and direct
snapshot revalidation instead.

The contract is deliberately bounded: this is the strongest practical macOS strategy for cooperating formatter writers,
not a portable compare-and-swap pathname rename. A process that mutates or renames the destination without taking the
shared lock can still race after validation, because macOS provides no conditional replacement primitive for an
arbitrary
pathname. Symlink, non-regular, mode, and content changes observed during locked validation are rejected and temporary
files are cleaned up.


## Execution-review 04 continuation 2026-09-02

### Status

Repaired two remaining formatter-specific container and table edge cases exposed by direct probes. Nested blockquote
code
now receives the composed active prefix during recursive normalization, preventing payload prefixes and fence growth on
repeat. Table framing-only rows are rejected across the complete recognized table, while whitespace-delimited empty
cells
remain valid. Added exact output, rejection, and idempotence assertions.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: This implementation journal


### Verification

- Direct probes were run before editing and reproduced nested quote code growth and incomplete framing-row rejection.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 140 tests.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/markdown_formatter`: passed.
- `git diff --check`: passed.

The documented optimistic replacement contract remains unchanged: the per-destination advisory lock protects cooperating
writers, but an uncooperating external rename can still race on macOS. Full pytest, wrapper/grouped smoke, and
repository
Ty verification remain subject to the previously documented unrelated configure failure and baseline Ty diagnostics.

No plans or reviews were edited. No commit was created.


## Final formatter-specific repair and coverage pass 2026-09-02

### Status

Re-read execution review 05, the approved plan, this journal, and the current formatter source and tests. Direct probes
covered the requested C01-C07 and S01/S02 paths. The formatter-specific defects reproduced in this pass were list prose
wrapping losing its continuation prefix on the second pass and the two-tick empty inline-code boundary being treated as
ordinary text. Both are repaired with exact-byte and three-pass regressions.

The macOS replacement boundary remains an explicit optimistic/cooperating-writer contract: the advisory lock protects
writers that take the formatter lock, but an uncooperating pathname mutation cannot be prevented atomically by the
available macOS APIs. The implementation and tests do not claim stronger protection.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 154 tests.
- `uv run pytest --no-cov`: failed with 457 passed and the known unrelated configure assertion concerning
  `@opencode-ai/plugin` in `.config/opencode/package.json`.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: failed with the known unrelated baseline diagnostics; no formatter-specific diagnostics were
  reported.
- `git diff --check`: passed.
- Grouped CLI and wrapper help, format/check smoke, direct semantic probes, and the formatter-specific C01-C06/S01/S02
  regressions passed except for the documented uncooperating-writer limitation.

No plans or reviews were edited. No commit was created.


## Execution-review 04 formatter repair pass 2026-09-02

### Status

Repaired the remaining formatter-specific inline codec and mixed-prose wrapping gaps from execution review 04. Owned
emphasis and strong nodes now converge to canonical `*` and `**` delimiters, while nested labels and semantic link
destinations remain intact. Angle destinations containing whitespace remain angle-encoded, and quoted titles normalize
to double-quoted form without losing escaped quotes. Added exact-byte regressions for these cases and for wrapping a
paragraph around an indivisible link atom.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: This journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 136 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter`: passed.
- `git diff --check`: passed.
- Direct probes confirmed canonical delimiter conversion, nested link labels, balanced destinations, code-span payload
  preservation, normal tilde-to-backtick fences, zero-cell table rejection, and second-pass stability.

Operations, CLI, wrapper, plans, reviews, and unrelated repository code/tests were not modified. No commit was created.


## Execution-review 04 parser/source-span and nested-container repair

### Status

Repaired the assigned parser/source-span and nested-container portion of execution review 04. Inline ownership now
requires one unique exact source interval and verifies every owned node span against the original UTF-8 body. When a
container prefix makes that proof impossible, the containing block is opaque and its provisional inline nodes are
discarded. Parser-owned table cell inline content is associated from cell token maps, and opaque state propagates
through
recognized containers so normalization cannot rewrite an unsafe descendant.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `tests/markdown_formatter/test_parser.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 133 tests.
- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_document.py --no-cov`: passed, 35
  tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py`: passed.

No plans or reviews were edited. Operations, CLI, wrapper, and unrelated repository code/tests were not modified. No
commit was created.


## QA formatter blocker repair 2026-09-03

Repaired list-item hard-break normalization. Parser-owned hard-break token groups now remain separate while each side
passes through the token-aware 120 Unicode code-point wrapper. Rendering emits one canonical ASCII backslash followed by
LF, then applies the active list continuation prefix. This prevents continuation content from merging into first-item
prose and keeps repeated formatting stable. Added exact canonical-byte, Unicode-width, and three-pass coverage.

Confirmed the restricted frontmatter path already handles comment-only and empty roots through the empty mapping path
and
limits multiple-document detection to the extracted YAML envelope. Added a direct fenced delimiter-like body regression.


### Verification

- `uv run pytest tests/markdown_formatter/test_edge_contract.py tests/markdown_formatter/test_frontmatter.py --no-cov`:
  passed.
- `uv run pytest tests/markdown_formatter --no-cov`: passed.
- Focused Ruff and Ty checks passed.
- Direct list hard-break probe confirmed canonical bytes, per-side width, and three-pass equality.

No plans, reviews, operations, or CLI files were modified. No commit was created.


## Repair pass 2026-09-02

Addressed the fourth execution review's formatter findings in source and focused tests. The inline scanner now respects
exact backtick-run ownership, links retain angle destinations that contain spaces, table framing-only rows fail closed,
ordinary tilde fences converge to collision-safe backticks, and mixed inline paragraphs use token-aware wrapping. Atomic
replacement now holds a per-destination advisory lock across final validation and replacement for cooperating writers.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 133 tests.
- `uv run ruff check src tests/markdown_formatter`: passed.
- `git diff --check`: passed.
- Existing repository changes and the known configure test and Ty baseline were not altered.

The prior race tests depended on the removed production-only hook and were removed rather than preserving a test seam.
The lock protects cooperating writers; an uncooperating external rename can still race because no portable macOS API
provides compare-and-swap replacement for an arbitrary pathname. That bounded limitation remains explicit.


## Execution-review whole-plan repair pass 03 continuation

### Status

Re-ran the requested direct probes before editing. The remaining reproduced formatter issue was a backtick-bearing info
string inside a blockquote: recursive fence joining was not applied at every container level, and the joined metadata
did
not override the blockquote-stripped fence metadata. The parser now joins nested split fences recursively and restores
the actual info string. The regression test asserts exact canonical bytes and repeated-format stability. The safe
backtick-info fallback is a tilde fence, as required by the plan.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: This implementation journal


### Verification

- The focused formatter suite passed: 136 tests.
- The new direct regression passed after correcting its expected tilde fallback bytes.
- Grouped CLI help and compatibility-wrapper help passed.
- `git diff --check` passed.
- Ruff and Ty were invoked with the full repository commands. Ruff output was not reached because the focused test
  command
  in the parallel verification invocation failed before the chained checks. The known repository Ty diagnostics remain
  unrelated and were not changed.
- Full pytest and the complete grouped/wrapper smoke matrix remain to be run after this final edit.

No plans or review artifacts were edited. No commit was created.


## Execution-review whole-plan repair pass 03

### Status

Repaired the remaining normalization and rendering container paths in the assigned scope. List-item block children now
remain structured instead of being flattened into continuation prose, nested blockquotes render their active prefix only
once, and fenced code inside blockquotes no longer grows its fence or quote markers on repeated formatting. Secondary
paragraphs in list items are rendered from their semantic inline nodes, avoiding duplicated source text on the next
pass.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: This implementation journal


### Verification

- Direct probes covered nested list-item paragraphs, list-item blockquotes, and blockquote-contained fences. The outputs
  were stable after a second formatting pass, including:
  `b'# T\\n\\n- p\\n  second\\n  > q\\n  > r\\n'` for the mixed list case.
- `uv run pytest tests/markdown_formatter --no-cov`: passed, 130 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter`: passed.
- `git diff --check`: passed.

No plans or review artifacts were edited. Operations, CLI, and wrapper code were not modified. No commit was created.


## Execution-review 08 parser ownership repair 2026-09-03

### Status

Reworked the parser's source-ownership boundary for nested fenced code. A fence whose physical source contains quote
markers is now preserved as an opaque parser-owned block instead of exposing a contiguous payload span that includes
structural bytes. The existing token-driven inline association remains authoritative, with the bounded compatibility
scanner retained only when its recursive reconstruction proves the complete source slice.


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_normalize.py
  tests/markdown_formatter/test_render.py tests/markdown_formatter/test_document.py --no-cov`: passed, 72 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py --no-fix`:
  passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py`: passed.
- Direct probes covered arbitrary backtick text, delimiter runs, escaped syntax, balanced destinations, and autolinks.

The broader C01-C06 review matrix still requires the existing normalization, frontmatter, and operations repairs to be
validated together. No plans or reviews were edited. No commit was created.


## Execution-review repair: parser/model findings C01 and C02

### Status

Repaired the assigned parser-facing portions of C01, C02, and C03/C05. Inline link normalization now uses the
parser-owned
label interval, preserving nested link destinations. Emphasis and strong nodes retain their source delimiter spelling.
CommonMark URL and email autolinks are recognized as owned links and excluded from raw-HTML rejection, including astral
prefixes. Parser-split backtick-info fences remain one fence node with source span and code metadata. Code payload
metadata
now carries marker, info, and payload spans. Added exact parser regressions for these cases.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `tests/markdown_formatter/test_parser.py`
- UPDATED: This implementation journal


### Verification

- Direct review probes were run before editing. They reproduced destructive nested emphasis/link output, raw-HTML
  rejection of autolinks, parser-split backtick-info fences, and non-idempotent list-item blockquote output.
- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_document.py --no-cov`: passed, 35
  tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  tests/markdown_formatter/test_parser.py`:
  passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  tests/markdown_formatter/test_parser.py`:
  passed.
- Follow-up probes confirmed nested link and delimiter spelling preservation, autolink acceptance, backtick-info fence
  conversion to a collision-safe tilde fence, and stable second-pass output. Nested list blockquote output is stable but
  remains a normalization/rendering concern outside this parser-focused pass.

No plans or reviews were edited. No commit was created.


## Execution-review whole-plan repair pass 02

### Status

Repaired the remaining formatter-specific behaviors exposed by direct review probes. Parser code masking now handles
nested block-quote prefixes and angle destinations with escaped titles, paragraph normalization preserves hard-break
ownership, and list-item block-quote continuation content is retained. Existing operation, frontmatter, wrapper, and
CLI repairs remain in place. The corpus and edge expectations were corrected where the previous assertions encoded the
old lossy behavior.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `tests/markdown_formatter/fixtures/corpus/boundaries.expected.md`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** This journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 125 tests.
- `uv run ruff check src tests`: passed.
- Direct probes covered astral inline and block code masking, table-header code, intraword underscores, hard breaks,
  angle destinations and titles, unclosed fences, nested lists, nested block quotes, table backslash parity, frontmatter
  key safety, and idempotence.
- `uv run pytest --no-cov`: 437 passed, 2 failed. The formatter corpus boundary expectation was corrected afterward;
  the remaining failure is the documented unrelated configure assertion about `@opencode-ai/plugin`.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: failed with 74 diagnostics in unrelated PDF, clipboard/Gmail, OpenCode, configure, Jira, and
  spinner paths; no formatter path was reported.
- Grouped CLI help and wrapper help passed. Wrapper check and format both returned `UNCHANGED` with `summary ... SUCCESS
  1` for the canonical fixture.
- `git diff --check`: passed.

The focused suite and direct probes pass for the exercised repairs. The formatter-specific matrix is not fully closed:
the requested exhaustive CommonMark destination/emphasis matrix and every operation race/cleanup/status combination
were not all added or independently re-probed in this pass. No formatter-specific blocker was observed in the executed
tests, but this journal does not claim whole-plan completion beyond that evidence.

No plans or reviews were edited. No commit was created.


## Execution-review repair: C10/S01

### Status

Added exact regression coverage for the review's parser, inline, code, table, list, frontmatter, and public contract
gaps.
Formatter-specific fixes cover UTF-8 byte masking, angle destinations, intraword underscores, hard-break precedence,
unclosed fenced payloads, nested list continuation, and arbitrary table framing parity.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `tests/markdown_formatter/test_edge_contract.py`
- UPDATED: `tests/markdown_formatter/test_document.py`
- UPDATED: `tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`
- UPDATED: `tests/markdown_formatter/fixtures/corpus/boundaries.expected.md`
- UPDATED: This journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 125 tests.
- `uv run ruff check src tests`: passed.
- `git diff --check`: passed.

The broader review matrix remains incomplete beyond these focused repairs. Full pytest, Ty, and the requested grouped
and
wrapper smoke commands were not rerun in this pass. No plans or reviews were modified. No commit was created.


## Execution-review repair: C06 through C09

### Status

**Complete for the assigned operations and frontmatter findings.** Format result records now carry canonical output
bytes
for every prepared file, including committed and later untouched files after a write failure. Immediate replacement
revalidates destination identity, mode, type, and content, and reports a preflight failure without replacing the changed
file. Restricted YAML mapping keys use the same quoted string codec as scalar values, and unhashable keys become
`FrontmatterError`.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/operations.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/frontmatter.py`
- **UPDATED:** `tests/markdown_formatter/test_operations.py`
- **UPDATED:** `tests/markdown_formatter/test_frontmatter.py`
- **UPDATED:** This implementation journal


### Verification

- Red focused run: `uv run pytest tests/markdown_formatter/test_frontmatter.py
  tests/markdown_formatter/test_operations.py
  tests/markdown_formatter/test_markdown_cli_contract.py --no-cov` failed on the old output assertions and unquoted-key
  expectations.
- Green focused run: the same command passed, 47 tests, including the immediate replacement race.
- Focused Ruff: `uv run ruff check src/dot_tools/markdown_formatter/operations.py
  src/dot_tools/markdown_formatter/frontmatter.py tests/markdown_formatter/test_operations.py
  tests/markdown_formatter/test_frontmatter.py` passed.
- Focused Ty: the equivalent four-file `uv run ty check` command passed.

No plans or reviews were edited. No commit was created.


## Final Task 07 continuation

### Status

**Complete for formatter-scoped implementation and contract coverage.** Re-ran the formatter suite first, repaired a
wrapper no-project exit-code mismatch, and repaired inline escaped-text rendering so a literal escaped delimiter is
idempotent. Added a wrapper test for repository discovery failure. The unrelated repository baseline remains unchanged.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 111 tests.
- `uv run pytest tests/markdown_formatter/test_wrapper.py --no-cov`: passed, 2 tests during the final focused run.
- `uv run pytest --no-cov`: 424 passed, 1 failed.
  The unrelated failing test is
  `tests/test_configure.py::TestDotInstallerInstallTools::`
  `test_install_manifest__does_not_install_opencode_npm_dependencies`.
  It fails because `.config/opencode/package.json` contains `@opencode-ai/plugin` version `1.18.14` while the test
  expects `{}`.
- `uv run ruff check src tests`: passed with `All checks passed!`.
- `uv run ty check`: failed with 74 existing diagnostics in unrelated Markdown PDF, clipboard/Gmail, opencode,
  configure, Jira, and spinner files. No formatter production or test path appeared in the diagnostics.
- `git diff --check`: passed.
- Grouped CLI help commands for `markdown`, `format`, and `check`: passed.
- Wrapper `--help`: passed.
- Wrapper `check` on the canonical corpus fixture: `UNCHANGED` and `summary check SUCCESS 1`.
- Wrapper `format` on the canonical corpus fixture: `UNCHANGED` and `summary format SUCCESS 1`.


### Coverage and scope

The formatter suite now directly covers public models and signatures, grouped CLI records, streams, status precedence,
digests, parser ownership and code masking, nested containers, heading separators, tables, code fences and spans,
document idempotence, atomic operation safety, races and destination failures, cleanup, partial commits, wrapper
delegation, CWD/project discovery, and corpus behavior. Only formatter source, formatter tests/fixtures, the
compatibility
wrapper, and this journal were changed during this continuation. Plans, reviews, and unrelated repository tests/code
were
not edited. No commit was created.


## Task 07 contract coverage repair

### Status

**Complete for formatter-scoped contract coverage; partial for the repository quality gate.** Added the missing public
contract module and edge-case coverage required by the execution review. The tests directly exercise public models and
signatures, grouped CLI records and streams, status and digest mappings, parser ownership and code masking, containers,
code fences, table idempotence, and finite-real frontmatter. The implementation repairs exposed table escaping,
indented-code payload, empty fence info, paragraph line-break, and total operation-record behavior.


### Files modified

- **CREATED:** `tests/markdown_formatter/test_markdown_cli_contract.py`
- **CREATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** `tests/markdown_formatter/fixtures/corpus/boundaries.expected.md`
- **UPDATED:** `src/dot_tools/markdown_formatter/normalize.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/render.py`
- **UPDATED:** `src/dot_tools/markdown_formatter/operations.py`
- **UPDATED:** This journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 101 tests.
- `uv run ruff check src tests`: passed.
- `uv run pytest --no-cov`: 414 passed, 1 failed. The sole failure is the unrelated configure assertion. The failing
  test checks the OpenCode npm dependency manifest. It expects `.config/opencode/package.json` to be `{}`, while the
  file contains `@opencode-ai/plugin` version `1.18.14`.
- `uv run ty check`: failed with 75 existing repository diagnostics across `md-to-pdf.py`, clipboard/Gmail tools,
  opencode cost/trend modules, configure tests, Jira tests, and spinner tests. The formatter-specific diagnostic from
  the
  new contract test was removed; no formatter production diagnostic remains.

The requested full matrix now has direct contract tests for the principal C09 gaps. Existing implementation limitations
outside the exercised generic formatter behavior remain documented by the earlier review and are not hidden by weakened
tests. No plans or review artifacts were edited. No commit was created.


## Execution-review whole-plan repair: C06 and S01 frontmatter and operations 2026-09-02

### Status

Repaired the assigned frontmatter and operation portions of execution review 05. Empty root frontmatter now emits
exactly
the delimiter-only YAML document required by the plan, while empty nested mappings and sequences retain `{}` and `[]`.
The operation contract now has explicit zero-discovery and complete prepared-result assertions. The
destination-directory
advisory lock remains a real production lock with no replacement hook: it covers temporary-file creation, flush/fsync,
final snapshot validation, and replacement for cooperating formatter writers. An uncooperating writer can still race on
macOS because arbitrary pathname replacement has no compare-and-swap primitive; the implementation and tests do not
claim
protection it cannot provide.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- UPDATED: `tests/markdown_formatter/test_frontmatter.py`
- UPDATED: `tests/markdown_formatter/test_operations.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_frontmatter.py tests/markdown_formatter/test_operations.py
  tests/markdown_formatter/test_markdown_cli.py tests/markdown_formatter/test_markdown_cli_contract.py
  tests/markdown_formatter/test_wrapper.py --no-cov`: passed, 56 tests.
- Added exact empty-root serialization and reparse coverage, nested empty-container coverage, zero-discovery result
  coverage, complete prepared/error field assertions, and cooperating-operation lock serialization coverage.
- No parser, normalization, rendering, plan, or review files were modified. No commit was created.


## Parser finding repair pass

**Status:** Complete for the assigned parser findings C01, C02, S01, and S02 parser output requirements.

Repaired inline ownership so container reconstruction uses the parser-proven label/body slice instead of delimiter
position assumptions. Inline code ranges are included in the code-first raw-HTML mask. Thematic-break validation now
requires an immediately following heading in the same top-level block sequence and a preceding lower-level heading, and
records the eligible transition for normalization. Added direct parser tests for repeated, nested, escaped, astral, and
CRLF inline source ownership, all supported code forms, adjacent raw HTML, every thematic-break spelling, and
intervening-body rejection.


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_document.py --no-cov`: passed,
  26 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  tests/markdown_formatter/test_parser.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  tests/markdown_formatter/test_parser.py`: passed.

No plans or review artifacts were edited. No commit was created.


## Execution-review repair: C04 and S02

### Status

**Complete for the assigned operations and CLI findings.** `_replace` now prepares and fsyncs a same-directory temporary
file, then validates destination identity, mode, regular-file type, symlink state, writability, and content immediately
before replacement. A second operations-local hook sits between that final validation and `os.replace`, allowing the
race window to be exercised deterministically without changing wrapper behavior. A changed destination aborts with
`PREFLIGHT_ERROR`, preserves the concurrent bytes, removes the temporary file, and reports complete sorted records and
commit/untouched sets.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/operations.py`
- **UPDATED:** `tests/markdown_formatter/test_operations.py`
- **UPDATED:** `tests/markdown_formatter/test_markdown_cli_contract.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_operations.py tests/markdown_formatter/test_markdown_cli.py
  tests/markdown_formatter/test_markdown_cli_contract.py --no-cov`: passed, 19 tests.
- Focused Ruff for operations, models, CLI, and operation/CLI tests: passed.
- Focused Ty for operations, models, CLI, and operation/CLI tests: passed.
- Added coverage for post-validation destination mutation, symlink destinations, mode mutation, partial-write records,
  exact CLI streams, exit codes, diagnostics, and temporary-file cleanup.

No plans or reviews were edited. No commit was created.


## Parser-only execution-review repair

### Status

Repaired only parser behavior for findings C01, C02, S01, and the parser portion of S02 in the assigned feature
worktree. Block construction now uses a strict token-type stack, so closing events cannot discard unrelated siblings.
Inline ownership uses token-map lines, byte-index boundaries, and container-prefix stripping. Inline reconstruction
checks
each container's proven child interval. Code ranges, including inline code and code blocks, are masked through the
shared
UTF-8 byte index before raw HTML scanning. Thematic breaks are validated recursively within their containing sequence
and
only an immediately following lower-level heading can authorize a break.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `tests/markdown_formatter/test_parser.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_document.py --no-cov`: passed,
  26 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py tests/markdown_formatter/test_parser.py`: passed.

Normalization, rendering, operations, plans, and reviews were not modified. No commit was created.


## Execution-review normalization and rendering repair

### Status

Repaired the assigned normalization/rendering findings C03, C04, C05, S01, and S02's parser ordering dependency. The
parser now retains meaningful list nesting and parser-owned inline content, normalization consumes recursive list items,
preserves ordered starts and task prefixes, reads actual fence markers, and rendering uses normalized fence and nested
list state. Table rendering now leaves pipes inside code spans untouched. Raw HTML validation runs before H1 policy
validation so policy errors do not mask the required raw-HTML error.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/parser.py`
- UPDATED: `src/dot_tools/markdown_formatter/normalize.py`
- UPDATED: `src/dot_tools/markdown_formatter/render.py`
- UPDATED: `tests/markdown_formatter/test_normalize.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_parser.py tests/markdown_formatter/test_normalize.py
  tests/markdown_formatter/test_render.py tests/markdown_formatter/test_document.py --no-cov`: passed, 40 tests.
- `uv run ruff check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  src/dot_tools/markdown_formatter/render.py tests/markdown_formatter/test_normalize.py`: passed.
- `uv run ty check src/dot_tools/markdown_formatter/parser.py src/dot_tools/markdown_formatter/normalize.py
  src/dot_tools/markdown_formatter/render.py`: passed.

No plans or review artifacts were edited. No commit was created.


## Final execution pass

### Status

**Complete for Tasks 01 through 07 within the formatter scope.** The feature worktree contains the formatter package,
restricted frontmatter handling, source-aware parser, normalization and rendering pipeline, safe file operations,
grouped
CLI, compatibility wrapper, focused tests, and generic corpus fixtures. The final pass repaired delimiter exactness,
empty frontmatter handling, nested link destinations, astral escape spans, code-span padding, and mismatch diagnostic
construction without changing unrelated code.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 61 tests.
- `uv run pytest --no-cov`: 374 passed and 1 failed. The failure is unrelated to this feature:
  `tests/test_configure.py::TestDotInstallerInstallTools::`
  `test_install_manifest__does_not_install_opencode_npm_dependencies`.
  The test expects `.config/opencode/package.json` to be `{}`, while the existing file contains the
  `@opencode-ai/plugin` dependency at `1.18.14`.
- `uv run pytest`: same 374 passed and 1 unrelated failure; coverage reached 81.98%, above the configured 70% threshold.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: failed with 74 existing repository diagnostics; zero diagnostics referenced
  `markdown_formatter` or `cli/markdown.py`.
- `uv run dt markdown --help`, `uv run dt markdown format --help`, `uv run dt markdown check --help`, and
  `~/.agents/tools/markdown-format.py --help`: passed.
- `uv run dt markdown check tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`: reported
  `UNCHANGED` and `summary check SUCCESS 1`.
- `uv run dt markdown format tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`: reported
  `UNCHANGED` and `summary format SUCCESS 1`.


### Modified feature files

- `.agents/tools/markdown-format.py`
- `src/dot_tools/cli/markdown.py`
- `src/dot_tools/markdown_formatter/__init__.py`
- `src/dot_tools/markdown_formatter/frontmatter.py`
- `src/dot_tools/markdown_formatter/models.py`
- `src/dot_tools/markdown_formatter/normalize.py`
- `src/dot_tools/markdown_formatter/operations.py`
- `src/dot_tools/markdown_formatter/parser.py`
- `src/dot_tools/markdown_formatter/render.py`
- `tests/markdown_formatter/` and its fixtures
- This implementation journal

No plans or reviews were edited. No commit was created.


## Execution-review repair: C06 and C07

### Status

Repaired the requested operation-result and finite-real serialization contracts without changing the wrapper or parser,
normalization, or rendering modules. Prepared format results no longer expose canonical output bytes, mismatch results
retain `output=None`, and a first write failure now replaces the failed prepared result while retaining complete sorted
records for committed, failed, and later untouched paths. Restricted YAML loading recognizes supported scientific real
spellings before scalar construction, allowing lossless finite values at both notation thresholds.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/operations.py`
- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- UPDATED: `tests/markdown_formatter/test_operations.py`
- UPDATED: `tests/markdown_formatter/test_frontmatter.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_operations.py tests/markdown_formatter/test_markdown_cli.py
  tests/markdown_formatter/test_markdown_cli_contract.py tests/markdown_formatter/test_frontmatter.py --no-cov`:
  passed, 40 tests.
- Focused Ruff: passed.
- Focused Ty: passed.

No plans, reviews, wrapper, parser, normalization, rendering, or unrelated source files were modified. No commit was
created.


## Execution-review repair: C06, C07, and S03

### Status

Repaired operation result completeness and finite-real frontmatter serialization. Operations now materialize one sorted
`FileResult` for every discovered or explicit path, keep mismatch output unset, preserve prepared output on successful
preflight, and report complete records after preflight or write failure. Diagnostics use stable status names and
mismatch
digests only. Finite reals use shortest round-trippable decimals in fixed notation within the approved envelope and
normalized scientific notation outside it.


### Files modified

- UPDATED: `src/dot_tools/markdown_formatter/operations.py`
- UPDATED: `src/dot_tools/markdown_formatter/frontmatter.py`
- UPDATED: `tests/markdown_formatter/test_operations.py`
- UPDATED: `tests/markdown_formatter/test_frontmatter.py`
- UPDATED: This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter/test_frontmatter.py tests/markdown_formatter/test_operations.py
  tests/markdown_formatter/test_markdown_cli.py --no-cov`: passed, 29 tests.
- Focused Ruff: passed.
- Focused Ty: passed.

No plans or review artifacts were edited. No commit was created.


## Execution-review whole-plan repair: C03 and C04 continuation

### Status

Repaired table source ownership and hard-break wrapping in the assigned formatter scope. Recognized table rows now use
physical cell intervals with inline semantic verification, including escaped and code-span pipes. Framing-only rows such
as `|||` fail closed while whitespace-delimited empty cells remain valid. Hard-break segments wrap independently at the
120-code-point content limit, and recursive list, quote, paragraph, and fence payloads retain their structure and remain
stable across three formatting passes.


### Files modified

- **UPDATED:** `src/dot_tools/markdown_formatter/parser.py`
- **UPDATED:** `tests/markdown_formatter/test_edge_contract.py`
- **UPDATED:** This implementation journal


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 158 tests.
- `uv run ruff check src tests --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct probes confirmed three-pass stability for hard-break prose, nested list children, blockquoted tables, escaped
  and code-span pipes, and Unicode-width output.


## Execution-review whole-plan repair: C01 secondary task paragraphs 2026-09-03

Repaired task-bearing secondary paragraphs by representing them as typed normalized paragraph blocks. The renderer now
uses the structural child column for those blocks while retaining the task-aware continuation column for first-paragraph
continuation lines. Nested task-item secondary paragraphs follow the same rule, preserving list structure, task state,
source order, LF/CRLF normalization, and three-pass idempotence.

Added exact LF/CRLF regressions for top-level and nested task-bearing secondary paragraphs. HTML handling remains
unchanged and no HTML policy logic was added.


### Verification

- `uv run pytest tests/markdown_formatter --no-cov`: passed, 376 tests.
- `uv run ruff check src/dot_tools/markdown_formatter tests/markdown_formatter --no-fix`: passed.
- `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`: passed.
- Direct LF/CRLF C01 task-secondary and accepted HTML probes passed.
- `git diff --check`: passed.

No plans or execution-review artifacts were edited. No commit was created.

Operations, CLI, wrapper, plans, and review artifacts were not modified. No commit was created.
