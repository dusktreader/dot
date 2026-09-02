# Implementation Plan: Generic AST-based Markdown formatter

This plan translates the approved generic formatter design into seven bounded, test-driven implementation tasks.


## Goal

Build the generic formatter inside the `dot_tools` package with restricted YAML frontmatter, `markdown-it-py`
CommonMark-plus-table parsing, byte-accurate source-span association, normalized AST state, deterministic rendering,
and safe file operations. Expose the package through the Typer group `dt markdown format PATH...` and
`dt markdown check PATH...`; keep `.agents/tools/markdown-format.py` as a thin compatibility wrapper that delegates to
those grouped commands. Preserve whole parser-delimited opaque blocks when ownership cannot be proven. Keep the
implementation generic and fail closed.


## Project Commands

### Synchronize dependencies

Command:

```shell
uv sync
```

Expected Output: The environment and lockfile include `markdown-it-py==4.2.0`.


### Run tests

Command:

```shell
uv run pytest
```

Expected Output: All tests pass with the configured coverage threshold.


### Inspect the Markdown command help

Command:

```shell
uv run dt markdown --help
uv run dt markdown format --help
uv run dt markdown check --help
```

Expected Output: The grouped command and both PATH-taking subcommands display help and exit successfully.


### Run Ruff

Command:

```shell
uv run ruff check src tests
```

Expected Output: Ruff reports no errors.


### Run Ty

Command:

```shell
uv run ty check
```

Expected Output: Ty reports no type errors.


## Project Standards

- [Repository guide](../../../../../.dot_agents/dot.md)
- [Worktree instructions](../../AGENTS.md)
- [Approved generic design](design-plan.md)
- [Implementation-plan structure](../../../../../.agents/artifacts/implementation-plan/description.md)
- [Markdown style guide](../../../../../.agents/instructions/markdown.md)
- Use Python 3.13+, `uv`, pytest, Ruff, Ty, and 120-character lines.
- The sibling `design-plan.md` above is authoritative and supersedes any stale profile-oriented design elsewhere.
  Keep the implementation generic and fail closed.


## Relevant Skills

- `execute-implementation-plan`
- `execute-implementation-task`
- `review-implementation-execution`
- `review-code`
- `write-docs`


## Execution

### 01: Establish dependency and public contracts

#### Acceptance Criteria

- AC01: Add `markdown-it-py==4.2.0` to `pyproject.toml` and refresh `uv.lock`.
- AC02: Create formatter modules under
  `src/dot_tools/markdown_formatter/{__init__,models,frontmatter,parser,normalize,render,operations}.py` and the
  Typer command group at `src/dot_tools/cli/markdown.py`.
- AC03: Implement the public models, statuses, signatures, and `dt markdown` CLI contract in the Public contract
  notes below.


#### Technical Notes


#### Public contract

`models.py` defines `FileSnapshot`, `FileResult`, and `OperationResult` dataclasses. `FileResult` fields are `path:
Path`, `status: FileStatus`, `message: str`, `output: bytes | None`, `error: str | None`, and `snapshot:
FileSnapshot | None`. `OperationResult` fields are `operation: Operation`, `status: OperationStatus`, `files:
tuple[FileResult, ...]`, `diagnostics: tuple[str, ...]`, `committed: tuple[Path, ...]`, and `untouched: tuple[Path,
...]`.

Define `FileStatus` values `FORMATTED`, `UNCHANGED`, `MISMATCH`, `INPUT_ERROR`, `READ_ERROR`, `PREFLIGHT_ERROR`, and
`WRITE_ERROR`; `OperationStatus` values `SUCCESS`, `MISMATCH`, `INPUT_ERROR`, `READ_ERROR`, `PREFLIGHT_ERROR`,
`PARTIAL_WRITE`, and `WRITE_ERROR`; and `Operation` values `FORMAT` and `CHECK`.

