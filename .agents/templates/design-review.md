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
     Finding numbers use a single-letter prefix: C## for Critical, S## for Significant, T## for Trivial. -->

### Critical

#### C01: {{ Title }}

- **Where**: {{ Section }} -- {{ Line number }}
- **Issue**: {{ Description }}
- **Impact**: {{ Concrete impact on downstream work }}
- **Suggestion**:
  ```
  {{ If applicable, a concrete rewrite snippet the user could accept verbatim }}
  ```


## Notes

{{
  Significant context for the orchestrator to use while discussing these findings with a human.
  Things like: "Findings C01 and S03 are related; resolving C01 likely resolves S03."
}}
