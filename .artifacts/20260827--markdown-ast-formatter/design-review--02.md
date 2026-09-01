# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 02**


## Source Artifact

.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review found no unresolved prior findings and no regressions:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✓: `Unknowns` now contains three short, explicit questions in a compliant flat list.
- **C02** ✓: The formatter-owned grammar and validation boundary now govern parser-permissive and forbidden syntax.
- **C03** ✓: The H1 exception is removed, affected agent documents are migrated, and recursive formatting has a
  zero-rejection gate.
- **S01** ✓: The frontmatter envelope, safe YAML model, rejected features, deterministic serialization, and
  data-preservation rule are explicit.
- **S02** ✓: Supported node kinds now have stated canonical rendering and unsupported kinds are rejected.
- **S03** ✓: H1 cardinality, heading depth, hierarchy transitions, and source versus inserted separators are specified.
- **S04** ✓: Formatter and wrapper failure behavior, diagnostics, ordering, and check semantics are explicit.
- **S05** ✓: Code fences are backtick-based, collision-safe, and constrained by an explicit newline and info-string
  policy.
- **S06** ✓: Table headers, separators, widths, alignment, cell boundaries, and malformed-input rejection are specified.
- **S07** ✓: Atomic per-file replacement, preflight timing, symlink and permission handling, concurrency checks, and
  batch failure boundaries are explicit.


## Findings

### Summary

No new findings. The revisions resolve the prior checklist without introducing a regression.


## Notes

The review was limited to the prior findings and regression check requested for iteration 02. The revised plan now
provides a consistent contract for validation, canonical rendering, migration, integration failures, and safe writes.