Fix signatures: `format_document(source: bytes) -> bytes`, `check_document(source: bytes) -> bytes`,
`format_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult`,
`check_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult`. The `markdown_cli` group in
`dot_tools.cli.markdown` exposes `format_markdown` and `check_markdown` subcommands. The grouped commands resolve
relative paths against process CWD, write diagnostics to stderr and summaries to stdout, and use exit `0` for
success/no-op, `1` for
check mismatch, `2` for input/path or frontmatter/parser/policy/raw-HTML failure, and `3` for read, write, or atomic
replacement failure. The total mapping is exact: `format_paths` with all files `FORMATTED` or `UNCHANGED` returns
`OperationStatus.SUCCESS` and exit `0`; any `INPUT_ERROR` returns `INPUT_ERROR` and exit `2`; any `PREFLIGHT_ERROR`
returns `PREFLIGHT_ERROR` and exit `2`; any `READ_ERROR` returns `READ_ERROR` and exit `3`; and any write failure
returns `PARTIAL_WRITE` and exit `3` when `committed` is nonempty, otherwise `WRITE_ERROR` and exit `3`.
`check_paths` returns `MISMATCH` and exit `1` for any `MISMATCH` without a higher-precedence input, preflight, read,
or write error; otherwise it maps errors as above, and only all `UNCHANGED`/zero files returns `SUCCESS` and exit `0`.
Mixed outcomes have precedence: input error > preflight error > read error > write/partial write > check mismatch >
success.

`FileResult` semantics are exact: `FORMATTED` has `message="formatted"`, `error=None`, and canonical replacement bytes
in `output`; `UNCHANGED` has `message="unchanged"`, `error=None`, and `output=None`; `MISMATCH` has
`message="mismatch"`, `error=None`, and `output=None`. Every error status has `message="error"`, `output=None`, and
`error` equal to the stable detail text emitted in its stderr diagnostic. Only mismatch diagnostics contain expected and
actual SHA-256 values. `snapshot` is present after a successful read and otherwise `None` when no trustworthy snapshot
exists. These rules apply to every `OperationResult`, including mixed outcomes and zero-file operations.


#### Steps

- Add the dependency and package skeleton, then add contract tests in `tests/markdown_formatter/test_models.py` and
  `tests/markdown_formatter/test_markdown_cli_contract.py` for the grouped command surface.
- Run the only Task 01 verification:

  ```shell
  uv sync
  ```


### 02: Implement restricted frontmatter

#### Acceptance Criteria

- AC01: `frontmatter.py` exposes `extract_frontmatter(source: bytes) -> tuple[Frontmatter | None, bytes]`,
  `validate_frontmatter(value: object) -> Mapping[str, object]`, and `serialize_frontmatter(value: Mapping[str, object])
  -> bytes`.
- AC02: Byte 0 line exactly `---` opens; the first later line exactly `---` closes. Missing close raises
  `FrontmatterError(ValueError)` and never becomes body Markdown.
- AC03: Accept only mapping roots with string keys, nested mappings/sequences, null, booleans, finite integers, finite
  reals, and strings. Permit only implicit YAML tags `null`, `bool`, `int`, `float`, and `str`; quoted values are
  strings.
  Reject duplicates, aliases, anchors, explicit tags, timestamps, binary, sets, multiple documents, invalid Unicode, and
  non-finite values with `FrontmatterError`.
- AC04: Serialize sorted mapping keys, two-space nesting, `{}`/`[]`, `- VALUE`, `null`, lowercase booleans, canonical
  integers, and finite reals using the approved `1e21`/`1e-6` thresholds, lowercase exponent, no plus sign or leading
  exponent zeroes, and loss rejection. Double-quote strings and escape backslash, quote, LF, CR, tab, and all other C0
  controls as `\\`, `\"`, `\n`, `\r`, `\t`, or `\u00NN`; reject surrogates and invalid Unicode. Emit delimiters,
  one blank line, body, and exactly one final LF.


#### Steps

- Add exact-byte fixtures under `tests/markdown_formatter/fixtures/frontmatter/` and tests in
  `tests/markdown_formatter/test_frontmatter.py`.
- Red phase:

  ```shell
  uv run pytest tests/markdown_formatter/test_frontmatter.py
  ```

