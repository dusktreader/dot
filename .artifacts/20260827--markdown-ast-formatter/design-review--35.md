# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 35 is a final targeted independent review of the table-rule correction and the replacement of thematic-break
formatting with deterministic heading-transition separators. It also checks obvious structural and profile regressions.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review found:

- **Critical**: 2
- **Significant**: 0
- **Trivial**: 0

**Approval**: Not approved. C01 and C02 require correction.


## Prior Review Resolution

- Review 34 had no findings. The table-rule correction remains fully resolved: the shared GFM/Zensical table owner and
  human-readable alignment algorithm are explicit and coherent.


## Findings

### Summary

| Finding | Title                                                   | Outcome |
| ------- | ------------------------------------------------------- | ------- |
| C01     | Thematic-break model contradicts the separator contract |         |
| C02     | Profile matrices are not nested under AC12              |         |


### Critical

#### C01: Thematic-break model contradicts the separator contract


#### Where

Canonical output, AC07 and AC09, approximately lines 96-146; GFM and Zensical profile matrices, approximately lines
187-224; Architecture, approximately lines 284-328.


#### Issue

The plan still represents thematic breaks in the AST and distinguishes “ordinary thematic breaks” (`---`) from a
hierarchy separator (`----`). AC09 also bases rendering on a thematic break immediately before a heading. The plan does
not state that the formatter inserts a separator exactly when heading order moves from a higher level to a lower level,
does not use the required canonical line bytes `---`, and does not define what happens to source `---` outside that
positional transition.


#### Impact

An implementation can preserve or classify authored thematic breaks, emit the prohibited `----`, or accept standalone
thematic-break nodes. The generated `---` can then reparse as a thematic-break AST node instead of layout, leaving
canonical reparsing and idempotence ambiguous. The contradiction affects AC07 and AC09 directly and prevents AC13 and
AC17 from proving semantic and byte stability.


#### Suggestion

Replace authored thematic-break behavior with one positional layout rule: for each heading whose level is lower than the
preceding heading level, insert one separator line immediately before that heading; the separator content bytes are
exactly three ASCII hyphens (`---`), followed by the canonical line ending, with no separator at any other heading
transition. Remove thematic-break nodes and ordinary/hierarchy canonicalization from AC07, AC09, both profile base rows,
and the architecture. State explicitly that source `---` outside that transition is rejected as unsupported or
normalized/removed, selecting one behavior. A `---` at the transition must be consumed by position rather than by
authored intent, and reparsing canonical output must recover layout rather than a thematic-break AST node. Reconcile the
complete-CommonMark claim with the selected behavior.


#### Outcome


#### C02: Profile matrices are not nested under AC12


#### Where

Acceptance Criteria, AC12 and the profile matrices, approximately lines 167-224.


#### Issue

`GFM profile` and `Zensical profile` use `####` headings, making them siblings of `#### AC12` rather than supporting
matrices nested beneath it. They are not numbered acceptance criteria, so the document structure does not clearly
associate the matrices with the ownership criterion. This reintroduces the structural regression that review 33 marked
resolved.


#### Impact

Structural consumers can treat the matrices as additional criteria or fail to associate them with AC12. This weakens the
profile ownership contract and is a direct regression of the required AC01-AC17 structure.


#### Suggestion

Change both profile headings to `##### GFM profile` and `##### Zensical profile` beneath `#### AC12`. Keep AC01 through
AC17 as the only `#### AC##` headings.


#### Outcome


## Notes

- The table correction has no finding. AC07 explicitly requires aligned columns for human readability, and both profile
  rows use the same shared owner, delimiter rule, ragged-row normalization, width calculation, padding, and alignment
  marker behavior.
- No separate regression was found in frontmatter, first-H1 and nested-heading policy, GFM default selection,
  `--zensical` opt-in, raw-HTML rejection, wrapper propagation, or optimistic write behavior. The separator
  contradiction
  still blocks the broader canonical-output and idempotence guarantees.
- No tests, builds, or linters were run.
