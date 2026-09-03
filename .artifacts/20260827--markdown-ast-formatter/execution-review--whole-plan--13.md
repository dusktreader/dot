# Execution Review: Generic AST-based Markdown formatter

This independent iteration-13 review starts from the current worktree diff, rechecks every review-12 issue, and runs
the documented plan-wide formatter, CLI, wrapper, safety, and quality-gate checks.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--12.md`


## Scope

**whole-plan - Iteration 13**

The review covers the current formatter implementation, tests, fixtures, CLI, wrapper, dependency, and recorded
execution changes. The plan, journal, and prior reviews were read but not modified.


## Issue Summary

- **Critical**:    2
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                            | Result                                                                                                                                                                                         |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                   | Passed. `markdown-it-py==4.2.0` resolves.                                                                                                                                                      |
| `uv run pytest tests/markdown_formatter --no-cov`                           | Passed: 217 tests.                                                                                                                                                                             |
| `uv run pytest`                                                             | Failed: 530 passed, 1 failed, 2 warnings. The sole failure is the documented unrelated configure baseline. Coverage was 84.55%, above the 70% threshold.                                       |
| `uv run ruff check src tests`                                               | Passed.                                                                                                                                                                                        |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                                                                                                        |
| `uv run ty check`                                                           | Failed with 74 documented diagnostics outside formatter scope. No formatter path appears.                                                                                                      |
| `uv run dt markdown --help`, grouped subcommand help                        | Passed.                                                                                                                                                                                        |
| Wrapper help, check, and format smoke                                       | Passed. The temporary canonical fixture remained unchanged and reported `SUCCESS`.                                                                                                             |
| `git diff --check`                                                          | Passed.                                                                                                                                                                                        |
| Build                                                                       | Skipped. No project-documented build command exists.                                                                                                                                           |
| Review-12 fence matrix                                                      | Marker mismatch, short marker, longer marker, payload-like suffix, valid split recovery, and LF/CRLF payload preservation passed. A four-space over-indented closer still drops payload bytes. |
| Review-12 code-span probe                                                   | The reported single-line cases matched reparsed CommonMark payloads; a multiline soft-break case loses its padded payload and is covered by C02.                                               |
| Review-12 nested-code probe                                                 | LF and CRLF payload line endings and trailing spaces were preserved; three-pass output converged.                                                                                              |
| Review-12 ordered-list probe                                                | Blockquote list start `12.` remained `12.` and reparsed metadata remained 12.                                                                                                                  |
| Review-12 link probe                                                        | Prose and table destinations containing backslashes emitted canonical angle destinations and converged.                                                                                        |
| Review-12 table probe                                                       | LF and CRLF tab-edge cell bytes and spans were preserved and output converged.                                                                                                                 |

The repository-wide pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The repository-wide Ty diagnostics remain in the documented PDF, clipboard/Gmail, OpenCode cost/trend, configure,
Jira, and spinner paths. They are unrelated baselines.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | Dependency and lockfile are present; `uv sync` passed.                                                     |
| 01/AC02 | ✓      | Public models and formatter modules exist.                                                                 |
| 01/AC03 | ⚠      | Public signatures and CLI surface pass contract tests, but formatter-specific findings C01 and C02 remain. |


### Task 02

| AC      | Status | Evidence                                                                                      |
| ------- | ------ | --------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | `frontmatter.py:87-143`; focused frontmatter tests pass.                                      |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact delimiters, missing-close failure, and body preservation pass. |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted YAML safety and finite-value tests pass.                  |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical scalar, mapping, nesting, and framing tests pass.         |


### Task 03

| AC      | Status | Evidence                                                                                                                    |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:318-350` records code spans, but over-indented closers are treated as boundaries; see C01.                       |
| 03/AC02 | ⚠      | Requested blocks and inline nodes are covered, but malformed split-fence text can be misclassified; see C02.                |
| 03/AC03 | ✗      | `parser.py:433-437` drops a valid payload line after accepting an over-indented closer; see C01.                            |
| 03/AC04 | ✗      | `parser.py:645-649` falls back to a delimiter scanner that invents code inside an unclosed invalid-info paragraph; see C02. |
| 03/AC05 | ✓      | `parser.py:985-1031`; code-first raw-HTML masking and policy tests pass.                                                    |
| 03/AC06 | ✓      | `parser.py:1050-1061`; task state and thematic-break transition tests pass.                                                 |


