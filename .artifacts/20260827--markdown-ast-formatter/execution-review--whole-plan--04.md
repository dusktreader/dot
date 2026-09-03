# Execution Review: Generic AST-based Markdown formatter

This review rechecks the completed formatter worktree against the approved implementation plan, implementation journal,
and prior execution reviews. It starts from the implementation diff and independently probes behavior that the focused
tests do not establish.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--01.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--02.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--03.md`


## Scope

**whole-plan - Iteration 04**

The review covers all formatter production code, CLI and wrapper code, dependency changes, tests, fixtures, and
implementation changes recorded across the journal. The plan, journal, and prior reviews were read but not modified.


## Issue Summary

- **Critical**: 7
- **Significant**: 2
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                                    | Result                                                                                                                                                                 |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                           | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                                                              |
| `uv run pytest tests/markdown_formatter --no-cov`                                   | Passed: 136 tests.                                                                                                                                                     |
| `uv run pytest`                                                                     | Failed: 449 passed, 1 failed. The failure is the independently confirmed unrelated configure assertion about `@opencode-ai/plugin` in `.config/opencode/package.json`. |
| `uv run ruff check src tests`                                                       | Passed: `All checks passed!`                                                                                                                                           |
| `uv run ty check`                                                                   | Failed with 74 diagnostics in unrelated PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears.                                 |
| `uv run dt markdown --help`                                                         | Passed.                                                                                                                                                                |
| `uv run dt markdown format --help`                                                  | Passed.                                                                                                                                                                |
| `uv run dt markdown check --help`                                                   | Passed.                                                                                                                                                                |
| `./.agents/tools/markdown-format.py --help`                                         | Passed.                                                                                                                                                                |
| Wrapper check and format smoke commands on the canonical fixture                    | Both reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                                                                                 |
| `git diff --check`                                                                  | Passed.                                                                                                                                                                |
| Direct inline, container, table, wrapping, fence, span, and replacement-race probes | Failed as described in C01-C07.                                                                                                                                        |

The full pytest failure and Ty diagnostics are excluded from the formatter issue count because both were reproduced
independently and name only unrelated baseline paths. They still mean the literal repository-wide Task 07 quality gate
is not green.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                                                                                       |
| --------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-27`, `uv.lock`, and `uv sync` provide the pinned dependency.                                                                                                                                                                                |
| 01/AC02   | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and the formatter package modules exist.                                                                                                                                                                     |
| 01/AC03   | ⚠      | Public models, signatures, and grouped commands exist. Exact canonical inline, code, container, and operation safety behavior remains broken in C01, C02, C05, and C07. `test_public_models_and_callable_signatures_are_stable` covers only the surface shape. |
| 02/AC01   | ✓      | `frontmatter.py:87-142` exposes extraction, validation, and serialization; `test_frontmatter.py` exercises all three.                                                                                                                                          |
| 02/AC02   | ✓      | `frontmatter.py:87-119` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                                                                                                                                          |
| 02/AC03   | ✓      | Event/node restrictions, duplicate keys, recursive types, invalid Unicode, unsafe tags, and finite-real values pass `test_frontmatter.py` and `test_edge_contract.py`.                                                                                         |
| 02/AC04   | ✓      | `frontmatter.py:142-230` emits sorted quoted mappings, restricted scalars, canonical finite reals, delimiters, blank-line framing, and round-trippable keys.                                                                                                   |
| 03/AC01   | ✗      | The requested AST classes and byte fields exist, but nested container inline spans do not identify the bytes they claim. See C03 and `parser.py:227-259`.                                                                                                      |
| 03/AC02   | ⚠      | CommonMark plus tables and the named node kinds are present, but the bounded scanner is not semantically equivalent for delimiter runs, code spans, or canonical link state. See C01.                                                                          |
| 03/AC03   | ✗      | `_inline_base` and `_reconstruct` can mark a source interval as owned even when its span crosses container prefixes, and table header/separator inline ownership is absent. See C03.                                                                           |
| 03/AC04   | ✗      | `_scan_inline` uses first-closer and first-backtick heuristics rather than parser-proven semantic ownership. The valid `` `a``b` `` case is split into two code nodes and reparses with a different payload. See C01.                                          |
| 03/AC05   | ⚠      | Code ranges and autolinks are masked for tested simple cases, and raw HTML is rejected. The implementation does not have complete parser-owned inline/table code ranges, and the broader canonical inline policy remains incomplete. See C03.                  |
| 03/AC06   | ✓      | `parser.py:483-494` validates immediate downward transitions and records task state at `parser.py:165-168`; focused parser tests cover these paths.                                                                                                            |
| 04/AC01   | ✓      | `normalize.py:16-92` defines the required normalized state, and `test_normalize.py` asserts state without importing rendering.                                                                                                                                 |
| 04/AC02   | ✗      | `normalize.py:341-348` disables wrapping whenever a paragraph contains an inline construct, and the inline codec does not canonicalize all delimiters, destinations, titles, or code semantics. See C01 and C05.                                               |
| 04/AC03   | ✗      | Simple lists pass, but nested code and opaque/container children are not normalized with a stable active prefix. See C02.                                                                                                                                      |
| 04/AC04   | ⚠      | Top-level heading spacing and source-break reuse pass. Nested recognized containers still fail the same local spacing and prefix guarantees. See C02.                                                                                                          |
| 04/AC05   | ✗      | Table normalization handles tested rectangular cases but accepts an all-pipe zero-cell row and does not establish the complete parser-owned semantic cell matrix. See C04.                                                                                     |
| 04/AC06   | ✗      | Payloads and info mapping pass selected cases, but a normal tilde fence remains tilde even though canonical code requires a backtick fence except for the backtick-info fallback. See C06.                                                                     |
| 05/AC01   | ✗      | Top-level LF and final-LF composition passes, but nested containers grow prefixes and code fences across passes. See C02 and C06.                                                                                                                              |
| 05/AC02   | ✗      | Exact code-span, inline, table, nested-container, and canonical fence behavior is not lossless. See C01, C02, C04, and C06.                                                                                                                                    |
| 05/AC03   | ✓      | `__init__.py:10-26` composes frontmatter extraction, parsing, normalization, rendering, and canonical checking, with the tested typed error propagation.                                                                                                       |
| 05/AC04   | ✗      | Golden tests cover representative cases, but the direct failures below are outside their assertions. See S01.                                                                                                                                                  |
| 06/AC01   | ✓      | `operations.py:18-32` resolves operands from CWD, recursively discovers `.md`, sorts, deduplicates, and records explicit invalid operands.                                                                                                                     |
| 06/AC02   | ⚠      | Preparation, atomic temporary files, mode preservation, stop-on-write-error, result completion, and cleanup pass selected tests. The replacement race remains unsafe. See C07.                                                                                 |
| 06/AC03   | ✗      | `_replace` checks the snapshot immediately before `os.replace`, but the check and replacement are not one conditional operation. A mutation in that interval is overwritten and reported as success. See C07.                                                  |
| 06/AC04   | ✓      | `operations.py:93-106` implements the documented status precedence, and contract tests cover input, mismatch, preflight, and partial-write mappings.                                                                                                           |
| 06/AC05   | ⚠      | Normal records, streams, digests, and representative failure mappings pass. The real replacement race and several required edge combinations remain untested or unsafe. See C07 and S02.                                                                       |
| 06/AC06   | ✓      | `markdown-format.py:11-25` captures entry CWD, resolves operands, discovers the repository, delegates normal modes, inherits streams, and returns the child code.                                                                                              |
| 06/AC07   | ⚠      | Registration and smoke/help behavior pass, but the required complete race, wrapper-mode, destination, and semantic edge matrix is not established. See S01 and S02.                                                                                            |
| 07/AC01   | ⚠      | The generic corpus covers the named categories, but it does not protect the direct failures in C01-C07.                                                                                                                                                        |
| 07/AC02   | ⚠      | Ruff passes and formatter tests pass. The repository-wide pytest and Ty commands remain at the independently confirmed unrelated baseline failures noted above.                                                                                                |