- Implement restricted loading, recursive validation, scalar codecs, and extraction. Use `UnicodeError` for invalid
  UTF-8.
- Green phase: rerun exactly `uv run pytest tests/markdown_formatter/test_frontmatter.py`.


### 03: Parse spans, opaque regions, and policy boundaries

#### Acceptance Criteria

- AC01: `parser.py` exposes `parse_document(body: bytes) -> DocumentAst` and dataclasses `DocumentAst`, `BlockNode`,
  `InlineNode`, `SourceSpan`, `CodePayload`, and `OpaqueBlock`; spans use byte offsets and token maps.
- AC02: Parse `MarkdownIt("commonmark").enable("table")`. Own headings, paragraphs, lists/items, block quotes, fenced
  and indented code, parser-identified tables, and inline text, code, emphasis, strong, links, images, and hard breaks.
  Scan source order with precedence code spans, images, links, escapes, strong/emphasis, hard breaks, then text.
- AC03: Build a byte index from decoded code-point boundaries. A child is owned only when its token map and byte index
  prove an exact interval and recursive reconstruction. Unmatched, mixed, repeated-text, CRLF, astral, or ambiguous
  intervals make the entire containing block opaque; ordinary unrecognized text remains text.
- AC04: The exact-source scanner is a bounded implementation, not a product `Unknown`. It operates on the exact UTF-8
  body-block slice with a byte cursor and emits sequential,
  non-overlapping spans. At each cursor, code span consumes a matching backtick run and opaque payload; image claims
  `![` before link `[`, then scans balanced label, destination, and title; hard break claims backslash plus LF or two
  or more spaces plus LF; strong claims `**` or `__`, and emphasis claims `*` or `_`, each requiring a matching
  unescaped closer and recursive scanning. A backslash escape consumes the next UTF-8 codepoint as literal text;
  otherwise consume the next codepoint as text. For every node, concatenate its source slice and child slices and
  require exact byte equality to the block slice, using cursor position for repeated text. An unclosed or mixed
  unrecognized construct remains ordinary text where parsing permits; an unknown child or unprovable span makes the
  containing block opaque. Fixtures assert ownership and opaque fallback for every listed form, nesting, repeated text,
  CRLF, and astral Unicode.
- AC05: Collect code ranges first. Scan raw HTML outside code, including opaque ranges, and raise
  `RawHtmlError(ValueError)`.
  HTML-looking code remains code. Enforce AST-scoped H1 policy with `StructureError(ValueError)`.
- AC06: Identify task markers and thematic breaks. A break outside an immediately required downward-heading transition
  raises `UnsupportedSyntaxError(ValueError)`. Preserve a recognized parent wholly when an opaque child would be
  altered.


#### Steps

- Add fixtures under `tests/markdown_formatter/fixtures/parser/` and `tests/markdown_formatter/test_parser.py`.
- Red phase: `uv run pytest tests/markdown_formatter/test_parser.py`.
- Implement token maps, byte indexing, code-first ranges, raw-HTML scanning, delimiter scanning, H1 policy, and
  whole-block
  opaque fallback. Raise `ParseError` for parser failures.
- Green phase: rerun exactly `uv run pytest tests/markdown_formatter/test_parser.py`.


### 04: Normalize owned structures

#### Acceptance Criteria

- AC01: `normalize.py` exposes `normalize_document(document: DocumentAst) -> NormalizedDocument` and dataclasses
  `HeadingSeparator`, `NormalizedHeading`, `NormalizedList`, `NormalizedTable`, `NormalizedCode`, and
  `NormalizedDocument`.
  Tests assert normalized AST/state only.
