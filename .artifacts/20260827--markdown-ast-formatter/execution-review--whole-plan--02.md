# Execution Review: Generic AST-based Markdown formatter

This review rechecks the complete formatter worktree against the approved generic implementation plan, the execution
journal, and the first execution review. It starts from the current diff and independently probes the formatter paths.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--01.md`


## Scope

**whole-plan - Iteration 02**

The review covers all formatter production code, CLI and wrapper code, tests, fixtures, dependency changes, and current
worktree changes recorded across the journal. The plan, journal, and prior review were read but not modified.


## Issue Summary

- **Critical**: 9
- **Significant**: 1
- **Trivial**: 0


## Verification Evidence

| Command                                                                                                      | Result                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                    | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                                                      |
| `uv run pytest tests/markdown_formatter --no-cov`                                                            | Passed: 111 tests. This does not cover the failed probes below.                                                                                                |
| `uv run pytest`                                                                                              | Failed: 424 passed, 1 failed. The failure is the documented unrelated configure assertion about `@opencode-ai/plugin` in `.config/opencode/package.json`.      |
| `uv run ruff check src tests`                                                                                | Passed: `All checks passed!`                                                                                                                                   |
| `uv run ty check`                                                                                            | Failed with 74 diagnostics in the documented unrelated Markdown PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears. |
| `uv run dt markdown --help`                                                                                  | Passed and lists the `format` and `check` subcommands.                                                                                                         |
| `uv run dt markdown format --help`                                                                           | Passed and accepts `PATH`.                                                                                                                                     |
| `uv run dt markdown check --help`                                                                            | Passed and accepts `PATH`.                                                                                                                                     |
| `./.agents/tools/markdown-format.py --help`                                                                  | Passed through `dt markdown --help`.                                                                                                                           |
| `./.agents/tools/markdown-format.py check tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`  | Passed with `UNCHANGED` and `summary check SUCCESS 1`.                                                                                                         |
| `./.agents/tools/markdown-format.py format tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md` | Passed with `UNCHANGED` and `summary format SUCCESS 1`.                                                                                                        |
| `git diff --check`                                                                                           | Passed.                                                                                                                                                        |
| Direct parser, normalization, rendering, frontmatter, and operation probes                                   | Failed as described in C01-C09.                                                                                                                                |

The full pytest configure failure and Ty diagnostics are baseline failures explicitly excluded from formatter findings.
The formatter-specific focused suite and Ruff pass do not establish the complete plan because several required edge
paths
fail outside the current tests.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                          |
| --------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-27`, `uv.lock`, and the successful `uv sync` run pin `markdown-it-py==4.2.0`.                                                                                                  |
| 01/AC02   | ✓      | The package modules and public models exist under `src/dot_tools/markdown_formatter/`; `models.py:8-66`.                                                                                          |
| 01/AC03   | ✗      | Public signatures and the grouped CLI exist, but formatted `FileResult.output` violates the exact contract at `operations.py:141-143`; see C08.                                                   |
| 02/AC01   | ✓      | `frontmatter.py:84-139` exposes extraction, validation, and serialization APIs; `test_frontmatter.py` exercises them.                                                                             |
| 02/AC02   | ✓      | `frontmatter.py:84-99` enforces byte-zero opening, exact closing lines, missing-close failure, and body-byte preservation.                                                                        |
| 02/AC03   | ✗      | YAML event and node restrictions exist, but unhashable mapping keys escape as `TypeError` and accepted string keys are emitted as invalid YAML; see C07.                                          |
| 02/AC04   | ✗      | Finite-real examples pass, but `serialize_frontmatter({"a: b": 1})` emits a document that cannot be reparsed; see C07.                                                                            |
| 03/AC01   | ⚠      | Byte-addressed spans and the requested AST dataclasses exist, but code masking converts between byte and character units incorrectly for astral text; see C01.                                    |
| 03/AC02   | ⚠      | CommonMark plus table parsing and basic block ownership work, but the inline scanner does not implement the required CommonMark delimiter and destination behavior; see C02.                      |
| 03/AC03   | ✗      | The scanner and reconstruction are not sufficient to prove semantic ownership, and code ranges are not reliably masked; see C01 and C02.                                                          |
| 03/AC04   | ✗      | `parser.py:226-292` claims intraword underscores and fails to recognize two-space hard breaks, while wrapping later splits owned spans; see C02 and C03.                                          |
| 03/AC05   | ✗      | Code-looking HTML with an astral prefix and code in table header cells raises `RawHtmlError`; see C01.                                                                                            |
| 03/AC06   | ✓      | Thematic breaks require an immediately following lower-level heading in the same block sequence at `parser.py:419-430`; parser tests cover all three spellings and intervening-body rejection.    |
| 04/AC01   | ✓      | Normalized state dataclasses and AST-only tests exist at `normalize.py:16-91` and `test_normalize.py`.                                                                                            |
| 04/AC02   | ✗      | Inline syntax is altered and long inline code is wrapped as prose at `normalize.py:314-318`; see C02 and C03.                                                                                     |
| 04/AC03   | ✗      | Basic nested markers now survive, but additional list paragraphs and block-quote children are silently dropped; see C04.                                                                          |
| 04/AC04   | ⚠      | Basic top-level separators are stable, but active container prefixes and recognized nested containers are not preserved; see C04.                                                                 |
| 04/AC05   | ✗      | Table code-span pipes work for the tested case, but even backslash parity before a framing pipe is misclassified; see C06.                                                                        |
| 04/AC06   | ✗      | Normalized fence state works for closed examples, but an unclosed fenced block loses its payload; see C05.                                                                                        |
| 05/AC01   | ✗      | LF composition and final-newline behavior work for simple nodes, but rendering is fed incomplete code and container state; see C04 and C05.                                                       |
| 05/AC02   | ✗      | Exact inline, list, table, and code rendering is not lossless or fully idempotent; see C02-C06.                                                                                                   |
| 05/AC03   | ⚠      | `__init__.py:10-26` has the intended pipeline and typed parser errors, but canonical output is wrong for the failed cases.                                                                        |
| 05/AC04   | ✗      | The golden tests cover 13 basic document/render cases, not the required failing edge matrix; see C10.                                                                                             |
| 06/AC01   | ✓      | `operations.py:18-32` resolves CWD paths, recursively discovers Markdown files, sorts, deduplicates, and records explicit invalid operands.                                                       |
| 06/AC02   | ✗      | The implementation prepares files and uses atomic replacement, but it does not revalidate snapshots immediately before replacement; see C09.                                                      |
| 06/AC03   | ✗      | Snapshot capture exists, but the safety comparison occurs in one preflight pass before the commit loop; see C09.                                                                                  |
| 06/AC04   | ✗      | Mismatch and failure records are mostly complete, but `FORMATTED` results have no required canonical `output`; see C08.                                                                           |
| 06/AC05   | ⚠      | Basic records, streams, digest diagnostics, and exit mapping pass, but uncovered races and failure records cannot establish the full contract; see C08-C10.                                       |
| 06/AC06   | ✓      | `markdown-format.py:11-25` delegates normal `format` and `check` modes to `uv run --project <repo> dt markdown ...`, captures entry CWD once, passes absolute operands, and returns child status. |
| 06/AC07   | ⚠      | Registration and smoke/help tests pass, but the required destination-race and edge contract matrix is incomplete; see C10.                                                                        |
| 07/AC01   | ⚠      | The generic corpus exists and covers basic headings, lists, tables, code, opaque blocks, and multi-file behavior, but it does not cover the required failed edge cases; see C10.                  |
| 07/AC02   | ⚠      | Ruff passes; formatter tests pass; the full pytest configure failure and Ty diagnostics are the documented unrelated baseline. Formatter behavior itself remains blocked by C01-C09.              |


