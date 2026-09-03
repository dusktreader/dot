# Execution Review: Generic AST-based Markdown formatter

This independent iteration-14 review starts from the current worktree diff, rechecks review 13 directly, and runs the
plan-wide formatter, CLI, wrapper, safety, and quality-gate checks.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--13.md`


## Scope

**whole-plan - Iteration 14**

The review covers the current formatter implementation, tests, fixtures, CLI, wrapper, dependency, and recorded
execution changes. The review started with the current diff. The plan, journal, design, and prior reviews were read but
not modified.


## Issue Summary

- **Critical**:    1
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                               | Result                                                                                                                                                                                   |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `git diff --stat`, `git diff --check`                                          | Current implementation diff inspected first; whitespace check passed.                                                                                                                    |
| `uv sync`                                                                      | Passed. `markdown-it-py==4.2.0` resolves.                                                                                                                                                |
| `uv run pytest tests/markdown_formatter --no-cov`                              | Passed: 229 tests.                                                                                                                                                                       |
| `uv run pytest`                                                                | 542 passed, 1 failed, 2 warnings. Coverage was 82.49%. The only failure is the documented unrelated configure assertion.                                                                 |
| `uv run ruff check src tests`                                                  | Passed.                                                                                                                                                                                  |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter`    | Passed.                                                                                                                                                                                  |
| `uv run ty check`                                                              | Failed with the documented 74-diagnostic repository baseline outside formatter scope. No formatter path appears.                                                                         |
| `uv run dt markdown --help`, grouped format/check help                         | Passed.                                                                                                                                                                                  |
| `./.agents/tools/markdown-format.py --help`                                    | Passed.                                                                                                                                                                                  |
| Target wrapper check and format smoke on the canonical fixture                 | Passed. Both reported `UNCHANGED` and `summary ... SUCCESS 1`.                                                                                                                           |
| Review-13 direct fence, inline, split-fence, nested, and opaque-boundary probe | All requested cases passed except an unclosed fenced block whose payload reaches EOF without a line ending. Its payload changed from `b"x"` to `b"x\\n"` after formatting and reparsing. |

The repository-wide pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics remain in the documented PDF, clipboard/Gmail, OpenCode cost/trend, configure, Jira,
and spinner paths. They are unrelated baselines.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                 |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| 01/AC01 | ✓      | `pyproject.toml`, `uv.lock`; `uv sync` passed.                                                                           |
| 01/AC02 | ✓      | Public formatter package and model modules exist.                                                                        |
| 01/AC03 | ⚠      | Public signatures and grouped CLI contract pass focused tests; the formatter-specific EOF payload defect remains in C01. |


### Task 02

| AC      | Status | Evidence                                                                                   |
| ------- | ------ | ------------------------------------------------------------------------------------------ |
| 02/AC01 | ✓      | `frontmatter.py:87-143`; focused frontmatter tests pass.                                   |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiter, missing-close, and body-preservation tests pass. |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted YAML safety and finite-value tests pass.               |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical scalar, mapping, nesting, and framing tests pass.      |


### Task 03

| AC      | Status | Evidence                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | `parser.py:112-128,187-350`; byte-addressed AST and code metadata are exercised by parser tests.              |
| 03/AC02 | ✓      | `parser.py:197-289`; requested blocks, fences, containers, tables, and inline constructs pass focused tests.  |
| 03/AC03 | ✓      | `parser.py:392-483`; exact ownership, recursive reconstruction, CRLF, astral, and opaque fallback tests pass. |
| 03/AC04 | ✓      | `parser.py:646-814`; semantic token association has no active legacy delimiter fallback.                      |
| 03/AC05 | ✓      | `parser.py:1027-1073`; code-first raw-HTML masking and policy tests pass.                                     |
| 03/AC06 | ✓      | `parser.py:1092-1103`; task state and thematic-break transition tests pass.                                   |


### Task 04

| AC      | Status | Evidence                                                                                       |
| ------- | ------ | ---------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94`; normalized-state tests pass.                                             |
| 04/AC02 | ✓      | `normalize.py:96-239,563-612`; wrapping, inline codecs, and code-span semantic tests pass.     |
| 04/AC03 | ✓      | `normalize.py:242-369`; list order, task state, nested structure, and continuation tests pass. |
| 04/AC04 | ✓      | `normalize.py:467-487`; heading state and separator tests pass.                                |
| 04/AC05 | ✓      | `normalize.py:414-464`; table geometry, escaping, code pipes, and edge tests pass.             |
| 04/AC06 | ✓      | `normalize.py:490-535`; code payload and nested fence state pass the focused LF/CRLF tests.    |


### Task 05

| AC      | Status | Evidence                                                                                                                                |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:168-196`; canonical rendering passes, but adding a synthetic newline before an EOF closer changes the reparsed code payload. |
| 05/AC02 | ⚠      | Code, table, inline, list, and separator fixtures pass; the direct EOF fence semantic assertion fails in C01.                           |
| 05/AC03 | ✓      | `src/dot_tools/markdown_formatter/__init__.py:10-27`; pipeline and typed-error tests pass.                                              |
| 05/AC04 | ⚠      | Existing golden and idempotence fixtures pass, but the EOF-without-LF boundary is not covered and fails the direct probe.               |


