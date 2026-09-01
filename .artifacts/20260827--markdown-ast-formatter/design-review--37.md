# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 37 is a final targeted approval review of the heading regression fix and the related heading-transition
separator behavior.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced no findings:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- Review 36 C01 ✓: `GFM profile` and `Zensical profile` are now `#####` headings nested under AC12. AC01 through AC17
  remain the only `#### AC##` headings.


## Findings

### Summary

No findings remain. **Approved.**


## Notes

- AC07 and AC09 consistently model `HeadingSeparator` as a formatter-generated layout node, with no thematic-break AST
  or preservation path.
- AC09 inserts exactly one separator immediately before a heading on a downward transition, never before the first H1 or
  on an equal or upward transition. It consumes `---`, `***`, and `___` only in that required position and rejects them
  elsewhere under the explicit thematic-break policy exclusion.
- The separator canonicalizes to `---` plus LF. AC07, AC09, AC13, and AC17 establish deterministic reparsing,
  normalized-AST equality, and byte-identical second-pass output.
- AC07 and both shared-table rows retain aligned-column rendering. AC04 and AC16 retain GFM as the default and explicit
  `--zensical` selection; AC05 and AC06 retain raw-HTML rejection; AC14 and AC15 retain safe preflight and optimistic
  atomic write behavior.
- No tests, builds, or linters were run, and the design plan was not edited.
