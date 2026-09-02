# Implementation Plan Review: Generic AST-based Markdown formatter

This iteration reviews the implementation plan against the approved simplified generic formatter design and the
canonical implementation-plan requirements.

**Iteration 01**


## Source Artifact

`.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 12
- **Trivial**:     3


## Findings

### Summary

| Finding | Title                                                      | Outcome |
| ------- | ---------------------------------------------------------- | ------- |
| C01     | Public interfaces are not specified sufficiently           |         |
| S01     | Task 01 runs focused tests before those tests exist        |         |
| S02     | The document-formatting pipeline has no assigned task      |         |
| S03     | Inline source-span feasibility remains unresolved          |         |
| S04     | Raw HTML classification precedes code classification       |         |
| S05     | Thematic-break reuse has no parser implementation          |         |
| S06     | Task-marker semantics are not implemented or tested        |         |
| S07     | The table contract loses several required invariants       |         |
| S08     | Code payload and final-newline boundaries are underspec.   |         |
| S09     | Wrapper dependencies and project resolution conflict       |         |
| S10     | CLI status and diagnostic behavior is not testable         |         |
| S11     | Frontmatter safety rules lack executable validation detail |         |
| S12     | Invalid body-byte handling is undefined                    |         |
| T01     | The resolver-selected release is not a real unknown        |         |
| T02     | Worktree instructions are absent from Project Standards    |         |
| T03     | A separator appears between sibling H2 sections            |         |


### Critical

#### C01: Public interfaces are not specified sufficiently


#### Where

Execution, Task 01, Acceptance Criteria and Steps, lines 124-139


#### Issue

AC03 requires explicit typed interfaces, but the plan only gives complete signatures for three functions.
`format_paths(...)`
and `check_paths(...)` are ellipses, and the later path and write functions have no signatures, result types, exception
contracts, or status model. The plan also does not name the public error types that `check_document`, `check_paths`, and
the CLI use to distinguish malformed input, formatting mismatches, and write failures.


#### Impact

The executor can produce incompatible APIs while satisfying the written AC. The CLI, wrapper, and tests can each invent
a
different error or result contract, making the five-stage architecture impossible to verify as one implementation.


#### Suggestion

Replace the ellipses with a signature table covering every public function, including `format_document`,
`check_document`, `collect_paths`, `format_paths`, `check_paths`, `format_file`, `check_file`, `preflight_files`, and
`atomic_replace`. Specify return values, typed exceptions, and which errors the CLI converts to each exit status. Make
the
absence of profile and Zensical parameters part of that API contract and add tests for it.


#### Outcome


### Significant

#### S01: Task 01 runs focused tests before those tests exist


#### Where

Project Commands, Run formatter tests, lines 39-50; Execution, Task 01, Steps, lines 130-139


#### Issue

The focused command names `tests/test_markdown_formatter.py`, `tests/test_markdown_frontmatter.py`,
`tests/test_markdown_renderer.py`, and `tests/test_cli_markdown.py`. Task 01 requires that command before Tasks 02, 03,
04, and 06 create those files.


#### Impact

The first task cannot complete its required verification on a clean worktree. The implementer must either ignore a
prescribed failing command or run work out of order.


#### Suggestion

Remove the focused test command from Task 01 and add the exact relevant command after each task creates its test module.
Reserve the combined focused command for the first point at which all four modules exist, or explicitly document that
Task 01 runs only `uv sync`.


#### Outcome


#### S02: The document-formatting pipeline has no assigned task


#### Where

Execution, Task 01, Steps, lines 135-139; Tasks 02-06, lines 142-314


#### Issue

Task 01 declares `format_document` and `check_document`, but no task explicitly wires frontmatter extraction, body
parsing, normalization, rendering, and final serialization into those entry points. Task 05 describes renderer helpers,
while Task 06 describes file operations, but neither assigns the document-level orchestration or its error behavior.
Task 04 calls `format_document` for idempotence before that orchestration has a planned implementation step.


#### Impact

The stages can be implemented independently while the public formatter skips a stage, handles frontmatter differently,
or returns inconsistent errors. The CLI may pass isolated tests without satisfying the approved end-to-end contract.


#### Suggestion

Add a named pipeline step, preferably to Task 05, that implements `format_document` and `check_document` over the five
stages. Specify the ordering, frontmatter/body boundary, final-newline policy, and typed failure behavior. Add exact
tests for frontmatter plus body, no frontmatter, malformed frontmatter, parser policy errors, and already-canonical
documents.


#### Outcome


#### S03: Inline source-span feasibility remains unresolved


#### Where

Execution, Task 03, Acceptance Criteria and Steps, lines 178-200; Unknowns, lines 351-354


#### Issue

The design owns ordinary inline text, code, emphasis, strong text, links, images, and hard breaks when source spans are
safe. The implementation plan leaves the central span-association strategy as a Task 03 experiment and provides no
algorithm for associating inline tokens with byte ranges. Line maps alone do not define the boundaries of inline
children.
The fallback is also not precise enough to say which ordinary paragraphs remain formatable and which become opaque.


#### Impact

If the library does not expose the required spans, the safe fallback can make ordinary prose opaque and defeat wrapping.
If the executor reconstructs spans by guesswork, it can alter escapes, Unicode, or opaque content, violating the
design's
preservation boundary.


#### Suggestion

Resolve this before execution by selecting a supported parser version and documenting a safe inline-span algorithm, or
explicitly limiting ownership to the spans that can be proven from source. Add an AC requiring ordinary Unicode prose
and
each supported inline node to receive a verified span, with mixed or unverifiable children preserved as one containing
block. Include escaped syntax, repeated text, CRLF, and non-ASCII fixtures.


#### Outcome


#### S04: Raw HTML classification precedes code classification


#### Where

Execution, Task 03, Acceptance Criteria AC04 and classification step, lines 184-200


#### Issue

The ordered classification says `raw HTML rejection` first and `code boundaries` second, but AC04 requires HTML-looking
code payloads to remain accepted. A source-wide raw HTML scan at the first stage will inspect fenced, indented, or
inline
code before the parser has excluded those ranges.


#### Impact

Valid code containing markup-like text can fail with `RawHtmlError`. Alternatively, an implementation may silently
change
the classification order, leaving the plan and its tests unable to establish which bytes the HTML policy covers.


#### Suggestion

Classify fenced, indented, and inline code first, record non-code source ranges, then scan only those ranges for raw
HTML,
including opaque ranges. Define the raw-HTML grammar separately from autolinks and ordinary angle-bracket text, and add
tests for each code boundary, actual raw HTML, comments, and opaque blocks.


#### Outcome


#### S05: Thematic-break reuse has no parser implementation


#### Where

Execution, Task 03 classification, Task 04 AC05 and Steps, lines 198-200 and 219-238


#### Issue

The design requires consuming a source `---`, `***`, or `___` immediately before a downward heading transition while
preserving thematic breaks elsewhere. The parser classification never identifies or records such source blocks, and the
normalizer only names the generated `HeadingSeparator`. Treating the source break as an undifferentiated opaque span
gives
the normalizer no safe way to consume it.


#### Impact

The formatter can emit a generated separator after the source separator, fail to canonicalize `***` and `___`, or alter
a
non-transition break. Nested containers and second-pass idempotence are especially likely to diverge.


#### Suggestion

Add a source thematic-break boundary or adjacent-source annotation during parsing. Have normalization consume it only
when
it is the immediate predecessor of a downward transition, replace it with `HeadingSeparator`, and otherwise preserve its
original bytes. Test all three spellings, no-break transitions, container prefixes, and a second formatting pass.


#### Outcome


#### S06: Task-marker semantics are not implemented or tested


#### Where

Execution, Task 04, Acceptance Criteria AC02-AC03 and Steps, lines 213-238


#### Issue

The plan requires preserving task-marker state and using the task-prefix width, but the parser configuration is only
CommonMark plus tables and no model field or recognition step stores a task prefix. The test description mentions list
columns without naming task-marker cases or the exact accepted spellings.


#### Impact

Nested task lists can receive the wrong continuation column, and normalization can treat `[ ]` or `[x]` as ordinary text
instead of preserving the required marker state. The resulting output can be structurally valid but violate repository
style or fail idempotence.


#### Suggestion

Define the task-marker grammar in the parser contract, store the prefix separately on each list item, and include its
width
in the list geometry calculation. Add ordered and unordered, nested, multi-digit, checked, unchecked, and marker-looking
ordinary-text fixtures with exact expected continuation indentation.


#### Outcome


#### S07: The table contract loses several required invariants


#### Where

Execution, Task 04, Acceptance Criteria AC06 and Steps, lines 221-237


#### Issue

AC06 summarizes table validation but omits executable details from the approved design: the header must be immediately
followed by the separator; each row permits at most one framing pipe on each edge; an all-pipe row has zero cells; the
separator has exactly the header count and is never padded; every extra data cell, including an empty one, is an error;
data cells pad on the right; widths use `max(content length, 3 + marker count)`; and literal pipe escaping must preserve
the required odd/even backslash run.


#### Impact

An implementation can silently drop extra cells or pad the separator, accept an invalid all-pipe row, or produce a
non-idempotent escape sequence while still claiming to satisfy AC06. The existing line-oriented wrapper has precisely
the
kind of broad row padding that the approved design rejects.


#### Suggestion

Copy the exact invariants into AC06 and map each one to a named test case. Specify the parser-to-normalizer error path
for
malformed recognized tables and the opaque fallback for unrecognized pipe text. Include escaped pipes, code-span pipes,
empty cells, short rows, extra cells, all framing variants, and all alignment markers.


#### Outcome


#### S08: Code payload and final-newline boundaries are underspecified


#### Where

Execution, Task 04 AC07 and Task 05 AC01-AC03, lines 224-225 and 248-265


#### Issue

The plan says indented and fenced code payloads remain untouched while also converting code to canonical fences and
emitting exactly one final LF. It does not define how an indented block's payload bytes are extracted, how terminal CRLF
or a missing terminal newline is handled, whether language matching applies to the first info token or the full info
text,
or how a tilde fence is closed when payload and info contain fence characters.


#### Impact

The renderer can remove payload indentation that is semantically part of the code, change CRLF or trailing bytes, emit
an
invalid fence, or add a newline inside a preserved payload. A second pass can then choose a different fence or payload.


#### Suggestion

Define source payload boundaries for fenced and indented code, the exact conversion of syntax indentation, fence sizing,
info-token handling, terminal-newline behavior, and the distinction between payload bytes and document separators. Add
golden fixtures for CRLF, trailing spaces, unterminated input, backtick and tilde runs, indented code, and empty
payloads.


#### Outcome


#### S09: Wrapper dependencies and project resolution conflict


#### Where

Execution, Task 01 AC02, and Task 06 Steps, lines 124-126 and 307-314


#### Issue

Task 06 makes the standalone script a thin delegating wrapper, but Task 01 requires its PEP 723 environment to install
`markdown-it-py` and `pyyaml`, even though the wrapper should not parse or serialize Markdown. The plan also says to
resolve
the project containing `pyproject.toml` without defining the search root, precedence when multiple projects exist, or
how
the captured caller CWD becomes the child process's path base.


#### Impact

The wrapper installs duplicate, unused parser dependencies and can delegate to the wrong project or resolve relative
paths
against a changed directory. Direct callers cannot rely on the claimed compatibility behavior, and the no-project
failure
case is the only case with a stated result.


#### Suggestion

Keep only dependencies used by the wrapper in its PEP 723 metadata, unless the plan explicitly defines a standalone
parser
mode. Specify the project search algorithm, capture `entry_cwd` before any resolution, convert relative user paths from
that directory, invoke the selected `dt` command with those paths, and propagate stdout, stderr, and the child exit
code.
Add tests from the repository root, a repository subdirectory, a directory outside the repository, and a no-project
copy.


#### Outcome


#### S10: CLI status and diagnostic behavior is not testable


#### Where

Execution, Task 06 AC02-AC04 and Steps, lines 280-314


#### Issue

The criteria say that commands “fail,” “report,” and “propagate status,” but do not define exit codes, diagnostic
format,
summary format, ordering, or whether a check mismatch reports the canonical diff, a path-only error, or both. The write
criteria also do not specify temporary-file cleanup or the exact committed/untouched report after an `os.replace`
failure.


#### Impact

Automation and callers can observe incompatible behavior while all tests assert only nonzero or zero. A partial write
error
can leave stale temporary files or an ambiguous report, and the wrapper may not preserve the CLI's actual status
semantics.


#### Suggestion

Add a CLI behavior table with exit codes and exact stdout/stderr responsibilities for success, input errors,
parse/policy
errors, check mismatches, preflight failures, and write failures. Define sorted report order, cleanup guarantees, and
the
single-file failure invariant. Assert those outputs and statuses in `test_cli_markdown.py` and add direct operation
tests
for preflight and replacement failure.


#### Outcome


#### S11: Frontmatter safety rules lack executable validation detail


#### Where

Execution, Task 02, Acceptance Criteria AC02-AC04 and Steps, lines 149-168


#### Issue

The plan repeats the safe YAML allowlist but does not specify how the restricted loader rejects aliases, anchors, tags,
duplicate keys, multiple documents, and implicit timestamp or non-boolean scalar resolution before object construction.
“Reject non-finite or lossy numeric representations” also lacks the exact round-trip test and failure rule. Unicode
validation is mentioned at the byte boundary but not for decoded escape values such as surrogate code points.


#### Impact

PyYAML can accept or coerce values outside the approved envelope, and serialization can emit a changed or invalid value
while passing broad happy-path tests. That violates the frontmatter safety boundary and makes exact output claims
unverifiable.


#### Suggestion

Specify node-level validation before construction, duplicate-key detection, explicit rejection of anchors, aliases,
tags,
and additional documents, the permitted scalar resolution rules, recursive Unicode validation, and the exact numeric
round-trip algorithm. Name fixtures with expected bytes for each forbidden construct and for threshold, negative-zero,
large, tiny, and lossy numeric values.


#### Outcome


#### S12: Invalid body-byte handling is undefined


#### Where

Execution, Task 02 Step 3 and Task 03 `parse_markdown` contract, lines 167-179


#### Issue

The public formatter accepts `bytes`, and the parser also accepts `body: bytes`, but the only decoding statement appears
in
the frontmatter task. The plan never says whether invalid UTF-8 in the body fails with a typed parser error, becomes one
opaque byte span, or is decoded with replacement characters. It also does not state how line-ending normalization
interacts
with source offsets after decoding.


#### Impact

Malformed input can be silently changed or cause an unclassified exception. Either outcome breaks the design's safe
opaque
boundary and makes byte-for-byte preservation impossible to reason about.


#### Suggestion

Choose and document one policy, preferably rejecting invalid UTF-8 before invoking `markdown-it-py` with a typed error.
Define
the UTF-8 byte-to-character line index for CRLF and non-ASCII text, and add tests for invalid bytes, CRLF, Unicode
astral
characters, and opaque spans containing trailing whitespace.


#### Outcome


### Trivial

#### T01: The resolver-selected release is not a real unknown


#### Where

Unknowns, lines 348-350


#### Issue

The exact lockfile version is normal dependency-resolution output, not an ambiguity requiring design review. The
meaningful
unknown is whether the chosen version supports the required token and parser behavior, which is already the second item.


#### Impact

The Unknowns section suggests that plan approval depends on a routine `uv sync` result while leaving the actual parser
API
compatibility decision unresolved.


#### Suggestion

Remove the release-selection item or rewrite it as a supported-version decision: select a version compatible with Python
3.13, verify the required parser behavior before implementation, and record the resulting constraint and lockfile entry.


#### Outcome


#### T02: Worktree instructions are absent from Project Standards


#### Where

Project Standards, lines 96-104


#### Issue

The plan links the repository guide, system README, Markdown and Python instructions, and `pyproject.toml`, but omits
the
worktree's `AGENTS.md`, which is the local instruction file explicitly governing this checkout.


#### Impact

An executor reading only the plan's standards can miss the repository-specific setup and layout requirements.


#### Suggestion

Add a link to `../../AGENTS.md` in Project Standards, or state why the worktree instruction file does not apply.


#### Outcome


#### T03: A separator appears between sibling H2 sections


#### Where

Project Commands and Project Standards, lines 94-96


#### Issue

The Markdown guide reserves separator bars for moving back to a higher heading level. The `----` bar separates two
sibling
H2 sections and is inconsistent with the rest of the plan.


#### Impact

The plan has a minor formatting violation and introduces a line that the formatter may interpret as a thematic break
when
the plan itself is parsed.


#### Suggestion

Remove the separator between `## Project Commands` and `## Project Standards`; retain separators only when returning to
a
higher-level section.


#### Outcome


----

## Notes

S03 is the main architectural gate. Resolve the inline source-span strategy before implementation rather than allowing
the
executor to discover that ordinary prose must become opaque. S04 and S05 should be resolved together because both depend
on
parser boundary classification. S07, S08, S09, and S10 need exact fixture or CLI contracts, not just broader test names.

The two listed Unknowns do not cover the other unresolved policy decisions. In particular, frontmatter scalar handling,
body decoding, and wrapper project discovery need answers before execution. No prior review resolution applies because
this
is iteration 01.
