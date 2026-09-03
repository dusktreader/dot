# Execution Review: Generic AST-based Markdown formatter

This review rechecks the formatter worktree against the approved implementation plan, implementation journal, and prior
execution review. It starts from the current diff and independently exercises the repaired paths rather than treating
passing tests or the journal's completion claims as evidence.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--02.md`


## Scope

**whole-plan - Iteration 03**

The review covers all formatter production code, CLI and wrapper code, tests, fixtures, dependency changes, and current
worktree changes recorded across the journal. The plan, journal, and prior reviews were read but not modified.


## Issue Summary

- **Critical**: 4
- **Significant**: 2
- **Trivial**: 0


## Verification Evidence

| Command                                                                                                      | Result                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                    | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                                             |
| `uv run pytest tests/markdown_formatter --no-cov`                                                            | Passed: 125 tests.                                                                                                                                    |
| `uv run pytest`                                                                                              | Failed: 438 passed, 1 failed. The failure is the unrelated configure assertion about `@opencode-ai/plugin` in `.config/opencode/package.json`.        |
| `uv run ruff check src tests`                                                                                | Passed: `All checks passed!`                                                                                                                          |
| `uv run ty check`                                                                                            | Failed with 74 diagnostics in the documented unrelated PDF, clipboard/Gmail, OpenCode, configure, Jira, and spinner paths. No formatter path appears. |
| `uv run dt markdown --help`                                                                                  | Passed and lists `format` and `check`.                                                                                                                |
| `uv run dt markdown format --help`                                                                           | Passed and accepts `PATH`.                                                                                                                            |
| `uv run dt markdown check --help`                                                                            | Passed and accepts `PATH`.                                                                                                                            |
| `./.agents/tools/markdown-format.py --help`                                                                  | Passed through the grouped CLI.                                                                                                                       |
| `./.agents/tools/markdown-format.py check tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md`  | Passed with `UNCHANGED` and `summary check SUCCESS 1`.                                                                                                |
| `./.agents/tools/markdown-format.py format tests/markdown_formatter/fixtures/corpus/frontmatter.expected.md` | Passed with `UNCHANGED` and `summary format SUCCESS 1`.                                                                                               |
| `git diff --check`                                                                                           | Passed.                                                                                                                                               |
| Direct parser, normalization, rendering, and operation probes                                                | Failed as described in C01-C04 and S01-S02 below.                                                                                                     |

The configure failure and Ty diagnostics reproduce the documented unrelated baseline and are excluded from the formatter
issue count. The focused formatter suite and Ruff pass do not establish whole-plan correctness.


## Acceptance Criteria Verification

