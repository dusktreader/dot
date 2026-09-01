# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 19 re-reviews C01 and S02 from iteration 18 and checks for regressions in the requested parser ownership,
serialization, precedence, policy, round-trip, write-safety, and plan-structure areas.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

The supporting-heading regression is fixed. The exact delimiter and math contract is substantially more explicit, but
it still does not define a complete reparse-safe serializer for delimiter boundaries, extension delimiters, or math
source encoding.


## Prior Review Resolution

- **C01** ✓: `Table serialization details`, `Block profile`, and `Inline and fence profile` are now `#####` supporting
  headings, while AC01 through AC17 remain the `#### AC##` headings.
- **S02** ⚠: Core delimiter collision handling, literal backslash output, table pipe escaping, and block-math delimiter
  protection are now specified more precisely. Closing-boundary behavior, extension-delimiter escaping, math escape
  parity, and the relationship between math delimiter metadata and canonical source remain unresolved.


## Findings

### Summary

| Finding ID | Title                                            | Outcome |
| ---------- | ------------------------------------------------ | ------- |
| S02        | Exact delimiter and math round trips remain open |         |


### Significant

#### S02: Exact delimiter and math round trips remain open


#### Where

AC07-AC08, AC12-AC13, approximately lines 167-177, 230-248, 407-410, and 466-483.


#### Issue

The plan adds exact-looking rules, but the remaining rules are not an executable, inverse serialization contract:

- The core delimiter algorithm says to escape a boundary when a run “would be recognized as a different delimiter.” That
  is still a parser-dependent predicate. It does not define the exact bytes examined at an opening or closing boundary,
  the left/right context, or how escaping avoids turning an enclosing closing delimiter into a literal delimiter.
- The algorithm is stated for core emphasis, strong, and strike. Mark, caret, and tilde only say to serialize recursive
  children with the same delimiter. They do not define collision handling when a child ends in that delimiter or when a
  semantic backslash is adjacent to it.
- Inline math uses fixed per-atom replacements for `$` and backslash, but does not define the parity calculation for
  adjacent encoded atoms. It also retains source delimiter kind as AST metadata while emitting one canonical delimiter
  spelling, so reparsing cannot recover that field as stated.
- Block math protects a body line equal to `$$` by adding a backslash, but does not define the inverse normalization
  that
  removes that protective byte. The canonical line therefore has no stated path back to the same semantic body.


#### Impact

Independent implementations can emit different bytes, and canonical output can reparse into a different inline or math
AST. Nested delimiter content, literal backslashes, extension styling, math containing dollars or delimiter-like lines,
and the stated idempotence guarantee remain untestable.


#### Suggestion

Replace the current delimiter and math prose with one complete semantic-atom serialization contract. Define exact
opening, closing, and sibling-boundary contexts; specify the delimiter-run and odd/even backslash predicates over the
already-emitted bytes; identify which child or boundary byte receives an escape; and apply the same contract to mark,
caret, and tilde. Define math serialization as an explicit inverse codec for adjacent literal backslashes and dollars,
including the protective encoding and decoding of a block body line equal to `$$`. Finally, either exclude source
delimiter kind from normalized-AST equality or preserve it in canonical source; retaining it while canonicalizing both
spellings to `$...$` and `$$...$$` cannot satisfy the reparse invariant.


#### Outcome


## Notes

The requested nested-heading policy, one-owner core/Betterem model, profile-versus-baseline precedence, fence
annotations, policy predicates, raw-HTML rejection, table shape and pipe rules, optimistic writes, multi-file behavior,
and canonical plan section structure are explicit enough for this review. No tests, builds, or linters were run.