## Scope Verification

| File or path                                                            | Justification                                      | Status |
| ----------------------------------------------------------------------- | -------------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                            | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                            | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public contracts                           | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration             | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML                            | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing and documented repair passes       | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and documented repair passes | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and documented repair passes     | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operations and atomic replacement          | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                              | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                       | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation                   | ✓      |
| `tests/markdown_formatter/`                                             | Tasks 02 through 07 fixtures and tests             | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                                   | ✓      |

No unrelated production subsystem or profile-specific formatter behavior was introduced. The wrapper and grouped CLI use
the requested `dt markdown format` and `dt markdown check` command shapes. No formatter source imports or invokes
Zensical, stale profiles, or the old standalone command implementation.


## Prior Review Resolution

- **Prior C01** ⚠: The specific false-opaque reconstruction bug is fixed. `parser.py:361-372` reconstructs child slices
  from `child_source`, and `test_parser.py:80-90` proves the listed links, images, emphasis, and repeated-text cases.
  The scanner still violates CommonMark semantics in new C02.
- **Prior C02** ✗: `parser.py:381-400` still fails to mask code ranges with astral text before raw-HTML scanning, and
  table header code is not represented in `block.inline`. See C01.
- **Prior C03** ⚠: Simple recursive list markers and one-line continuations now survive through `normalize.py:159-184`,
  but multiple paragraphs, list-item block quotes, and nested quote prefixes are still dropped or duplicated. See C04.
