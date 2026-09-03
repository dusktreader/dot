# Execution Review: Generic AST-based Markdown formatter

This review evaluates the complete formatter worktree against the approved implementation plan and execution journal.
The review starts from the diff against the parent branch, then verifies the implementation, tests, and documented
quality-gate claims.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`


## Scope

**whole-plan** - Iteration 01

The review covers the current worktree relative to the parent branch, including committed and unstaged changes recorded
in the journal. The review does not modify production code, tests, the plan, or the journal.


## Issue Summary

- **Critical**: 9
- **Significant**: 2
- **Trivial**: 0


## Verification Evidence

| Command                                                                                                         | Result                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                       | Passed. The environment resolved the pinned `markdown-it-py==4.2.0`.                                                                                                                                                                                                                                                                        |
| `uv run pytest tests/markdown_formatter --no-cov`                                                               | Passed: 61 tests. This is a focused suite, not proof of the complete plan.                                                                                                                                                                                                                                                                  |
| `uv run pytest`                                                                                                 | Failed: 374 passed, 1 failed. The failure is `tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies`; the exact assertion is `E AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}`. This is the documented unrelated repository failure. |
| `uv run ruff check src tests`                                                                                   | Passed: `All checks passed!`                                                                                                                                                                                                                                                                                                                |
| `uv run ty check`                                                                                               | Failed with 74 diagnostics. The reported paths are existing `md-to-pdf.py`, clipboard/Gmail tools, opencode cost/trend modules, configure/Jira tests, and spinner tests; no formatter path appears in the output. This is the documented unrelated baseline failure.                                                                        |
| `uv run dt markdown --help`                                                                                     | Passed.                                                                                                                                                                                                                                                                                                                                     |
| `uv run dt markdown format --help`                                                                              | Passed.                                                                                                                                                                                                                                                                                                                                     |
| `uv run dt markdown check --help`                                                                               | Passed.                                                                                                                                                                                                                                                                                                                                     |
| `~/.agents/tools/markdown-format.py --help`                                                                     | Passed, but this resolves the user-level symlink and is not a feature-worktree delegation test.                                                                                                                                                                                                                                             |
| `./.agents/tools/markdown-format.py check tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`     | Passed: `UNCHANGED` and `summary check SUCCESS 1`.                                                                                                                                                                                                                                                                                          |
| Direct probes for inline code HTML, tilde fences, nested lists, finite frontmatter reals, and table idempotence | Failed as described in C02, C03, C04, C05, and C07.                                                                                                                                                                                                                                                                                         |

The focused formatter tests pass because they exercise a small happy-path corpus. They do not exercise the plan's
required
contract tests, race and destination-safety cases, complete inline codecs, nested containers, or the exhaustive table
and
code-span fixtures.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                                                                       |
| --------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml:10-26`, `uv.lock`, and the successful `uv sync` command add the pinned dependency.                                                                                                                                             |
| 01/AC02   | ✓      | The package modules exist under `src/dot_tools/markdown_formatter/`; `models.py:8-66` defines the requested enums and dataclasses.                                                                                                             |
| 01/AC03   | ⚠      | `__init__.py:10-26` and `cli/markdown.py:27-36` expose the requested functions and commands, but exact result semantics fail in C06 and no planned CLI contract module exists.                                                                 |
| 02/AC01   | ✓      | `frontmatter.py:73-128` exposes extraction, validation, and serialization; `test_frontmatter.py` covers the basic APIs.                                                                                                                        |
| 02/AC02   | ✓      | `frontmatter.py:73-105` implements byte-zero opening, exact closing, missing-close failure, and body-byte return; `test_requires_byte_zero_delimiter_and_exact_closing_line`.                                                                  |
| 02/AC03   | ⚠      | Event and node checks exist at `frontmatter.py:38-70`, but the required finite-real acceptance is undermined by C07 and the fixture coverage is not complete.                                                                                  |
| 02/AC04   | ✗      | `frontmatter.py:196-207` rejects representable finite decimal values; see C07. The exact scalar and empty-root fixture matrix is absent.                                                                                                       |
| 03/AC01   | ⚠      | `parser.py:35-107` defines the requested AST and byte spans, but inline ownership is not proven from token maps; see C01.                                                                                                                      |
| 03/AC02   | ✗      | `parser.py:100-175` invokes CommonMark plus tables and recognizes several block kinds, but owned inline nodes are not safely normalized and recognized containers are later discarded or preserved wholesale.                                  |
| 03/AC03   | ✗      | `parser.py:185-246` scans source bytes, but `parser.py:284-285` performs an invalid child reconstruction check that makes valid constructs opaque; see C01.                                                                                    |
| 03/AC04   | ✗      | The scanner in `parser.py:199-244` is not a CommonMark-proven scanner for nested delimiters, destinations, titles, and escapes. The parser test only asserts node names and concatenation, not ownership.                                      |
| 03/AC05   | ✗      | `parser.py:294-302` masks block code only, so inline code containing HTML is rejected; see C02. H1 coverage is limited to the simplest ATX cases.                                                                                              |
| 03/AC06   | ⚠      | Task metadata is recorded at `parser.py:159-162`, but thematic-break validation at `parser.py:309-316` is not positional and normalization does not preserve all source breaks; see S01.                                                       |
| 04/AC01   | ✓      | `normalize.py:10-75` defines the requested normalized state and `test_normalize.py` asserts state without importing rendering.                                                                                                                 |
| 04/AC02   | ✗      | `normalize.py:78-123` does not implement the required inline codecs, and paragraph wrapping at `normalize.py:237-241` can split structural inline syntax. The exact code-span fixture set is incomplete.                                       |
| 04/AC03   | ✗      | `normalize.py:126-145` finds flat marker-looking lines and `render.py:60-64` emits them without continuation geometry or nesting; see C03.                                                                                                     |
| 04/AC04   | ✗      | `normalize.py:199-212` uses one document-global heading level and `render.py:89-90` inserts two blank lines between every block. Local parent spacing and exact separator reuse are not implemented; see S02.                                  |
| 04/AC05   | ✗      | `normalize.py:148-193` and `render.py:17-57` do not preserve code-span pipes, compute escaped widths, or maintain literal-pipe parity; see C04.                                                                                                |
| 04/AC06   | ✗      | `normalize.py:214-231` misreads tilde-fence info and stores a fence that `render.py:8-14` ignores; see C05.                                                                                                                                    |
| 05/AC01   | ⚠      | `render.py:67-90` provides LF joining and a final newline, and basic opaque/code tests pass, but code and container rendering are not correct for the full contract.                                                                           |
| 05/AC02   | ✗      | Renderer output changes code-span table content and malformed tilde-fence info; see C04 and C05.                                                                                                                                               |
| 05/AC03   | ⚠      | `__init__.py:10-26` composes extraction, parsing, normalization, and rendering and propagates broad `ValueError` subclasses, but the resulting canonical bytes are wrong for the failed cases above.                                           |
| 05/AC04   | ✗      | The render/document tests cover 13 basic cases, not the required exact inline, table, payload, and idempotence matrix.                                                                                                                         |
| 06/AC01   | ✓      | `operations.py:18-32` resolves, discovers, sorts, and deduplicates basic paths; `test_collects_recursively_sorts_and_deduplicates` passes.                                                                                                     |
| 06/AC02   | ✗      | `operations.py:135-156` preflights some files and atomically replaces prepared files, but it omits prepared and later untouched `FileResult` records after preflight or write failure. This violates the total record contract; see C06.       |
| 06/AC03   | ⚠      | `operations.py:35-77` captures content and identity and uses same-directory temporary replacement, but the race, destination-type, read-only, cleanup, and partial-commit matrix is not tested.                                                |
| 06/AC04   | ✗      | `operations.py:123-125` sets non-`None` output for `MISMATCH`, contrary to the plan, and result lists are incomplete on failures; see C06.                                                                                                     |
| 06/AC05   | ✗      | The CLI prints basic records, but the exact diagnostic and one-record-per-sorted-file contract is not established. The planned contract tests and most failure cases are absent; see C06 and C09.                                              |
| 06/AC06   | ⚠      | `markdown-format.py:10-29` delegates the two normal modes with absolute operands, entry-CWD execution, stream inheritance, and repository discovery. Only one mocked `check` path is tested, and wrapper failure/help edge cases are untested. |
| 06/AC07   | ✗      | `src/dot_tools/cli/main.py:35-39` registers the group and help passes, but the required `test_markdown_cli_contract.py` is absent and the required operations/wrapper coverage is not present; see C09.                                        |
| 07/AC01   | ⚠      | The corpus directory and `test_corpus.py` exist, but the corpus contains only a small happy-path set and does not cover the required edge matrix, races, or complete multi-file failure behavior.                                              |
| 07/AC02   | ✗      | Ruff passes, but the full pytest and Ty gates fail as recorded above. The failures are unrelated baseline failures for this worktree; formatter-specific correctness still fails C01-C07.                                                      |


