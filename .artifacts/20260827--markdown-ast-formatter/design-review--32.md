# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 32 independently reviews the requested change from Zensical-default to GFM-default behavior and the required
structural regression checks. One critical structural regression remains.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review found:

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- **C01** ⚠: Review 31 recorded the profile headings as nested under AC12, but the current plan has both profile
  headings
  at `####` level again. The structural correction has regressed.
- **S01** ✓: The complete unsupported-claim predicates and malformed or incomplete versus unknown-text fallback
  distinctions remain in AC05.


## Findings

### Summary

| Finding ID | Title                           | Outcome |
| ---------- | ------------------------------- | ------- |
| C01        | Profile headings are not nested |         |


### Critical

#### C01: Profile headings are not nested under AC12


#### Where

Acceptance Criteria, AC12 profile matrices, lines 183 and 196


#### Issue

`GFM profile` and `Zensical profile` are `####` headings, making them siblings of AC12 and the other acceptance
criteria instead of `#####` supporting headings nested under AC12. This contradicts the structural correction recorded
in review 31.


#### Impact

The plan is not structurally valid with the required AC01-AC17 hierarchy. A consumer that inventories `####` headings
cannot associate either profile matrix with AC12 without an undocumented interpretation.


#### Suggestion

Change both headings to `##### GFM profile` and `##### Zensical profile`. Keep AC01 through AC17 as the only `#### AC##`
headings.


#### Outcome


## Notes

The requested default-profile review otherwise found no stale Zensical default. Goal, `format`, `check`, wrapper,
recursive migration, and architecture consistently select GFM when omitted and require `--zensical` for Zensical.
The flags remain mutually exclusive. Exact parser, tokenizer, fixture, and Zensical pins, ownership and dispatch,
raw-HTML rejection, canonical rendering, first-H1 policy, write safety, and idempotence behavior remain intact. No
tests, builds, or linters were run.
