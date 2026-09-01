# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 26 re-reviews the revised plan for the targeted removal of the separate MkDocs Material oracle. The review
finds no regressions, contradictions, or changes to previously approved behavior.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The targeted review finds:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0

**Approval**: Approved. No findings remain.


## Prior Review Resolution

- **S02** ✓: The corrected delimiter-boundary sentinel and exact flanking predicates remain explicit in AC07, with no
  regression from the reference cleanup.


## Findings

### Summary

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

- The fixture-only reference set names Zensical, Python-Markdown, and PyMdown. Runtime parser dependencies are
  separately
  identified and are not presented as compatibility oracles.
- No Material oracle, package, or configuration reference remains. Zensical's `theme: null` and `build: false` settings
  are explicit fixture-only values, while theme, generated output, and build behavior remain outside the contract.
- The finite source profile, ownership and fallback rules, pinned versions, parser options, and reference options remain
  explicit and coherent.
- AC01 through AC17 remain present and ordered. H1-first enforcement, skipped-level rejection, nested-heading rejection,
  and recursive nested-block behavior remain explicit.
- Raw HTML is still rejected from Markdown body source while valid autolinks, angle destinations, escaped syntax, code,
  and frontmatter retain their stated boundaries.
- No tests, builds, or linters were run.
