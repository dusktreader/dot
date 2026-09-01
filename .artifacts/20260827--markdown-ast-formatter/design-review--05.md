# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 05 re-reviews the revised plan against iteration 04, with emphasis on the finite dialect, dispatch,
canonicalization, parser boundaries, separator idempotence, and optimistic writes.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**: 2
- **Significant**: 4
- **Trivial**: 0


## Prior Review Resolution

- **C01** ⚠: Dependency versions, parser preset, oracle extension names, and a source matrix were added, but the
  complete parser and oracle options, finite vocabularies, and several lexical grammars remain unspecified.
- **S01** ⚠: A precedence table and explicit admonition/details tie-breaker were added, but the table contradicts the
  inline precedence rules by placing all core inline grammar before profile inline grammar.
- **S02** ⚠: The `[X]` task marker and a policy disclaimer were added, but the complete-baseline claim does not
  enumerate
  the valid CommonMark/GFM forms rejected by AC03 and the heading hierarchy policy.
- **S03** ✓: Raw HTML is scoped to the Markdown body and its code, autolink, destination, escaped-text, entity, and
  malformed tag-like boundaries are explicit.
- **S04** ⚠: The matrix now defines substantially more source and AST behavior, but several rows still lack executable
  canonical bytes, escaping, or placement rules.
- **S05** ⚠: Width, entity, destination, title, escape, and code-span rules are more concrete, but the destination
  predicate and whitespace and wrapping algorithm are still incomplete.
- **S06** ✓: Code payload trailing spaces and trailing line endings are explicitly preserved.
- **S07** ✓: `----` is reclassified by position on reparse, making inserted hierarchy separators stable.
- **S08** ✓: The write contract now explicitly promises optimistic detection rather than absolute concurrency safety and
  defines rejection of changed, non-regular, symlink, and read-only destinations.


## Findings

### Summary

| Finding | Title                                       | Outcome |
| ------- | ------------------------------------------- | ------- |
| C01     | Pinned configuration is not fully pinned    |         |
| C02     | Design plan contains a noncanonical section |         |
| S01     | Dispatch precedence contradicts itself      |         |
| S02     | Baseline exclusions are incomplete          |         |
| S04     | Extension canonicalization remains partial  |         |
| S05     | Inline lexical rules remain incomplete      |         |


### Critical

#### C01: Pinned configuration is not fully pinned


#### Where

AC05 and the extension source matrix, lines 62–216


#### Issue

Dependency versions and a named extension set are now present, but they do not freeze the dialect. The plan does not
state the complete `markdown-it-py` option set or each oracle extension's options. The admonition and details kind sets,
emoji catalog contents, and several identifiers and terms are also referred to as finite or valid without being defined.


#### Impact

Different conforming implementations can accept different bytes or assign different AST meaning. Compatibility fixtures
and canonical output remain non-reproducible, and the implementation plan lacks an authoritative acceptance boundary.


#### Suggestion

Specify every parser and oracle option, and enumerate the finite kind and shortcode sets. Define exact lexical grammars
for directive identifiers, footnote IDs, definition-list terms, paths, and other currently open categories. Treat any
catalog or vocabulary as immutable contract data with an exact, versioned definition.


#### Outcome


#### C02: Design plan contains a noncanonical section


#### Where

Top-level “Migration and verification” section, lines 312–319


#### Issue

The artifact adds a top-level section not defined by the canonical design-plan structure. The required sections are
Goal,
Acceptance Criteria, Architecture, Unknowns, and optional Technical Notes.


#### Impact

The plan violates the artifact contract and gives downstream consumers no canonical location for migration and rollout
requirements.


#### Suggestion

Move the migration and verification requirements into the relevant acceptance criteria, Architecture, Unknowns, or
Technical Notes, then remove the extra top-level section.


#### Outcome


### Significant

#### S01: Dispatch precedence contradicts itself


#### Where

Inline precedence, lines 218–222, and the Architecture dispatch table, lines 288–304


#### Issue

The dispatch table gives priority 9 to all core CommonMark/GFM block and inline grammar, then priority 10 to profile
inline grammar. The inline matrix instead places extension spans before ordinary emphasis, strong, and strike. Betterem
delimiters therefore overlap core emphasis with two conflicting owners, despite the claim that predicates are disjoint.


#### Impact

The same source can produce different nodes or let a malformed extension fall through to core prose. The fail-closed and
deterministic-owner guarantees are not implementable from these conflicting orders.


#### Suggestion

Separate block and inline dispatch tables, then make one inline order authoritative: code, links and autolinks, profile
spans and markers, core emphasis and strike, symbols, and ordinary text. Define the claim and rejection behavior for
each
recognized opener in that order.


#### Outcome


#### S02: Baseline exclusions are incomplete


#### Where

Goal and AC03–AC04, lines 9–59; heading policy in AC09, lines 130–139


#### Issue

The plan calls parser coverage complete CommonMark/GFM except raw HTML and says policy exceptions are in AC09 and AC10.
However, AC03 rejects otherwise valid documents with a leading non-H1, multiple or nested H1s, and AC09 rejects skipped
heading levels. Those valid source forms are not included in the explicit exclusion statement. The task-list `[X]` case
is
now covered.


#### Impact

The fixture contract still cannot distinguish complete parser acceptance from intentional repository policy rejection.
Implementers may either weaken the H1 and hierarchy policy or incorrectly report valid baseline fixtures as parser gaps.


#### Suggestion

Rename the claim to complete parser coverage and list every formatter-policy exclusion in AC04, including AC03 and the
heading hierarchy rule, then test parser coverage and policy rejection as separate fixture classes.


#### Outcome


#### S04: Extension canonicalization remains partial


#### Where

Block and inline extension matrices, lines 177–230, and AC13


#### Issue

The matrix promises exact canonical bytes for every row, but the Zensical row gives no canonical rendering rule,
emoji does not state its canonical source form, and labels, titles, definitions, and other quoted values lack complete
escaping and whitespace rules. Betterem and smartsymbols defer canonical text to a pinned oracle rather than defining
the
formatter's serialization.


#### Impact

Equivalent extension inputs can serialize differently or fail a second parse while still satisfying the prose. AST
meaning, idempotence, and relationship-preservation fixtures remain underdetermined.


#### Suggestion

For every matrix row, specify the exact canonical bytes, escaping, spacing, nesting, and placement of definitions and
metadata. Make the formatter's rules authoritative; use oracle output only for compatibility fixtures, not
serialization.


#### Outcome


#### S05: Inline lexical rules remain incomplete


#### Where

AC08 and AC10, lines 111–149


#### Issue

The link-destination rule does not define the full bare-destination predicate, including balanced-parenthesis cases, or
say when the bare versus angle-bracket form is selected. “A core or profile claim predicate” remains an indirect rule,
and soft-break wrapping does not define whitespace normalization or exact break opportunities.


#### Impact

Conforming implementations can choose different destination syntax, whitespace, and wrap points. Boundary cases can
change meaning or fail the required deterministic and idempotent output.


#### Suggestion

Define the complete destination and title lexical grammars, name the predicates used by ordinary-text escaping, and
state
the whitespace normalization and line-break algorithm, including tabs, existing soft breaks, and unbreakable tokens.


#### Outcome


## Notes

The raw-HTML boundary, code preservation, separator idempotence, and optimistic write contract are resolved with no
regression found. C01 and S04 are related: the finite vocabularies and grammars must be fixed before their canonical
serialization can be made executable. The plan is not ready for approval while the critical and significant findings
remain open.
