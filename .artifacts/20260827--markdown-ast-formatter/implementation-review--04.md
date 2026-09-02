# Implementation Plan Review: Generic AST-based Markdown formatter

This re-review checks only the specified review-03 findings and obvious regressions in task order. No tests, builds, or
linters were run.

**Iteration 04**


## Source Artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The review retains findings:

- **Critical**: 1
- **Significant**: 3
- **Trivial**: 1


## Prior Review Resolution

- **C01** ✓: The plan explicitly limits the implementation to the generic CommonMark-plus-table formatter and excludes
  profiles, profile flags, profile-specific dependencies, rollout requirements, Zensical, plugins, oracle comparisons,
  extension ecosystems, and profile arguments.
- **C02** ✗: The plan contains no `##### Public contract` subsection beneath a Task 01 `#### Technical Notes` section.
  The contract material is embedded in Task 01 acceptance criteria instead of resolving the required heading-level
  structure.
- **C03** ✓: The plan includes `## Unknowns` and explicitly states that no unresolved implementation unknowns remain.
- **S01** ⚠: The plan now states scanner precedence, byte-index interval proof, recursive reconstruction, and opaque
  fallback conditions. It still does not define the per-form delimiter and escape grammar, a concrete child-span proof
  algorithm, or expected ownership and opaque-range fixtures for every owned inline form and boundary.
- **S02** ✓: The plan now raises `UnsupportedSyntaxError` for a break outside an immediately required downward-heading
  transition and assigns canonical `HeadingSeparator` reuse or insertion at the required transition.
- **S03** ✓: The frontmatter contract now names the allowed implicit tags and quoted-string rule, recursive value
  limits,
  duplicate and unsafe YAML constructs, Unicode/control validation, scalar escaping, numeric thresholds, and loss
  rejection.
- **S04** ⚠: The plan now defines result fields, status enums, broad status mappings, exit codes, stream direction,
  ordering, preflight aggregation, and partial-write fields. It still does not define the exact stdout record and
  summary
  schemas, complete operation-status mapping for every file outcome, diagnostic aggregation shape, or mismatch details.
- **S05** ✓: The plan names `.agents/tools/markdown-format.py` as the wrapper, retains
  `.config/opencode/tools/markdown_format.ts` as its caller, and supplies exact direct and wrapper smoke commands.
- **S06** ⚠: The plan now specifies canonical inline state and several table geometry and literal-pipe constraints. It
  still leaves the exact inline codecs, hard-break spelling, delimiter and code-span escaping, and complete table
  separator and literal-pipe serialization algorithms underdefined.
- **S07** ✓: Tasks 02 through 06 now name exact red-phase and green-phase commands, and Task 06 includes the exact smoke
  commands for the direct CLI and wrapper.
- **S08** ✓: Task 06 assigns snapshots and immediate pre-replacement validation to operations, names content, identity,
  symlink, regular-file, and read-only checks, and covers cleanup, partial commits, and the corresponding tests.
- **T01** ✗: The Project Standards link remains
  `../../../../../.artifacts/20260827--markdown-ast-formatter/design-plan.md`, which review 03 identified as invalid
  from the worktree and not an authoritative simplified design reference. The plan does not identify the superseded
  design explicitly.


## Findings

### Summary

| Finding ID | Title                                                       | Outcome |
| ---------- | ----------------------------------------------------------- | ------- |
| C02        | Public contract heading-level requirement remains unmet     |         |
| S01        | Inline span proof remains insufficiently executable         |         |
| S04        | CLI result and output schemas remain underspecified         |         |
| S06        | Canonical inline and table serialization remains incomplete |         |
| T01        | Approved design reference remains invalid                   |         |


### Critical

#### C02: Public contract heading-level requirement remains unmet


#### Where

Task 01 contract material and the top-level implementation-plan structure.


#### Issue

The plan has no `#### Technical Notes` section containing a `##### Public contract` subsection. The public model,
status, signature, and CLI behavior are specified in Task 01 acceptance criteria, but the structural defect identified
by review 03 was not repaired.


#### Impact

The artifact still does not match the required canonical task structure. Structural consumers can reject or misclassify
the public contract before execution begins.


