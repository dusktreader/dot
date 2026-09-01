# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 36 is a targeted independent review of the heading-transition separator change and its direct regressions.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- Review 34's table correction remains intact in AC07 and both shared-table profile rows. No table regression was found.


## Findings

### Summary

| Finding | Title                                             | Outcome |
| ------- | ------------------------------------------------- | ------- |
| C01     | Profile matrix headings are not nested under AC12 |         |


### Critical

#### C01: Profile matrix headings are not nested under AC12


#### Where

Acceptance Criteria, AC12, approximately lines 179-235; specifically lines 199 and 212.


#### Issue

`GFM profile` and `Zensical profile` use `####`, the same heading level as `AC12`, rather than a child level.
They are therefore sibling sections instead of headings nested under AC12.


#### Impact

The profile matrices are not structurally scoped to the executable syntax-ownership criterion. This violates the
required AC12 nesting and can cause document consumers to interpret the unnumbered profile sections as peers of the
numbered acceptance criteria.


#### Suggestion

Change both profile headings to `##### GFM profile` and `##### Zensical profile`, keep `AC01` through `AC17` at their
consistent `#### ACnn` level, and apply the canonical higher-level section spacing before AC13 if required by the
Markdown formatter.


#### Outcome


----

## Notes

- AC07 and AC09 define only a formatter-generated `HeadingSeparator`, with no thematic-break AST or preservation
  concept. The node is emitted exactly as `---` plus LF when a heading level decreases from the immediately preceding
  heading, and never otherwise.
- AC05, the GFM matrix, and the Zensical matrix explicitly exclude thematic-break source constructs. AC09 consumes
  `---`, `***`, and `___` only at a required downward transition, canonicalizes each to `---`, and rejects them
  elsewhere without intent inference.
- AC07, AC09, AC13, and AC17 make reparsing, idempotence, and exact separator behavior coherent.
- GFM defaulting, `--zensical`, raw-HTML rejection, and write safety remain covered by the existing criteria. Human-
  readable table alignment remains intact.
- No tests, builds, or linters were run, and the design plan was not edited.