| Task / AC | Status | Evidence                                                                                                                                                                                                                                        |
| --------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01   | ✓      | `pyproject.toml`, `uv.lock`, and `uv sync` pin `markdown-it-py==4.2.0`.                                                                                                                                                                         |
| 01/AC02   | ✓      | Formatter package and model modules exist under `src/dot_tools/markdown_formatter/`.                                                                                                                                                            |
| 01/AC03   | ✗      | Public result models and grouped CLI exist, but valid CommonMark content still violates canonical rendering and idempotence in C01-C03.                                                                                                         |
| 02/AC01   | ✓      | `frontmatter.py:87-142` exposes extraction, validation, and serialization; focused tests exercise the APIs.                                                                                                                                     |
| 02/AC02   | ✓      | `frontmatter.py:87-119` enforces byte-zero opening, exact closing, missing-close failure, and body-byte preservation.                                                                                                                           |
| 02/AC03   | ✓      | Event/node restrictions, duplicate checks, recursive value validation, invalid Unicode, and finite-real handling pass the focused tests.                                                                                                        |
| 02/AC04   | ✓      | `frontmatter.py:142-230` emits deterministic quoted keys, scalar forms, nesting, delimiters, blank line, and round-trippable finite reals.                                                                                                      |
| 03/AC01   | ⚠      | Byte-addressed AST spans exist, but recognized container source association is not safe for nested quote and indented-code cases; see C02 and C03.                                                                                              |
| 03/AC02   | ⚠      | Basic CommonMark/table parsing and inline kinds work, but the scanner is not semantically faithful for nested links, strong/emphasis delimiter runs, autolinks, and fence-bearing info; see C01-C03.                                            |
| 03/AC03   | ✗      | The parser marks malformed ownership as owned instead of opaque in nested-link and malformed fence cases, and recognized containers can be rewritten around children whose source interval is not safely represented.                           |
| 03/AC04   | ✗      | `parser.py:249-269` uses delimiter-position heuristics rather than CommonMark flanking/token ownership. Nested link content and several underscore/strong forms are rendered into different structure.                                          |
| 03/AC05   | ✗      | Raw HTML is rejected for valid parser-owned autolinks, while table and inline code masking works only for selected simple cases; see C02.                                                                                                       |
| 03/AC06   | ⚠      | Top-level thematic-break transition behavior passes direct basic probes, but container-local transition preservation is entangled with the broken quote/container renderer; see C03.                                                            |
| 04/AC01   | ✓      | Normalized state dataclasses exist and focused tests assert state without importing rendering.                                                                                                                                                  |
| 04/AC02   | ✗      | `_inline` rewrites nested delimiter spelling into invalid or changed CommonMark (`**foo __bar__**` becomes `**foo **bar****`), and prose wrapping still operates on rendered bytes instead of an indivisible token stream; see C01.             |
| 04/AC03   | ✗      | Simple recursive list markers and task columns pass, but list-item block quotes lose quote markers, multiple quote lines escape the active list column, and opaque children are not propagated safely; see C03.                                 |
| 04/AC04   | ⚠      | Top-level generated separators are stable, but source spacing and recognized nested container composition remain wrong; see C03.                                                                                                                |
| 04/AC05   | ⚠      | Basic table alignment, padding, code-span pipes, and odd/even trailing framing probes pass in selected forms, but the required semantic/lossless matrix is not established and table parsing is still dependent on incomplete inline ownership. |
| 04/AC06   | ✗      | Closed and unclosed ordinary fences pass, but a backtick-bearing info string on a backtick fence is parsed as a paragraph plus a fence and is not preserved as one code block; see C02.                                                         |
| 05/AC01   | ✗      | Renderer joins recognized blocks correctly only at top level. Nested blockquote code is re-prefixed on every pass, proving that canonical LF/final-LF composition does not preserve recognized container state.                                 |
| 05/AC02   | ✗      | Exact nested inline, nested quote/list, autolink, and fence-info rendering is not lossless or idempotent; see C01-C03.                                                                                                                          |
| 05/AC03   | ✓      | `__init__.py:10-21` composes extraction, parse, normalize, and render and propagates the typed parser/frontmatter errors for exercised cases.                                                                                                   |
| 05/AC04   | ✗      | Golden fixtures cover the focused happy path, but the direct failures below are outside the assertions and violate the required edge matrix.                                                                                                    |
| 06/AC01   | ✓      | `operations.py:18-32` resolves CWD paths, recursively discovers `.md`, sorts, deduplicates, and records explicit invalid operands.                                                                                                              |
| 06/AC02   | ⚠      | Preflight-all-before-write, atomic replacement, mode preservation, partial commit reporting, and cleanup pass selected tests, but the immediate race window remains exploitable; see C04.                                                       |
| 06/AC03   | ✗      | `_replace` revalidates before creating the temporary file, not immediately before `os.replace`; see C04.                                                                                                                                        |
| 06/AC04   | ✓      | Tested result precedence and complete sorted records match the documented status mapping for the exercised failures.                                                                                                                            |
| 06/AC05   | ⚠      | The normal CLI stream and digest behavior pass, but the failed race and untested destination/atomic edge combinations prevent establishing the full contract.                                                                                   |
| 06/AC06   | ✓      | The wrapper captures entry CWD, resolves operands, walks to a project, delegates both normal modes, inherits child streams, and propagates the child return code.                                                                               |
| 06/AC07   | ⚠      | Group registration/help and representative wrapper/operations tests pass, but the required complete race, container, and edge contract matrix is incomplete.                                                                                    |
| 07/AC01   | ⚠      | Generic corpus fixtures exist and cover the main categories, but they do not protect the direct failures in C01-C03 or the immediate replacement race in C04.                                                                                   |
| 07/AC02   | ⚠      | Ruff passes. Full pytest and Ty remain baseline failures and are excluded, but formatter-specific behavior is still blocked by C01-C04 and coverage gaps S01-S02.                                                                               |


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

