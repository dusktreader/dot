# Design Plan Review: Canonical AST-based Markdown formatter

Independent targeted review of the heading-separator spacing correction and its adjacent contracts.

**Iteration 38**


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced no findings:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- Review 37 contained no unresolved findings. The targeted heading-transition behavior remains explicitly specified.


## Findings

### Summary

No findings remain. **Approved.**


## Notes

- AC07, AC09, AC13, AC17, and the architecture agree that a downward transition renders `---` between the
  preceding block and the lower-level heading, with exactly one blank line on each side. The stated result matches
  `### h3 heading\n\nloren ipsum.\n\n---\n\n## h2 heading`.
- The AST contains formatter-owned `HeadingSeparator` layout nodes only. AC05, AC07, AC09, both profile matrices, and
  the architecture exclude thematic-break AST nodes and preservation. `---`, `***`, and `___` are consumed only in a
  required downward transition and rejected elsewhere, making source handling deterministic.
- AC09 explicitly omits separators for equal or upward transitions and before the first H1. AC07, AC09, AC13, AC17,
  and the architecture require positional reparsing, normalized-AST equality, and idempotent bytes.
- Table alignment remains covered by AC07 and the shared GFM/Zensical table rows. AC04 and AC16 retain GFM as the
  default and require `--zensical` for Zensical. AC05 and AC06 retain raw-HTML rejection, while AC14 and AC15 retain
  preflight safety and optimistic atomic writes.
- No tests, builds, or linters were run, and the design plan was not edited.