### Task 06

| AC      | Status | Evidence                                                                                                          |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-40`; collection, discovery, sorting, deduplication, and explicit errors pass.                   |
| 06/AC02 | ✓      | `operations.py:90-117,195-230`; preflight, atomic replacement, stop-on-write-error, and cleanup tests pass.       |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshots, destination checks, locks, fsync, mode preservation, and collision tests pass. |
| 06/AC04 | ✓      | `operations.py:123-136,195-230`; status precedence and format/check mappings pass.                                |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-25`; records, streams, diagnostics, digests, and exits pass.         |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, discovery, delegation, and passthrough pass.               |
| 06/AC07 | ✓      | `src/dot_tools/cli/main.py:31-39`; grouped registration and wrapper/CLI contract tests pass.                      |


### Task 07

| AC      | Status | Evidence                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | Generic corpus coverage passes, but it omits the EOF-without-LF fenced-payload boundary exposed by the direct probe.                            |
| 07/AC02 | ✗      | Focused pytest and Ruff pass, but formatter-specific C01 remains. Full pytest and repository Ty retain only the documented unrelated baselines. |


## Scope Verification

| File or path                                                            | Justification                               | Status |
| ----------------------------------------------------------------------- | ------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency                          | ✓      |
| `uv.lock`                                                               | Task 01 dependency lock                     | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public result models                | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document pipeline           | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML                     | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, policy, and repairs | ✓      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repairs           | ✓      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repairs               | ✓      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 safe operations                     | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                       | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility wrapper               | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 coverage                | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                            | ✓      |

The implementation remains within the approved formatter, dependency, CLI, wrapper, registration, test, fixture, and
journal scope. No unrelated production subsystem was changed.


## Prior Review Resolution

| Review 13 finding                                                     | Status | Current evidence                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Over-indented fenced-code closers drop payload bytes              | ⚠      | Zero, three, and four indentation columns, marker mismatch/length, EOF with a payload line ending, and nested fences now preserve exact payloads and converge. An unclosed top-level fence ending at EOF without a line ending still changes `b"x"` to `b"x\\n"` after rendering and reparsing. See C01. |
| C02 Parser fallback rewrites soft-break code and split-fence text     | ✓      | `parser.py:646-668` no longer invokes the legacy scanner. LF/CRLF padded code retains semantic `b" x "`; invalid-info split paragraphs remain text without code nodes; valid split recovery and three-pass output pass.                                                                                  |
| S01 Opaque block boundaries add an extra blank line before separators | ✓      | `render.py:204-217` adds only missing LF bytes. LF/CRLF opaque bytes, trailing whitespace, generated separators, and three-pass output pass.                                                                                                                                                             |


## Findings

### Summary

| Finding | Title                                               | Outcome |
| ------- | --------------------------------------------------- | ------- |
| C01     | Unclosed EOF fences gain a semantic payload newline |         |


### Critical

#### C01 Unclosed EOF fences gain a semantic payload newline


#### Where

`src/dot_tools/markdown_formatter/parser.py:318-346`, `src/dot_tools/markdown_formatter/normalize.py:503-518`, and
`src/dot_tools/markdown_formatter/render.py:176-179`


#### Issue

The parser correctly records an unclosed fenced source ending at EOF without a line ending as `CodePayload.payload ==
b"x"`. Normalization retains that payload, but rendering unconditionally appends `b"\\n"` before the synthetic closing
fence whenever the payload does not end in a line ending. The output for `b"# T\\n\\n```text\\nx"` therefore contains a
new physical payload line ending, and reparsing returns `b"x\\n"`.


#### Impact

Formatting changes code payload semantics at the exact EOF boundary. The output is idempotent, but idempotence does not
make the first-pass payload change safe. This violates the plan's requirement to preserve code payload bytes and the
requested EOF source/semantic assertion.


#### Fix

Preserve an unclosed fenced block whose payload has no terminal line ending as an opaque source region, or introduce an
explicit unclosed-code representation that does not synthesize a payload newline. Add LF/CRLF boundary tests that
compare
the original `CodePayload.payload`, reparsed payload, exact output bytes, and three formatting passes.


#### Outcome


----

### Significant

None.


### Trivial

None.


## Skills Applied

- `review-implementation-execution`: project-local
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 must be resolved before approval because formatting changes a fenced code payload at EOF. The review-13 C02 and S01
findings are resolved. The unrelated configure pytest failure and 74 repository-wide Ty diagnostics remain documented
baselines and are not formatter blockers.