## Scope Verification

| File or path                                                            | Justification                                      | Status |
| ----------------------------------------------------------------------- | -------------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                            | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                            | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public contracts                           | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration             | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted frontmatter                     | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing and documented repair passes       | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and documented repair passes | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and documented repair passes     | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operations and atomic replacement          | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                              | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                       | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation                   | ✓      |
| `tests/markdown_formatter/`                                             | Tasks 02 through 07 fixtures and tests             | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                                   | ✓      |

All modified production paths are within the approved formatter, CLI, wrapper, dependency, and registration scope. The
test path is marked ⚠ because it does not protect the direct failures, not because it is out of scope.


## Prior Review Resolution

Review 03 is the immediate predecessor; its findings also consolidate the corresponding finding chains from Reviews 01
and 02.

| Prior finding                                                    | Status | Current evidence                                                                                                                                                                                                                                        |
| ---------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/C01 inline normalization changes CommonMark semantics         | ✗      | The scanner still splits `` `a``b` `` and the normalizer still preserves noncanonical delimiter/destination forms. See `parser.py:268-344` and `normalize.py:95-141`.                                                                                   |
| 03/C02 code and parser boundaries lose valid structure           | ⚠      | Backtick-info fences and autolinks were repaired, but code-span semantic ownership and canonical fence behavior remain broken. See C01 and C06.                                                                                                         |
| 03/C03 nested containers are not lossless or idempotent          | ✗      | List-contained code grows indentation on every pass, nested blockquote fences grow prefixes and fence length, and opaque quote content is rewritten. See C02.                                                                                           |
| 03/C04 snapshot validation is not immediate before replacement   | ✗      | A mutation between the final `_safe_destination` call and `os.replace` is overwritten while the operation returns `SUCCESS`. See C07.                                                                                                                   |
| 03/S01 parser, container, and table edge coverage is missing     | ✗      | The direct failures in C01-C06 remain absent from behavioral assertions. See S01.                                                                                                                                                                       |
| 03/S02 operation safety and CLI edge coverage is incomplete      | ⚠      | A deterministic seam was added, but it mutates before the second check rather than proving protection against mutation in the final check-to-replace interval. Wrapper format delegation and several destination combinations remain untested. See S02. |
| 01/C06 and 02/C08 result and baseline classifications            | ✓      | `operations.py:147-161` now carries prepared output and complete records. The unrelated configure and Ty failures were independently reproduced and still name no formatter path.                                                                       |
| 01/C07 and 02/C07 finite-real and string-key frontmatter defects | ✓      | `frontmatter.py:146-230` and the focused frontmatter tests cover quoted keys, unhashable keys, and finite-real notation.                                                                                                                                |


