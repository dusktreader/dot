# Implementation Plan Review: Generic AST-based Markdown formatter

This re-review checks the revised implementation plan against the prior review, the canonical artifact structure, and
the
linked approved design. It does not execute tests, builds, or linters.

**Iteration 02**


## Source Artifact

`.artifacts/20260827--markdown-ast-formatter/implementation-plan.md`


## Overview

The review surfaced findings:

- **Critical**:    2
- **Significant**: 8
- **Trivial**:     1


## Prior Review Resolution

- **C01** ✓: Task 01 now lists signatures for all previously incomplete public functions and names the typed error
  families.
- **S01** ✓: Task 01 runs only `uv sync`; focused test commands now follow the tasks that create their test modules.
- **S02** ✓: Task 05 now assigns the complete document pipeline and its canonical reparse check.
- **S03** ⚠: A pinned parser, delimiter-aware scanning, byte reconstruction checks, and whole-block opaque fallback are
  now
  stated, but the exact owned-inline grammar remains an execution-time unknown.
- **S04** ✓: Code ranges are identified before raw-HTML scanning, with non-code scanning and code fixtures required.
- **S05** ⚠: Source-break annotations and reuse are now assigned, but preserving breaks outside transitions conflicts
  with the
  approved design's rejection policy.
- **S06** ✓: Task-marker grammar, separate state, geometry, canonical spellings, and focused fixtures are specified.
- **S07** ⚠: The table invariants are substantially complete, but the extra-cell behavior conflicts with the approved
  design's
  profile-owned rectangular-table contract.
- **S08** ✓: Fenced and indented payload boundaries, fence sizing, info handling, line endings, and collision fixtures
  are now
  specified.
- **S09** ⚠: Wrapper-only dependencies, entry-CWD capture, upward project lookup, absolute path conversion, and
  delegation
  tests are present, but lookup precedence and child-CWD behavior remain implicit.
- **S10** ⚠: Exit codes and output streams are now named, but status values and exact diagnostic/report formats remain
  underspecified.
- **S11** ⚠: Node-level validation and forbidden-feature fixtures are now required, but the allowed scalar/tag model and
  numeric round-trip algorithm are not executable enough.
- **S12** ✓: Strict UTF-8 decoding now has a named typed parser error and source-line mapping requirements.
- **T01** ✓: The routine release-selection unknown was removed.
- **T02** ✓: Worktree instructions are now listed in Project Standards.
- **T03** ✓: The separator between sibling H2 sections was removed.


## Findings

### Summary

| Finding | Title                                                          | Outcome |
| ------- | -------------------------------------------------------------- | ------- |
| C01     | The plan implements a different scope than the approved design |         |
| C02     | Public contract is at the wrong task heading level             |         |
| S01     | Inline ownership and span proof remain too abstract            |         |
| S02     | Source-break behavior contradicts the approved policy          |         |
| S03     | Table extra-cell behavior contradicts the approved contract    |         |
| S04     | Frontmatter validation lacks an executable scalar algorithm    |         |
| S05     | CLI and operation statuses are not fully testable              |         |
| S06     | Renderer golden tests are ordered before the renderer          |         |
| S07     | Wrapper project resolution still has implicit behavior         |         |
| S08     | Approved-design rollout work is absent from execution          |         |
| T01     | Approved design reference link is incorrect                    |         |


### Critical

#### C01: The plan implements a different scope than the approved design


#### Where

Goal — lines 9-15; Project Standards — line 100; all Execution tasks.


#### Issue

The linked approved design requires explicit GFM and Zensical profiles, profile flags and defaults, complete CommonMark
baseline coverage, profile ownership matrices, GFM linkification, Zensical source forms, cross-profile rejection, and
the
associated pinned dependencies and fixtures. The revised plan explicitly rejects profiles and Zensical, limits the
feature
to CommonMark plus tables, adds only `markdown-it-py`, and states that no public API or CLI accepts profile arguments.


#### Impact

This plan cannot produce the approved feature. An implementation can satisfy every task here while omitting the profile
selection, syntax ownership, compatibility behavior, and rollout guarantees that the design makes contractual.


#### Suggestion

Align the plan with the linked design by adding the profile context, both profile implementations, all accepted and
unsupported claim predicates, direct parser/tokenizer dependencies, fixture/reference work, and profile-aware CLI and
wrapper behavior. If the generic scope is intentional, first replace or explicitly supersede the linked design with an
approved design that defines that scope.


#### Outcome


#### C02: Public contract is at the wrong task heading level


#### Where

Execution — Task 01 — Technical Notes — lines 138-143.