No unrelated formatter subsystem or profile-specific behavior was introduced. The test path is marked ⚠ because its
assertions leave the concrete failures below unprotected, not because the path is out of scope.


## Prior Review Resolution

- **C01** ⚠: Astral-prefix inline, fenced, indented, and table code HTML masking now passes, and table code ranges are
  handled in the tested forms. However, valid CommonMark autolinks are still rejected and malformed ownership remains
  owned in new cases. See C01-C02.
- **C02** ⚠: Inline-code masking and angle destinations are repaired for the tested forms. Nested links, valid
  autolinks,
  and the backtick-info fence boundary still fail. See C01-C02.
- **C03** ⚠: Multiple list paragraphs and simple nested lists now retain content. List-item block quotes still lose
  quote
  markers or escape the active list column, and blockquote-contained fences are unstable. See C03.
- **C04** ⚠: Arbitrary backslash parity for tested table rows now passes. The full semantic table matrix is not proven,
  especially where parser inline ownership is incomplete. See S01.
- **C05** ⚠: Ordinary closed, unclosed, tilde, and empty fences pass. A backtick-containing info string on a backtick
  fence is parsed incorrectly and loses the original code block. See C02.
- **C06** ✓: `FORMATTED` results now carry canonical output bytes, mismatch/error outputs remain unset, and partial
  result
  records are complete in the tested paths.
- **C07** ✓: Restricted string-key serialization, unhashable keys, and finite-real notation pass the focused tests.
- **C08** ✓ as a baseline classification: the unrelated configure failure and 74 unrelated Ty diagnostics reproduce; no
  formatter path is named.
- **C09** ⚠: Contract tests now cover result fields, representative streams, races, and major edge categories, but they
  do not cover the newly reproducible nested-link, autolink, nested-container, backtick-info, or non-idempotent list/
  quote cases. See S01.
- **S01** ✓: The parser now requires an immediately following lower-level heading and records only eligible transitions
  in
  the tested top-level cases.
- **S02** ⚠: Container-local heading state and basic prefixes are present, but nested blockquote rendering still adds an
  extra prefix and is not idempotent. See C03.


## Findings

### Summary

| Finding | Title                                                                | Outcome |
| ------- | -------------------------------------------------------------------- | ------- |
| C01     | Inline normalization changes valid CommonMark semantics              |         |
| C02     | Code and container parsing still loses valid source structure        |         |
| C03     | Nested recognized containers are not idempotent or lossless          |         |
| C04     | Snapshot validation is not immediate before replacement              |         |
| S01     | Required parser, container, and table edge coverage is still missing |         |
| S02     | Operation safety and CLI edge coverage is incomplete                 |         |


### Critical

#### C01: Inline normalization changes valid CommonMark semantics


#### Where

`src/dot_tools/markdown_formatter/parser.py:249-269` and `src/dot_tools/markdown_formatter/normalize.py:94-135`


#### Issue

The byte scanner claims delimiter pairs with simple first-closer heuristics and the normalizer emits fixed `*`/`**`
delimiters without carrying the parser's semantic delimiter structure. This rewrites valid nested emphasis/strong input
into a different parse. For example, `**foo __bar__**` formats as `**foo **bar****`; reparsing that output produces one
large strong node rather than the original nested strong node. A nested link such as `[a [b](u)](v)` formats as
`[a [b](u)](u)](v)` and grows on each subsequent pass because `_inline` locates the first `](` in the full node source
instead of the outer link's proven destination boundary (`normalize.py:108-115`).


