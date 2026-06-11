# Design Plan Review: {{ Title }}

**Iteration {{ N }}**


## Source Artifact

{{ path to artifact }}


## Overview

The review surfaced findings:

- **Critical**:    {{ critical count }}
- **Significant**: {{ significant count }}
- **Trivial**:     {{ trivial count }}


## Prior Review Resolution

<!-- Include this section only for re-reviews (N > 01). Omit for the first review.
     For each prior finding, mark resolved (✓), partial (⚠), or unresolved (✗) with a note. -->

- **C01** ✓ / ⚠ / ✗: {{ note }}


## Findings

<!-- Add a subsection for each severity level that has findings (Critical, Significant, Trivial).
     Within each level, add one entry per finding. Omit levels with no findings.
     Finding numbers use a single-letter prefix: C## for Critical, S## for Significant, T## for Trivial.

     Formatting rules:
     - Each finding field is an h5 heading (Where, Issue, Impact, Suggestion, Outcome).
     - Every heading must be followed by a blank line before its content.
     - Every heading must be preceded by two blank lines UNLESS it is the first child of its parent
       section (i.e. directly after the #### finding heading with no prior content). -->

### Summary

<!-- One row per finding. Written by the reviewer with Outcome left empty.
     The orchestrator fills in the Outcome column after discussing each finding with the human.
     Each Outcome entry should be one sentence describing how the finding was addressed (or why it
     was deferred/overridden), not just a status word like "Fully addressed". -->

| Finding | Title                   | Outcome              |
| ------- | ----------------------- | -------------------- |
| C01     | {{ title }}             | {{ outcome status }} |

### Critical

#### C01: {{ Title }}

##### Where

{{ Section }} — {{ Line number }}


##### Issue

{{ Description }}


##### Impact

{{ Concrete impact on downstream work }}


##### Suggestion

{{ If applicable, a concrete rewrite the reviewer could accept verbatim }}


##### Outcome

<!-- Filled in by the orchestrator after discussing with the human. Describe whether the finding
     was accepted and applied, partially applied, deferred, or overridden, and why. -->


## Notes

{{
  Significant context for the orchestrator to use while discussing these findings with a human.
  Things like: "Findings C01 and S03 are related; resolving C01 likely resolves S03."
}}
