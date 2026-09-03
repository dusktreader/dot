# Execution Review: Generic AST-based Markdown formatter

This review rechecks the current formatter against the approved implementation plan, the complete implementation
journal, and execution review 08. The focused quality gates pass, but independent probes still find formatter-specific
data-loss, semantic, and operation-contract defects.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--08.md`


## Scope

**whole-plan - Iteration 09**

The review covers the formatter package, parser and source spans, normalization and rendering, frontmatter, operations,
grouped CLI, compatibility wrapper, dependency and registration changes, tests, and fixtures recorded in the journal.
The plan, journal, and prior review were read but not modified.


## Issue Summary

- **Critical**:    5
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                                                                                                                    | Result                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                                                                                                           | Passed. The pinned `markdown-it-py==4.2.0` environment resolves.                                              |
| `uv run pytest tests/markdown_formatter --no-cov`                                                                                                                   | Passed: 202 tests. The suite does not exercise the failures below.                                            |
| `uv run pytest`                                                                                                                                                     | Failed: 515 passed, 1 failed. The failure is the independently confirmed unrelated configure assertion below. |
| `uv run ruff check src tests`                                                                                                                                       | Passed: `All checks passed!`.                                                                                 |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`                                                                                         | Passed.                                                                                                       |
| `uv run ty check`                                                                                                                                                   | Failed with 74 diagnostics in existing non-formatter paths. No formatter path appears.                        |
| `git diff --check`                                                                                                                                                  | Passed.                                                                                                       |
| Grouped help and wrapper help                                                                                                                                       | Passed for `dt markdown`, both subcommands, and the wrapper.                                                  |
| Grouped and wrapper canonical-file smoke                                                                                                                            | Passed. Both modes report `UNCHANGED` and `summary ... SUCCESS 1`.                                            |
| Empty lists, frontmatter body delimiters, opaque code HTML, nested LF/CRLF fence payloads, hard breaks, center tables, and temp collisions                          | Passed for the repaired cases exercised by the current tests and direct probes.                               |
| List first-child code/heading, parser-backed escaped/code-pipe data cells, nested two-level heading descent, adjacent inline atoms, and recursive discovery failure | Failed in independent probes. See C07-C11.                                                                    |

The full pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The test expects `.config/opencode/package.json` to be empty while the existing file contains the OpenCode plugin
dependency. This remains unrelated to the formatter. The repository-wide Ty diagnostics are likewise outside the
formatter paths and were independently confirmed.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                               |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `pyproject.toml`, `uv.lock`, and the successful `uv sync` run provide the pinned dependency.                                           |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/{__init__,models}.py` and the stage modules exist with the requested public names.                   |
| 01/AC03 | ⚠      | `models.py:8-66`, `cli/markdown.py:15-24`, and the contract tests establish the surface, but C07-C11 leave public behavior incomplete. |


### Task 02

| AC      | Status | Evidence                                                                                                                                |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-143` exposes extraction, validation, and serialization; `test_frontmatter.py` exercises all three.                   |
| 02/AC02 | ✓      | `frontmatter.py:87-109` enforces the byte-zero opener, first exact closing line, missing-close error, and body preservation.            |
| 02/AC03 | ✓      | `frontmatter.py:52-117` rejects aliases, anchors, explicit tags, duplicates, unsupported nodes, invalid Unicode, and non-finite values. |
| 02/AC04 | ✓      | `frontmatter.py:140-230` implements deterministic key ordering, scalar codecs, framing, and the required blank line; exact tests pass.  |


### Task 03