## Findings

### Summary

| Finding | Title                                                                      | Outcome |
| ------- | -------------------------------------------------------------------------- | ------- |
| C01     | Inline ownership and canonical codecs still change semantics               |         |
| C02     | Recognized nested containers rewrite opaque content and grow on repeat     |         |
| C03     | Nested source spans and table inline ownership are not proven              |         |
| C04     | All-pipe zero-cell tables are accepted and normalized                      |         |
| C05     | Prose containing inline constructs is never wrapped                        |         |
| C06     | Normal tilde fences violate the canonical code-fence contract              |         |
| C07     | Replacement remains vulnerable after the final optimistic check            |         |
| S01     | Focused tests still miss direct semantic and preservation failures         |         |
| S02     | Operation and wrapper edge coverage does not establish the safety contract |         |


### Critical

#### C01: Inline ownership and canonical codecs still change semantics


#### Where

`src/dot_tools/markdown_formatter/parser.py:268-344` and
`src/dot_tools/markdown_formatter/normalize.py:95-141,152-162`


#### Issue

The byte scanner finds the first matching backtick or delimiter instead of using the parser's semantic inline payload
and
delimiter structure. For `# T` followed by `` `a``b` ``, `parse_document` emits two code nodes, `b'`a`'` and `b'`b`'`,
although CommonMark gives one code span with payload `a``b`. Formatting emits `` ```a``````b``` ``, which reparses with
payload `a``````b`. The same codec preserves `__foo__` instead of the required canonical `**foo**`, and preserves an
angle destination such as `[x](<url>)` instead of reducing it to the required bare `url` form. Titles are copied rather
than normalized to the required double-quoted form.


#### Impact

Owned inline syntax changes semantic payloads and does not satisfy canonical delimiter, destination, or title
serialization. This is data loss in a path the formatter claims to own, not an extension that can be safely left opaque.


#### Fix

Build inline state from markdown-it token children and attributes, retaining semantic code payloads, actual delimiter
runs, labels, destinations, and titles. Apply the specified canonical codecs recursively. Mark the entire containing
block
opaque when a semantic source interval cannot be proven, and add semantic-reparse tests for code-run, nested delimiter,
destination, title, escape, and idempotence cases.


#### Outcome


----

#### C02: Recognized nested containers rewrite opaque content and grow on repeat


#### Where

`src/dot_tools/markdown_formatter/normalize.py:165-202,282-353` and
`src/dot_tools/markdown_formatter/render.py:78-145`


#### Issue