#### Issue

`Public contract` is an `####` heading alongside `Technical Notes`, not a `#####` subsection beneath it. The canonical
implementation-plan structure requires every Technical Notes subsection to use `#####`.


#### Impact

The document does not match the canonical task structure. Consumers can interpret the contract as a second task-level
field,
and structural validation will reject the artifact even apart from its feature-scope mismatch.


#### Suggestion

Change `#### Public contract` to `##### Public contract` and retain it under `#### Technical Notes`.


#### Outcome


### Significant

#### S01: Inline ownership and span proof remain too abstract


#### Where

Execution — Task 03 — AC02 and Steps — lines 208-237; Unknowns — lines 395-400.


#### Issue

The plan names a “small delimiter-aware scanner” but does not enumerate the owned inline forms, define its delimiter and
escape handling, or state how nested children map to byte spans. The only Unknown asks whether the approach can prove
every
child span during Task 03. The whole-block opaque fallback is safe for bytes, but it can make all ordinary inline
content
opaque and therefore unformatable.


#### Impact

The executor can choose incompatible ownership boundaries or silently reduce the formatter to opaque paragraph
preservation.
That would violate the approved AST ownership and wrapping behavior while passing only the preservation fixtures.


#### Suggestion

List every owned inline form and its source-scanning order, define the escape/nesting/repeated-text rules and
reconstruction
invariant, and state which forms are intentionally opaque. Resolve parser feasibility before execution or make the
opaque
fallback an explicit, accepted scope boundary with corresponding ACs.


#### Outcome


#### S02: Source-break behavior contradicts the approved policy


#### Where

Execution — Task 03 — AC06 — lines 222-224; Task 04 — AC05 — lines 261-264.


#### Issue

The plan recognizes thematic breaks broadly and says to preserve them outside heading transitions. The approved design
rejects source thematic-break constructs outside a required downward heading transition. It only consumes `---`, `***`,
or
`___` positionally when that transition requires a generated `HeadingSeparator`.


#### Impact

The implementation can accept unsupported source syntax and preserve noncanonical breaks, contrary to the approved
policy
and its idempotent positional separator contract.


#### Suggestion

Make a source break outside an immediately required downward transition a typed policy or unsupported-syntax error. At
the
required slot, consume it and emit the canonical `HeadingSeparator`; re-recognize only that generated separator at the
same
slot on the second pass.


#### Outcome


#### S03: Table extra-cell behavior contradicts the approved contract


#### Where

Execution — Task 04 — AC06 — lines 266-272; approved design — AC07 — lines 112-120.


#### Issue

The plan says every non-framing extra data cell, including an empty cell, is an error. The approved design says short
rows
gain empty cells and excess cells are discarded according to the owning profile's rectangular-table contract. The
revised
plan also has no profile owner whose contract could define that behavior.


#### Impact

The formatter will reject inputs that the approved design requires it to normalize, and fixture expectations cannot
agree
between the plan and design.


#### Suggestion

Reconcile the table contract with the approved design before execution. State the selected profile's rectangular-row
rule,
including whether excess cells are discarded or rejected, then make parser errors, normalization, and exact fixtures use
that
single rule.


#### Outcome


#### S04: Frontmatter validation lacks an executable scalar algorithm


#### Where

Execution — Task 02 — AC02-AC04 and Steps — lines 175-196.


#### Issue

The plan requires node inspection and rejects many YAML features, but it does not define the exact allowed node tags,
explicit-tag behavior, scalar resolution rules, control-character boundary, recursive Unicode checks, or the comparison
used
to decide that a real number round-trips without loss. “Disallowed scalar forms” and “cannot round-trip without loss”
leave
implementation-critical decisions open.


#### Impact

Different restricted loaders can accept different implicit scalars or serialize numerics differently while claiming to
meet
the same ACs. Unsafe or lossy frontmatter can pass broad happy-path tests.


#### Suggestion

Specify the permitted node-tag set and reject explicit tags, anchors, aliases, and duplicate keys before construction.
Define
the exact recursive Unicode/control validation and numeric algorithm, such as parsing the canonical scalar back into the
approved numeric model and comparing its exact value and type, with expected bytes and failures for every threshold and
loss
case.


#### Outcome


#### S05: CLI and operation statuses are not fully testable


#### Where

Execution — Task 01 — contract table — lines 158-161; Task 06 — AC02-AC03 — lines 334-342.


#### Issue