| AC      | Status | Evidence                                                                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:35-128,511-523` provides byte-addressed AST and table/fence spans. C08 shows that required table cell forms are not owned.                                                           |
| 03/AC02 | ⚠      | `parser.py:197-346,448-483` owns the basic structures and repaired nested fence metadata, but parser-backed escaped/code-pipe cells fall back opaque in C08.                                    |
| 03/AC03 | ⚠      | `parser.py:423-445,631-739` proves many exact intervals and nested LF/CRLF fence metadata, but C08 rejects required parser-owned cell intervals and C10 exposes a semantic fallback path.       |
| 03/AC04 | ⚠      | The semantic-token pass and bounded fallback cover the tested delimiter, link, image, escape, and hard-break cases, but C10 changes adjacent inline semantics.                                  |
| 03/AC05 | ✓      | `parser.py:948-994` collects recognized and opaque code ranges before scanning HTML; direct inline, indented, fenced, and nested-code probes reject raw HTML while accepting code-looking HTML. |
| 03/AC06 | ✓      | `parser.py:942-945,1013-1024` enforces top-level H1 and source-break policy, and `parser.py:274-278` records task state in covered forms.                                                       |


### Task 04

| AC      | Status | Evidence                                                                                                                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94` defines the requested normalized state; `test_normalize.py` asserts state directly.                                                                                                      |
| 04/AC02 | ✗      | `normalize.py:491-535` inserts separators between adjacent inline nodes during wrapping. C10 shows semantic changes for `a[x](url)b` and `foo\\bar`.                                                          |
| 04/AC03 | ✗      | `normalize.py:221-285` skips `item.children[0]` whenever the first list child is not a paragraph. C07 loses valid list-item headings and fenced code.                                                         |
| 04/AC04 | ✗      | `normalize.py:398-483` and `render.py:118-126` do not preserve blank boundaries inside recursively rendered containers. C09 turns a paragraph before a generated separator into a setext heading on pass two. |
| 04/AC05 | ✗      | `normalize.py:343-370` contains the marker-width repair, but C08 prevents the ordered table algorithm from running for required escaped/code-pipe data cells.                                                 |
| 04/AC06 | ✓      | `normalize.py:420-463` uses parser-owned semantic payloads, preserves LF/CRLF payload bytes, maps shell aliases, and selects collision-safe fences in the covered direct and nested cases.                    |


### Task 05

| AC      | Status | Evidence                                                                                                                                                                                              |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✗      | `render.py:118-126` joins children of a nested normalized container with one LF, unlike the document-level blank-line join at `render.py:159`. C09 demonstrates non-idempotent nested heading output. |
| 05/AC02 | ✗      | `render.py:27-84,97-115` renders the normalized structures, but C07 drops first non-paragraph list children and C08 leaves required table cases opaque.                                               |
| 05/AC03 | ⚠      | `__init__.py:10-21` composes the typed stages and preserves the listed errors, but the invalid canonical behavior in C07-C10 remains observable through the public pipeline.                          |
| 05/AC04 | ⚠      | The golden corpus and idempotence tests pass for covered inputs, but the required uncovered cases identified in S03 are not represented by exact expected bytes.                                      |


### Task 06