#### Impact

The formatter changes inline semantics and can mutate a document on every run. This violates the CommonMark ownership,
exact rendering, preservation, and idempotence requirements in Tasks 03-05. The failure is in owned syntax, not an
unsupported extension that could be preserved opaque.


#### Fix

Build the inline codec from parser token ownership and semantic children, retaining each construct's actual opener,
closer, destination, title, and delimiter run. For a link/image, store the outer label and destination/title spans or
emit from markdown-it attributes while preserving the required canonical destination/title rules. If nested ownership
cannot be proven, mark the containing block opaque instead of rewriting it. Add exact output and semantic-reparse tests
for nested links/images, nested strong/emphasis, intraword delimiters, escapes, and second-pass idempotence.


#### Outcome


----

#### C02: Valid code and parser boundaries are still corrupted


#### Where

`src/dot_tools/markdown_formatter/parser.py:172-181, 249-259` and
`src/dot_tools/markdown_formatter/normalize.py:300-318`


#### Issue

Fence metadata is extracted by a regular expression that assumes the first line is a normal fence, but the parser's
CommonMark block boundary is not validated against that assumption. A backtick fence with backtick-bearing info, for
example with a backtick in its info string is parsed by markdown-it as a paragraph followed by a separate fence. The
formatter emits a longer backtick run followed by an empty `text` fence, losing the original block's one code payload
and info string. The same
source does not enter the prescribed tilde fallback because it is no longer represented as one fence node.

The parser also does not preserve parser semantics for autolinks: `<https://x>` and `<foo@example.com>` are recognized
CommonMark links by markdown-it but `_reject_raw_html` sees the raw `<` and raises `RawHtmlError`. The code-first policy
must exempt valid parser-owned autolinks while still rejecting actual HTML.


#### Impact

Valid code and inline syntax is rejected or rewritten into extra blocks, violating code payload/info preservation,
raw-HTML
policy, and the bounded CommonMark contract. The fence case is data loss and is not a safe opaque fallback.


#### Fix

Use the parser token's actual `markup`, `info`, `content`, and map to establish one fence node and preserve all payload
bytes. Handle the design's backtick-info rule explicitly: emit a collision-safe tilde fence when a valid backtick fence
has backticks in info, or preserve the parser-delimited block if the source is not representable in the owned subset.
Collect and mask all parser-owned autolink ranges before raw-HTML scanning. Add tests for backtick and tilde info
strings,
EOF/CRLF payloads, autolink URL/email forms, and adjacent HTML.


#### Outcome


----

#### C03: Nested recognized containers are not idempotent or lossless


#### Where

`src/dot_tools/markdown_formatter/normalize.py:159-193, 273-342` and `src/dot_tools/markdown_formatter/render.py:86-117`


#### Issue

The normalized state stores nested content without the active prefix that produced it. `_normalize_blocks` accepts a
`prefix` parameter but never uses it (`normalize.py:273-278`); `_list` strips blockquote content to raw bytes and the
renderer adds only a fixed continuation indentation. Consequently, a list-item block quote such as:

```text
# T

- first
  > quote
  > more
- second
```