## Scope Verification

| File or path                                                            | Justification                                     | Status |
| ----------------------------------------------------------------------- | ------------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01, dependency step                          | ✓      |
| `uv.lock`                                                               | Task 01, dependency step                          | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01, public contract step                     | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05, public document orchestration    | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02, restricted frontmatter                   | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 and the documented Task 07 corpus repairs | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 and the documented Task 07 corpus repairs | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 and the documented Task 07 corpus repairs | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06, operations and atomic replacement        | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06, Typer adaptation                         | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06, command registration                     | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06, compatibility delegation wrapper         | ✓      |
| `tests/markdown_formatter/`                                             | Tasks 02 through 07, focused tests and fixtures   | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record updates                          | ✓      |

No unrelated production subsystem was introduced. The modified formatter, CLI, wrapper, dependency, and test paths are
all
within the approved scope. The ⚠ on the test path reflects insufficient coverage, not scope creep.


## Findings

### Summary

| Finding | Title                                                                       | Outcome |
| ------- | --------------------------------------------------------------------------- | ------- |
| C01     | Valid inline constructs are incorrectly made opaque                         |         |
| C02     | Inline code is included in raw-HTML rejection                               |         |
| C03     | Nested list and continuation structure is discarded                         |         |
| C04     | Table formatting changes semantic cell content and is not idempotent        |         |
| C05     | Tilde fenced-code info and fence state are corrupted                        |         |
| C06     | Operation results violate the total file and output contracts               |         |
| C07     | Lossless finite decimal frontmatter values are rejected                     |         |
| C08     | Full quality gates remain red on the documented baseline                    |         |
| C09     | Required contract and edge-case test coverage is missing                    |         |
| S01     | Thematic breaks are removed without positional transition proof             |         |
| S02     | Heading spacing and recognized container normalization are global or absent |         |


