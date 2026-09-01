# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 34 is a targeted independent review of the table-rule correction. It checks AC07 and both profile table rows,
plus the requested regression surface. No broader design review was performed.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The targeted review found:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0

**Approval**: Approved. No findings remain.


## Prior Review Resolution

- No prior findings remain from review 33. That review approved the heading correction; this pass independently checks
  the
  subsequent table-formatting correction within the requested scope.


## Findings

### Summary

No findings remain.


## Notes

- AC07 requires human-readable aligned columns with leading and trailing pipes, exactly one ASCII space inside each
  pipe,
  canonical inline cell rendering, ordinary-space trimming, Unicode code-point width measurement, and width-based
  padding.
- AC07 defines separator alignment markers and minimum dash widths, GFM ragged-row normalization, short-row empty-cell
  filling, excess-cell handling, malformed or block-content rejection, code-span pipe preservation, and the settled
  literal-pipe backslash-parity codec.
- The GFM and Zensical shared-table rows name the same owner and the same AC07 algorithm. Their source claims,
  ragged-row
  behavior, canonical cell treatment, pipe framing, Unicode padding, and alignment-marker handling are consistent.
- AC07's reparse requirement, reinforced by AC13 and AC17, covers table idempotence. Profile selection and GFM
  defaulting,
  raw-HTML rejection, canonical rendering, and optimistic write behavior show no obvious regression.
- No tests, builds, or linters were run.