The revised plan adds exit codes and assigns stdout versus stderr, but `OperationResult.status` has no allowed values or
semantics, and the exact per-file status lines, summary format, mismatch details, error aggregation, and write-failure
report are unspecified. “Sufficient for deterministic CLI reporting” and “deterministic summaries” are not observable
contracts.


#### Impact

The CLI, direct operation callers, and wrapper can expose incompatible result objects or output while all broad status
tests
still pass. Automation cannot reliably distinguish unchanged, committed, preflight-failed, and partially committed
files.


#### Suggestion

Add a behavior table mapping each operation outcome to the result status, stdout records and order, stderr diagnostic
fields,
and exit code. Define mismatch context, preflight aggregation, committed/untouched ordering after a write failure, and
temporary-file cleanup, then assert those exact records in direct and CLI tests.


#### Outcome


#### S06: Renderer golden tests are ordered before the renderer


#### Where

Execution — Task 04 — Steps — lines 283-291; Task 05 — Steps — lines 317-321.


#### Issue

Task 04 creates and runs `tests/test_markdown_renderer.py` with “exact golden bytes,” but Task 04 implements only
`normalize.py`. The renderer functions are not assigned until Task 05, so the named golden-byte tests depend on a later
task.


#### Impact

Task 04 cannot pass on a clean worktree if those tests import or exercise `render.py`. This violates the stated
sequential,
test-driven task order and encourages the executor to run tasks out of order or weaken the tests.


#### Suggestion

Keep Task 04 tests at the normalized-AST/state level and run only those tests there. Move exact-byte golden tests to
Task 05
after renderer and orchestration implementation, or move renderer implementation into Task 04.


#### Outcome


#### S07: Wrapper project resolution still has implicit behavior


#### Where

Execution — Task 06 — AC04 — lines 343-347.


#### Issue

The plan says the wrapper walks upward from its script location and finds the repository `pyproject.toml`, but it does
not
define the search termination condition, nearest-project precedence when ancestors contain multiple projects, whether
the
child runs with the captured entry CWD, or how the selected project root is derived from the file.


#### Impact

The wrapper can select a different project in a nested or copied installation, and its behavior cannot be asserted
precisely
in the root, subdirectory, outside, and no-project fixtures.


#### Suggestion

Define an algorithm that starts at the resolved script directory, checks each ancestor through the filesystem root,
selects
the first matching `pyproject.toml`, derives its parent as the `--project` directory, and reports a deterministic
no-project
error. State whether the child uses `entry_cwd`; if absolute path conversion makes that irrelevant, make that invariant
explicit and test it.


#### Outcome


#### S08: Approved-design rollout work is absent from execution


#### Where

Execution — Task 07 — AC01-AC04 and Steps — lines 374-390; Unknowns — lines 393-400.


#### Issue

The approved design requires migration of every affected supported document before recursive GFM formatting,
compatibility
fixtures for its safe-YAML model, complete profile-matrix fixtures, and a zero-rejected-corpus rollout gate. Task 07
adds
focused interaction fixtures but no migration or corpus-verification task. Its only Unknown is inline-span feasibility,
not
the approved design's corpus migration, scalar compatibility, and deeply nested fixture questions.


#### Impact

The implementation can pass its local tests while recursive formatting still rejects supported documents or changes the
controlled corpus. The rollout safety and compatibility claims in the approved design remain unverifiable.


#### Suggestion

Add ordered migration and corpus-verification work, with an inventory of affected documents, expected migrated bytes, a
zero-rejection gate, and a second-pass identity check. Carry the approved design's remaining answerable Unknowns into
this
plan or explicitly resolve them in the relevant tasks.


#### Outcome


### Trivial

#### T01: Approved design reference link is incorrect


#### Where

Project Standards — line 100.


#### Issue

From the implementation-plan location, `../../../../.artifacts/20260827--markdown-ast-formatter/design-plan.md` points
to a
repository-root `.artifacts` directory. The approved design is beside the plan at
`.artifacts/20260827--markdown-ast-formatter/design-plan.md`.


#### Impact

An executor following Project Standards cannot open the design reference from the plan, weakening the primary alignment
check.


#### Suggestion

Link to `design-plan.md` in the same artifact directory, or use the correct relative path from the plan file.


#### Outcome


----

## Notes

The revisions resolved the prior findings on Task 01 ordering, document orchestration, code-first HTML rejection,
task-marker state, code payload boundaries, invalid UTF-8 handling, worktree instructions, and sibling-section
formatting.
They do not resolve the approved-design scope conflict, and several revisions introduce behavior that is safer or more
specific than the prior draft but still differs from the approved contract.

The plan is **not approved**. No tests, builds, or linters were run for this review.
