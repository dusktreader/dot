# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 25 is the final independent review of only S02 from iteration 24. It verifies the corrected delimiter
boundary sentinel and the requested neighboring invariants without expanding scope.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0

**Approval**: Approved. S02 is fully resolved, and no findings remain.


## Prior Review Resolution

- **S02** ✓: The plan now defines a missing neighbor before or after a source boundary as Unicode whitespace and not
  punctuation. Together with the exact Unicode flanking predicates, this supplies the CommonMark boundary behavior
  that was missing in iteration 24.


## Findings

### Summary

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

- The left- and right-flanking predicates in AC07 are the exact CommonMark boolean forms. The corrected sentinel makes
  punctuation-edge cases such as `*(foo)*` and `*foo!*` valid, and the same values apply to core and profile runs.
- Core owns `*`, `_`, `**`, `__`, and `~~`; profile syntax owns `==`, `^^`, `^`, and `~`. Longest-run precedence,
  opening/closing/sibling boundary protection, backslash parity, and the finite `encode_literal` codec are explicit.
  Delimiter source spelling is excluded from normalized-AST equality.
- The inline and block math codecs are finite and inverse by their stated left-to-right rules. Table pipe escaping,
  code-span protection, width calculation, ragged-row normalization, and recursive label escaping are explicit.
- Block and inline dispatch orders preserve profile precedence and baseline fallback for incomplete openers. Recursive
  support blocks, heading policy, sequential AC01-AC17 structure, raw-HTML rejection, reparsing/idempotence, and
  optimistic per-file writes remain covered without a separate regression.

No tests, builds, or linters were run.
