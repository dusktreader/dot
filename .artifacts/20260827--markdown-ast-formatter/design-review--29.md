# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 29 re-reviews the plan against iteration 28, limited to C01 and the S01-S04 checklist requested for this
pass. C01 remains unresolved and S01 remains partially resolved. The remaining checklist items are resolved without
regressions. The plan is not approved.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 1
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✗: The GFM and Zensical profile headings remain `####` siblings of `#### AC12`; they are not nested `#####`
  headings.
- **S01** ⚠: Claim and fallback language now covers required bodies, terminators, incomplete forms, and shared table
  fallback, but the Zensical-side rejection of GFM-only syntax still lacks a finite, explicit claim predicate.
- **S02** ✓: Shared task-list, table, and reference ownership is single and consistent in both profile matrices, with
  dedicated shared owners excluded from the base rows.
- **S03** ✓: Dispatch is an ordered phase sequence with selected-profile gating; unselected recognizers are unavailable.
- **S04** ✓: Runtime and reference dependency pins, parser options, fixture configuration, and omitted-profile defaults
  remain exact. Zensical remains the default for `format`, `check`, and the wrapper.


## Findings

### Summary

| Finding ID | Title                                             | Outcome |
| ---------- | ------------------------------------------------- | ------- |
| C01        | Profile matrices remain outside AC12              |         |
| S01        | Cross-profile claim predicate is still not finite |         |


### Critical

#### C01: Profile matrices remain outside AC12


#### Where

Acceptance Criteria, `AC12` and the `GFM profile` and `Zensical profile` headings, lines 154-187


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


### Significant

#### S01: Cross-profile claim predicate is still not finite


#### Where

`AC05`, `AC12`, and the GFM-only row in the Zensical matrix, lines 56-73, 154-164, and 209


#### Issue

The revision clearly states that selected-profile claims include required bodies and termination, that incomplete
forms fall back to baseline text, and that a shared table requires a valid delimiter row. However, the Zensical matrix
defines an unsupported GFM construct only as a “complete GFM-only construct,” meaning syntax absent from the matrix.
That is not a finite claim predicate. It does not define which GFM source forms reserve their spans under `--zensical`,
nor distinguish them from unknown extension-like text, which AC05 says remains baseline text.


#### Impact

Independent implementations cannot produce a deterministic, testable cross-profile rejection set under `--zensical`.
The same source can be rejected as a complete unsupported GFM construct or accepted as ordinary baseline text, so
cross-profile rejection and fallback behavior remain under-specified.


#### Suggestion

Define the unsupported GFM claim predicate as a finite, testable grammar or enumerated set of complete GFM-only source
forms. For each form, state the required delimiters, body, and terminator, and state that malformed or incomplete forms
fall back to baseline text while unknown extension-like text remains baseline text. Apply the same explicit distinction
to any Zensical-only claims rejected under `--gfm`.


#### Outcome


## Notes

The shared task-list, table, and reference rows use the same named owners in both profile matrices, and the base rows
exclude those dedicated constructs. The numbered dispatch sequence places profile validation, references, raw HTML,
shared blocks, attachments, profile blocks, inline parsing, normalization, and rendering in order; it also explicitly
makes unselected recognizers unavailable.

The exact runtime and fixture pins and options remain unchanged. Omitted profiles still default to Zensical for
`format`, `check`, and the wrapper. The approved raw-HTML rejection, canonical rendering, first-H1 policy, optimistic
writes, and second-pass idempotence contracts remain present. No tests, builds, or linters were run.
