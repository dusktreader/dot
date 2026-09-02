# Implementation Plan Review: Generic AST-based Markdown formatter

This final independent re-review checks review 02's findings, the canonical implementation-plan structure, and whether
the narrowed generic formatter plan is executable. No tests, builds, or linters were run.

**Iteration 03**


## Source Artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The review surfaced findings:

- **Critical**:    2
- **Significant**: 8
- **Trivial**:     1


## Prior Review Resolution

- **C01** ✓: The plan now intentionally implements the narrowed generic CommonMark-plus-table scope, with no profile
  flags, profile matrices, profile-specific dependencies, or rollout requirements.
- **C02** ✗: `Public contract` remains an `####` sibling of `#### Technical Notes` instead of a `#####` subsection.
- **S01** ⚠: Owned inline forms, source-order scanning, reconstruction, and opaque fallback are named, but precedence
  and
  per-form source-proof rules remain too abstract for safe implementation.
- **S02** ✗: The plan still preserves source breaks outside a downward heading transition, contrary to the approved
  policy
  recorded by review 02.
- **S03** ✓: The narrowed table contract states short-row padding, extra-cell rejection, separator checks, framing,
  code-span protection, and literal-pipe parity without profile-owned behavior.
- **S04** ⚠: Numeric thresholds and round-trip intent are more specific, but the exact YAML tag, scalar-resolution,
  control-validation, and escaping rules remain open.
- **S05** ⚠: Status and exit-code enums, ordering, streams, and broad write behavior are present, but result fields,
  output records, aggregation, and partial-commit reporting remain open.
- **S06** ✓: Normalization tests are explicitly state-level and renderer golden tests are deferred until Task 05.
- **S07** ✓: Wrapper CWD capture, absolute paths, nearest-ancestor lookup, root termination, delegation, and no-project
  behavior are explicit.
- **S08** ✓: Profile-specific rollout and corpus work are absent consistently with the narrowed generic scope.
- **T01** ✗: The approved design reference remains an invalid path from the worktree and does not identify an
  authoritative
  simplified design artifact.


## Findings

### Summary

| Finding ID | Title                                                     | Outcome |
| ---------- | --------------------------------------------------------- | ------- |
| C01        | Public contract remains at the wrong heading level        |         |
| C02        | Canonical Unknowns section is missing                     |         |
| S01        | Inline span proof still leaves ownership decisions open   |         |
| S02        | Source-break policy still contradicts the approved design |         |
| S03        | Frontmatter validation is not fully executable            |         |
| S04        | CLI result and output contracts remain underspecified     |         |
| S05        | Wrapper target and smoke commands are not named           |         |
| S06        | Canonical inline and table rendering rules are incomplete |         |
| S07        | Test commands omit the required red phase                 |         |
| S08        | Optimistic replacement safety is not assigned             |         |
| T01        | Approved design reference link remains invalid            |         |


### Critical

#### C01: Public contract remains at the wrong heading level


#### Where

Execution — Task 01 — Technical Notes — approximately lines 126-129


#### Issue

`Public contract` is headed `####`, alongside `Technical Notes`, rather than `#####` beneath it. This is the structural
defect carried forward from review 02 C02.


#### Impact

The plan does not match the canonical task structure. Consumers can interpret the contract as another task-level field,
and structural validation can reject the artifact before execution begins.


#### Suggestion

Change `#### Public contract` to `##### Public contract` and keep it under `#### Technical Notes`.


#### Outcome


#### C02: Canonical Unknowns section is missing


#### Where

Top-level plan structure — between Execution and Technical Notes — approximately lines 376-401


#### Issue

The canonical implementation-plan artifact includes an `## Unknowns` section. The revised plan moves directly from
`## Execution` to `## Technical Notes` and does not state whether any execution-blocking ambiguities remain.


#### Impact

The artifact is structurally incomplete, and reviewers cannot distinguish an intentional zero-unknowns decision from
requirements that the planner omitted. This also prevents a clean check for stale profile or Unknown requirements.


#### Suggestion

Add `## Unknowns` before `## Technical Notes`. State that no unresolved implementation unknowns remain if that is the
approved decision, or list each remaining answerable question with its resolution owner and task. Do not reintroduce the
superseded profile-specific Unknowns.


#### Outcome


### Significant

#### S01: Inline span proof still leaves ownership decisions open


#### Where

Execution — Task 03 AC02 and Steps — approximately lines 208-242


#### Issue