| AC      | Status | Evidence                                                                                                                                                                                                                                                                                                                               |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ⚠      | `operations.py:21-35` resolves, sorts, deduplicates, and discovers normal paths, but C11 shows recursive discovery `OSError` escapes instead of becoming an operation result.                                                                                                                                                          |
| 06/AC02 | ✓      | `operations.py:85-112,189-218` preflights before writing, uses same-directory temporary files, stops after the first replacement error, and reports committed/untouched paths in covered cases.                                                                                                                                        |
| 06/AC03 | ✓      | `operations.py:38-83,91-103` captures bytes and identity, uses a destination-directory advisory lock, validates immediately before replace, preserves mode, and safely cleans only a temporary file created by this invocation. The uncooperating-writer limitation is explicitly documented in `operations.py:68-75` and the journal. |
| 06/AC04 | ✓      | `operations.py:118-131,189-224` implements the documented status precedence and format/check mappings for exercised outcomes.                                                                                                                                                                                                          |
| 06/AC05 | ⚠      | `operations.py:134-143` and the CLI emit the required records and digest-only mismatch diagnostics, but the discovery/read-error contract and its exact streams are not tested; C11 also escapes before a result exists.                                                                                                               |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-28` captures entry CWD, discovers the repository, delegates through `uv run --project`, and passes child streams and status in both modes.                                                                                                                                                        |
| 06/AC07 | ⚠      | The registration and representative CLI/wrapper tests pass, but the complete race, discovery, error-status, and parser/table contract matrix is incomplete.                                                                                                                                                                            |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                             |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 07/AC01 | ⚠      | `tests/markdown_formatter/fixtures/corpus/` covers the broad categories, but the edge-contract suite does not assert canonical ownership for C07-C10 or recursive discovery failure. |
| 07/AC02 | ✗      | Formatter-focused pytest, Ruff, and focused Ty pass, but C07-C11 remain. Full pytest and repository Ty are red only for the independently confirmed baseline issues described above. |


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

All reviewed changes remain within the approved formatter, CLI, wrapper, dependency, registration, and test scope. The
warnings above identify incomplete behavior and coverage inside that scope, not scope creep.


## Prior Review Resolution

| Review 08 finding                              | Status | Current evidence                                                                                                                                                                                                                                                                           |
| ---------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C01 Empty list items crash                     | ✓      | `normalize.py:232-236` initializes the empty branch; `test_edge_contract.py:302-307` confirms empty top-level and nested items no longer crash and converge. The new first-child loss is reported separately as C07 below.                                                                 |
| C02 Body delimiter isolation                   | ✓      | `frontmatter.py:99-117` limits YAML parsing to the extracted envelope; `test_frontmatter.py:27-39` and direct fenced-delimiter probes preserve body bytes.                                                                                                                                 |
| C03 Opaque code HTML masking                   | ✓      | `parser.py:966-977` scans code-looking ranges inside opaque blocks; direct opaque inline, indented, nested-code, and raw-HTML probes confirm code is masked while adjacent raw HTML still fails.                                                                                           |
| C04 Nested fence semantic payload/source spans | ✓      | `parser.py:318-343` derives semantic LF/CRLF payloads after container-prefix removal. `test_parser.py:203-216` confirms `payload == b"x" + line_ending`, valid marker/info spans, a complete enclosing fence span, and intentional `payload_span is None` for discontiguous nested source. |
| C05 List hard-break width and canonical bytes  | ✓      | `normalize.py:491-510` retains hard-break groups and `test_edge_contract.py:241-267` confirms canonical `\\` plus LF, per-side width, Unicode handling, and three-pass equality.                                                                                                           |
| C06 Temp collision cleanup                     | ✓      | `operations.py:87-110` tracks creation and inode identity before unlinking; `test_operations.py:232-261` confirms a pre-existing collision file survives and no created temporary remains.                                                                                                 |
| S01 Center-table marker width                  | ✓      | `normalize.py:361-365`, `render.py:60-74`, and `test_edge_contract.py:177-180,295-300` use two center markers and the required minimum width.                                                                                                                                              |
| S02 Regression coverage                        | ⚠      | The focused suite grew to 202 tests and covers the named repairs, but it still lacks the exact semantic assertions listed in S03 below.                                                                                                                                                    |


## Findings

### Summary

| Finding | Title                                                                    | Outcome |
| ------- | ------------------------------------------------------------------------ | ------- |
| C07     | First non-paragraph list children are silently discarded                 |         |
| C08     | Required escaped and code-pipe table cells fall back opaque              |         |
| C09     | Nested container rendering creates a non-idempotent setext heading       |         |
| C10     | Inline wrapping inserts bytes that change adjacent text semantics        |         |
| C11     | Recursive discovery filesystem errors escape the operation contract      |         |
| S03     | Required edge and operation contract coverage still has false-green gaps |         |


### Critical

#### C07: First non-paragraph list children are silently discarded


#### Where

`src/dot_tools/markdown_formatter/normalize.py:221-285`


#### Issue

The list normalizer obtains the first paragraph separately, then processes non-paragraph children with
`item.children[1:]`. When the first child is a fenced code block or a heading, that child is skipped entirely. This is
not an opaque fallback: the parser has recognized the child and the normalizer emits a shorter list item.

Independent probes reproduce data loss:

```text
format_document(b"# T\n\n- ```text\n  x\n  ```\n")
== b"# T\n\n- \n"