- **Prior C04** ⚠: Code-span pipes and the tested odd backslash case are preserved, but `_split_row` only recognizes one
  escaped trailing backslash at `normalize.py:187-215`; an even run before a framing pipe fails. See C06.
- **Prior C05** ✓: Valid tilde-fence info and stored fence state now flow through `parser.py:175-181`,
  `normalize.py:285-302`, and `render.py:107-110`; the prior `~~~bash` corruption is gone. Unclosed payload handling
  remains a new C05 defect.
- **Prior C06** ⚠: Mismatch output is now `None` and failure result lists are complete in the tested paths, but the
  original public contract also requires canonical replacement bytes in every `FORMATTED` result. See C08.
- **Prior C07** ✓: The tested finite-real values and threshold notation now round-trip through `frontmatter.py:200-226`
  and the frontmatter tests. This review found a separate accepted-string-key serialization defect in C07.
- **Prior C08** ✓ as a baseline classification: the unrelated configure failure and 74 unrelated Ty diagnostics
  reproduce; no formatter path is named. They are excluded from the issue count per the review request.
- **Prior C09** ⚠: Contract modules and edge tests were added, but they do not exercise the failed astral masking,
  inline semantics, unclosed fence, multi-paragraph list, arbitrary trailing backslash parity, accepted-key
  serialization, immediate snapshot race, or formatted-output semantics. See C10.
- **Prior S01** ✓: `parser.py:422-429` now requires the immediate next block to be a lower-level heading and records
  only that transition. The positional parser tests pass.
- **Prior S02** ⚠: Heading state is container-local for basic block quotes, but `normalize.py:258-323` ignores the
  active `prefix` argument and `render.py:115-117` composes nested prefixes incorrectly. See C04.


## Findings

### Summary

| Finding | Title                                                                       | Outcome |
| ------- | --------------------------------------------------------------------------- | ------- |
| C01     | Code masking uses character indexes as byte offsets                         |         |
| C02     | Inline scanning changes CommonMark semantics and rejects valid destinations |         |
| C03     | Prose wrapping splits owned inline constructs                               |         |
| C04     | Recognized list and quote children are silently lost or re-prefixed         |         |
| C05     | Unclosed fenced code loses its payload                                      |         |
| C06     | Table backslash parity misclassifies framing pipes                          |         |
| C07     | Restricted frontmatter accepts values it cannot serialize safely            |         |
| C08     | `FORMATTED` results omit required replacement bytes                         |         |
| C09     | Snapshot validation is not immediate before replacement                     |         |
| S01     | Required edge and contract coverage still does not test the failing paths   |         |


### Critical

#### C01: Code masking uses character indexes as byte offsets


#### Where

`src/dot_tools/markdown_formatter/parser.py:381-400`


#### Issue

`_char_offset` returns a character index from a byte offset, but `_reject_raw_html` passes that character index back to
`_offset_index`, which expects a byte offset. The conversion works for ASCII and fails when an astral character occurs
before the code range. Table header inline code is also absent from the block's inline nodes, so it is never added to
the
mask.


#### Impact

Valid HTML-looking content in inline, fenced, indented, or table code is rejected instead of remaining code. For
example,
both `format_document(b"# 😀\n\n`<div>`\n")` and the equivalent fenced and indented cases raise `RawHtmlError`. A table
with `` ` <x> ` `` in its header also raises `RawHtmlError`. This violates the code-first raw-HTML policy and makes
astral source content behavior depend on its position.


#### Fix

Use one shared UTF-8 byte-to-character index and apply it exactly once, or mask byte ranges before decoding. Collect
code
ranges from every parser-owned inline cell and code block, including table header and separator content, before running
the HTML scan. Add astral-prefix tests for every code form and table cells.


#### Outcome


----

#### C02: Inline scanning changes CommonMark semantics and rejects valid destinations


#### Where

`src/dot_tools/markdown_formatter/parser.py:226-292`, `src/dot_tools/markdown_formatter/normalize.py:94-135`, and
`src/dot_tools/markdown_formatter/parser.py:399-400`


#### Issue

The byte scanner treats every matching `_` pair as emphasis, including intraword underscores that CommonMark leaves as
text. It does not claim a two-space hard break because the text fast path consumes the spaces and newline before the
hard-break branch runs. Link and image destinations are copied from the original node rather than rendered with the
required bare-versus-angle and escaping rules. The raw-HTML regex then rejects valid angle destinations such as
`[x](<url with space>)` because it sees `<url` outside the code mask.


#### Impact

