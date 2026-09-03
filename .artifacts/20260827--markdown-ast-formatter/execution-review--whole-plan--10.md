# Execution Review: Generic AST-based Markdown formatter

This review independently rechecks the current formatter against the approved implementation plan, its execution
journal, and execution review 09. The focused formatter gates pass, but direct probes still find formatter-specific
code, line-ending, list-structure, frontmatter, and table-canonicalization defects.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--09.md`


## Scope

**whole-plan - Iteration 10**

The review covers the formatter package, frontmatter, parser and byte spans, normalization and rendering, operations,
the grouped CLI, the compatibility wrapper, dependency and registration changes, tests, fixtures, and the complete
journal history. The plan, journal, and prior review were read but not modified.


## Issue Summary

- **Critical**:    5
- **Significant**: 2
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                            | Result                                                                                                                                                              |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                   | Passed. The environment resolves the pinned `markdown-it-py==4.2.0`.                                                                                                |
| `uv run pytest tests/markdown_formatter --no-cov`                           | Passed: 204 tests. The focused suite does not cover all failures below.                                                                                             |
| `uv run pytest --no-cov`                                                    | Failed: 517 passed, 1 failed. The failure is the independently confirmed configure baseline.                                                                        |
| `uv run pytest`                                                             | Failed: 517 passed, 1 failed; coverage reached 83.99%. The same configure baseline failed.                                                                          |
| `uv run ruff check src tests`                                               | Passed: `All checks passed!`.                                                                                                                                       |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                                                                             |
| `uv run ty check`                                                           | Failed with 74 diagnostics outside formatter scope. No formatter path appears.                                                                                      |
| `git diff --check`                                                          | Passed.                                                                                                                                                             |
| Grouped and wrapper help                                                    | Passed for `dt markdown`, both subcommands, and the wrapper.                                                                                                        |
| Grouped and wrapper canonical smoke                                         | Passed. Both modes report `UNCHANGED` and `summary ... SUCCESS 1`.                                                                                                  |
| Independent parser, normalization, rendering, and frontmatter probes        | Failed for wrong fence closure, recognized CRLF body text, mixed list child ordering, empty fenced payload, finite-real roundtrip, and table link canonicalization. |

The repository-wide pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The test compares the existing OpenCode package manifest with an empty mapping. The manifest contains the plugin
dependency independently of the formatter changes. The 74 repository-wide Ty diagnostics are likewise outside the
formatter paths and were independently confirmed. They are baseline evidence, not formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                                            |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                                  |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and the stage modules exist with the requested public names.                                      |
| 01/AC03 | ⚠      | `models.py:8-66`, `cli/markdown.py:15-24`, and focused contract tests establish the surface, but the public pipeline still exposes C01-C05 and S01. |


### Task 02

| AC      | Status | Evidence                                                                                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 02/AC01 | ✓      | `frontmatter.py:87-143` exposes extraction, validation, and serialization; `test_frontmatter.py` exercises all three.                                  |
| 02/AC02 | ✓      | `frontmatter.py:87-109` enforces byte-zero opening, first exact closing line, missing-close failure, and body preservation.                            |
| 02/AC03 | ⚠      | `frontmatter.py:52-137` rejects the tested unsafe YAML forms and non-finite values, but numeric spelling and real roundtrip are not complete. See C05. |
| 02/AC04 | ✗      | `frontmatter.py:204-230` accepts a finite real whose canonical fixed form reparses as a different integer value. See C05.                              |


### Task 03

| AC      | Status | Evidence                                                                                                                                                            |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:35-128,448-532` provides byte-addressed AST, table rows/cells, and fence spans, but fence boundary handling is incorrect. See C01.                       |
| 03/AC02 | ⚠      | `parser.py:197-345,448-487` owns the requested basic structures and repaired table code-pipe ownership, but recognized code boundaries still lose payload. See C01. |
| 03/AC03 | ⚠      | `parser.py:423-445,640-748` proves many exact UTF-8 intervals, but the parser's fence recovery does not prove the actual closing delimiter. See C01.                |
| 03/AC04 | ✓      | `parser.py:606-952` uses the semantic-token pass and bounded source scanner; direct adjacent-atom and non-escapable-backslash probes preserve semantics.            |
| 03/AC05 | ✓      | `parser.py:961-1007` masks recognized code ranges before raw-HTML scanning; focused tests reject raw HTML and accept HTML-looking code.                             |
| 03/AC06 | ✓      | `parser.py:955-1037` applies top-level H1, task, and thematic-break policy; focused parser tests cover these boundaries.                                            |


