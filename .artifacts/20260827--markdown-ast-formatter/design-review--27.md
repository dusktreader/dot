# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 27 reviews the revised explicit GFM and Zensical profiles, with Zensical as the default and no separate
Material oracle. The profile changes introduce one structural regression and several unresolved profile, fixture, and
dispatch contracts. The plan is not approved.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 1
- **Significant**: 4
- **Trivial**: 0


## Prior Review Resolution

- **S02** ✓: The corrected delimiter-boundary sentinel and the surrounding delimiter ownership rules remain present,
  with no regression found in that area.


## Findings

### Summary

| Finding ID | Title                                            | Outcome |
| ---------- | ------------------------------------------------ | ------- |
| C01        | Profile matrices are not nested under AC12       |         |
| S01        | Profile rejection rules conflict with fallback   |         |
| S02        | Check profile omission conflicts with defaulting |         |
| S03        | Reference fixture configuration is not exact     |         |
| S04        | Matrix ownership and dispatch are not explicit   |         |


### Critical

#### C01: Profile matrices are not nested under AC12


#### Where

Acceptance Criteria, `AC12`, lines 148-192


#### Issue

`GFM profile` and `Zensical profile` are `####` headings, making them siblings of `#### AC12` and the other
acceptance criteria. They are supporting matrix sections for AC12, not additional acceptance criteria. AC01 through
AC17 remain sequential, but the new profile headings break the required nested structure.


#### Impact

A consumer that inventories `####` headings cannot distinguish the two profile matrices from acceptance criteria or
associate them with AC12 without applying an undocumented interpretation. This reverses the previously corrected
heading structure.


#### Suggestion

Change both headings to `##### GFM profile` and `##### Zensical profile` under AC12. Keep AC01 through AC17 as the
only `#### AC##` headings.


#### Outcome


----

### Significant

#### S01: Profile rejection rules conflict with fallback


#### Where

AC05 and the GFM and Zensical matrices, lines 56-67 and 158-197


#### Issue

AC05 says incomplete profile openers and ordinary punctuation remain baseline text. The GFM table row simultaneously
says missing headers or separators and malformed separators fail, without defining which of those inputs constitutes a
complete table attempt rather than an incomplete opener. The task-list rejection example has the same problem: GFM and
Zensical both accept `[ ]`, `[x]`, and `[X]` immediately after a list marker in a list item, so the plan identifies no
GFM task-list form that the Zensical contract excludes.


#### Impact

The same source can be either valid baseline text or a profile error, and the same task-list source can be either
GFM-only or shared. Independent implementations will therefore disagree on profile acceptance and cross-profile
rejection while still appearing to follow the matrix.


#### Suggestion

Define the finite predicate for an attempted GFM table and state whether malformed attempts fail or fall back to
CommonMark text. Remove the task-list example as GFM-only unless a concrete excluded form is added; otherwise declare
the two task-list rows shared with one semantic contract.


#### Outcome


#### S02: Check profile omission conflicts with defaulting


#### Where

AC04 and AC16, lines 48-53 and 225-231


#### Issue

AC04 says the selected profile is required again for `check`, while AC16 says the OpenCode wrapper defaults an omitted
profile to Zensical. The goal and AC04 also establish Zensical as the default generally. The plan does not say whether
an omitted `check` profile is an explicit-error case or a Zensical selection, nor how a GFM-formatted file can be
checked without its profile being supplied.


#### Impact

The formatter and wrapper can disagree about whether an omitted profile is valid. A check of GFM canonical source can
silently use Zensical and report a false difference, violating the same-profile comparison contract.


#### Suggestion

Choose one rule and state it in both AC04 and AC16. If the default applies to `check`, say that omission selects
Zensical and that GFM checks require `--gfm`. If `check` requires an explicit profile, remove the wrapper default for
that mode. Define the same rule for the formatter and wrapper.


#### Outcome


#### S03: Reference fixture configuration is not exact


#### Where

Architecture, lines 250-274


#### Issue

The package versions are pinned, but the configuration is not. `gfm-like2` is named without defining its exact preset
contents or how formal task lists and extended autolinks are enabled. The Python-Markdown and PyMdown fixture uses a
“settled extension and option set” and “selected PyMdown extensions” without enumerating them. The Zensical fixture is
described as having no theme, plugins, extensions, or build, but does not give the exact configuration values. The
previously explicit fixture-only `theme: null` and `build: false` values are no longer present.


#### Impact

Reference runs are not reproducible, and fixture output cannot demonstrate that acceptance is limited to the stated
matrices. Implementers may enable incidental parser or extension behavior, especially for GFM task lists, or restore
the removed Material oracle indirectly through an unspecified ecosystem configuration.


#### Suggestion

Enumerate the exact runtime preset, parser options, tokenizer options, and any extension responsible for each GFM row.
List every Python-Markdown/PyMdown extension and option used by the fixture, and state the literal Zensical no-theme and
no-build configuration values. Keep all of these fixture-only and retain the explicit statement that Material is not a
reference dependency.


#### Outcome


#### S04: Matrix ownership and dispatch are not explicit


#### Where

AC12 and Architecture, lines 148-155 and 250-261


#### Issue

AC12 requires one owner per accepted matrix row, but both matrices expose only `Area`, source semantics, and rendering;
they do not identify the owner. The architecture says that the GFM core configuration enables tables, task lists,
strike, and extended autolinks, while also describing profile adapters and selected-profile recognizers, without
assigning those rows to the core, the GFM adapter, or a formatter-owned recognizer. The overlapping GFM and Zensical
task-list spelling makes this omission observable.


#### Impact

Dispatch can accidentally enable GFM behavior in Zensical or let two components claim the same source. That would
violate
the one-owner rule and the required cross-profile rejection behavior even if each matrix row looks complete in
isolation.


#### Suggestion

Add an owner designation to every accepted row, including the exact core or adapter responsible for each GFM extension.
State the block and inline dispatch order, the raw-HTML classification point, and the shared task-list ownership and
claim predicate. Keep unselected profile recognizers unavailable rather than relying on parser configuration defaults.


#### Outcome


## Notes

- AC01-AC11 and AC13-AC17 retain coherent shared frontmatter, raw-HTML, canonical serialization, migration,
  idempotence, `check`, and optimistic write-safety intent once the profile contracts above are resolved.
- The distinction between multi-file preflight failure and a later per-file commit failure remains explicit: preflight
  writes nothing, while an earlier committed sibling may remain after a later commit failure.
- No tests, builds, or linters were run.