`format_document(b"# T\n\nfoo_bar_baz\n")` changes ordinary text to `foo*bar*baz`, and
`format_document(b"# T\n\nfoo  \nbar\n")` produces `foo   bar` instead of a canonical hard break. A valid angle
destination raises `RawHtmlError`. These are semantic changes and policy false positives in the owned inline subset.


#### Fix

Implement CommonMark delimiter-flanking rules, test hard-break precedence before the text run, and encode link/image
labels, destinations, and titles from semantic state. Exclude parser-identified valid autolinks and angle destinations
from raw-HTML rejection while continuing to reject actual HTML nodes.


#### Outcome


----

#### C03: Prose wrapping splits owned inline constructs


#### Where

`src/dot_tools/markdown_formatter/normalize.py:314-318`


#### Issue

Paragraph normalization first produces Markdown bytes containing inline delimiters, decodes them as plain text, and
passes
the result to `textwrap.wrap`. It has no awareness of code spans, links, emphasis, or strong nodes and can insert a
newline
inside any of them.


#### Impact

A long inline code span is split into two lines. The next formatting pass reparses the split bytes as separate structure
and drops the remainder. A direct probe with a 40-word code span produced a first output containing two partial lines
and
a second output containing only an empty fenced block. This violates no-splitting, semantic preservation, and
idempotence.


#### Fix

Wrap a normalized inline token stream, not already-rendered Markdown bytes. Treat each code span, link, image, emphasis,
and strong node as an indivisible token while measuring ordinary text in Unicode code points. Add long-span exact-byte
and
second-pass tests.


#### Outcome


----

#### C04: Recognized list and quote children are silently lost or re-prefixed


#### Where

`src/dot_tools/markdown_formatter/normalize.py:159-184`, `src/dot_tools/markdown_formatter/normalize.py:258-323`, and
`src/dot_tools/markdown_formatter/render.py:78-117`


#### Issue

`_list` selects only the first paragraph in each list item and only recursively normalizes list children. Additional
paragraphs and block quotes are discarded. The `prefix` argument is unused during normalization, while each nested
`NormalizedContainer` adds a fixed `b"> "` during rendering. The active prefix is therefore not composed across nested
containers.


#### Impact

`- first` followed by an indented second paragraph formats to only `- first`. A list-item block quote disappears, and
`> > text` formats to `> > > text`. The formatter silently changes recognized document structure, continuation columns,
and
container-local heading behavior instead of preserving or falling back to the containing block.


#### Fix

Normalize every owned block child in list items, including continuation paragraphs and block quotes, with an explicit
active-prefix state. If lazy continuation ownership is not proven, preserve the complete containing list as opaque.
Compose
prefixes recursively and add tests for multiple paragraphs, list-item quotes, nested quotes, and headings inside them.


#### Outcome


----

#### C05: Unclosed fenced code loses its payload


#### Where

`src/dot_tools/markdown_formatter/normalize.py:280-302`


#### Issue

Fenced payload extraction unconditionally uses `lines[1:-1]`, assuming the final source line is a closing fence.
CommonMark
can produce a fenced-code token for an unclosed fence. In that case the final line is payload, not a close marker, and
this
slice drops it.


#### Impact

`format_document(b"# T\n\n```text\npayload\n")` returns a `text` fence with an empty payload. The formatter loses user
code and violates the unconditional
code-payload preservation rule.


#### Fix

Use parser token metadata or verify an actual closing fence before removing the final line. Preserve all payload bytes
for
an unclosed token, then choose a collision-safe canonical closing fence and add closed and unclosed payload tests with
trailing spaces and CRLF.


#### Outcome


----

#### C06: Table backslash parity misclassifies framing pipes


#### Where

`src/dot_tools/markdown_formatter/normalize.py:187-215`


#### Issue

The trailing-framing check only excludes a pipe ending in exactly one backslash with `not line.endswith(b"\\|")`. It
does
not apply the required backslash-parity rule. A trailing pipe preceded by an even run is a framing pipe, but the scanner
leaves it in the row and then treats it as a delimiter, creating an extra cell.


#### Impact

A valid one-column table with a literal backslash before its trailing framing pipe, for example
`| a\\\\|` after the header and separator, raises `TableError: table row has too many cells` instead of preserving the
cell. This violates the arbitrary backslash-run, framing, and lossless-table requirements.


#### Fix

Count the complete trailing backslash run and remove the pipe as framing only when its parity makes the pipe structural.
Apply the same semantic parity algorithm to internal literal pipes, measure widths after escaping, and add exact
fixtures
for zero through several backslashes immediately before both internal and trailing pipes.


#### Outcome


----

