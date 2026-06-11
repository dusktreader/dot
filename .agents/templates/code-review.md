# Code Review: {{ Title }}

**Iteration {{ N }}**


## Source

<!-- List each file reviewed. -->

- `{{ file }}`


## Verification Evidence

```
Tests:    {{ command }} → {{ result, or "skipped" }}
Build:    {{ command }} → {{ result, or "skipped" }}
Linter:   {{ command }} → {{ result, or "skipped" }}
Coverage: {{ command }} → {{ result, or "skipped (no project-documented command)" }}
```


## Issue Summary

- **Critical**:    {{ count }}
- **Significant**: {{ count }}
- **Trivial**:     {{ count }}


## Prior Review Resolution

<!-- Include only for re-reviews (N > 01). Omit for first review.
     For each prior finding, mark resolved (✓), partial (⚠), or unresolved (✗) with a note. -->

- **C01** ✓ / ⚠ / ✗: {{ note }}


## Findings

<!-- Add a subsection for each severity level that has findings (Critical, Significant, Trivial).
     Within each level, add one entry per finding. Omit levels with no findings.
     Finding numbers use a single-letter prefix: C## for Critical, S## for Significant, T## for Trivial.

     Formatting rules:
     - Each finding field is an h5 heading (Where, Issue, Impact, Fix, Outcome).
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

`file:line`


##### Issue

{{ Description }}


##### Impact

{{ Concrete impact }}


##### Fix

{{ Specific action needed }}


##### Outcome

<!-- Filled in by the orchestrator after discussing with the human. Describe whether the finding
     was accepted and applied, partially applied, deferred, or overridden, and why. -->


## Skills Applied

<!-- List each skill loaded. Note whether project-local or global fallback. -->

- {{ skill name }}: {{ project-local | global fallback }}


## Decision

**{{ APPROVED | BLOCKED — CHANGES REQUIRED }}**

{{
  If blocked: list the findings that must be resolved before re-review.
  If approved: confirm that all quality gates passed.
}}