### Critical

#### C01: Valid inline constructs are incorrectly made opaque


#### Where

`src/dot_tools/markdown_formatter/parser.py:208-224` and `src/dot_tools/markdown_formatter/parser.py:284-285`


#### Issue

The scanner creates children for links, emphasis, and strong nodes, but `_reconstruct` compares child source against
`node.source[1:-1]` for every construct. For `[link](url)`, that expected slice is `link](url`, not the label source.
For
`**bold**`, it is `*bold*`, not `bold`. Valid recognized paragraphs therefore fail reconstruction and become a whole
`OpaqueBlock`.


#### Impact

The formatter skips canonical inline encoding for ordinary paragraphs containing links, images, emphasis, or strong
text.
It does not normalize delimiter spelling, escapes, destinations, titles, or nested inline structure as required. A
direct
probe shows `parse_document(b"# T\\n\\n[link](url)\\n").blocks[1].opaque is not None`; the focused parser test checks
only the inline kinds and concatenation, so it misses the failure.


#### Fix

Associate inline nodes with markdown-it token maps and construct-specific source intervals. Reconstruct each node from
its
actual opener, child interval, destination, title, and closer, then mark only genuinely unprovable containing blocks
opaque.
Add exact canonical tests for every inline form, nesting, repeated text, CRLF, astral text, escapes, destinations, and
titles.


#### Outcome


#### C02: Inline code is included in raw-HTML rejection


#### Where

`src/dot_tools/markdown_formatter/parser.py:294-302`


#### Issue

The code-first masking pass replaces only `fence` and `code_block` spans. It never masks inline
`InlineNode(kind="code")`
spans before applying the raw-HTML regex to the complete decoded source.


#### Impact

Valid code containing markup-like text fails the required code-first policy. For example,
`format_document(b"# T\\n\\n`<div>`\\n")` raises `RawHtmlError`, although `<div>` is code and must remain accepted.


#### Fix

Collect and mask fenced, indented, and inline code ranges before scanning raw HTML, including ranges nested inside owned
paragraphs and opaque blocks. Add tests for each code boundary and for actual HTML immediately adjacent to code.


#### Outcome


#### C03: Nested list and continuation structure is discarded


#### Where

`src/dot_tools/markdown_formatter/normalize.py:126-145` and `src/dot_tools/markdown_formatter/render.py:60-64`


#### Issue

`_list` uses a line regex over the complete list source and treats every marker-looking line as a sibling item. It does
not
use the parser tree, child items, block quotes, lazy continuation, or active container prefixes. The renderer then emits
every item as an unindented top-level marker and never emits continuation lines.


#### Impact

Formatting changes list structure. A direct probe of
`# T`, `- parent`, `  - child`, and `  continuation` produces only `- parent` and `- child`; the nested item and
continuation geometry are lost. This violates list order, nesting, task-prefix columns, block-quote columns, and opaque
fallback requirements.


#### Fix

