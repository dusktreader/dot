# Execution Review: Generic AST-based Markdown formatter

This independent iteration-11 review starts from the current worktree diff, rechecks every prior finding C01-C05 and
S01-S02, and exercises the approved parser, normalization, rendering, operations, CLI, and wrapper contracts directly.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--10.md`


## Scope

**whole-plan - Iteration 11**

The review covers the current formatter diff and all formatter files and tests listed by the journal. The plan, journal,
and prior review were read but not modified. The re-review explicitly validates prior findings, exact bytes, parser
ownership and source spans, semantic reparses, and three-pass idempotence.


## Issue Summary

- **Critical**:    1
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                            | Result                                                                                                  |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                   | Passed. The environment resolves `markdown-it-py==4.2.0`.                                               |
| `uv run pytest tests/markdown_formatter --no-cov`                           | Passed: 204 tests.                                                                                      |
| `uv run pytest`                                                             | Failed: 517 passed, 1 failed, 2 warnings. The failure is the documented unrelated configure baseline.   |
| `uv run ruff check src tests`                                               | Passed: `All checks passed!`.                                                                           |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                 |
| `uv run ty check`                                                           | Failed with 74 diagnostics outside formatter scope. No formatter path appears.                          |
| `git diff --check`                                                          | Passed.                                                                                                 |
| `uv run dt markdown --help`                                                 | Passed.                                                                                                 |
| `uv run dt markdown format --help`                                          | Passed.                                                                                                 |
| `uv run dt markdown check --help`                                           | Passed.                                                                                                 |
| `~/.agents/tools/markdown-format.py --help`                                 | Passed.                                                                                                 |
| Wrapper `check` and `format` smoke on the approved design document          | Passed. Both report `UNCHANGED` and `summary ... SUCCESS 1`.                                            |
| Direct prior-finding matrix                                                 | C01, C02, C03, C05, and S01 pass. C04 remains a formatter-specific semantic regression.                 |
| Direct three-pass matrix                                                    | Passes for the corrected cases; fails the C04 block-quote list case because pass 2 changes bytes again. |

The repository-wide pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The failing test compares the existing `.config/opencode/package.json` with an empty dependency mapping. This is an
unrelated configure baseline, not a formatter blocker. The repository-wide Ty run reports the documented 74 baseline
diagnostics in PDF, clipboard/Gmail, OpenCode cost/trend, configure, Jira, and spinner paths. The formatter-only Ty run
passes, so those diagnostics are unrelated baselines rather than formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 01/AC01 | ✓      | `pyproject.toml`, `uv.lock`, and the passed `uv sync` command.                                                                                         |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and the formatter stage modules.                                                                     |
| 01/AC03 | ⚠      | Public models, signatures, and CLI surface exist, but C04 leaves the public formatter pipeline semantically incorrect for a valid recursive container. |


### Task 02

| AC      | Status | Evidence                                                                                                             |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-143`; focused frontmatter tests pass.                                                             |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; byte-zero open, exact first close, missing-close failure, and body preservation pass.       |
| 02/AC03 | ✓      | `frontmatter.py:52-137,204-235`; unsafe YAML forms, finite-real validation, and type-preserving reparse probes pass. |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; exact serializer and adversarial finite-real roundtrip probes pass.                        |


### Task 03