format_document(b"# T\n\n- # H\n")
== b"# T\n\n- \n"
```

Both inputs are parser-owned list structures. The approved subset includes fenced code, headings, and list-item block
children, and recognized headings inside containers remain in scope. Empty-list safety was repaired, but the repair now
preserves an empty marker by dropping valid content in a different empty-paragraph shape.


#### Impact

Valid Markdown content is silently destroyed. Formatting is not lossless, and the public document pipeline violates the
fail-closed requirement by neither normalizing nor preserving the containing list item unchanged.


#### Fix

Iterate every `item.children` entry rather than slicing from index one. Handle the first child and later children
through
the same paragraph, nested-list, and block-child paths, preserving headings and code blocks with the active list prefix.
Add exact-byte and semantic tests for a list whose first child is a heading, fenced code, indented code, block quote,
and
nested list, including task and nested-container variants.


#### Outcome


----

### Critical

#### C08: Required escaped and code-pipe table cells fall back opaque


#### Where

`src/dot_tools/markdown_formatter/parser.py:448-483`


#### Issue

For a parser-identified table, `_table_inlines` requires each physical cell to match the parser token's semantic
content. Escaped literal pipes remain in the physical source but are not decoded by `_inline_semantic`, so
`_semantic_cell_matches` returns false. Markdown-it also exposes a data cell containing a code-span pipe as truncated
content, so that case fails the same ownership check. `_blocks` then marks the entire table opaque at lines 227-230.

Independent probes show both required forms remain unchanged instead of receiving canonical table serialization:

```text
b"# T\n\n| h | x |\n| --- | --- |\n| a\\|b | y |\n"
```

and

```text
b"# T\n\n| h | x |\n| --- | --- |\n| a | `y|z` |\n"
```

`parse_document` reports `table.opaque is True` for both, and `format_document` returns the source unchanged. The
compatibility-table path handles some header cases, which is why the current table tests pass, but normal parser-backed
data rows do not satisfy the approved table contract.


#### Impact

Recognized pipe tables containing explicitly supported escaped pipes or code-span pipes are not normalized, aligned, or
re-rendered. The formatter fails the lossless canonical table requirement and gives false confidence because idempotence
alone passes for the opaque fallback.


#### Fix

Own physical cells using the table row parser and a source-aware inline scanner before comparing parser semantics.
Decode
backslash escapes for semantic comparison while retaining the encoded source interval, and handle code-span pipes as
cell content without allowing the table splitter to treat them as framing. Keep the complete table opaque only when the
physical interval cannot be proven. Add exact LF/CRLF tests for escaped and code-pipe cells in header and data rows,
including repeated cells, arbitrary backslash parity, canonical bytes, source spans, and three-pass output.


#### Outcome


----

### Critical

#### C09: Nested container rendering creates a non-idempotent setext heading


#### Where

`src/dot_tools/markdown_formatter/render.py:118-126,158-160`


#### Issue

Document-level normalized containers join child blocks with blank lines, but `_render_block` joins children of a nested
`NormalizedContainer` with one LF. A generated `---` separator therefore follows a paragraph without a blank boundary
inside a two-level block quote. CommonMark reparses the paragraph plus separator as a setext H2.

Independent probe:

```text
source = b"# T\n\n> > ## A\n> > body\n> > ### B\n"
first = format_document(source)
second = format_document(first)

