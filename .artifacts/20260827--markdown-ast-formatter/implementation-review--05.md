# Implementation Plan Review: Generic AST-based Markdown formatter

This re-review checks only findings C02, S01, S04, S06, and T01 from implementation-review--04, plus regressions in
generic scope and task ordering. No tests, builds, or linters were run.


**Iteration 05**


## Source Artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The re-review retains findings:

- **Critical**: 0
- **Significant**: 2
- **Trivial**: 1


## Prior Review Resolution

- **C02** ✓: Task 01 now contains `#### Technical Notes` with the required `##### Public contract` subsection beneath
  it.
- **S01** ✓: Task 03 now specifies scanner precedence, byte-cursor spans, token-map and byte-index interval proof,
  recursive reconstruction, ordinary-text fallback, opaque-block fallback, and fixtures covering each listed inline form
  across nesting, repeated text, CRLF, and astral Unicode.
- **S04** ⚠: The plan now specifies the stdout record and summary formats, stderr diagnostic format and ordering,
  mismatch digests, committed and untouched behavior, and the principal operation mappings. It still does not provide a
  total mapping for every `FileStatus`: `READ_ERROR` has no stated `OperationStatus`, and precedence for mixed file
  outcomes is not defined.
- **S06** ⚠: The plan now specifies canonical emphasis, strong, hard-break, and code-span fence rules and adds table
  geometry constraints. Exact link/image escaping, code-span padding, and a complete table separator and literal-pipe
  serialization algorithm remain underdefined.
- **T01** ✗: The Project Standards link remains
  `../../../../../.artifacts/20260827--markdown-ast-formatter/design-plan.md`, which review-04 identified as invalid
  from the worktree and not an authoritative approved generic design reference.


## Findings

### Summary

| Finding ID | Title                                                       | Outcome |
| ---------- | ----------------------------------------------------------- | ------- |
| S04        | CLI result and output mappings are not total                |         |
| S06        | Canonical inline and table serialization remains incomplete |         |
| T01        | Approved design reference remains invalid                   |         |


### Significant

#### S04: CLI result and output mappings are not total


#### Where

Task 01 Public contract and Task 06 AC03-AC05.


#### Issue

The plan now fixes the serialized stdout records and summary, stderr diagnostic ordering and fields, mismatch digest
details, and committed/untouched behavior. However, the operation-status mapping is still not total. `FileStatus`
includes `READ_ERROR`, but `OperationStatus` has no `READ_ERROR` value and AC04 does not state which operation status a
read failure produces. The plan also does not define precedence when one operation encounters more than one file-outcome
category.


#### Impact

Direct callers cannot determine the required `OperationResult.status` for read failures or mixed failures while
remaining
within the stated contract. Implementations can therefore disagree about status, summary output, and exit behavior for
the same multi-file operation.


#### Suggestion

Add a total behavior table mapping every `FileStatus` to the operation status for both format and check, including read
failures. Define precedence for mixed outcomes and state the exact `FileResult.message`, `error`, and `output` values
for
each status, alongside the already specified stdout and stderr records.


#### Outcome

Partially resolved; carry forward.


#### S06: Canonical inline and table serialization remains incomplete


#### Where

Task 04 AC02 and AC05, and Task 05 AC02.


#### Issue

The plan fixes several canonical forms, but phrases such as “canonical escaping” and “required padding” do not define
the exact codecs. Link and image label, destination, and title escaping is unspecified, as are the exact code-span
padding
cases. Table rules state widths, marker counts, framing, and parity constraints, but do not give a complete
serialization
procedure for separator dashes and cell content containing literal pipes and backslashes.


#### Impact

Two implementations can still produce different bytes or alter inline meaning while satisfying the stated criteria.
Exact-byte fixtures and idempotence tests cannot derive all expected output from the plan, especially for links, images,
code-span boundary spaces, and escaped table content.


#### Suggestion

Specify the exact inline codecs: characters escaped in ordinary text, link and image labels, destinations, and titles;
delimiter escaping; code-span padding for empty and boundary-space payloads; and the final hard-break spelling. Specify
a
step-by-step table serializer covering marker-owned separator dashes, width and padding calculations, framing, and
literal-pipe/backslash encoding, with expected bytes for every boundary case.


#### Outcome

Partially resolved; carry forward.


### Trivial

#### T01: Approved design reference remains invalid


#### Where

Project Standards — approved generic design reference.


#### Issue

The plan still points to the path identified by review-04 as invalid from the worktree and does not identify the actual
authoritative approved generic design artifact or explicitly mark the stale reference as superseded.


#### Impact

An executor cannot verify the approved design from the listed standard and may consult a stale or nonexistent artifact.


#### Suggestion

Link the actual approved generic design artifact, or explicitly identify the adjacent profile-oriented design as
superseded and state that the generic scope in this plan is authoritative.


#### Outcome

Unresolved.


## Regression Checks

The plan remains generic and introduces no stale profile or Zensical scope, profile flags, profile-specific
dependencies,
or related tasks. Task ordering has no regression: frontmatter precedes body parsing, parser spans precede
normalization,
normalization precedes rendering, the document pipeline precedes file operations, and operations precede CLI and wrapper
integration.


**Approval**: Not approved.