### Task 04

| AC      | Status | Evidence                                                                                    |
| ------- | ------ | ------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94`; normalized-state tests pass.                                          |
| 04/AC02 | ✓      | `normalize.py:96-166,563-612`; wrapping, inline codecs, and code-span semantic probes pass. |
| 04/AC03 | ✓      | `normalize.py:242-323`; ordered starts, tasks, nested lists, and continuation probes pass.  |
| 04/AC04 | ✓      | `normalize.py:467-555`; heading and separator state is stable in the exercised cases.       |
| 04/AC05 | ✓      | `normalize.py:414-464`; table geometry, escaping, code pipes, and tab-edge probes pass.     |
| 04/AC06 | ✓      | `normalize.py:490-535`; code payload and fence state pass the LF/CRLF nested probes.        |


### Task 05

| AC      | Status | Evidence                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ⚠      | `render.py:168-196` renders canonical nodes, but unconditional block joining adds a blank line around a terminal-newline opaque block; see S01. |
| 05/AC02 | ✗      | Fence boundary preservation and invalid split-fence handling fail in C01 and C02.                                                               |
| 05/AC03 | ✓      | `src/dot_tools/markdown_formatter/__init__.py:10-27`; document pipeline and typed error propagation pass.                                       |
| 05/AC04 | ⚠      | Existing golden and idempotence fixtures pass, but they omit the C01, C02, and S01 cases.                                                       |


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

| AC      | Status | Evidence                                                                                                                                |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ⚠      | The generic corpus covers the listed categories, but omits over-indented closers, unclosed split recovery, and opaque-boundary spacing. |
| 07/AC02 | ✗      | Focused pytest and Ruff pass, but C01, C02, and S01 remain. Full pytest and repository Ty retain documented unrelated baselines.        |


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

| Review 12 finding                                                    | Status | Current evidence                                                                                                                                                                                                                                     |
| -------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Short indented fence closers are accepted and dropped            | ⚠      | The reported two-space short marker, mismatched marker, longer marker, payload-like suffix, and LF/CRLF cases now pass. However, the closer matcher still accepts unlimited indentation, so a four-space marker line is dropped as payload. See C01. |
| C02 Code-span payload spaces are trimmed twice                       | ✓      | `normalize.py:149-166`; independent source-versus-reparsed payload comparison passed for multiple leading/trailing-space cases.                                                                                                                      |
| C03 Nested code rendering changes CRLF payload bytes                 | ✓      | `render.py:137-152,204-218`; independent nested LF/CRLF and trailing-space probe passed through three formatting passes.                                                                                                                             |
| S01 Blockquote ordered lists lose their starting marker              | ✓      | `parser.py:274-277`, `normalize.py:242-251`; `12.` survives blockquote formatting and reparsed metadata remains 12.                                                                                                                                  |
| S02 Link destinations with backslashes remain noncanonical bare URLs | ✓      | `normalize.py:169-226`; prose and table backslash destinations emit canonical angle form and converge.                                                                                                                                               |
| S03 Table cell edge tabs are stripped despite the lossless algorithm | ✓      | `parser.py:512-536`, `normalize.py:414-464`; LF/CRLF spans and tab-edge output preserve the tab bytes.                                                                                                                                               |


## Findings

### Summary

| Finding | Title                                                             | Outcome |
| ------- | ----------------------------------------------------------------- | ------- |
| C01     | Over-indented fenced-code closers drop payload bytes              |         |
| C02     | Parser fallback rewrites soft-break code and split-fence text     |         |
| S01     | Opaque block boundaries add an extra blank line before separators |         |


### Critical

#### C01 Over-indented fenced-code closers drop payload bytes


#### Where

`src/dot_tools/markdown_formatter/parser.py:318-340,433-437`


#### Issue

`_is_fence_closer` permits any number of leading spaces or tabs. CommonMark permits at most three columns of
closing-fence
indentation after the active container prefix. For a top-level fence, a four-space line containing four backticks is
payload, but the parser accepts it as a closer before comparing only the marker run.


#### Impact

The formatter silently removes source code. This direct input:

````text
# T

```text
x
    ````