first  == b"# T\n\n> > ## A\n> > body\n> > ---\n> > ### B\n"
second == b"# T\n\n> > ## A\n> > ## body\n> > ---\n> > ### B\n"
```

The second pass changes `body` into a heading. This is a recognized nested container, not an opaque preservation case.


#### Impact

Formatting changes document structure on a second pass and violates local heading spacing, downward-separator
placement, and idempotence. It also makes source-break semantics depend on container depth.


#### Fix

Use the same block-separation policy for every recursive container renderer. Preserve a blank line before and after a
generated separator and between adjacent normalized blocks wherever the containing syntax requires it. Add two-level
and deeper block-quote/list-container tests with paragraph-to-heading descent, source separator reuse, and three-pass
AST
equality.


#### Outcome


----

### Critical

#### C10: Inline wrapping inserts bytes that change adjacent text semantics


#### Where

`src/dot_tools/markdown_formatter/normalize.py:491-535`


#### Issue

`_wrap_inline_tokens` treats every inline node as a word token and inserts an ASCII space between adjacent nodes. The
parser's compatibility scanner can also split ordinary text around a backslash into separate text nodes. The normalizer
then inserts spaces that were not in the source and were not required for a structural escape.

Independent probes reproduce both forms:

```text
format_document(b"# T\n\na[x](url)b\n") == b"# T\n\na [x](url) b\n"
format_document(b"# T\n\nfoo\\bar\n") == b"# T\n\nfoo \\b ar\n"
```

The first source has adjacent ordinary text and a link. The second has a backslash before a non-punctuation code point,
which CommonMark treats as literal text rather than a Markdown escape. Both outputs are idempotent only because the
inserted spaces become the next input; idempotence does not prove semantic preservation.


#### Impact

The formatter changes rendered text and link adjacency for valid Markdown. This violates the inline codec requirement to
preserve ordinary text and the parser requirement that a backslash consume only the permitted escaped code point.


#### Fix

Wrap only at actual whitespace boundaries and preserve adjacency between inline atoms. Coalesce adjacent text intervals
before token-aware wrapping, or carry explicit separator ownership instead of unconditionally joining node tokens with a
space. Treat a backslash before a non-escapable character as one ordinary text interval. Add exact semantic-reparse
tests
for adjacent links, images, code, emphasis, escapes, Unicode, and literal backslashes.


#### Outcome


----

### Critical

#### C11: Recursive discovery filesystem errors escape the operation contract


#### Where

`src/dot_tools/markdown_formatter/operations.py:21-35`


#### Issue

Directory discovery calls `path.rglob("*.md")` and filesystem predicates without catching `OSError`. A simulated
discovery failure raises directly from `check_paths` instead of producing a `FileResult`, `OperationResult`, diagnostic,
and documented exit status.

Independent probe:

```text
monkeypatch Path.rglob to raise OSError("discovery fail")
check_paths([directory])
== raises OSError("discovery fail")
```

The rest of the operation layer catches file reads and maps them to `READ_ERROR`, but collection is an external
filesystem operation in the same public path.


#### Impact

Permission errors, directory races, and other discovery failures bypass the total result/status/diagnostic contract and
can crash the grouped CLI without the required exit 3 record. Multi-file safety and deterministic reporting cannot be
assured when collection fails partway through.


#### Fix

Catch `OSError` around directory traversal and path-stat operations. Return a sorted `READ_ERROR` or the explicitly
documented collection error result with `message="error"`, stable detail text, a diagnostic, and the correct operation
status and exit mapping. Add subprocess-level tests for recursive discovery failure and mixed discovery/read/mismatch
precedence.


#### Outcome


----

### Significant

#### S03: Required edge and operation contract coverage still has false-green gaps


#### Where

`tests/markdown_formatter/test_edge_contract.py:158-175,270-307`, `tests/markdown_formatter/test_operations.py`, and
the corpus fixtures under `tests/markdown_formatter/fixtures/corpus/`


#### Issue

The focused suite reports 202 passing tests, but several required boundaries either have no test or assert only
idempotence, which opaque preservation can satisfy without implementing the contract. Missing or insufficient assertions
include:

- canonical ownership and expected bytes for parser-backed escaped-pipe and code-span-pipe data cells;
- first-child list headings and fenced/indented code, where the current implementation loses content;
- two-level nested-container heading descent and generated separator spacing;
- adjacent inline atoms and non-escapable backslashes;
- recursive directory discovery errors, read-error records, and the full mixed status/exit/diagnostic precedence matrix.

The current table test at `test_edge_contract.py:158-175` checks `format_document(output) == output` and source-row
presence. An opaque output therefore passes even though the table was never normalized. The empty-list test at lines
302-307 likewise checks convergence but not preservation of first non-paragraph children.


#### Impact

The green formatter suite does not prove the plan's required edge and contract behavior and allowed the five current
blockers to survive multiple repair passes.


#### Fix

Add exact expected-byte, semantic-reparse, AST ownership, and source-span assertions for every case above. Add CLI
subprocess tests for discovery/read/preflight/write errors, all precedence combinations, sorted diagnostics, and exact
stdout/stderr/exit records. Assert that required recognized forms are not opaque rather than using idempotence as the
only oracle.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C07-C11 must be resolved before approval. S03 must be addressed in the same pass. The unrelated configure pytest
failure and repository-wide Ty diagnostics are independently confirmed baseline issues and are excluded from formatter
findings.