The plan lists owned inline forms and requires a source-order delimiter scanner, but it does not define dispatch
precedence for links, images, escapes, code spans, and nested delimiters, or the proof rule for each child span when
source text repeats. It also does not say which unrecognized candidates remain text and which force the containing block
opaque.


#### Impact

An executor can choose incompatible ownership boundaries or fall back to opaque paragraphs for ordinary prose. Guessing
offsets can alter escaped syntax, astral text, repeated text, or nested semantics while still passing preservation
tests.


#### Suggestion

Specify scanner dispatch order, delimiter and escape grammar, per-node reconstruction invariants, the child-span proof
algorithm, and the exact fallback boundary. Add expected ownership and opaque-range fixtures for every owned form,
including repeated text, nesting, CRLF, and astral Unicode.


#### Outcome


#### S02: Source-break policy still contradicts the approved design


#### Where

Execution — Task 03 AC06 and Task 04 AC05 — approximately lines 224-229 and 267-270


#### Issue

The plan preserves `---`, `***`, and `___` source breaks verbatim when they do not precede a downward heading
transition.
Review 02 S02 identified this as a conflict with the approved policy, which rejects thematic-break source constructs
outside the required generated-separator position. The revised plan retains the conflicting behavior.


#### Impact

An implementation can accept unsupported thematic-break syntax and retain noncanonical source bytes. This violates the
policy boundary and can make canonical reparsing and idempotence diverge from the approved contract.


#### Suggestion

Make any source break outside an immediately required downward transition a typed policy or unsupported-syntax error. At
the required slot, consume the source spelling and emit only the canonical `HeadingSeparator`; test all spellings,
container prefixes, no-break transitions, and the second formatting pass.


#### Outcome


#### S03: Frontmatter validation is not fully executable


#### Where

Execution — Task 02 AC02-AC04 — approximately lines 170-184


#### Issue

“Core tags,” “other controls,” and “same approved numeric type and exact value” do not identify the exact YAML tag URI
allowlist, implicit scalar-resolution rules, surrogate and Unicode checks after escape decoding, or canonical escape
notation for non-tab control characters. The plan rejects timestamps and explicit tags but leaves parser-level rules
that
distinguish them from allowed strings and numbers implicit.


#### Impact

Different restricted PyYAML implementations can accept different scalar spellings or serialize different bytes while
claiming to satisfy the same criteria. Unsafe values, lossy numbers, or noncanonical escapes can therefore pass broad
fixtures.


#### Suggestion

Name the permitted YAML tag set and quoted/unquoted scalar-resolution rules. Define recursive scalar validation,
decoded-Unicode and surrogate/control boundaries, the exact escape codec, and the exact numeric comparison model. Add
expected bytes and failures for each rule.


#### Outcome


#### S04: CLI result and output contracts remain underspecified


#### Where

Execution — Task 01 Public contract and Task 06 AC02-AC03 — approximately lines 133-155 and 341-348


#### Issue

The plan enumerates `FileResult.status` and `OperationResult.status`, but it does not define the result dataclass fields
or map each success, mismatch, preflight, read, input, and write outcome to an operation status. It also omits the exact
stdout record format, summary records, diagnostic aggregation, mismatch details, and committed and untouched ordering
after a partial write failure.


#### Impact

Direct callers, the CLI, and tests can implement incompatible result objects and output while satisfying the stated
status enums. Automation cannot reliably distinguish an unchanged file, a preflight failure, and a partially committed
operation.


#### Suggestion

Add a behavior table listing every operation outcome, result status, complete result fields, sorted stdout records,
stderr diagnostic fields, exit code, and committed/untouched semantics. Assert those exact values in direct-operation
and
CLI tests, including aggregated preflight and first-write-failure cases.


#### Outcome


#### S05: Wrapper target and smoke commands are not named


#### Where

Execution — Task 06 Steps — approximately lines 360-373


#### Issue

Task 06 says to “replace standalone formatter logic” and run CLI/wrapper smoke tests, but it does not name the wrapper
file to replace or provide exact smoke commands. The existing standalone formatter and its OpenCode caller are not
connected to the task's file list or test module by name.


#### Impact

The executor can implement a new wrapper without replacing the live entry point, or omit wrapper-specific verification
while the focused CLI test passes. The claimed compatibility behavior would remain unverified.


#### Suggestion