y
```text
````

produces a code payload containing only `x`, omitting the `    ```` and `y` lines. The focused suite does not cover the
maximum indentation boundary.


#### Fix

After removing only the proven container and opening-fence structural indentation, reject a closer with more than three
indent columns. Then require the closer to use the opener character and at least its marker length. Add LF and CRLF
regressions for zero, three, and four indentation columns, mismatched and short markers, payload-like suffixes, EOF, and
split recovery, asserting exact payload bytes and three-pass convergence.


#### Outcome


----

#### C02 Parser fallback rewrites soft-break code and split-fence text


#### Where

`src/dot_tools/markdown_formatter/parser.py:645-649,799-875`


#### Issue

When semantic inline-token association fails at a soft break, `_scan_inline` invokes the legacy delimiter scanner. That
scanner does not retain the parser's semantic code payload and can invent code nodes. A valid multiline padded code span
has these body bytes:

````text
`  x  `
x
````

The parser's CommonMark payload is `b" x "`, but the legacy node has only a raw payload span. The same fallback also
misclassifies an unclosed invalid-info paragraph such as the following as containing an inline code span:

````text
```foo`bar
x
````


#### Impact

The valid padded input formats first as:

````text
# T

``` x ```
x
````

The next pass emits a triple-backtick code span with payload `b"x"`, so the code payload changes from `b" x "` to
`b"x"` and the output is not idempotent. The invalid split-fence input also changes its literal backtick sequence
instead of preserving the unclosed, unrecognized construct.


#### Fix

Do not invoke the legacy delimiter scanner when the parser's semantic child stream cannot be associated exactly.
Preserve
the complete paragraph as opaque, or return ordinary text only when the parser token stream proves that representation.
Add LF and CRLF tests for padded multiline code spans, closed split recovery, short and over-indented candidate closers,
and unclosed split input with an intervening heading, asserting parser ownership, semantic tokens, exact bytes, and
three-pass output.


#### Outcome


----

### Significant

#### S01 Opaque block boundaries add an extra blank line before separators


#### Where

`src/dot_tools/markdown_formatter/normalize.py:475-487` and `src/dot_tools/markdown_formatter/render.py:168-196`


#### Issue

Opaque blocks retain their terminal line ending, but `render_document` joins every rendered block with two LF bytes.
For an opaque block followed by a downward heading, that creates two blank lines before the generated separator instead
of
the one blank line required by the separator contract.


#### Impact

This input:

```text
# T

\x00 opaque

## H
```

formats with `b"\\x00 opaque\\n\\n\\n---\\n\\n## H\\n"`. Opaque bytes remain intact, but heading and separator spacing
is
not exact. The output is stable, so the existing idempotence-only coverage is false-green for this boundary.


#### Fix

Use a boundary-aware block join that adds exactly the required separator bytes without stripping or rewriting an opaque
block's source. Add LF and CRLF tests with trailing opaque whitespace, a generated downward separator, and a second-pass
byte comparison.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 and C02 must be resolved before approval because they drop or rewrite formatter input. S01 must also be resolved to
satisfy exact container and separator spacing. The unrelated configure pytest failure and 74 repository-wide Ty
diagnostics remain documented baselines and are not formatter blockers.
