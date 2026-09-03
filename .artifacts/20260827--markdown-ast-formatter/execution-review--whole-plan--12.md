# Execution Review: Generic AST-based Markdown formatter

This independent iteration-12 review starts from the current worktree diff, resolves review 11 C01, and rechecks the
formatter against the approved plan with focused QA and adversarial byte and semantic probes.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`
- **Approved design**: `.artifacts/20260827--markdown-ast-formatter/design-plan.md`
- **Prior review**: `.artifacts/20260827--markdown-ast-formatter/execution-review--whole-plan--11.md`


## Scope

**whole-plan - Iteration 12**

The review covers the current formatter diff and all formatter files, tests, fixtures, CLI, wrapper, dependency, and
journal changes recorded across the plan. The plan, journal, and prior reviews were read but not modified. Review 11 C01
was checked for LF and CRLF heading ownership, exact source spans, semantic reparsing, and three-pass byte convergence.


## Issue Summary

- **Critical**:    3
- **Significant**: 3
- **Trivial**:     0


## Verification Evidence

| Command or probe                                                            | Result                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv sync`                                                                   | Passed. The environment resolves `markdown-it-py==4.2.0`.                                                                                                                                                               |
| `uv run pytest tests/markdown_formatter --no-cov`                           | Passed: 206 tests.                                                                                                                                                                                                      |
| `uv run pytest`                                                             | Failed: 519 passed, 1 failed, 2 warnings. The sole failure is the documented unrelated configure baseline. Coverage reached 84.21%, above the 70% threshold.                                                            |
| `uv run ruff check src tests`                                               | Passed: `All checks passed!`.                                                                                                                                                                                           |
| `uv run ty check src/dot_tools/markdown_formatter tests/markdown_formatter` | Passed.                                                                                                                                                                                                                 |
| `uv run ty check`                                                           | Failed with 74 diagnostics outside formatter scope. No formatter path appears.                                                                                                                                          |
| `git diff --check`                                                          | Passed.                                                                                                                                                                                                                 |
| `uv run dt markdown --help`, grouped subcommand help                        | Passed.                                                                                                                                                                                                                 |
| Wrapper `--help`, `check`, and canonical `format` smoke                     | Passed. The canonical fixture remained unchanged and reported `summary ... SUCCESS 1`.                                                                                                                                  |
| Review 11 C01 LF/CRLF probe                                                 | Passed. Heading content is `H`, its span slices exactly `H`, and first, second, and third output bytes match for both line endings.                                                                                     |
| Independent boundary probes                                                 | Failed for short indented fence closers, padded inline-code semantic preservation, nested code CRLF preservation, blockquote ordered-list starts, link destination canonicalization, and table edge tabs. See findings. |
| Build                                                                       | Skipped (no project-documented build command).                                                                                                                                                                          |

The repository-wide pytest failure is:

```text
FAILED tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__does_not_install_opencode_npm_dependencies
E       AssertionError: assert {'dependencies': {'@opencode-ai/plugin': '1.18.14'}} == {}
```

The failing test compares the existing `.config/opencode/package.json` with an empty dependency mapping. The 74
repository-wide Ty diagnostics remain in the documented PDF, clipboard/Gmail, OpenCode cost/trend, configure, Jira, and
spinner paths. Formatter-only Ty passes, so these are unrelated baselines rather than formatter findings.


## Acceptance Criteria Verification

### Task 01

| AC      | Status | Evidence                                                                                                                       |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| 01/AC01 | ✓      | `pyproject.toml:10-16`, `uv.lock`, and the passed `uv sync` command.                                                           |
| 01/AC02 | ✓      | `src/dot_tools/markdown_formatter/models.py:8-66` and the stage modules exist.                                                 |
| 01/AC03 | ⚠      | Public models, signatures, and CLI surface exist, but the public pipeline still exposes the formatter-specific findings below. |


### Task 02

| AC      | Status | Evidence                                                                                                                 |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| 02/AC01 | ✓      | `frontmatter.py:87-143`; focused frontmatter tests pass.                                                                 |
| 02/AC02 | ✓      | `frontmatter.py:87-117`; exact byte-zero opening, first closing line, missing-close failure, and body preservation pass. |
| 02/AC03 | ✓      | `frontmatter.py:52-137`; restricted YAML safety and finite-value checks pass.                                            |
| 02/AC04 | ✓      | `frontmatter.py:140-235`; canonical mapping, scalar, and framing tests pass.                                             |