| AC      | Status | Evidence                                                                                                                                    |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:35-128,286-348`; byte-addressed AST, table rows/cells, and code metadata spans were directly checked.                            |
| 03/AC02 | ✓      | `parser.py:112-128,197-350,612-857`; CommonMark-plus-table ownership and requested inline/block forms pass the focused and direct matrices. |
| 03/AC03 | ✓      | `parser.py:179-194,429-451,947-958`; repeated text, astral UTF-8, CRLF, and nested ownership slices were directly verified.                 |
| 03/AC04 | ✓      | `parser.py:612-857`; semantic-token association, bounded fallback, recursive reconstruction, and opaque fallback pass the prior matrix.     |
| 03/AC05 | ✓      | `parser.py:967-1013`; code-first raw-HTML masking and policy probes pass.                                                                   |
| 03/AC06 | ✓      | `parser.py:961-1043`; task state and thematic-break transition validation pass.                                                             |


### Task 04

| AC      | Status | Evidence                                                                                                                                                                                                  |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94,527-529`; normalized state tests pass.                                                                                                                                                |
| 04/AC02 | ✓      | `normalize.py:96-163,532-581`; CRLF prose, inline ownership, wrapping, and code-span state pass.                                                                                                          |
| 04/AC03 | ✗      | `normalize.py:210-290,309-336`; a valid list inside a block quote with a heading child prepends the structural list marker to heading content, causing repeated formatting to add another `- #`. See C04. |
| 04/AC04 | ✓      | `normalize.py:436-524`; heading separators and ordinary nested container cases pass.                                                                                                                      |
| 04/AC05 | ✓      | `normalize.py:381-433`; table geometry, parity, cell canonicalization, and zero-cell/extra-cell probes pass.                                                                                              |
| 04/AC06 | ✓      | `normalize.py:459-504`; code payload metadata, marker selection, and empty-payload state pass.                                                                                                            |


### Task 05

| AC      | Status | Evidence                                                                                                                                                 |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✓      | `render.py:162-190`; recognized nodes use LF and empty code payloads do not gain a synthetic newline.                                                    |
| 05/AC02 | ✓      | `render.py:18-159`; code, list, heading, table, opaque, and inline render probes pass except the C04 input.                                              |
| 05/AC03 | ✓      | `src/dot_tools/markdown_formatter/__init__.py:10-27`; document orchestration and exception propagation pass.                                             |
| 05/AC04 | ⚠      | 204 focused tests and exact corpus fixtures pass, but the direct C04 semantic reparse and three-pass probe exposes an untested recursive-container path. |


### Task 06

| AC      | Status | Evidence                                                                                                                                                               |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-40`; sorting, lexical deduplication, recursive discovery, explicit path errors, and zero discovery pass.                                             |
| 06/AC02 | ✓      | `operations.py:151-175,195-230`; all-file preparation, atomic replacement, stop-on-first-write-error, commit sets, and cleanup pass.                                   |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshot identity/content/type/mode checks, lock, fsync, replacement, symlink/read-only rejection, and collision safety probes pass.           |
| 06/AC04 | ✓      | `operations.py:123-137,195-230`; status precedence and format/check mappings pass the direct operation matrix.                                                         |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-25`; exact records, streams, digest-only mismatch diagnostics, partial writes, and exit codes pass the direct CLI matrix. |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; entry CWD capture, repository discovery, absolute operand delegation, stream passthrough, and no-project exit 2 pass.        |
| 06/AC07 | ✓      | `src/dot_tools/cli/main.py:31-39` and focused CLI/wrapper tests; grouped registration and smoke commands pass.                                                         |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                      |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Corpus fixtures cover the listed categories, but the direct C04 recursive block-quote list case is not in the oracle set.                                                     |
| 07/AC02 | ✗      | Formatter-focused tests, Ruff, and formatter-only Ty pass; the formatter-specific C04 finding remains. Repository pytest and Ty failures are separately documented baselines. |


## Scope Verification

| File or path                                                            | Justification                               | Status |
| ----------------------------------------------------------------------- | ------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency                          | ✓      |
| `uv.lock`                                                               | Task 01 dependency lock                     | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public result models                | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document pipeline           | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML                     | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, policy, and repairs | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repairs           | ⚠      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repairs               | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 safe operations                     | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                       | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility wrapper               | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 coverage                | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                            | ✓      |

The current diff remains within the approved formatter, dependency, CLI, wrapper, registration, test, fixture, and
journal scope. No unrelated production subsystem was changed.


## Prior Review Resolution

