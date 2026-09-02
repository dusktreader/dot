# Implementation Plan Review: Generic AST-based Markdown formatter

This final re-review checks only the findings from `implementation-review--05.md` and obvious regressions in the
generic scope, task contracts, ordering, and safety boundaries. No tests, builds, or linters were run.


**Iteration 06**


## Source Artifact

`implementation-plan.md` in the reviewed artifact directory.


## Overview

The review retains one significant finding:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- **S04** ✓: Task 01 and Task 06 now define every listed file and operation status, mixed-outcome precedence, result
  fields, committed and untouched paths, diagnostics, and exit-code mapping.
- **S06** ⚠: Inline delimiters, destinations, titles, hard breaks, code fences, table geometry, and literal-pipe parity
  are substantially specified, but code-span boundary-space semantics and the complete table serialization order remain
  ambiguous.
- **T01** ✓: Project Standards now links the adjacent `design-plan.md` and explicitly supersedes stale profile-oriented
  material. The plan contains no profile, Zensical, or oracle scope.


## Findings

### Summary

| Finding ID | Title                                                       | Outcome |
| ---------- | ----------------------------------------------------------- | ------- |
| S06        | Inline and table serialization still has boundary ambiguity |         |


### Significant

#### S06: Inline and table serialization still has boundary ambiguity


#### Where

Execution, Task 04 AC02 and AC05-AC06, and Task 05 AC02, approximately lines 227-257 and 275-278.


#### Issue

The plan specifies many canonical forms, but it does not define how the code-span renderer preserves semantic payloads
with leading or trailing spaces. The rule adds padding only when the payload begins or ends with a backtick, while
CommonMark code-span trimming makes other boundary-space payloads sensitive to the emitted padding. The table algorithm
also says to apply literal-pipe encoding before padding without defining whether width counts the added escape bytes,
and
"preserves alignment marker positions" does not state the exact marker and dash construction order.


#### Impact

Different implementations can emit different bytes or change code-span payloads while satisfying the stated acceptance
criteria. Table columns can also receive different widths around escaped pipes or alignment markers, defeating the exact
byte and idempotence guarantees.


#### Suggestion

Specify the code-span algorithm for empty, all-space, and leading/trailing-space payloads, including the exact emitted
padding and semantic payload after reparsing. Rewrite table serialization as an ordered algorithm that states when
inline rendering, pipe encoding, width measurement, marker placement, padding, and framing occur, and whether width
counts semantic characters or rendered escape bytes. Include expected bytes for those boundary cases.


#### Outcome


## Notes

The generic scope, sibling design link, Task 01 heading hierarchy, parser span and opaque fallback rules, raw-HTML and
source-break policy, task-marker state, red/green ordering, wrapper delegation and CWD behavior, optimistic replacement
safety, generic corpus, quality gates, and explicit zero-unknowns statement show no regression. Approval remains blocked
only by S06.