### Task 04

| AC      | Status | Evidence                                                                                                                                                                       |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 04/AC01 | ✓      | `normalize.py:16-94` defines the requested normalized state and `test_normalize.py` asserts state directly.                                                                    |
| 04/AC02 | ✗      | `normalize.py:534-582` wraps from raw text-node source and can retain CRLF in a recognized paragraph; the canonical recognized-node LF rule is violated. See C03.              |
| 04/AC03 | ✗      | `normalize.py:210-292` chooses the first paragraph as item content and renders other children separately, changing valid mixed list-child structure. See C04.                  |
| 04/AC04 | ⚠      | `normalize.py:438-526` handles the repaired nested heading/separator cases, but recursive list-child boundaries can still change heading and paragraph relationships. See C04. |
| 04/AC05 | ⚠      | `normalize.py:383-435` validates table geometry and pipe parity, but `_table_inline` bypasses the canonical link/image codec. See S01.                                         |
| 04/AC06 | ✗      | `normalize.py:461-505` consumes code payload state, but the empty closed-fence payload is rendered with an added newline. See C02.                                             |


### Task 05

| AC      | Status | Evidence                                                                                                                                                                     |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✗      | `render.py:156-184` adds a newline to empty code payloads and the pipeline retains CRLF in recognized prose. See C02 and C03.                                                |
| 05/AC02 | ⚠      | `render.py:27-84,97-153` renders canonical structures and passes the covered corpus, but mixed list blocks, empty fences, and table links are not contract-correct.          |
| 05/AC03 | ✓      | `__init__.py:10-27` composes extraction, parse, normalize, and render while preserving the documented exception families; operation-level effects remain covered separately. |
| 05/AC04 | ⚠      | Corpus golden and idempotence tests pass, but the required exact cases in C01-C05 and S01 are absent or false-green. See S02.                                                |


### Task 06

