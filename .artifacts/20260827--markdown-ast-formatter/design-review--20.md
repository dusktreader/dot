# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 20**

Iteration 20 re-reviews S02 from iteration 19 and checks the requested parser ownership, round-trip, precedence, policy,
and safety contracts for regressions.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

The structural heading fix remains correct. S02 is only partially resolved: the plan is more explicit, but it still
lacks
an inverse-safe delimiter and math serialization contract.


## Prior Review Resolution

- **S02** ⚠: Core delimiter ownership, recursive boundary handling, inline and block math spellings, and table escaping
  are
  more explicit. Exact collision predicates, extension-delimiter handling, math escape decoding and metadata equality,
  and
  general table backslash parity remain unresolved.


## Findings

### Summary

| Finding ID | Title                                            | Outcome |
| ---------- | ------------------------------------------------ | ------- |
| S02        | Exact delimiter and math round trips remain open |         |


### Significant

#### S02: Exact delimiter and math round trips remain open


#### Where

AC07-AC08, AC11-AC13, and the table serialization details, approximately lines 167-248, 327-350, 407-412, and 466-483.


#### Issue

The revised plan closes the ownership question: core owns every `*` and `_` run, Betterem does not compete with core,
and
longest-delimiter precedence is stated for the profile forms. The surrounding profile-baseline precedence,
nested-heading
policy, fence contract, raw-HTML rejection, policy predicates, idempotence target, and write-safety contract also remain
consistent. The byte-level inverse contract is still incomplete:

- Core collision handling still delegates “recognized as a different delimiter” to an undefined parser predicate. It
  does
  not specify exact opening, closing, and sibling bytes, or the existing-backslash parity that determines whether an
  added
  escape protects the boundary. Mark, caret, and single-tilde spans are only told to recurse with the same delimiter;
  they
  receive no collision rule.
- Inline math specifies fixed emitted strings for literal dollars and backslashes, but defines no decoder or parity rule
  for
  adjacent runs. It also retains source delimiter kind as AST metadata while canonicalizing both `$...$` and `\(...\)`
  to
  `$...$`, so the stated reparse-equality guarantee cannot include that metadata.
- Block math protects a body line equal to `$$` by adding a backslash, but specifies no inverse removal of that
  protective
  byte. Reparsing therefore has no stated route back to the original body line.
- Table serialization covers one literal backslash immediately before one literal pipe with three backslashes, but does
  not
  define the odd/even rule for arbitrary runs of semantic backslashes before a pipe.


#### Impact

Independent implementations can emit different canonical bytes, and canonical output can reparse into different inline,
table, or math nodes. Nested delimiter content, adjacent math escapes, protected block-math lines, and repeated literal
backslashes remain untestable despite the global idempotence claim.


#### Suggestion

Replace the prose with one finite, byte-level inverse contract. Define the exact delimiter-run, left/right-context, and
existing-backslash parity predicates at every opening, closing, and sibling boundary, then apply that same contract to
core
delimiters and mark, caret, and tilde. Define table escaping as a formula over the complete preceding semantic backslash
run. Define math encoding and decoding for arbitrary adjacent dollar/backslash runs and explicitly decode block-math
protection. Finally, either exclude source delimiter kind from normalized-AST equality or preserve it in canonical
source.


#### Outcome


## Notes

The iteration 19 structural fix did not regress: supporting sections remain `#####` headings while AC sections remain
`####` headings. Nested H1 rejection, skipped-level policy, profile-versus-baseline precedence, fence metadata and
annotations, raw HTML, policy rejection, idempotence, and optimistic per-file write safety are explicit enough for this
focused re-review. No tests, builds, or linters were run.