- AC02: Wrap prose at 120 Unicode code points excluding indentation, code, and tables; do not split unbreakable tokens.
  Ordinary text emits original Unicode and escapes only syntax punctuation necessary to prevent a structural parse.
  Emphasis emits `*children*`; strong emits `**children**`; both recursively encode children and put one backslash
  before
  a literal delimiter or backslash when needed. A hard break is exactly one ASCII backslash plus LF. Link/image labels
  use the same inline codec. Destinations use bare form only with no whitespace, angle brackets, or backslashes and
  balanced parentheses; otherwise use angle form with backslash escaping. Titles use double quotes with backslash and
  double-quote escapes. For code spans, first parse the semantic payload using CommonMark: normalize every internal LF
  or CRLF to one ASCII space, then remove exactly one leading and one trailing ASCII space only when both are present
  and the normalized payload is not all spaces. Render that normalized payload with a backtick fence of length
  `max(3, longest consecutive backtick run in the normalized payload + 1)`. If the normalized payload begins or ends
  with a backtick, add exactly one ASCII space immediately inside both delimiters; otherwise add none. If the payload
  is all spaces, preserve every space and add no trimming or padding. An empty payload emits adjacent delimiters.
  Reparsing the canonical span must recover the same semantic payload. Exact-byte fixtures cover empty, all-space,
  leading-space, trailing-space, both-space, ordinary, and backtick-boundary payloads, with expected bytes and reparsed
  semantic payloads for each case. At minimum, the fixture table uses `repr`-style byte strings to make delimiters and
  spaces unambiguous:

  ```text
  semantic payload       canonical bytes
  ""                     b"``````"
  "   "                  b"```   ```"
  " x"                   b"``` x```"
  "x "                   b"```x ```"
  " x "                  b"```x```"
  "`x`"                  b"``` `x` ```"
  ```
- AC03: Preserve list order and task state. Ordered lists retain the first marker and later decimal sequence; unordered
  markers become `-`. Continuation indentation is active prefix plus marker width and `[ ] ` or `[x] ` task prefix, with
  recursive nested and block-quote columns. Unknown lazy continuation stays opaque.
- AC04: Apply exact heading spacing and downward `HeadingSeparator` reuse/insertion from the design. Reject source
  breaks
  outside the required transition. Do not add edge blanks.
- AC05: Enforce table header/separator adjacency and zero-cell errors (`TableError(ValueError)`). Apply this ordered
  serialization algorithm: (a) remove at most one leading and trailing framing pipe; framing pipes are not cells; (b)
  render each semantic cell to canonical inline bytes; (c) strip only ordinary ASCII spaces from each cell's edges; (d)
  encode a semantic literal backslash run of length `k` immediately before a literal pipe as `2k+1` ASCII backslashes
  plus `|`, encode a literal pipe alone as one backslash plus `|`, and leave code-span pipes untouched; (e) measure
  Unicode code-point width of the rendered escaped cell bytes, including escape bytes; (f) let the header establish the
  column count, pad short data rows with empty cells, error on extra non-framing data cells, and require the separator
  row to have exactly the header count without padding; (g) preserve each separator marker as unaligned, left, right,
  or center, set each column width to `max(content width, 3 + marker count)`, and fill separator dashes to that width;
  (h) right-pad data cells to that width and emit `| ` at row start and ` |` at row end; and (i) preserve row order and
  require reparsing and a second normalization/render pass to produce identical bytes. Exact fixtures cover unframed,
  leading-framed, trailing-framed, and doubly-framed rows; empty and all-pipe rows; each marker; short and extra data
  rows; escaped pipes and arbitrary backslash runs; and code-span pipes. Fixtures record exact input and output bytes,
  including framing pipes, separator markers, escape bytes, and padding.


#### Steps

- Add state fixtures under `tests/markdown_formatter/fixtures/normalize/` and
  `tests/markdown_formatter/test_normalize.py`.
- Red phase: `uv run pytest tests/markdown_formatter/test_normalize.py`.
- Implement wrapping, inline state, list columns, heading/separator state, table geometry, code fence state, and opaque
  propagation.
- Green phase: rerun exactly `uv run pytest tests/markdown_formatter/test_normalize.py`.


### 05: Render and orchestrate documents

#### Acceptance Criteria

- AC01: `render.py` exposes `render_document(document: NormalizedDocument) -> bytes`; canonical nodes use LF and exactly
  one final LF, while opaque blocks and code payloads retain specified bytes.
