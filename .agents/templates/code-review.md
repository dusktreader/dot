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
     Finding numbers use a single-letter prefix: C## for Critical, S## for Significant, T## for Trivial. -->

### Critical

#### C01: {{ Title }}

- **Where**: `file:line`
- **Issue**: {{ Description }}
- **Impact**: {{ Concrete impact }}
- **Fix**: {{ Specific action needed }}


## Skills Applied

<!-- List each skill loaded. Note whether project-local or global fallback. -->

- {{ skill name }}: {{ project-local | global fallback }}


## Decision

**{{ APPROVED | BLOCKED — CHANGES REQUIRED }}**

{{
  If blocked: list the findings that must be resolved before re-review.
  If approved: confirm that all quality gates passed.
}}