| Review 10 finding                                                   | Status | Current evidence                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Fence closing rules accept the wrong marker and discard payload | ✓      | `parser.py:318-348`; exact mismatched-character, shorter, longer, payload-marker, EOF, LF, and CRLF probes retain `CodePayload.payload`, preserve the enclosing source span, reparse semantically, and converge in three passes.                                                                                                                                                                  |
| C02 Empty closed fences gain an unowned payload newline             | ✓      | `render.py:170-173` and `render.py:143-146`; `b"```text\\n```\\n"` remains exactly that for an empty payload, while a real blank payload remains `b"\\n"`; parser payload and three-pass bytes agree.                                                                                                                                                                                             |
| C03 Recognized CRLF prose bypasses LF canonicalization              | ✓      | `normalize.py:96-138,141-147,516-519`; recognized LF/CRLF prose outputs LF-only bytes, including astral text and hard breaks, while opaque/code payloads retain their contractually preserved bytes.                                                                                                                                                                                              |
| C04 Mixed list child blocks are reordered and reparsed differently  | ✗      | `normalize.py:309-336` removes list markers before cloning a child but does not remove the outer block-quote prefix before heading content extraction. Direct input `b"# T\\n\\n> - # H\\n>   text\\n"` outputs `b"# T\\n\\n> - # - # H\\n> \\n>   text\\n"`; the second and third passes add another `- #` each time. The output changes valid heading content and is not three-pass idempotent. |
| S01 Table cells bypass the canonical inline codec for links         | ✓      | `normalize.py:419-433`; direct bare-title, angle-destination, image-title, balanced-parenthesis, and hard-break table probes use the recursive inline path and canonicalize bare quoted titles without changing code-span pipes.                                                                                                                                                                  |
| S02 Focused coverage permits false-green whole-plan claims          | ✓      | `test_edge_contract.py`, `test_parser.py`, `test_frontmatter.py`, `test_operations.py`, and the full 204-test focused run now cover C01-C03, C05, S01, ownership/spans, reparses, and three-pass checks. The newly exposed C04 case is a remaining coverage gap, not a false-green resolution.                                                                                                    |


## Findings

### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| C01     | Block-quote list heading content grows on every formatting pass |         |


### Critical

#### C01: Block-quote list heading content grows on every formatting pass


#### Where

`src/dot_tools/markdown_formatter/normalize.py:309-336`, specifically the `heading_source` extraction in
`_list_child_without_marker`.


#### Issue

The list-child clone removes an item marker from the first physical line, then strips block-quote prefixes from the
clone. For a heading nested in a list nested in a block quote, `child.source` is `b"> - # H\\n"`. The first loop removes
the list marker only when it is at byte 0, so the quote-prefixed marker remains. `_strip_container_prefix` then produces
`b"- # H\\n"`, and the heading branch removes the `#` syntax but leaves `b"- # H"` as heading content. Rendering emits
`b"> - # - # H\\n"`, adding structural text to the heading. On the next parse the same path repeats, so output is not
idempotent.


#### Impact

This is a valid recursive list/container input. The formatter changes heading semantics, violates the active-prefix list
contract, and fails the required three-pass idempotence guarantee. It is a formatter blocker independent of the
unrelated
configure and repository Ty baselines.


#### Evidence

```text
source:  b"# T\\n\\n> - # H\\n>   text\\n"
pass 1:  b"# T\\n\\n> - # - # H\\n> \\n>   text\\n"
pass 2:  b"# T\\n\\n> - # - # - # H\\n> \\n>   text\\n"
pass 3:  b"# T\\n\\n> - # - # - # - # H\\n> \\n>   text\\n"
```

The source parser identifies a non-opaque block quote, bullet list, list item, heading, and paragraph. The output
reparses to the same block shape but with different heading text, so structural convergence alone does not prove
semantic
preservation.


#### Fix

Strip all proven container prefixes before removing the list marker, or use the parser-owned heading inline/source span
instead of reconstructing heading content from `clone.source`. Add an exact regression that asserts source and output
heading semantics, parser ownership and source slices, semantic reparse equality, and identical first, second, and third
output bytes for LF and CRLF block-quote list inputs.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local skill
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 must be resolved before approval. The unrelated configure pytest failure and 74 repository-wide Ty diagnostics are
documented baselines and are not formatter blockers. Approval is withheld solely because the formatter-specific C01
regression remains.