- AC02: Render canonical inline delimiters, hard breaks, lists, headings, separators, tables, and code by applying the
  exact CommonMark code-span boundary algorithm and ordered table serialization algorithm in Task 04 AC02 and AC05,
  respectively. Exact-byte fixtures cover the code-span empty, all-space, leading-space, trailing-space, both-space,
  and backtick-boundary payloads, plus every table framing, empty/all-pipe-row, alignment-marker, separator-width,
  short-row, extra-row, escaped-pipe, arbitrary-backslash-run, and code-span-pipe case. Reparse and formatting again
  produce identical bytes.
- AC03: `format_document` extracts, parses, normalizes, and renders; `check_document` computes identical canonical bytes
  without writing. Propagate exactly `FrontmatterError`, `UnicodeError`, `RawHtmlError`, `StructureError`,
  `UnsupportedSyntaxError`, `TableError`, or `ParseError`.
- AC04: Golden fixtures under `tests/markdown_formatter/fixtures/render/` cover exact bytes and idempotence.


#### Steps

- Add `tests/markdown_formatter/test_render.py` and `test_document.py` golden/idempotence tests.
- Red phase: `uv run pytest tests/markdown_formatter/test_render.py tests/markdown_formatter/test_document.py`.
- Implement renderers and the complete document pipeline.
- Green phase: rerun exactly `uv run pytest tests/markdown_formatter/test_render.py
  tests/markdown_formatter/test_document.py`.

Public document orchestration remains in `dot_tools.markdown_formatter`; no document pipeline belongs in the Typer
command module.


### 06: Add operations, CLI, and wrapper

#### Acceptance Criteria

- AC01: `operations.py` collects files/recursive `.md` discovery, resolves direct paths from CWD, sorts and
  deduplicates,
  and reports explicit missing/non-Markdown paths as `INPUT_ERROR`; zero discovery is success.
- AC02: Preflight every file and compute all outputs before writing. Atomically replace sorted files, preserve mode,
  stop
  at the first write error, report sorted `committed` and `untouched`, and clean temporary files. `check` never writes.
- AC03: `operations.py` owns snapshot capture, immediate comparison, destination safety, same-directory temp
  flush/fsync/os.replace, mode preservation, cleanup, and tests. Capture bytes, identity, metadata, and destination type
  in `FileSnapshot`; immediately before replacement reject changed content/identity, symlinks, non-regular, and
  read-only
  destinations as `PREFLIGHT_ERROR`. Capture bytes digest and `stat` identity/mode/type, and compare all immediately
  before replace. Map reads to `READ_ERROR`, replacement to `WRITE_ERROR`, and partial commits to `PARTIAL_WRITE`.
- AC04: File statuses and operation mappings use the total contract in Task 01. Format is `SUCCESS` only for
  `FORMATTED`/`UNCHANGED`; check is `MISMATCH` for any mismatch; read errors use `READ_ERROR`; and write errors use
  `PARTIAL_WRITE` after an earlier commit or `WRITE_ERROR` otherwise. Mixed outcomes use input/path, preflight, read,
  write/partial-write, mismatch, then success precedence.
- AC05: Emit exactly one stdout record per sorted file as `<status> <absolute-path>`, then
  `summary <operation> <status> <count>`. Emit stderr diagnostics exactly as
  `<absolute-path>: <error-kind>: <message>`, sorted by path then kind/message. Check mismatch diagnostics include
  expected and actual SHA-256 digests, never raw content. Preflight failure commits no files and leaves all prepared
  files untouched. The first write failure stops; earlier paths are committed and the failed and later paths are
  untouched. Exit codes are 0 for success/no-op, 1 for check mismatch, 2 for input/path/frontmatter/parser/policy or
  raw-HTML failures, and 3 for read/write/atomic replacement failures.