Normalize parser-owned list and list-item nodes recursively. Store active container prefixes, rendered marker widths,
task
prefix widths, and continuation blocks in normalized state, then render those columns without flattening. Preserve the
containing list opaque when lazy continuation ownership cannot be proven. Add nested, multi-digit, task, quote, and lazy
continuation fixtures.


#### Outcome


#### C04: Table formatting changes semantic cell content and is not idempotent


#### Where

`src/dot_tools/markdown_formatter/normalize.py:148-193` and `src/dot_tools/markdown_formatter/render.py:17-57`


#### Issue

The table path treats normalized cell bytes as raw text. It does not distinguish code-span pipes from delimiter pipes,
computes widths before required escaped serialization, and applies the pipe/backslash escape loop to every pipe in the
cell.
It also uses a trailing-pipe test that does not implement the required backslash-parity rule.


#### Impact

The formatter changes code payloads and can produce different bytes on a second pass. For input with `` `a|b` ``, the
output contains `` `a\\|b` ``, which changes the code-span payload. For an escaped literal pipe, the first pass emits an
additional backslash run and the second pass differs. A direct probe of the required table shapes confirms both
failures.
This violates the no-data-loss and idempotence requirements.


#### Fix

Parse semantic cells with the inline AST before serialization. Remove only one framing pipe at each edge, leave
code-span
pipes untouched, apply the specified `2k+1` parity encoding only to semantic literal pipes, measure escaped Unicode
width,
validate header/separator counts, and require reparsing plus a second canonical pass to match. Add the exact framing,
empty-row, marker, short-row, extra-row, escaped-pipe, arbitrary-backslash, and code-span-pipe fixtures.


#### Outcome


#### C05: Tilde fenced-code info and fence state are corrupted


#### Where

`src/dot_tools/markdown_formatter/parser.py:169-175`, `src/dot_tools/markdown_formatter/normalize.py:214-231`, and
`src/dot_tools/markdown_formatter/render.py:8-14`


#### Issue

The parser strips only a literal ````` `` prefix when reading a fence info string, so a `~~~bash` opening fence becomes
info `~~~bash`. Normalization computes a `fence` field, but the renderer ignores that field and independently chooses a
marker.


#### Impact

Formatting a valid tilde-fenced document produces malformed output such as `````~~~bash`` as the opening line and loses
the intended info token. The code-fence contract therefore fails for a supported fence spelling, even though the basic
backtick corpus passes.


#### Fix

Read the actual parser fence markup and info token, preserve the info text exactly except for the specified `bash`/`sh`
mapping, and render the normalized fence stored in `NormalizedCode`. Add fenced and indented payload tests for backtick
and
tilde boundaries, trailing spaces, CRLF, empty payloads, and backtick-bearing info strings.


#### Outcome


#### C06: Operation results violate the total file and output contracts


#### Where

`src/dot_tools/markdown_formatter/operations.py:123-156`


#### Issue

For a check mismatch, `_prepare` constructs `FileResult(..., output=output, ...)` at line 125, although the contract
requires
`MISMATCH` to have `output=None`. For format, prepared files receive no result until they commit. If a later preflight
check
fails at lines 138-141 or a write fails at lines 143-151, the prepared files and later untouched files are absent from
`OperationResult.files`, even though the plan requires one sorted record for every file and explicit committed/untouched
reporting.


#### Impact

The CLI cannot emit the required one-record-per-file output or accurately describe untouched files after a preflight or
partial-write failure. Consumers also receive a nonconforming mismatch object. This breaks the status/result/diagnostic
contract independently of formatter byte correctness.


#### Fix

Build one `FileResult` for every sorted discovered or explicit-error path during preparation. Keep mismatch output
unset,
retain the canonical bytes only in internal preparation state, and assign final statuses to failed and later untouched
paths
when preflight or commit stops. Add exact mixed-outcome, preflight, partial-write, zero-file, and CLI stream assertions.


#### Outcome