formats as `- first`, `  quote`, `more`, `- second`; the second quote line escapes the list content column. A second
pass
formats it differently by indenting `more`, so the output is not idempotent. A blockquote-contained fence similarly
gains
an additional `>` prefix and changes on every pass (`> ````text` ... becomes `> `````text` ...). Opaque recognized
children are also rewrapped instead of preserving the containing block as required by the design.


#### Impact

The formatter silently changes nested list/quote geometry and code structure. It can corrupt active prefixes, alter
parser
boundaries, and repeatedly grow output. This violates Tasks 04-05 and the design's requirement to preserve a containing
block when child ownership is not safely rewritable.


#### Fix

Represent active prefix and indentation as normalized state at every recursive container level. Normalize every
list-item
block child, including quote, code, heading, and paragraph children, through that prefix state. Render container
prefixes
exactly once. When a child is opaque or its source map cannot be composed safely, emit the entire containing list/quote
as
opaque. Add exact multi-line quote/list tests, nested quotes, quote headings/separators, nested code, opaque children,
and
second-pass equality assertions.


#### Outcome


----

#### C04: Snapshot validation is not immediate before replacement


#### Where

`src/dot_tools/markdown_formatter/operations.py:64-79`


#### Issue

`_replace` calls `_safe_destination` at line 66, then creates and writes the temporary file, flushes/fsyncs it, changes
its mode, and finally calls `os.replace`. The destination can change after the safety check and before replacement. A
direct probe patched `os.fsync` to modify the destination during that window; `format_paths` returned `SUCCESS` and
overwrote the concurrent edit with stale canonical output.


#### Impact

The formatter can destroy a concurrent edit while reporting success. This violates the plan's immediate identity,
metadata, type, and content comparison requirement and the data-integrity guarantee for atomic multi-file formatting.


#### Fix

Keep the temporary file preparation separate from commit, but revalidate the destination identity, mode, type, and
content
after the temporary file is fully flushed and immediately before `os.replace`. If validation fails, remove the temporary
file, report `PREFLIGHT_ERROR`, stop in sorted order, and leave the destination unchanged.


#### Outcome


----

### Significant

#### S01: Required parser, container, and table edge coverage is still missing


#### Where

`tests/markdown_formatter/` and the edge requirements in `implementation-plan.md:194-318, 404-418`


#### Issue

The 125-test focused suite covers the repaired examples but still does not assert the direct failures above. Missing
behavioral protection includes nested links/images, nested delimiter-run semantics, valid autolinks, backtick-bearing
info on backtick fences, multi-line list-item quotes, nested blockquote fences, opaque-child propagation, and semantic
reparse equality. The table suite also does not establish the complete lossless framing/parity matrix together with
every
supported inline form in cells. Existing idempotence checks can pass after a first destructive rewrite because the
second
pass stabilizes the already-corrupted output.


#### Impact

The focused green suite still permits semantic data loss, repeated output growth, and policy false positives. The
journal
and prior review therefore cannot claim that C01-C09 and S01 are resolved merely because the newly added tests pass.


#### Fix

Add exact-byte plus semantic-reparse tests for every form listed above. For each formerly failing case, assert the
pre-repair test fails and the post-repair test passes, including three-pass idempotence where nesting is involved.
Assert
that an opaque fallback preserves the entire original byte span.


#### Outcome


----

#### S02: Operation safety and CLI edge coverage is incomplete


#### Where

`tests/markdown_formatter/test_operations.py`, `test_markdown_cli_contract.py`, and `operations.py:64-186`


#### Issue

The race test mutates the later file from a patched `_safe_destination` call, which proves only that the current call
sequence can be observed. It does not exercise the real mutation window between the safety check and `os.replace`. The
required atomic matrix also lacks an independent test for a destination mutation after temporary-file fsync, and does
not
fully assert file identity/mode/type comparison, cleanup, stream output, and committed/untouched fields for that
failure.


#### Impact

The tests give false confidence about the most important data-integrity guarantee. A real concurrent edit can still be
overwritten without a failure status, as demonstrated by the direct probe.


#### Fix

Add a deterministic hook or synchronization barrier in the test seam immediately after final destination validation and
before `os.replace`, then mutate the destination and assert `PREFLIGHT_ERROR`, no replacement of that file, accurate
`committed`/`untouched`, one sorted record per path, cleanup, and CLI exit/status streams. Keep the seam in tests or in
an
operations-local injectable primitive, not as a production test-only bypass.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: system agent definition
- `editing`: system instruction for the review artifact
- `markdown`: system instruction and formatter workflow


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, C03, and C04 must be resolved before approval. S01 and S02 should be addressed in the same pass because the
current tests do not protect the required semantic-preservation and atomic-safety contracts. The unrelated configure
pytest failure and Ty diagnostics remain excluded baseline failures because they still do not reference formatter code.