- AC06: Replace target `.agents/tools/markdown-format.py` with a thin wrapper. Import only `typer` if used; capture
  `entry_cwd = Path.cwd()` once; resolve wrapper operands from `entry_cwd`; locate the repository by walking
  `Path(__file__).resolve().parent` and parents through filesystem root for the first directory containing
  `pyproject.toml`; invoke `uv run --project <repo> dt markdown format/check <absolute paths>` with subprocess CWD
  `entry_cwd`,
  passing child stdout, stderr, and return code through, with no project exit `2`. The existing TS caller remains
  unchanged unless required. The wrapper target is `.agents/tools/markdown-format.py`; use
  `~/.agents/tools/markdown-format.py --help` or `uv run .agents/tools/markdown-format.py --help` only if executable,
  not `uv run python .agents/tools/markdown-format.py --help`. Smoke expectations: grouped and wrapper `--help` succeed;
  wrapper `check` reports `UNCHANGED` and summary `SUCCESS` for canonical design input; wrapper `format` reports
  `UNCHANGED` and summary `SUCCESS` on the second pass.
- AC07: Register `markdown_cli` with the existing `cli` Typer application in `src/dot_tools/cli/main.py`. Tests cover
  the `dt markdown` CLI and wrapper CWD, repository/root/no-project discovery, outside-repository and absolute paths,
  grouped help, passthrough, races, symlink/non-regular/read-only destinations, cleanup, partial commits, exact
  records, diagnostics, digests, and status mappings. Smoke:

  ```shell
   uv run dt markdown --help
   uv run dt markdown format --help
   uv run dt markdown check --help
  ~/.agents/tools/markdown-format.py --help
  ~/.agents/tools/markdown-format.py check .artifacts/20260827--markdown-ast-formatter/design-plan.md
  ~/.agents/tools/markdown-format.py format .artifacts/20260827--markdown-ast-formatter/design-plan.md
  ```


#### Steps

- Add `test_operations.py`, `test_markdown_cli.py`, and `test_wrapper.py` with temporary-directory and subprocess
  fixtures. Test grouped format/check behavior and wrapper delegation to `dt markdown format/check`.
- Red phase: `uv run pytest tests/markdown_formatter/test_operations.py tests/markdown_formatter/test_markdown_cli.py
  tests/markdown_formatter/test_wrapper.py`.
- Implement operations, `src/dot_tools/cli/markdown.py`, its registration in `src/dot_tools/cli/main.py`, and the
  wrapper, including snapshots, preflight, atomic replacement, cleanup, statuses, and output contracts. Keep public
  document orchestration in `dot_tools.markdown_formatter`; the CLI only adapts Typer arguments and exit/output
  handling to package operations.
- Green phase: rerun exactly the same three test modules, then run all six smoke commands.


### 07: Complete generic corpus and quality gate

#### Acceptance Criteria

- AC01: Generic corpus fixtures under `tests/markdown_formatter/fixtures/corpus/` cover frontmatter, boundaries,
  headings,
  lists, tables, code, raw HTML, opaque spans, source-break policy, idempotence, and multi-file failure behavior.
- AC02: Full pytest, Ruff, and Ty gates pass for the bounded generic formatter.


#### Steps

- Add `tests/markdown_formatter/test_corpus.py` and exact expected-byte companions.
- Run `uv run pytest`, `uv run ruff check src tests`, and `uv run ty check`.
- Review the final diff for scope, exception families, result fields, streams, atomic safety, and wrapper delegation.


## Unknowns

No unresolved implementation unknowns remain because unprovable inline spans use the prescribed opaque fallback.


## Technical Notes

The sibling `design-plan.md` in this artifact directory is the authoritative approved generic design for execution.
Any stale profile-oriented design elsewhere is superseded; do not consult it or introduce profile-specific scope.


### Preservation and errors

Opaque spans remain byte-for-byte, including CRLF and trailing whitespace. Recognized nodes use canonical LF. Never
guess
source offsets or silently downgrade a policy violation. `FrontmatterError`, `RawHtmlError`, `StructureError`,
`UnsupportedSyntaxError`, and `TableError` derive from `ValueError`; `ParseError` represents parser failures.


### Operation ordering

Collect, sort, deduplicate, read, snapshot, preflight, and render every file before any replacement. Replace in sorted
order,
stop at the first write failure, report committed and untouched files, and clean temporary files in `finally` blocks.