| AC      | Status | Evidence                                                                                                                                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 06/AC01 | ✓      | `operations.py:15-40` resolves CWD operands, recursively discovers Markdown files, sorts and deduplicates, catches traversal errors, and the focused tests cover zero discovery and discovery failure. |
| 06/AC02 | ✓      | `operations.py:90-117,195-230` prepares before writing, uses same-directory temporary files, stops on the first write error, reports commit sets, and cleans temporary files.                          |
| 06/AC03 | ✓      | `operations.py:43-117` captures bytes and lstat identity/mode/type, checks destination safety, holds the destination lock, fsyncs temporary contents, and preserves mode.                              |
| 06/AC04 | ✓      | `operations.py:123-136,195-230` implements the documented status precedence and format/check mappings for the exercised outcomes.                                                                      |
| 06/AC05 | ⚠      | `operations.py:139-148` and `cli/markdown.py:15-24` emit sorted records and digest-only mismatch diagnostics, but the full mixed precedence and exact stream matrix is not covered. See S02.           |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25` captures entry CWD, walks from the resolved wrapper path, delegates through `uv run --project`, and passes child streams/status.                              |
| 06/AC07 | ⚠      | `main.py:20-39` registers the group and representative CLI/wrapper tests pass, but the complete operation and formatter edge matrix is not covered. See S02.                                           |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                                         |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 07/AC01 | ⚠      | `tests/markdown_formatter/fixtures/corpus/` covers the broad categories, but it has no exact semantic cases for C01-C05 or table link canonicalization.                                          |
| 07/AC02 | ✗      | Formatter-focused pytest, Ruff, and Ty pass, but formatter-specific findings remain. The full pytest and repository Ty commands also retain the independently confirmed baseline failures above. |


## Scope Verification

| File or path                                                            | Justification                                     | Status |
| ----------------------------------------------------------------------- | ------------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency step                           | ✓      |
| `uv.lock`                                                               | Task 01 dependency step                           | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public result contracts                   | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document orchestration            | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML envelope                  | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, policy, and repair passes | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repair passes           | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repair passes               | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 operation safety and result mapping       | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                             | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                      | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility delegation                  | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 focused tests and corpus      | ✓      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                                  | ✓      |

All reviewed changes remain within the approved formatter, dependency, CLI, wrapper, registration, test, fixture, and
journal scope. No unrelated production subsystem was changed.


## Prior Review Resolution

| Review 09 finding                                                       | Status | Current evidence                                                                                                                                                                                                                        |
| ----------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C07 First non-paragraph list children are silently discarded            | ⚠      | The simple `- # H` and `- ```text` cases now retain their child content, but `normalize.py:222-290` still moves a later heading/code child around the paragraph selected as item content. The residual mixed-child defect is C04 below. |
| C08 Required escaped and code-pipe table cells fall back opaque         | ✓      | `parser.py:448-487` now uses physical cell intervals; direct escaped-pipe and code-pipe probes produce non-opaque tables, exact cell spans, canonical output, and stable formatter reparses.                                            |
| C09 Nested container rendering creates a non-idempotent setext heading  | ✓      | `render.py:132-140,187-189` uses recursive block joins; the two-level quote descent probe now emits blank boundaries and converges in three passes.                                                                                     |
| C10 Inline wrapping inserts bytes that change adjacent text semantics   | ✓      | `normalize.py:556-582` preserves atom adjacency and the direct `a[x](url)b` and `foo\\bar` probes return unchanged semantics and stable bytes.                                                                                          |
| C11 Recursive discovery filesystem errors escape the operation contract | ✓      | `operations.py:21-40` catches traversal `OSError`; `test_operations.py::test_recursive_discovery_oserror_is_a_read_error_result` verifies the complete result and diagnostic.                                                           |
| S03 Required edge and operation coverage has false-green gaps           | ⚠      | Discovery coverage was added, but the exact cases listed above still lack semantic/ownership assertions. The current 204-test pass does not rule out C01-C05 or S01.                                                                    |


## Findings

### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| C01     | Fence closing rules accept the wrong marker and discard payload |         |
| C02     | Empty closed fences gain an unowned payload newline             |         |
| C03     | Recognized CRLF prose bypasses LF canonicalization              |         |
| C04     | Mixed list child blocks are reordered and reparsed differently  |         |
| C05     | A finite real fails the required frontmatter roundtrip          |         |
| S01     | Table cells bypass the canonical inline codec for links         |         |
| S02     | Focused coverage still permits false-green whole-plan claims    |         |


### Critical

#### C01: Fence closing rules accept the wrong marker and discard payload


#### Where

`src/dot_tools/markdown_formatter/parser.py:318-344`, especially line 327.


#### Issue

The parser derives the opening fence marker, but the payload loop treats any run of three or more backticks or tildes as
a closing fence. It does not require the closing character to match the opener or the closing run to be at least as long
as the opener. The recovery path in `_join_split_backtick_fences` has the same boundary weakness.

Independent probes show data loss:

```text
source = b"# T\n\n```text\n~~~\nkeep\n```\n"
format_document(source) == b"# T\n\n```text\n\n```\n"
```

The `~~~` line is payload for a backtick fence, but the implementation treats it as the closer and drops both it and
`keep`. A shorter backtick run inside a longer backtick fence produces the same failure and can split the remaining
source into unrelated blocks.


#### Impact

Valid fenced code is silently destroyed. The formatter violates code payload preservation, parser source boundaries,
reparse stability, and the fail-closed requirement.


#### Fix

Carry the opening fence character and length through parsing and recovery. Accept a closer only when it uses the same
character, has at least the opening length, and contains no disallowed info text. Treat an absent valid closer as the
documented unclosed-fence case without consuming unrelated following blocks. Add exact LF/CRLF tests for mismatched
characters, shorter closers, longer closers, payload marker runs, and EOF.


