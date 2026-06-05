# Execution Review: {{ Title }}


## Source Artifacts

- **Implementation journal**: {{ path to implementation journal }}
- **Implementation plan**: {{ path found via journal }}


## Scope

**{{ task-NN | whole-plan | re-review }}** — Iteration {{ N }}


## Issue Summary

- **Critical**:    {{ count }}
- **Significant**: {{ count }}
- **Trivial**:     {{ count }}


## Verification Evidence

```
Tests:    {{ command }} → {{ result }}
Build:    {{ command }} → {{ result }}
Linter:   {{ command }} → {{ result }}
Coverage: {{ command, or "skipped (no project-documented command)" }} → {{ result }}
```


## Acceptance Criteria Verification

<!-- For task-NN scope: one row per AC in the task.
     For whole-plan scope: group rows by task.
     Omit this section for re-review if AC status is unchanged from the prior review. -->

| AC    | Status      | Evidence                                    |
| ----- | ----------- | ------------------------------------------- |
| AC01  | ✓ / ⚠ / ✗   | `file:line`, test `{{ test name }}`         |


## Scope Verification

<!-- One row per file listed in the journal as modified. -->

| File           | Justified by          | Status      |
| -------------- | --------------------- | ----------- |
| `{{ file }}`   | {{ task N, step M }}  | ✓ / ⚠ / ✗   |


## Prior Review Resolution

<!-- Include this section only for re-reviews. Omit it otherwise.
     For each prior finding, mark resolved (✓), partial (⚠), or unresolved (✗) with file:line evidence. -->

- **C01** ✓ / ⚠ / ✗: {{ evidence or explanation }}


## Findings

<!-- Add a subsection for each severity level that has findings (Critical, Significant, Trivial).
     Within each level, add one entry per finding. Omit levels with no findings.
     Finding numbers use a single-letter prefix: C## for Critical, S## for Significant, T## for Trivial. -->

### Critical

#### C01: {{ Title }}

- **Where**: `file:line`
- **Issue**: {{ Description }}
- **Impact**: {{ Concrete impact }}
- **Fix**: {{ Specific action needed }}


## Skills Applied

<!-- List each skill loaded. Note whether it was project-local or a global fallback. -->

- {{ skill name }}: {{ project-local | global fallback }}


## Decision

**{{ APPROVED | BLOCKED — CHANGES REQUIRED }}**

{{
  If blocked: list the findings that must be resolved before re-review.
  If approved: confirm that all quality gates passed and the AC are satisfied.
}}