### Task 03

| AC      | Status | Evidence                                                                                                                                 |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ⚠      | `parser.py:318-348` exposes code metadata spans, but the closer test incorrectly counts indentation. See C01.                            |
| 03/AC02 | ⚠      | `parser.py:197-350` owns the requested structures, but a valid fenced-code payload can be discarded. See C01.                            |
| 03/AC03 | ⚠      | `parser.py:451-458` proves many exact intervals, but the current fence boundary does not prove ownership before dropping bytes. See C01. |
| 03/AC04 | ✓      | `parser.py:619-965`; semantic-token association, bounded fallback, recursive reconstruction, and inline ownership tests pass.            |
| 03/AC05 | ✓      | `parser.py:974-1020`; code-first raw-HTML masking and policy tests pass.                                                                 |
| 03/AC06 | ✓      | `parser.py:968-1049`; task state and thematic-break transition tests pass.                                                               |


### Task 04

| AC      | Status | Evidence                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | `normalize.py:16-94`; normalized state tests pass.                                                                                              |
| 04/AC02 | ✗      | `normalize.py:149-163` trims one space again after consuming markdown-it's already normalized code payload. See C02.                            |
| 04/AC03 | ✗      | `normalize.py:210-217` defaults a blockquote list's first ordered marker to `1.` instead of preserving `12.`. See S01.                          |
| 04/AC04 | ✓      | `normalize.py:436-524`; heading spacing and separator probes pass, including review 11 C01's nested heading case.                               |
| 04/AC05 | ✗      | `parser.py:503-525` and `normalize.py:344-378` strip tabs from cell edges even though the approved algorithm strips only ASCII spaces. See S03. |
| 04/AC06 | ⚠      | `normalize.py:459-503` retains code state, but nested rendering later changes CRLF payload line endings. See C03.                               |


### Task 05

| AC      | Status | Evidence                                                                                                                                                      |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✗      | `render.py:133-146` uses `splitlines()` for nested blocks and therefore changes nested code payload CRLF to LF. See C03.                                      |
| 05/AC02 | ✗      | Code-span semantic preservation fails for the multiple-space payload probe, and fenced closer validation fails for an indented short marker. See C01 and C02. |
| 05/AC03 | ✓      | `src/dot_tools/markdown_formatter/__init__.py:10-27`; document orchestration and exception propagation pass.                                                  |
| 05/AC04 | ⚠      | Golden and idempotence fixtures pass, but they omit the semantic and byte-preservation cases identified in C01-C03.                                           |


### Task 06

| AC      | Status | Evidence                                                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | `operations.py:15-40`; collection, recursive discovery, lexical deduplication, explicit errors, and zero discovery pass.   |
| 06/AC02 | ✓      | `operations.py:90-117,195-230`; prepare-all, atomic replacement, stop-on-first-write-error, commit sets, and cleanup pass. |
| 06/AC03 | ✓      | `operations.py:43-117`; snapshots, destination safety, lock coverage, fsync, mode preservation, and collision tests pass.  |
| 06/AC04 | ✓      | `operations.py:123-136,195-230`; status precedence and format/check mappings pass.                                         |
| 06/AC05 | ✓      | `operations.py:139-148`, `cli/markdown.py:15-25`; records, diagnostics, digests, streams, and exit mappings pass.          |
| 06/AC06 | ✓      | `.agents/tools/markdown-format.py:11-25`; CWD capture, repository discovery, delegation, and passthrough pass.             |
| 06/AC07 | ✓      | `src/dot_tools/cli/main.py:31-39`; grouped registration and wrapper/CLI smoke tests pass.                                  |


### Task 07

| AC      | Status | Evidence                                                                                                                                                                 |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 07/AC01 | ⚠      | Corpus fixtures cover the listed categories, but omit the failing short-closer, padded-code, nested-CRLF, ordered-quote, link-backslash, and tab-edge cases.             |
| 07/AC02 | ✗      | Formatter pytest, Ruff, and formatter-only Ty pass, but six formatter-specific findings remain. Repository pytest and Ty also retain the documented unrelated baselines. |


## Scope Verification