#### C07: Lossless finite decimal frontmatter values are rejected


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:189-207`


#### Issue

For values in the fixed-decimal range, `_float_text` calls `format(value, "f")`, which defaults to six fractional
digits,
then compares the rounded text back to the original float and rejects it if it differs. This rejects ordinary finite
values
that the approved envelope requires the serializer to represent.


#### Impact

`serialize_frontmatter({"value": 1.2345678})` raises `FrontmatterError("real cannot be represented without loss")`
instead of
emitting a lossless canonical real. Valid frontmatter documents can therefore not be formatted, and the claimed accepted
finite-real subset is false.


#### Fix

Use a shortest round-trippable decimal representation, apply the approved scientific-notation thresholds and exponent
normalization to that representation, and reject only values that cannot survive the specified canonical conversion. Add
boundary and representative-value tests for fixed and scientific forms, negative zero, subnormal values, and round
trips.


#### Outcome


#### C08: Full quality gates remain red on the documented baseline


#### Where

The project commands in `implementation-plan.md:29-73` and the current verification run.


#### Issue

The full pytest command fails on the existing OpenCode npm dependency assertion, and Ty reports 74 existing diagnostics
in
unrelated modules. The exact pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

Ty's output begins with unresolved imports in `.agents/tools/md-to-pdf.py`, `.config/opencode/tools/clipboard_image.py`,
and `.config/opencode/tools/gmail_cleanup.py`, followed by existing type errors in opencode, configure, Jira, and
spinner
code, and ends with `Found 74 diagnostics`.


#### Impact

Task 07/AC02 is not green in this worktree. These failures are not caused by the formatter and should not be
misclassified as
formatter regressions, but they still prevent the plan's literal full quality-gate acceptance claim.


#### Fix

Resolve or explicitly baseline the unrelated configure and Ty failures in the repository's quality policy before
claiming a
green full-plan gate. No formatter production-code change is indicated by this finding.


#### Outcome


#### C09: Required contract and edge-case test coverage is missing


#### Where

`tests/markdown_formatter/` and the Task 06 and Task 07 test requirements in `implementation-plan.md:370-418`


#### Issue

The implementation journal claims completion, but the required `test_markdown_cli_contract.py` does not exist. The 61
focused
tests do not cover the plan's exact result model semantics, all CLI stream and exit mappings, format-mode wrapper
delegation, no-project/outside-repository discovery, symlink/non-regular/read-only destinations, snapshot races,
cleanup,
partial commits, or the complete inline, table, code, heading, list, and opaque matrices.


#### Impact

Passing tests conceal the failures in C01-C07. New public operations and formatting paths are not behaviorally
established,
and the implementation can claim acceptance while violating data preservation, safety, and output contracts.


#### Fix

Add the planned contract modules and exact-byte fixtures. Exercise every public function and status mapping, both
wrapper
modes, all destination and race cases, every required inline/table/code boundary, nested containers, source-break
policy,
idempotence, and multi-file failure ordering. Assert semantic reparsing, not only line coverage or happy-path bytes.


#### Outcome


### Significant

#### S01: Thematic breaks are removed without positional transition proof


#### Where

`src/dot_tools/markdown_formatter/parser.py:309-316` and `src/dot_tools/markdown_formatter/normalize.py:199-202`


#### Issue

The parser accepts a thematic break whenever any later heading has a greater level than the nearest prior heading; it
does not
require the break to be immediately before that heading. Normalization then drops any thematic break when any future
heading
exists, regardless of intervening body content or transition direction.


#### Impact

Source structure is silently deleted. A break between body text and a later child heading is treated as the heading
separator,
even though it is not the immediately preceding transition block. Breaks outside the required transition must remain
verbatim,
and invalid breaks must fail rather than disappear.


#### Fix

Evaluate each break against the immediately following heading in the same container and the immediately preceding
heading state.
Consume only an eligible source spelling, generate one separator only when required, and preserve or reject every other
break.
Add intervening-body, sibling, equal-level, upward, container, and second-pass tests.


#### Outcome


#### S02: Heading spacing and recognized container normalization are global or absent


#### Where

`src/dot_tools/markdown_formatter/normalize.py:196-212`, `src/dot_tools/markdown_formatter/normalize.py:232-245`, and
`src/dot_tools/markdown_formatter/render.py:67-90`


#### Issue

Heading state is tracked with one `previous_heading` value for the whole document. The renderer joins every normalized
block
with two blank lines, while block quotes and list containers are emitted as opaque source instead of receiving local
heading,
prose, list, or separator normalization.


#### Impact

The implementation cannot apply the nearest-parent/no-body spacing rule inside containers and cannot preserve active
prefixes
for generated separators. It also leaves recognized block quotes outside the owned formatting surface, contrary to the
plan.


#### Fix

Normalize each recognized container with its own heading stack, prior-body state, and active prefix. Represent spacing
and
separator decisions in normalized state rather than inferring them by joining all blocks with one delimiter. Add nested
quote,
list, parent-without-body, sibling, and edge-spacing fixtures.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, C03, C04, C05, C06, C07, and C09 must be resolved before re-review. C08 is a documented unrelated repository
baseline failure and is not attributed to the formatter, but Task 07/AC02 remains literally unsatisfied until the
baseline is
resolved or formally exempted. S01 and S02 should be fixed in the same implementation pass.