#### Suggestion

Add the required Task 01 `#### Technical Notes` section and place the public contract beneath it as
`##### Public contract`, without duplicating or weakening the existing acceptance criteria.


#### Outcome

Unresolved.


### Significant

#### S01: Inline span proof remains insufficiently executable


#### Where

Task 03 AC02-AC03 and the Task 03 steps.


#### Issue

The plan gives a precedence list and requires exact byte intervals plus recursive reconstruction, but it does not define
the delimiter and escape grammar for each inline form, the concrete child-span proof procedure, or the exact distinction
between an unrecognized candidate that remains text and one that makes its containing block opaque. The fixture step
also
does not enumerate ownership and opaque-range expectations for each form across repeated text, nesting, CRLF, and astral
Unicode.


#### Impact

Executors can still choose incompatible ownership boundaries or offset calculations while satisfying the broad proof
language. That can change escaped or nested semantics and can make ordinary prose opaque unnecessarily.


#### Suggestion

Specify the scanner grammar and dispatch operation for code spans, images, links, escapes, strong/emphasis, hard breaks,
and text. Define the per-node reconstruction invariant and child-span proof algorithm, then name exact ownership and
opaque-range fixtures for every form and the repeated, nested, CRLF, and astral boundaries.


#### Outcome

Partially resolved; carry forward.


#### S04: CLI result and output schemas remain underspecified


#### Where

Task 01 AC03-AC06 and Task 06 AC02-AC04.


#### Issue

The plan now provides dataclass fields and broad status and stream requirements, but it still does not specify the exact
serialized fields and order of each stdout per-file record and summary, the complete mapping from every file outcome to
an
operation status, the diagnostic aggregation shape, or the mismatch details. Committed and untouched semantics after
each
partial-write branch also remain only narrative.


#### Impact

Direct callers and CLI consumers can produce incompatible result objects or output while meeting the stated enums and
exit codes. Automation still cannot reliably distinguish all unchanged, mismatch, preflight, read, input, and write
outcomes.


#### Suggestion

Add a behavior table covering every operation outcome. Define complete result values, exact stdout record and summary
schemas, stderr diagnostic fields and aggregation order, exit code, mismatch details, and committed/untouched contents
for preflight failure and first-write-failure cases. Assert those values in direct-operation and CLI tests.


#### Outcome

Partially resolved; carry forward.


#### S06: Canonical inline and table serialization remains incomplete


#### Where

Task 04 AC02 and AC05, and Task 05 AC02.


#### Issue

The plan names canonical inline delimiter and escape state, but it does not specify the exact codecs for emphasis,
strong, links, images, code spans, and hard breaks. Table geometry has more constraints, yet the meaning of content
length,
separator-dash construction, and literal-pipe serialization is not fully defined as a canonical byte algorithm.


#### Impact

Two implementations can still emit different bytes or alter inline meaning while satisfying the broad rendering
criteria.
Exact-byte fixtures and idempotence tests cannot derive all expected output from the plan.


#### Suggestion

Define the canonical inline codecs, hard-break spelling, escaping rules, and code-span fence selection. Complete the
table
width, minimum-separator, marker-owned-dash, padding, framing, and literal-pipe serialization algorithm, with exact
expected-byte fixtures for every boundary.


#### Outcome

Partially resolved; carry forward.


### Trivial

#### T01: Approved design reference remains invalid


#### Where

Project Standards — approved generic design reference.


#### Issue

The plan still points to the path identified by review 03 as invalid from the worktree and does not state which
authoritative simplified design artifact replaces the stale profile-oriented design.


#### Impact

An executor cannot verify the approved design from the listed standard and may consult a stale or nonexistent artifact.


#### Suggestion

Link the actual approved simplified design artifact, or explicitly identify the adjacent profile-oriented design as
superseded and state that the generic scope in this plan is authoritative.


#### Outcome

Unresolved.


## Notes

No obvious task-order regression is present. Frontmatter still precedes body parsing, parser spans precede
normalization,
normalization precedes rendering, the document pipeline precedes file operations, and operations precede CLI and wrapper
integration. The findings above are limited to the specified review-03 items.


**Approval**: Not approved.