| File or path                                                            | Justification                               | Status |
| ----------------------------------------------------------------------- | ------------------------------------------- | ------ |
| `pyproject.toml`                                                        | Task 01 dependency                          | ✓      |
| `uv.lock`                                                               | Task 01 dependency lock                     | ✓      |
| `src/dot_tools/markdown_formatter/models.py`                            | Task 01 public result models                | ✓      |
| `src/dot_tools/markdown_formatter/__init__.py`                          | Tasks 01 and 05 document pipeline           | ✓      |
| `src/dot_tools/markdown_formatter/frontmatter.py`                       | Task 02 restricted YAML                     | ✓      |
| `src/dot_tools/markdown_formatter/parser.py`                            | Task 03 parsing, spans, policy, and repairs | ⚠      |
| `src/dot_tools/markdown_formatter/normalize.py`                         | Task 04 normalization and repairs           | ⚠      |
| `src/dot_tools/markdown_formatter/render.py`                            | Task 05 rendering and repairs               | ⚠      |
| `src/dot_tools/markdown_formatter/operations.py`                        | Task 06 safe operations                     | ✓      |
| `src/dot_tools/cli/markdown.py`                                         | Task 06 Typer adapter                       | ✓      |
| `src/dot_tools/cli/main.py`                                             | Task 06 command registration                | ✓      |
| `.agents/tools/markdown-format.py`                                      | Task 06 compatibility wrapper               | ✓      |
| `tests/markdown_formatter/` and fixtures                                | Tasks 02 through 07 coverage                | ⚠      |
| `.artifacts/20260827--markdown-ast-formatter/implementation-journal.md` | Execution record                            | ✓      |

The implementation remains within the approved formatter, dependency, CLI, wrapper, registration, test, fixture, and
journal scope. No unrelated production subsystem was changed.


## Prior Review Resolution

| Review 11 finding                                                   | Status | Current evidence                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 Block-quote list heading content grows on every formatting pass | ✓      | `parser.py:396-405` strips the proven list marker after container prefixes, and `normalize.py:309-335` strips prefixes before cloning. `test_edge_contract.py:288-307` and the independent LF/CRLF probe verify exact `H` ownership, semantic reparsing, and identical first, second, and third output bytes. |


## Findings

### Summary

| Finding | Title                                                            | Outcome |
| ------- | ---------------------------------------------------------------- | ------- |
| C01     | Short indented fence closers are accepted and dropped            |         |
| C02     | Code-span payload spaces are trimmed twice                       |         |
| C03     | Nested code rendering changes CRLF payload bytes                 |         |
| S01     | Blockquote ordered lists lose their starting marker              |         |
| S02     | Link destinations with backslashes remain noncanonical bare URLs |         |
| S03     | Table cell edge tabs are stripped despite the lossless algorithm |         |


### Critical

#### C01 Short indented fence closers are accepted and dropped


#### Where

`src/dot_tools/markdown_formatter/parser.py:318-348`, specifically the closer test at lines 329-331.


#### Issue

The parser compares `len(closing.group(0).rstrip(...))` with the opening marker length. Leading indentation is included
in
that length. A top-level opener of three backticks therefore accepts a valid payload line containing two backticks when
the line begins with two spaces.


#### Impact

The formatter silently deletes code payload bytes. For the probe source with a three-backtick text fence, an `x` payload
line, and a two-backtick line prefixed by two spaces, the parser records only `b\"x\\n\"` and the formatter emits a
fence containing only `x`. The source line `b\"  ``\\n\"` is neither a valid closer nor preserved payload. This violates
fenced-code preservation, parser ownership, and fail-closed behavior.


#### Fix

Compare only the closing marker run, requiring the same character and a run at least as long as the opener. Treat a
short indented run as payload. Add LF and CRLF tests for mismatched, short, longer, payload-marker, and EOF cases with
semantic payload and three-pass assertions.


#### Outcome


----

#### C02 Code-span payload spaces are trimmed twice


#### Where

`src/dot_tools/markdown_formatter/normalize.py:149-163`, specifically lines 157-159.


#### Issue

`parser.py` stores markdown-it's semantic code payload. CommonMark has already removed one leading and trailing space
from the raw `b\"  x  \"` interior, so the parser payload is `b\" x \"`. `_inline_code` then removes another pair.


#### Impact

The formatter changes code semantics while producing stable bytes. The body line containing a code span with two leading
and two trailing spaces has source payload `b\" x \"`, but the canonical output emits a three-backtick fence containing
only `x`, which reparses as payload `b\"x\"`. The existing output-only assertion in `test_edge_contract.py:223-236` is
false-green because it never compares source and reparsed code payloads.