List and quote normalization stores child content without a composable active-prefix state. The fixed quote prefix and
list continuation prefix are then applied again during rendering. The formatter changes
`# T\n\n- first\n  ```text\n  x\n  ```\n` to a list whose code payload line is indented four spaces, and a second pass
indents it six spaces. Nested quote fences similarly gain quote markers and fence length on each pass. A parser-marked
opaque quote child is not propagated to the containing quote: `> \x00 opaque\r\n` becomes `> > \x00 opaque\n`.


#### Impact

Recognized list and quote structure is rewritten, opaque bytes are normalized, and output is not idempotent. The
formatter
violates the explicit requirement to preserve a containing block when rewriting a child would alter its source.


#### Fix

Represent the active prefix and content column at every recursive container level. Normalize every owned child against
that state and render each prefix exactly once. If any child is opaque or its source map cannot be composed, preserve
the
complete containing list or quote as `NormalizedOpaque`.


#### Outcome


----

#### C03: Nested source spans and table inline ownership are not proven


#### Where

`src/dot_tools/markdown_formatter/parser.py:131-204,227-259,433-464`


#### Issue

`_inline_base` searches for de-prefixed content inside a source range that still contains container prefixes. For
`# T\n\n> one\n> two\n`, the nested paragraph owns `b"one\ntwo"` but reports `SourceSpan(5, 12)`; the source slice at
that
span is `b"> one\n>"`, not the inline bytes. This is not a parser-proven byte interval. Table construction also ignores
`thead`, `tbody`, `tr`, `th`, and `td` tokens and attaches only the last data-row inline token to the table block.
Header
and separator code therefore have no parser-owned inline nodes; the later raw-HTML pass uses a regular-expression table
workaround instead.


#### Impact

AST consumers cannot trust the promised byte spans or recursively prove ownership. Code-first masking and table semantic
normalization depend on heuristics, so a valid code-looking region can be falsely rejected or an unowned region can be
rewritten.


#### Fix

Derive every nested interval from token maps plus an explicit per-container line-prefix map. Require
`body[span.start:span.end] == node.source` for every owned node. Build table row/cell inline state from parser-owned
cell
tokens, including headers and separators, or preserve the complete table opaque when that proof is unavailable.


#### Outcome


----

#### C04: All-pipe zero-cell tables are accepted and normalized


#### Where

`src/dot_tools/markdown_formatter/normalize.py:205-257`


#### Issue

`_split_row` removes one leading and one trailing pipe from `||` and returns empty cells rather than representing a row
with zero cells. Consequently, `format_document(b"# T\\n\\n||\\n|---|\\n|x|\\n")` succeeds and emits a two-column table.
The approved table contract explicitly treats a row consisting only of framing pipes as zero cells and requires a
`TableError` for a zero-cell header or separator.


#### Impact

Malformed table structure is accepted, assigned a different column count, and rewritten. This violates the fail-closed
table policy and can discard the distinction between framing pipes and empty semantic cells.


#### Fix

Represent framing pipes separately from cell content. Reject a row with no semantic cells before alignment or padding,
and
add exact tests for `|`, `||`, `| |`, all-pipe separators, framing parity, short rows, extra rows, and code-span pipes.


#### Outcome


----

#### C05: Prose containing inline constructs is never wrapped


#### Where

`src/dot_tools/markdown_formatter/normalize.py:144-150,341-348`


#### Issue

Paragraph normalization sends encoded paragraphs containing any code, link, image, emphasis, strong, or hard-break node
straight to the output without wrapping. A paragraph containing 30 ordinary words followed by an inline code span
remains
one line beyond the 120 Unicode code-point limit. The alternative `textwrap.wrap` branch only handles paragraphs with no
recognized inline structure and cannot split ordinary prose around indivisible inline tokens.


#### Impact

The formatter violates the central prose-width rule whenever a paragraph contains an owned inline construct. It also
encourages a later implementation to split syntax if wrapping is added without token-aware measurement.


#### Fix

Wrap a normalized inline token stream. Measure ordinary text in Unicode code points excluding indentation, treat each
code,
link, image, emphasis, and strong node as an indivisible rendered token, preserve hard breaks, and never split an
unbreakable token. Add long mixed-paragraph exact-byte and idempotence tests.


#### Outcome


----

#### C06: Normal tilde fences violate the canonical code-fence contract


#### Where

`src/dot_tools/markdown_formatter/normalize.py:304-329` and
`src/dot_tools/markdown_formatter/render.py:126-138`


