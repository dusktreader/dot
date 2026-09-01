# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 28 re-reviews the targeted two-profile revision against iteration 27. The plan resolves the defaulting and
reference-fixture findings, but the matrix structure and parts of the ownership, dispatch, and cross-profile contracts
remain unresolved. The plan is not approved.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 1
- **Significant**: 3
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✗: The GFM and Zensical matrices remain `####` siblings of `#### AC12` instead of nested `#####` sections.
- **S01** ⚠: Table and shared task-list semantics are clearer, but the complete-construct claim and fallback rules
  remain ambiguous for malformed or incomplete profile syntax.
- **S02** ✓: Omission selects Zensical for both `format` and `check`, and GFM output requires `--gfm` when checked.
- **S03** ✓: Runtime, fixture, and dependency versions and configuration values are now enumerated.
- **S04** ⚠: Owner columns and a high-level dispatch statement were added, but shared rows still overlap base owners
  and block/inline precedence is not fully specified.


## Findings

### Summary

| Finding ID | Title                                                   | Outcome |
| ---------- | ------------------------------------------------------- | ------- |
| C01        | Profile matrices remain outside AC12                    |         |
| S01        | Cross-profile claim and fallback predicates are unclear |         |
| S02        | Shared rows have overlapping and inconsistent owners    |         |
| S03        | Dispatch does not define complete phase precedence      |         |


### Critical

#### C01: Profile matrices remain outside AC12


#### Where

Acceptance Criteria, `AC12` and the `GFM profile` and `Zensical profile` headings, lines 150-201


#### Issue

The two profile headings are still `####` headings, making them siblings of `#### AC12` and of the other acceptance
criteria. They are supporting matrices for AC12, not additional acceptance criteria.


#### Impact

A consumer that inventories `####` headings cannot distinguish the two matrices from AC01-AC17 or associate them with
AC12 without an undocumented interpretation. This is the same structural regression identified in iteration 27.


#### Suggestion

Change both profile headings to `##### GFM profile` and `##### Zensical profile` under `#### AC12`. Keep AC01 through
AC17 as the only `#### AC##` headings.


#### Outcome


----

### Significant

#### S01: Cross-profile claim and fallback predicates are unclear


#### Where

`AC05` and the GFM and Zensical matrices, lines 56-69 and 169-202


#### Issue

The revision adds “complete unsupported profile construct” and “complete GFM table attempt” language, but does not
define a finite claim predicate for unsupported constructs. The accepted Zensical rows require structure such as
nonempty four-space children, while the cross-profile examples name bare forms such as `!!!`, `=== "..."`, and `@if`.
It is therefore unclear whether those examples are complete constructs that fail or incomplete openers that remain
baseline text. The table rule also says a malformed intended delimiter is baseline text unless it is part of a complete
attempt, while a complete attempt is defined by delimiter cells satisfying the valid grammar.


#### Impact

The same malformed or incomplete source can receive either a profile diagnostic or ordinary CommonMark treatment.
Independent implementations can consequently disagree on cross-profile rejection, ordinary-punctuation fallback, and
whether malformed table syntax is claimed by the table adapter.


#### Suggestion

Define a separate finite claim predicate for every profile-only construct and distinguish it from the successful
acceptance predicate. State whether a recognized opener with missing or malformed children is baseline text or a profile
error. For tables, explicitly classify a header plus invalid delimiter as either a baseline fallback or a rejected
complete attempt, and remove examples that are syntactically incomplete unless they show their required children.


#### Outcome


----

#### S02: Shared rows have overlapping and inconsistent owners


#### Where

`AC12` ownership statements and the GFM and Zensical matrices, lines 152-164, 169-201


#### Issue

The GFM CommonMark base row includes references while a separate References row assigns them to the Reference
prepass. The Zensical CommonMark base row includes references, task lists, and tables while separate shared rows assign
task lists and tables to the shared adapters, and the architecture still assigns reference collection to a prepass.
The matrices therefore do not give each shared source construct one unambiguous owner, nor do they use the same explicit
owner representation for references in both profiles.


#### Impact

An implementation can let the core parser and a prepass or shared adapter both claim the same source. That can produce
different AST ownership and dispatch behavior between profiles, violating the one-owner rule and the requirement that
shared task, table, and reference semantics be identical.


#### Suggestion

Remove references, task lists, and tables from the base-row source contracts where dedicated shared rows own them. Add
an explicit shared Reference prepass row to both matrices, or otherwise name the same sole owner in both profiles. State
that each shared source spelling is claimed exactly once before profile-specific dispatch.


#### Outcome


----

#### S03: Dispatch does not define complete phase precedence


#### Where

`AC12` and Architecture, lines 152-164 and 268-273


#### Issue

The architecture names profile gating, raw-HTML classification, shared task/table recognition, profile recognizers,
reference collection, and post-block attributes, but it does not give them one complete ordered phase list. In
particular, “block/inline recognizers” does not establish block-versus-inline order or precedence among core, shared,
and selected-profile recognizers, and the reference prepass is mentioned separately rather than placed in that order.


#### Impact

Implementations can classify the same source differently when a profile form overlaps baseline syntax or when an
attribute, reference, table, or task marker crosses a block boundary. That leaves profile rejection, AST nesting, and
shared semantic preservation under-specified despite the owner table.


#### Suggestion

Add a numbered dispatch sequence that places profile validation, reference collection, raw-HTML classification outside
code, block recognition, post-block attachments, inline recognition, normalization, and rendering in one order. Define
the precedence within block and inline dispatch and state that a complete selected-profile claim reserves its source
before fallback text parsing.


#### Outcome


## Notes

- Profile flag selection, mutual exclusion, repeated-flag handling, invalid-value diagnostics, Zensical omission for
  both modes, wrapper propagation, and the GFM `check` requirement are explicit enough for this review.
- The exact runtime options, reference fixture configurations, pinned dependencies, and exclusion of Material as an
  authority are explicit enough for this review.
- No regression was found in the retained raw-HTML rejection, canonical serialization, first-H1 policy, optimistic
  writes, or second-pass idempotence contracts.
- No tests, builds, or linters were run.