Name `.agents/tools/markdown-format.py` as the standalone wrapper, name `.config/opencode/tools/markdown_format.ts` as
its caller if it remains in scope, and add exact commands or test targets for help, root/subdirectory,
outside-repository,
no-project, absolute-path forwarding, stdout/stderr passthrough, and exit-code propagation.


#### Outcome


#### S06: Canonical inline and table rendering rules are incomplete


#### Where

Execution — Task 04 AC05-AC06 and Task 05 AC02-AC03 — approximately lines 267-318


#### Issue

The plan requires the renderer to honor inline semantics but does not specify canonical delimiter escaping for emphasis,
strong, links, images, code spans, or hard breaks. The table rules also omit the exact maximum-column-width,
minimum-separator-dash, and literal-pipe serialization algorithm needed to derive canonical bytes.


#### Impact

Two implementations can produce different canonical bytes or change inline meaning while satisfying the broad renderer
criterion. Exact-byte and idempotence tests cannot derive their expected output from the plan.


#### Suggestion

Add the canonical inline codecs, hard-break spelling, escaping and code-span fence rules, and the complete table width,
separator, and literal-pipe algorithm to normalization or rendering. Name exact expected-byte fixtures for each
boundary.


#### Outcome


#### S07: Test commands omit the required red phase


#### Where

Execution — Tasks 02-04 and 06 Steps — approximately lines 186-197, 231-242, 290-297, and 360-373


#### Issue

Functionality tasks write failing tests and then implement, but their steps do not run the tests before implementation
to
confirm the red phase. Task 04 also says to run “only the normalization state tests created in this task” without naming
the test module or exact command. Task 06 names the CLI test command but leaves wrapper smoke invocation unspecified.


#### Impact

An executor cannot perform the prescribed task verification deterministically. Tests can be skipped, placed in the wrong
scope, or weakened without an observable failing baseline.


#### Suggestion

Add an exact failing-test command before each implementation step, followed by the passing command. Name the Task 04
normalization test module and command, and add exact wrapper smoke commands or a named test target with expected exit
codes and stdout/stderr assertions.


#### Outcome


#### S08: Optimistic replacement safety is not assigned


#### Where

Execution — Task 06 AC03 and Operations steps — approximately lines 345-368


#### Issue

The approved write contract requires a per-file snapshot of bytes, identity, metadata, and destination type, followed by
an immediate pre-replacement comparison that rejects content or identity changes, symlinks, non-regular destinations,
and read-only destinations. The plan assigns atomic temporary-file replacement and mode preservation but not those
optimistic concurrency and destination-safety checks.


#### Impact

Concurrent edits can be overwritten after preflight, and unsafe destinations can be replaced despite the claimed safe
multi-file behavior. This is a correctness and data-loss risk independent of parser correctness.


#### Suggestion

Assign snapshot capture and immediate pre-replacement validation to `operations.py`. Define the typed failure and result
status for every mismatch or unsafe destination, preserve the original, clean the temporary file, and add direct and CLI
fixtures for concurrent content, identity, symlink, non-regular, and read-only cases.


#### Outcome


### Trivial

#### T01: Approved design reference link remains invalid


#### Where

Project Standards — approved design plan — approximately line 88


#### Issue

`../../../../../.artifacts/20260827--markdown-ast-formatter/design-plan.md` points outside the worktree artifact
directory.
The adjacent `design-plan.md` is also the profile-oriented artifact, while this implementation plan explicitly removes
profiles.


#### Impact

An executor cannot verify scope alignment from Project Standards, and a path-only fix could accidentally reintroduce
stale profile requirements.


#### Suggestion

Link to the actual approved simplified design artifact, or explicitly identify the adjacent profile-oriented design as
superseded and make the generic scope authoritative in this plan. Do not point the plan at the stale design by accident.


#### Outcome


## Notes

The revised plan resolves review 02 C01, S03, S06, S07, and S08: the generic scope is explicit, table extra-cell
behavior is settled for that scope, renderer tests follow renderer implementation, and the wrapper lookup algorithm is
defined. It does not yet resolve the canonical structure, source-break policy, byte-level frontmatter and rendering
contracts, operation result model, replacement safety, or exact task verification.

Task ordering is otherwise coherent: frontmatter precedes body parsing, code ranges precede raw-HTML scanning,
normalization precedes rendering, the document pipeline precedes file operations, and file operations precede CLI
integration. No stale profile requirements appear in the execution tasks, but the linked design remains stale and
invalid, so scope authority must be repaired before approval.

**Approval**: Not approved.