#### Outcome


----

#### C02: Empty closed fences gain an unowned payload newline


#### Where

`src/dot_tools/markdown_formatter/normalize.py:461-505` and
`src/dot_tools/markdown_formatter/render.py:132-140,156-184`.


#### Issue

For a closed fence with no payload line, the parser produces `CodePayload(payload=b"")`. Both render paths then apply
`payload if payload.endswith((b"\n", b"\r")) else payload + b"\n"`, turning the empty payload into one newline byte.

Independent probe:

```text
source = b"# T\n\n~~~text\n~~~\n"
format_document(source) == b"# T\n\n```text\n\n```\n"
```

The canonical result reparses with a payload containing `b"\n"`, not the original empty semantic payload. The focused
empty-fence test uses a source that already contains a blank payload line, so it does not detect this case.


#### Impact

The formatter changes code semantics and violates the plan's unconditional code-payload preservation rule. Idempotence
does not prove correctness because the inserted newline becomes stable on the next pass.


#### Fix

Render an empty payload as an opener line followed immediately by the closing marker, without synthesizing a payload
line. Append a line ending only when a nonempty payload lacks one. Add exact closed-empty, one-blank-line, EOF, LF, and
CRLF tests that assert `CodePayload.payload`, output bytes, and reparsed payload.


#### Outcome


----

#### C03: Recognized CRLF prose bypasses LF canonicalization


#### Where

`src/dot_tools/markdown_formatter/normalize.py:534-582`, especially lines 559-565.


#### Issue

The normalizer computes an LF-normalized `encoded` value, but `_wrap_inline_tokens` reconstructs text atoms from
`node.source`. For a recognized paragraph whose soft line break is CRLF, the raw node source wins and the CRLF survives
rendering.

Independent probe:

```text
format_document(b"# T\r\n\r\none\r\ntwo\r\n") == b"# T\n\none\r\ntwo\n"
```

The paragraph is parser-owned, not opaque, and the output contains CRLF inside a recognized node. The design requires
recognized nodes and final document separators to use LF; only opaque spans and specified code payload bytes retain
source line endings.


#### Impact

The formatter emits noncanonical line endings in ordinary body text. This makes output platform/source dependent and
violates the document-level byte contract even though the output is idempotent.


#### Fix

Tokenize and emit the normalized `encoded` text, or normalize each owned text atom before wrapping. Preserve CRLF only
in
opaque source and code payload state. Add a direct exact-byte LF/CRLF soft-break test, including astral text and a
recognized paragraph with multiple lines.


#### Outcome


----

#### C04: Mixed list child blocks are reordered and reparsed differently


#### Where

`src/dot_tools/markdown_formatter/normalize.py:210-292` and `src/dot_tools/markdown_formatter/render.py:97-119`.


#### Issue

The list normalizer always selects the first paragraph child as `NormalizedListItem.content`, then stores every other
child in a separate `children` sequence. The renderer writes the selected paragraph first and appends all other blocks
after it, inserting blank lines between them. That is not the source order or the source container relationship for
lazy and mixed list items.

Independent probes show semantic changes:

```text
source = b"# T\n\n- # H\n  text\n"
output = b"# T\n\n- text\n\n  # H\n"

source = b"# T\n\n- first\n  ```text\n  code\n  ```\n  after\n"
output = b"# T\n\n- first\n\n  ```text\n  code\n  ```\n\n  after\n"
```

The first source places the heading before its lazy paragraph, while the output places the paragraph first. The second
source is one list item with a lazy paragraph around a code block; the output creates separate paragraph blocks and
changes
the rendered Markdown AST. The simple first-child-only heading and fence cases pass, which is why the current focused
tests do not expose this broader defect.


#### Impact

Valid recognized list content is reordered or assigned different paragraph boundaries. Formatting changes document
semantics and violates recursive list, block-child, and three-pass AST preservation requirements.


#### Fix

Normalize `item.children` in source order. Keep a first paragraph inline only when the parser proves it is the item's
content paragraph; otherwise render the first child through the same block path as every later child. Preserve lazy
continuations as the parser-owned list structure, and add exact semantic-reparse tests for heading, fenced code,
indented code, block quote, secondary paragraph, task, nested-list, and mixed-child items.