#### Issue

Normalization chooses the fence character from the source marker and rendering uses that stored value. A normal source
`~~~text\nx\n~~~` therefore remains a tilde fence. The approved design requires backtick fences for fenced and indented
code,
with a tilde fence only when the info text contains a backtick and a backtick fence cannot represent it.


#### Impact

Canonical code output depends on the input fence spelling, so equivalent documents do not converge to the specified
representation. The tested backtick-info fallback does not establish the normal tilde case.


#### Fix

Always select a collision-safe backtick fence from the payload. Select a tilde fence only for backtick-bearing info,
using
the longest payload tilde run, while preserving payload bytes and the normalized info token. Add exact backtick and
tilde
fixtures for closed, unclosed, CRLF, empty, collision, and info-bearing payloads.


#### Outcome


----

#### C07: Replacement remains vulnerable after the final optimistic check


#### Where

`src/dot_tools/markdown_formatter/operations.py:48-86`


#### Issue

`_replace` performs `_safe_destination`, invokes the no-op `_before_replace` test seam, performs a second
`_safe_destination`, and then calls `os.replace`. The second check is not conditional with the replacement. A probe that
mutates the destination immediately before the `os.replace` call returns `SUCCESS`, commits stale output, and overwrites
the
concurrent bytes. The production no-op seam exists only to make a test observe an otherwise unprotected interval.


#### Impact

The formatter can destroy a concurrent edit while reporting a successful commit. Atomic rename protects readers from a
partial file, but it does not protect the destination identity or content across the check-to-replace race.


#### Fix

Use an operating-system-supported conditional replacement or a synchronization strategy that makes the destination check
and commit one protected operation, and define the behavior when an external writer does not participate. Remove the
production-only no-op test hook. Exercise mutation after the last validation and assert preflight status, untouched
bytes,
commit sets, and cleanup.


#### Outcome


----

### Significant

#### S01: Focused tests still miss direct semantic and preservation failures


#### Where

`tests/markdown_formatter/` and the Task 03 through Task 07 fixture requirements in
`implementation-plan.md:194-418`


#### Issue

The 136-test formatter suite passes while direct probes still fail. Missing behavioral assertions include semantic code
span reparsing, canonical link destinations and titles, mixed emphasis delimiter state, nested list code, opaque quote
propagation, exact nested byte spans, zero-cell tables, mixed inline prose wrapping, normal tilde canonicalization, and
mutation after the final destination validation. Several existing tests assert first-pass equality or idempotence
without
asserting the original semantic payload, so a destructive first rewrite can pass.


#### Impact

The focused green suite does not establish the acceptance criteria and allowed the journal to claim completion while
formatter-owned content, source spans, and safety behavior remain wrong.


#### Fix

Add exact-byte plus semantic-reparse tests for every direct failure above. Assert all `FileResult` fields, stream
records,
exit codes, committed and untouched paths, source-span slices, and three-pass idempotence. Keep malformed or unprovable
cases explicitly opaque or rejected.


#### Outcome


----

#### S02: Operation and wrapper edge coverage does not establish the safety contract


#### Where

`tests/markdown_formatter/test_operations.py`, `test_markdown_cli_contract.py`, `test_wrapper.py`, and
`operations.py:64-86`


#### Issue

The operation race test mutates a later file during a patched `_safe_destination` call, and the final-validation test
mutates during `_before_replace`. Neither proves that production behavior detects a mutation after the last real
validation
and before `os.replace`; the direct replacement probe demonstrates the gap. Wrapper tests exercise only mocked `check`
delegation, not the required mocked `format` delegation, and do not cover the full outside-repository and absolute-path
matrix.


#### Impact

Tests validate the test seam rather than the actual replacement boundary and leave wrapper delegation regressions
possible.
The operation result contract appears complete under mocked failures without establishing real destination safety.


#### Fix

Test both wrapper modes and CWD/project discovery with exact child argv and streams. Use an operations-level replacement
primitive that can be deterministically synchronized without a no-op production hook, then test mutation at the final
validation boundary, symlink/type/mode changes, cleanup, partial commits, and every precedence combination.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction for the review artifact
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C07 must be resolved before approval. S01 and S02 must be addressed in the same pass because the current tests do
not protect the semantic preservation, parser ownership, container, table, wrapping, code-fence, or replacement-safety
contracts. The unrelated configure pytest failure and Ty diagnostics remain excluded from the formatter findings because
they were independently reproduced and do not reference formatter code.
