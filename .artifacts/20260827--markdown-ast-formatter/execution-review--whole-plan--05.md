# Execution Review: Generic AST-based Markdown formatter

This review rechecks the current formatter against the approved implementation plan, the full execution journal, and
execution review 04. It starts from the implementation diff and uses independent semantic, preservation, and operation
probes rather than treating focused test results or journal claims as proof.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--04.md`
- **Earlier reviews**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--01.md` through
  `execution-review--whole-plan--03.md`


## Scope

**whole-plan - Iteration 05**

The review covers the formatter package, document pipeline, grouped CLI, compatibility wrapper, dependency and
registration changes, tests, fixtures, and all implementation changes recorded in the journal. The plan, journal, and
prior reviews were read but not modified.


## Issue Summary

- **Critical**: 7
- **Significant**: 2
- **Trivial**: 0


## Verification Evidence

| Command or probe                                                         | Result                                                                                                                                 |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                              |
| `uv run pytest tests/markdown_formatter --no-cov`                        | Passed: 144 tests.                                                                                                                     |
| `uv run pytest`                                                          | Failed: 457 passed, 1 failed. The failure is the unrelated configure assertion shown below.                                            |
| `uv run ruff check src tests`                                            | Passed: `All checks passed!`                                                                                                           |
| `uv run ty check`                                                        | Failed: 74 diagnostics, all in existing PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears. |
| `uv run dt markdown --help`                                              | Passed.                                                                                                                                |
| `uv run dt markdown format --help`                                       | Passed.                                                                                                                                |
| `uv run dt markdown check --help`                                        | Passed.                                                                                                                                |
| `./.agents/tools/markdown-format.py --help`                              | Passed.                                                                                                                                |
| Wrapper check and format smoke on the canonical fixture                  | Passed. Both reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                                         |
| `git diff --check`                                                       | Passed.                                                                                                                                |
| Independent inline, wrapping, nested-code, table, and replacement probes | Failed as described in C01-C06.                                                                                                        |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The Ty run ends with `Found 74 diagnostics`; its reported files do not include `src/dot_tools/markdown_formatter`,
`src/dot_tools/cli/markdown.py`, or the wrapper. These are known unrelated repository baseline failures, but the literal
repository-wide Task 07 quality gate is not green.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                                 |
| --------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-27`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                                                                                       |
| 01/AC02   | ✓      | The formatter package and public model modules exist under `src/dot_tools/markdown_formatter/`.                                                                                                          |
| 01/AC03   | ⚠      | Public names and grouped commands exist, but inline, nested-code, table, and operation-safety behavior fails in C01-C06.                                                                                 |
| 02/AC01   | ✓      | `frontmatter.py:87-142` exposes extraction, validation, and serialization; focused tests exercise all three.                                                                                             |
| 02/AC02   | ✓      | `frontmatter.py:87-119` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                                                                                    |
| 02/AC03   | ✓      | Event/node restrictions, duplicate keys, recursive types, invalid Unicode, unsafe tags, and finite-real cases pass focused tests.                                                                        |
| 02/AC04   | ⚠      | Scalar and nested serialization pass tested cases, but empty-root framing emits `{}` instead of an empty YAML document. See S01.                                                                         |
| 03/AC01   | ✗      | Requested byte spans exist, but table inline nodes can claim duplicate or non-corresponding source intervals. See C03.                                                                                   |
| 03/AC02   | ✗      | CommonMark parsing is present, but the bounded scanner changes intraword and nested delimiter semantics. See C01.                                                                                        |
| 03/AC03   | ✗      | Exact ownership is not proven for table cells and the scanner's split text nodes can be canonicalized differently on pass two. See C01 and C03.                                                          |
| 03/AC04   | ✗      | `_scan_inline` uses first-closer and special-character heuristics rather than complete CommonMark delimiter ownership. See C01.                                                                          |
| 03/AC05   | ⚠      | Astral-prefix code, ordinary inline code, simple autolinks, and adjacent HTML pass probes, but valid URI autolinks outside the narrow regex are rejected and table code ownership is heuristic. See C03. |
| 03/AC06   | ⚠      | Top-level thematic-break tests pass, but nested task state is lost in a quoted list and unsafe nested structures fall back inconsistently. See C02.                                                      |
| 04/AC01   | ✓      | Normalized state dataclasses exist and `test_normalize.py` asserts state without importing rendering.                                                                                                    |
| 04/AC02   | ✗      | Mixed hard-break prose exceeds 120 code points, list prose is not wrapped, and owned inline semantics change. See C01 and C04.                                                                           |
| 04/AC03   | ✗      | Nested list structure survives simple cases, but list-contained code accumulates indentation and quoted task markers lose state. See C02.                                                                |
| 04/AC04   | ⚠      | Top-level separator insertion is stable, while recursive local spacing depends on opaque fallback and is not established for all recognized containers.                                                  |
| 04/AC05   | ✗      | Tables accept all-pipe rows with semantic zero cells and table cells do not consistently use the canonical inline codec. See C03.                                                                        |
| 04/AC06   | ⚠      | Normal tilde conversion and backtick-info fallback pass, but CommonMark code-span semantics are read from raw delimiters and are not stable for padded payloads. See C05.                                |
| 05/AC01   | ✗      | Canonical LF and final-LF composition passes for simple nodes, but nested list code grows on every pass. See C02.                                                                                        |
| 05/AC02   | ✗      | Inline, nested-container, table, and code-span output is not fully lossless or idempotent. See C01-C05.                                                                                                  |
| 05/AC03   | ⚠      | The package pipeline and typed error propagation are present in `__init__.py:10-26`, but canonical output is wrong for the failed cases.                                                                 |
| 05/AC04   | ✗      | Golden tests cover representative cases but miss the independently reproduced semantic and preservation failures. See S02.                                                                               |
| 06/AC01   | ✓      | `operations.py:20-34` resolves CWD paths, recursively discovers `.md`, sorts, deduplicates, and reports explicit invalid operands.                                                                       |
| 06/AC02   | ⚠      | Preparation, mode preservation, atomic replacement, stop-on-write-error, result completion, and cleanup pass selected cases. External-writer safety remains incomplete. See C06.                         |
| 06/AC03   | ✗      | Snapshot validation is immediate within the cooperating lock, but an uncooperating mutation after validation is overwritten. See C06.                                                                    |
| 06/AC04   | ✓      | `operations.py:107-120` implements the documented status precedence and focused contract tests cover representative mappings.                                                                            |
| 06/AC05   | ⚠      | Records, streams, digests, and representative failures pass, but the real external race and several required edge combinations remain unsafe or untested. See C06 and S02.                               |
| 06/AC06   | ✓      | The wrapper captures entry CWD, resolves absolute operands, discovers the repository, delegates both normal modes, and propagates child status.                                                          |
| 06/AC07   | ⚠      | Registration and smoke/help behavior pass, but the complete wrapper, destination, race, and semantic edge matrix is not established. See S02.                                                            |
| 07/AC01   | ⚠      | The corpus covers the named categories at a representative level but does not protect C01-C06 or the empty-root case.                                                                                    |
| 07/AC02   | ✗      | Ruff passes, but formatter correctness fails C01-C06 and the repository-wide pytest and Ty gates remain at the unrelated baseline failures. See C07.                                                     |


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
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operations and replacement safety          | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                              | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                       | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation wrapper           | ✓      |
| `tests/markdown_formatter/`                                             | Tasks 02 through 07 focused tests and fixtures     | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                                   | ✓      |

All modified production paths are within the approved formatter, CLI, wrapper, dependency, and registration scope. The
test path is marked partial because it does not establish the required edge matrix, not because it is out of scope.


## Prior Review Resolution

| Review 04 finding                                                   | Status | Current evidence                                                                                                                                                                                                                       |
| ------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Inline ownership and canonical codecs change semantics          | ✗      | `foo_bar_baz` changes to `foo _bar _baz`, then changes again on pass two; nested emphasis also changes structure. See C01.                                                                                                             |
| C02 Recognized nested containers rewrite opaque content or grow     | ⚠      | Simple quote/list cases improved, but list-contained code grows indentation on every pass and quoted task state is lost. See C02.                                                                                                      |
| C03 Nested source spans and table inline ownership are not proven   | ✗      | Repeated table cell text receives duplicate spans, and separator cells have no parser-owned inline representation. See C03.                                                                                                            |
| C04 All-pipe zero-cell tables are accepted                          | ✗      | `|||` is still accepted as a two-column table instead of failing closed. See C03.                                                                                                                                                      |
| C05 Prose containing inline constructs is not wrapped               | ✗      | Mixed atom wrapping exists, but hard-break paragraphs and list prose exceed the 120-code-point rule. See C04.                                                                                                                          |
| C06 Normal tilde fences violate the canonical contract              | ✓      | Normal `~~~text` inputs converge to backticks, and backtick-bearing info uses a collision-safe tilde fence.                                                                                                                            |
| C07 Replacement remains vulnerable after the final optimistic check | ✗      | A mutation injected immediately before `os.replace` is overwritten and the operation returns `SUCCESS`. See C06. The cooperating advisory-lock limitation is explicit but does not satisfy an unconditional external-writer guarantee. |
| S01 Focused tests miss direct semantic and preservation failures    | ✗      | The 144-test suite still does not assert intraword text, nested delimiter semantics, hard-break wrapping, list code idempotence, all-pipe rows, empty-root framing, or an uncooperating race. See S02.                                 |
| S02 Operation and wrapper edge coverage is incomplete               | ⚠      | Destination lock and failure tests were added, but wrapper tests still exercise only mocked `check` delegation and no test establishes the external race boundary. See S02.                                                            |


## Findings

### Summary

| Finding | Title                                                                  | Outcome |
| ------- | ---------------------------------------------------------------------- | ------- |
| C01     | Inline scanning and codecs still change valid CommonMark semantics     |         |
| C02     | List-contained code and nested task state are not lossless             |         |
| C03     | Table ownership and zero-cell validation are incomplete                |         |
| C04     | 120-code-point wrapping stops at hard breaks and lists                 |         |
| C05     | Code-span normalization does not use the semantic payload              |         |
| C06     | Advisory locking does not prevent an external post-check overwrite     |         |
| C07     | Repository-wide quality gates remain red on the known baseline         |         |
| S01     | Empty frontmatter roots do not use the approved empty-document framing |         |
| S02     | Tests do not establish the complete approved contract                  |         |


### Critical

#### C01: Inline scanning and codecs still change valid CommonMark semantics


#### Where

`src/dot_tools/markdown_formatter/parser.py:337-413` and `src/dot_tools/markdown_formatter/normalize.py:95-137`


#### Issue

The scanner stops text runs at every backtick, bracket, exclamation mark, asterisk, underscore, or backslash, then
claims delimiters with a first-closer heuristic. An unrecognized intraword underscore is therefore split into separate
text nodes and the wrapping path inserts spaces between those nodes. Independent probes produce:

```text
foo_bar_baz -> foo _bar _baz -> foo *bar * baz
***foo***bar -> ***foo** *bar
**foo__bar__** -> **foo**bar****
```

The first input is not emphasis in CommonMark. The latter inputs have different delimiter structure after formatting.
The output can be stable after it has already been corrupted, so the existing idempotence assertions do not prove
semantic preservation.


#### Impact

Owned inline text and nested emphasis/strong content change meaning. This violates parser ownership, the inline codec,
canonical output, and the no-data-loss requirement in Tasks 03 through 05.


#### Fix

Build inline state from markdown-it child tokens and semantic attributes, or preserve the complete containing block when
those semantics cannot be associated with a proven byte interval. Make ordinary unrecognized punctuation part of one
text atom, apply delimiter-flanking rules, and recursively encode the proven child structure. Add semantic reparse tests
for intraword delimiters, mixed delimiter runs, nested emphasis, escapes, repeated text, and second-pass output.


#### Outcome


----

#### C02: List-contained code and nested task state are not lossless


#### Where

`src/dot_tools/markdown_formatter/normalize.py:205-242,331-377` and
`src/dot_tools/markdown_formatter/render.py:91-104`


#### Issue

List child blocks are normalized with an empty prefix, even though their source includes the active list indentation.
The renderer then applies the continuation column without first removing the source prefix from code payload lines. A
direct three-pass probe shows:

```text
source: - first / two-space fenced code containing x
pass 1: the payload line has four leading spaces
pass 2: the payload line has six leading spaces
pass 3: the payload line has eight leading spaces
```

The same path loses task state inside a quoted nested list: `> - [ ] task` formats as `> - task`. The parser's task
regular expression only recognizes a marker at the beginning of the raw list-item source, not after a block-quote
prefix.


#### Impact

Repeated formatting changes code payload bytes and eventually changes block interpretation. Nested task semantics are
discarded. This violates recursive list columns, code-payload preservation, task state, and idempotence.


#### Fix

Carry a composed active prefix and content column through every list and quote level. Strip exactly the structural
prefix
from owned child source before normalization, render it exactly once, and recognize task markers from parser-owned list
item tokens after container prefixes are accounted for. If the prefix cannot be proven, preserve the complete containing
list as opaque.


#### Outcome


----

#### C03: Table ownership and zero-cell validation are incomplete


#### Where

`src/dot_tools/markdown_formatter/parser.py:135-151,299-316` and
`src/dot_tools/markdown_formatter/normalize.py:245-328`


#### Issue

The parser drops table row and cell events, then attaches each inline token by searching its content from the beginning
of
the whole physical row. For repeated cells, two header nodes can both claim the first occurrence. For example, a header
containing `x` and `x` yields two nodes with the same `SourceSpan`; separator cells have no parser-owned inline nodes at
all. Normalization consequently relies on raw row rescanning rather than the promised parser-proven semantic cell state.

The zero-cell check only rejects `|` and `||`. An all-pipe header such as `|||` is accepted and reformatted as a table
with
two empty columns, although it has no semantic cell content and the approved contract requires framing-only rows to fail
closed.

Table cells also bypass the full inline codec for links and images in `_table_inline`, so a table cell such as a link
with
an angle destination is not canonicalized the same way as an ordinary paragraph cell.


#### Impact

AST consumers cannot trust table source spans. Code-first HTML masking and table semantics depend on heuristics,
malformed
all-pipe structures are rewritten, and table cells can diverge from document inline canonicalization.


#### Fix

Represent table rows and cells explicitly from parser token positions, including header and separator ownership, and
require every claimed span to slice the original bytes. Reject every framing-only all-pipe row before padding. Reuse the
same recursive inline encoder in cells, apply backslash parity only to semantic literal pipes, measure escaped Unicode
width, and add repeated-cell, separator, link, code-pipe, all-pipe, and parity tests.


#### Outcome


----

#### C04: 120-code-point wrapping stops at hard breaks and lists


#### Where

`src/dot_tools/markdown_formatter/normalize.py:140-145,205-242,404-428`


#### Issue

`_wrap_inline` returns the entire encoded paragraph as soon as it sees any newline. That makes a paragraph with ordinary
prose on both sides of a hard break exempt from wrapping. A direct probe with 35 words on each side produces lines of
175
and 174 Unicode code points. List item content is never passed through `_wrap_inline`; a 40-word list item produces a
single line over 200 code points.


#### Impact

The central 120-code-point formatting rule is violated for valid owned prose. The failure occurs precisely where the
plan
requires hard breaks and active list indentation to be handled without splitting inline atoms.


#### Fix

Tokenize and wrap each hard-break-delimited prose segment independently, retaining exactly one canonical backslash plus
LF at the break. Apply the same token-aware wrapping to list-item paragraphs with the available content width measured
without structural indentation, and leave unbreakable atoms intact.


#### Outcome


----

#### C05: Code-span normalization does not use the semantic payload


#### Where

`src/dot_tools/markdown_formatter/normalize.py:148-158` and `src/dot_tools/markdown_formatter/parser.py:357-364`


#### Issue

`_inline_code` derives the payload by slicing raw source delimiters instead of using the parser's semantic code-inline
content. For input with two padding spaces on both sides of `x`, the first pass emits a code span containing one space
on
each side, while the second pass trims those spaces and emits a different span. The direct output is:

```text
input:  `  x  `
pass 1: ``` x ```
pass 2: ```x```
```

The implementation also does not recover parser text for the empty inline-code boundary represented by a two-backtick
source, even though the approved fixture contract requires a canonical empty payload representation.


#### Impact

Valid code-span payloads are not canonicalized from CommonMark semantics and are not idempotent. This violates the exact
empty, padding, newline, and backtick-boundary cases in Task 04 and Task 05.


#### Fix

Retain markdown-it's semantic code-inline content and actual delimiter run in the parser model. Normalize internal LF
and
CRLF, apply the exact one-space trimming rule to that semantic payload, choose the collision-safe fence, and verify that
reparsing recovers the same payload for every required boundary fixture.


#### Outcome


----

#### C06: Advisory locking does not prevent an external post-check overwrite


#### Where

`src/dot_tools/markdown_formatter/operations.py:66-100,178-207`


#### Issue

The destination lock serializes formatter writers that explicitly take the same lock, and `_replace` performs a final
snapshot check under that lock. The check and `os.replace` are still separate operations. A process that does not honor
the
lock can mutate the destination after `_safe_destination` returns and before `os.replace`. An independent probe injected
that mutation at the replacement boundary; `format_paths` returned `SUCCESS`, reported `FORMATTED`, and overwrote the
concurrent bytes.

The journal correctly states that this is an advisory lock for cooperating writers. That limitation is honest, but it
does
not satisfy the plan's unconditional immediate-comparison and fail-safe replacement contract for arbitrary external
writers.


#### Impact

A concurrent edit can be destroyed while the operation reports a successful commit. Atomic rename prevents torn reads
but
does not provide compare-and-swap protection for the pathname.


#### Fix

Either provide an operating-system-level conditional replacement strategy, or narrow the approved contract explicitly to
cooperating writers and make the resulting limitation part of the public safety guarantee. In either case, retain a real
boundary test that distinguishes a cooperating lock holder from an uncooperating mutation and reports the documented
behavior accurately.


#### Outcome


----

#### C07: Repository-wide quality gates remain red on the known baseline


#### Where

The project commands in `implementation-plan.md:16-73` and the independent verification run above.


#### Issue

The required full pytest command fails on the existing OpenCode plugin manifest assertion, and the required Ty command
reports 74 diagnostics in unrelated repository paths. The exact pytest assertion is recorded in Verification Evidence.
The focused formatter suite and Ruff pass, but the plan's literal full quality gate is not green.


#### Impact

Task 07/AC02 cannot be marked fully satisfied in this worktree. The failures are not attributed to the formatter, but
they
must remain visible rather than being presented as a clean repository gate.


#### Fix

Resolve or formally baseline the unrelated configure and Ty failures in repository quality policy before claiming a
green
whole-repository gate. No formatter production change is indicated by this finding.


#### Outcome


### Significant

#### S01: Empty frontmatter roots do not use the approved empty-document framing


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:167-201`


