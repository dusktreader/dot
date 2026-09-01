# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 30 independently re-reviews the revised plan against iteration 29, limited to C01, S01, and the requested
regression checklist. S01 is resolved, but C01 remains unresolved. The plan is not approved.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✗: The GFM and Zensical profile headings remain `####` siblings of `#### AC12`, rather than `#####` headings
  nested under AC12.
- **S01** ✓: AC05 now enumerates complete unsupported Zensical and GFM claim forms, states their completeness
  requirements, and distinguishes malformed or incomplete candidates from unknown extension-like baseline text.


## Findings

### Summary

| Finding ID | Title                                | Outcome |
| ---------- | ------------------------------------ | ------- |
| C01        | Profile matrices remain outside AC12 |         |


### Critical

#### C01: Profile matrices remain outside AC12


#### Where

Acceptance Criteria, `AC12` and the `GFM profile` and `Zensical profile` headings, lines 161-196


#### Issue

The two profile headings are still `####` headings. They remain siblings of `#### AC12` and the other acceptance
criteria instead of being supporting matrices nested under AC12.


#### Impact

A consumer that inventories `####` headings cannot distinguish the profile matrices from AC01-AC17 or associate them
with AC12 without an undocumented interpretation.


#### Suggestion

Change both profile headings to `##### GFM profile` and `##### Zensical profile` under `#### AC12`. Keep AC01 through
AC17 as the only `#### AC##` headings.


#### Outcome


## Notes

The requested checks found no regressions in profile defaults or CLI behavior, shared task-list/table/reference
ownership, dispatch, exact pins or parser options, raw-HTML rejection, canonical behavior, first-H1 policy, writes,
or idempotence. No tests, builds, or linters were run.