#### C07: Restricted frontmatter accepts values it cannot serialize safely


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:29-36` and `src/dot_tools/markdown_formatter/frontmatter.py:164-179`


#### Issue

The restricted loader tests `if key in result` without converting an unhashable YAML key failure into
`FrontmatterError`.
The serializer writes mapping keys with raw `f"{key}:"` text instead of the string scalar codec. String keys containing
YAML syntax are allowed by `validate_frontmatter` but can produce invalid YAML or change the root type on the next
parse.


#### Impact

`extract_frontmatter(b"---\n? [a]\n: b\n---\n# T\n")` raises a raw `TypeError` rather than the required
`FrontmatterError`. `serialize_frontmatter({"a: b": 1})` emits `a: b: 1`, which cannot be reparsed, and a key such as
`"true"` is emitted as a boolean-looking key. The accepted string-key envelope is therefore not safe, lossless, or
idempotent.


#### Fix

Catch unhashable-key construction failures and raise `FrontmatterError`. Serialize keys through the same quoted string
codec as values, preserving Unicode and control escaping, then add round-trip tests for colon, newline, boolean-looking,
empty, and Unicode keys.


#### Outcome


----

#### C08: `FORMATTED` results omit required replacement bytes


#### Where

`src/dot_tools/markdown_formatter/operations.py:134-148`


#### Issue

`_complete_results` constructs every prepared file as `FileResult(..., status=FORMATTED, snapshot=snapshot)` without
assigning the prepared `output` bytes. The plan explicitly requires `FORMATTED` to carry canonical replacement bytes,
while only `UNCHANGED` and `MISMATCH` have `output=None`.


#### Impact

Consumers cannot inspect the canonical result of a successful format operation, and committed versus untouched prepared
files are indistinguishable from an incomplete result. The current test `test_operations.py:80-82` asserts `output is
None`
for all partial-write records, confirming the tests encode the wrong contract rather than catching it.


#### Fix

Carry prepared output into the `FORMATTED` `FileResult` for every prepared path, including committed and later untouched
records after a write failure. Keep `output=None` only for `UNCHANGED`, `MISMATCH`, and error statuses, and assert the
exact field matrix in the contract tests.


#### Outcome


----

#### C09: Snapshot validation is not immediate before replacement


#### Where

`src/dot_tools/markdown_formatter/operations.py:157-177`


#### Issue

The implementation checks `_safe_destination` for every prepared file in one preflight loop, then starts a separate
commit
loop. `_replace` only writes the prepared bytes and calls `os.replace`; it does not recheck the snapshot immediately
before
replacement. A file can change after the preflight check and before its replacement.


#### Impact

The formatter can overwrite a concurrent edit with stale canonical output and still return `SUCCESS`. A direct probe
changed the second file after the preflight pass began, then allowed the commit loop to replace it; the result committed
both files and replaced the concurrent bytes. This violates the optimistic snapshot safety and data-integrity contract.


#### Fix

Revalidate identity, mode, type, and content immediately before each `os.replace`, not only in a prior batch. On a
failed
revalidation, do not replace that file, stop according to the documented commit ordering, and report the preflight
failure
with accurate committed and untouched paths. Add a race test that mutates a later file between the batch preflight and
its
replacement.


#### Outcome


### Significant

#### S01: Required edge and contract coverage still does not test the failing paths


#### Where

`tests/markdown_formatter/` and the Task 02 through Task 07 test requirements in `implementation-plan.md:181-418`


#### Issue

The focused suite has 111 tests, but its assertions do not cover the concrete failures above. Missing cases include
astral-prefix code masking, code in table headers, CommonMark intraword delimiters, two-space hard breaks, angle link
destinations, long inline spans, multiple list paragraphs, list-item quotes, unclosed fences, even trailing backslash
parity, unsafe string keys, immediate snapshot races, and the required `FORMATTED.output` field matrix. Some current
tests
assert only idempotence or substring presence, which can pass while content is already lost.


#### Impact

The green focused suite gives false confidence and allowed the executor's journal to claim completion while direct
probes
still violate parser, preservation, safety, and public-result acceptance criteria. The full generic corpus is not a
behavioral substitute for the plan's exact boundary matrix.


#### Fix

Add exact-byte and semantic-reparse tests for each listed path. Assert all `FileResult` fields, stream output, statuses,
committed/untouched records, and race behavior. Include explicit failures for unsafe frontmatter constructs and ensure
the tests fail before each corresponding repair.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction for the review artifact
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C09 must be resolved before approval. S01 must be addressed in the same pass because the current focused tests do
not
protect the required parser, preservation, operation-safety, or public-result contracts. The unrelated configure pytest
failure and Ty diagnostics remain baseline and are not required formatter fixes for this review.