#### Outcome


----

#### C05: A finite real fails the required frontmatter roundtrip


#### Where

`src/dot_tools/markdown_formatter/frontmatter.py:204-230`.


#### Issue

The fixed-notation branch removes the decimal point and trailing zeroes, then accepts the resulting integer spelling
when
`float(text) == value`. For a finite real whose binary value is not exactly the emitted integer, YAML reparses the
canonical bytes as an integer with a different Python value.

Independent probe:

```text
value = 1.2345678901234567e20
encoded = serialize_frontmatter({"x": value})
# encoded contains: "x": 123456789012345670000
extract_frontmatter(encoded)[0]["x"] == value  # False
```

The current loss check validates a float conversion, not the actual restricted YAML reparse. The emitted scalar is an


#### Impact

Frontmatter serialization is not lossless for an accepted finite real. A format/check pass can change numeric data while
the focused tests pass because they cover only values whose emitted spelling happens to compare equal after parsing.


#### Fix

Define losslessness against the restricted loader and reject any real whose canonical spelling does not reparse to the
same accepted scalar value and type, or retain an unambiguous real spelling where the approved numeric algorithm permits
it. Add boundary and adversarial finite-real tests around fixed notation, scientific notation, large integral-looking
floats, subnormals, negative zero, and exponent normalization.


#### Outcome


### Significant

#### S01: Table cells bypass the canonical inline codec for links


#### Where

`src/dot_tools/markdown_formatter/normalize.py:408-435`.


#### Issue

`_table_inline` canonicalizes text, code, emphasis, and strong nodes, but its fallback appends `node.source` unchanged.
Links, images, and hard breaks therefore bypass the inline codec required by the table serialization algorithm.

Independent probe:

```text
source = b"# T\n\n| h |\n| --- |\n| [x](u 't') |\n"
format_document(source) contains b"[x](u 't')"
```

The ordinary inline pipeline canonicalizes the same title to `[x](u "t")`, but the table pipeline leaves the single
quoted title unchanged. The table output is stable only because the bypassed source is reused on the next pass.


#### Impact

Recognized tables are not serialized by the ordered canonical inline algorithm. Link/image titles, destinations, and
hard
breaks can retain noncanonical or source-dependent syntax, and idempotence hides the missing transformation.


#### Fix

Use the same recursive inline codec for every owned table cell node, including links, images, hard breaks, and nested
labels. Keep the table-specific pipe escaping and width measurement after inline canonicalization. Add exact table tests
for link/image titles, angle and bare destinations, nested labels, hard breaks, and LF/CRLF inputs.


#### Outcome


----

#### S02: Focused coverage still permits false-green whole-plan claims


#### Where

`tests/markdown_formatter/test_edge_contract.py`, `test_parser.py`, `test_normalize.py`, `test_render.py`, and the
corpus fixtures under `tests/markdown_formatter/fixtures/`.


#### Issue

The focused suite's 204 passing tests verifies the repaired examples, but it does not assert the exact behaviors needed
to
catch the current defects. In particular, it lacks exact expected bytes plus semantic or AST assertions for mismatched
fence closers, closed-empty fences, recognized CRLF prose, mixed list-child order, adversarial finite-real roundtrip,
and
table link canonicalization. Several table and container checks rely on convergence, which opaque preservation or source
reuse can satisfy without proving normalization.


#### Impact

The suite reports a green formatter despite data loss and semantic changes in the public pipeline. Prior execution
claims
that the whole plan is complete are not supported by the current oracle set.


#### Fix

Add exact-byte, parser-ownership, source-span, semantic-reparse, and three-pass assertions for every case named above.
Add operation subprocess coverage for the remaining mixed status, diagnostic, and exit precedence combinations, then run
the full documented command set and record the independently confirmed repository baselines separately.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C05 must be resolved before approval. S01 and S02 must be addressed in the same pass. The unrelated configure pytest
failure and repository-wide Ty diagnostics are independently confirmed baseline issues and remain excluded from the
formatter findings.