#### Fix

Apply the CommonMark leading/trailing-space rule exactly once, either before storing the parser payload or in the
normalizer, not both. Add a semantic payload equality assertion for multiple leading and trailing spaces.


#### Outcome


----

#### C03 Nested code rendering changes CRLF payload bytes


#### Where

`src/dot_tools/markdown_formatter/render.py:133-146` and `render.py:176-180`, where nested rendered blocks are converted
through `splitlines()` before prefixes are applied.


#### Issue

The parser and normalized state preserve a nested code payload ending in CRLF, but `_render_block_lines` discards line
endings and `_list_item` rebuilds the nested block with LF separators.


#### Impact

For a nested list/blockquote fence with `b\"x  \\r\\n\"` payload, the output contains `b\"x  \\n\"`; reparsing changes
the code payload bytes even though the code payload is required to remain untouched. The same
loss occurs for nested code under any container that uses the line-splitting renderer.


#### Fix

Prefix nested code lines without discarding the payload's original line-ending bytes. Keep structural separators
canonical LF while retaining every byte in the code payload, and add LF/CRLF nested list and blockquote assertions.


#### Outcome


----

### Significant

#### S01 Blockquote ordered lists lose their starting marker


#### Where

`src/dot_tools/markdown_formatter/normalize.py:210-217`.


#### Issue

`_list` searches `block.source` with `\s*(\d+)[.)]`. A parser-owned list inside a block quote starts with `>`, so the
match
fails and `block.metadata` has no start value. The normalizer defaults to `1`.


#### Impact

`b\"# T\\n\\n> 12. first\\n> 13. second\\n\"` formats as `b\"# T\\n\\n> 1. first\\n> 2. second\\n\"`. This changes the
ordered-list start semantics required by the plan, although the result is idempotent.


#### Fix

Record the parser's first decimal marker in list metadata, or strip proven container prefixes before extracting the
marker. Preserve that start for every recursively normalized list.


#### Outcome


----

#### S02 Link destinations with backslashes remain noncanonical bare URLs


#### Where

`src/dot_tools/markdown_formatter/normalize.py:166-207`.


#### Issue

The destination codec does not enforce the approved bare-form restrictions. It leaves `foo\\bar` in bare form and strips
the angle brackets from `<foo\\bar>` instead of selecting angle form with escaped backslashes.


#### Impact

`b\"[x](foo\\\\bar)\"` and `b\"[x](<foo\\\\bar>)\"` both remain noncanonical `b\"[x](foo\\\\bar)\"`. They happen to
retain link semantics, but violate the specified deterministic destination representation and the table-cell inline
codec contract when the same link appears in a table.


#### Fix

Decode the parser-owned destination, use bare form only when it has no whitespace, angle brackets, or backslashes and
has
balanced parentheses, and otherwise emit angle form with the required backslash escaping. Add direct and table-cell
tests for literal backslashes.


#### Outcome


----

#### S03 Table cell edge tabs are stripped despite the lossless algorithm


#### Where

`src/dot_tools/markdown_formatter/parser.py:503-525` and `src/dot_tools/markdown_formatter/normalize.py:344-378`.


#### Issue

The physical cell splitters use default `.strip()`, which removes tabs as well as spaces. The approved table algorithm
strips only ordinary ASCII spaces from cell edges.


#### Impact

`b\"| \\tfoo\\t |\\n| --- |\\n| \\tbar\\t |\\n\"` formats as `b\"| foo |\\n| --- |\\n| bar |\\n\"`, dropping cell bytes
and changing the exact source-owned table content. The parser's cell spans also exclude those
tab bytes.


#### Fix

Use `.strip(b\" \")` only after removing framing pipes, preserve tabs in cell sources and spans, and measure the
resulting canonical cell bytes according to the approved Unicode-width algorithm. Add exact LF/CRLF tab-edge tests.


#### Outcome


## Skills Applied

- `review-implementation-execution`: project-local
- `engineer-reviewer`: global agent definition
- `editing`: global instruction
- `markdown`: global instruction


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C02, and C03 must be resolved before approval. S01, S02, and S03 must also be resolved because they violate
formatter-specific plan contracts. The unrelated configure pytest failure and 74 repository-wide Ty diagnostics remain
documented baselines and are not formatter blockers.