#### Issue

The approved design says an empty frontmatter root emits an empty YAML document between the delimiters. The serializer
currently routes `{}` through the generic mapping branch and emits:

```text
---
{}
---

```

That is a flow empty mapping value, not an empty YAML document. Formatting a document beginning with an empty
frontmatter
envelope therefore inserts a new content line instead of preserving the approved canonical framing. Existing tests only
exercise extraction of an empty envelope and do not assert serialized root bytes.


#### Impact

Valid empty-root frontmatter does not converge to the specified exact byte representation, and the serializer contract
is
not fully covered.


#### Fix

Special-case an empty root in `serialize_frontmatter` to emit the approved delimiter-only YAML document while continuing
to
emit `{}` and `[]` for empty nested mapping and sequence values. Add an exact formatting and round-trip fixture.


#### Outcome


----

#### S02: Tests do not establish the complete approved contract


#### Where

`tests/markdown_formatter/` and the Task 03 through Task 07 fixture requirements in `implementation-plan.md:194-418`


#### Issue

The focused suite passes, but it does not catch the direct failures in C01-C06 or S01. Missing or insufficient
assertions
include semantic reparsing of intraword and nested delimiters, list-contained code payloads, quoted task state, all-pipe
tables, table repeated-cell spans, hard-break/list wrapping, padded code spans, empty-root framing, and mutation by an
uncooperating writer. The wrapper test exercises mocked `check` delegation only, not mocked `format` delegation or the
complete outside-repository and absolute-path matrix. The test named
`test_zero_file_operation_is_success_with_empty_records` actually supplies an explicit missing path and expects
`INPUT_ERROR`, so it does not test zero discovery.


#### Impact

Passing tests provide false confidence and allow destructive first-pass rewrites to appear compliant when a second pass
only stabilizes the already-corrupted output. The journal's formatter-scoped completion claim is not supported by the
behavioral evidence.


#### Fix

Add exact-byte plus semantic-reparse tests for every direct failure and three-pass idempotence for recursive containers.
Assert every `FileResult` field, stream, status, digest, commit/untouched set, and cleanup result. Add both wrapper
modes,
project discovery, CWD, destination-type, and external-writer tests, and replace the misleading zero-file test with a
true
empty-directory case.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction for the review artifact
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C06 must be resolved before approval. C07 is an unrelated but still blocking repository-wide quality-gate failure.
S01 and S02 must be addressed in the same pass because the current tests do not protect the frontmatter, semantic
inline,
recursive-container, table, wrapping, code-span, or operation-safety contracts. The advisory-lock limitation must be
resolved as a contract decision, not hidden behind the cooperating-writer test.
