# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 03**


## Source Artifact

.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**: 1
- **Significant**: 6
- **Trivial**: 0


## Prior Review Resolution

Iteration 02 recorded no new findings. The iteration-01 checklist remains resolved as follows:

- **C01** ✓: The Unknowns section remains a compliant three-item flat list. The unpinned language matrix is a new
  substantive gap, not a recurrence of the structural issue.
- **C02** ✓: The formatter-owned validation boundary remains authoritative. The expanded adapter architecture leaves a
  separate conformance gap described in S01.
- **C03** ✓: The H1 exception remains removed, with migration and a zero-rejection corpus gate.
- **S01** ✓: The frontmatter envelope, safe data model, rejection rules, and deterministic serialization requirement
  remain explicit.
- **S02** ✓: The plan still names canonical rendering for the previously identified node kinds.
- **S03** ✓: H1 cardinality, heading depth, hierarchy transitions, and source versus inserted separators remain
  explicit.
- **S04** ✓: Formatter and wrapper failure behavior, diagnostics, ordering, and check semantics remain explicit.
- **S05** ✓: Code fences remain backtick-based, collision-safe, and constrained by an explicit newline policy.
- **S06** ✓: Table headers, separators, widths, alignment, cell boundaries, and malformed-input rejection remain
  explicit.
- **S07** ✓: Atomic replacement, preflight timing, symlink and permission handling, concurrency checks, and batch
  failure boundaries remain explicit.


## Findings

### Summary

| Finding | Title                                                    | Outcome |
| ------- | -------------------------------------------------------- | ------- |
| C01     | The pinned compatibility language is not actually pinned |         |
| S01     | Adapter dispatch and conformance are unspecified         |         |
| S02     | Complete CommonMark/GFM conflicts with rejection rules   |         |
| S03     | The raw-HTML boundary is not operationally defined       |         |
| S04     | Extension canonicalization is not specified              |         |
| S05     | Inline and width normalization is underdefined           |         |
| S06     | Code preservation conflicts with global whitespace       |         |


### Critical

#### C01: The pinned compatibility language is not actually pinned


#### Where

Acceptance Criteria — AC05 and AC17, lines 56–79 and 190–195; Unknowns, lines 233–238; Architecture, lines 205–210


#### Issue

The plan calls the Zensical, MkDocs Material, and PyMdown syntax set pinned, but supplies no package versions,
enabled-extension configuration, custom SuperFences configuration, or exact Zensical directive grammar. The phrase
"when that syntax has a formatter-owned AST representation" makes the supported language depend on an implementation
choice. AC17 also requires coverage of a "complete" matrix that the plan never enumerates.


#### Impact

There is no authoritative accepted language or rejection boundary. Different dependency versions and configurations
can accept different constructs, so AC05, AC11, AC13, and AC17 cannot be tested reproducibly or handed to an
implementation planner as a finite scope.


#### Suggestion

Resolve the compatibility unknown before approval. Name the exact parser and extension versions and configurations,
then provide a finite matrix for each feature with accepted grammar, invalid cases, canonical source output, and
semantic metadata. Pin parser behavior only; keep theme and build rendering outside the matrix. Replace the
implementation-dependent AST-representation qualifier with that explicit matrix.


#### Outcome


### Significant

#### S01: Adapter dispatch and conformance are unspecified


#### Where

Architecture — lines 200–215


#### Issue

The architecture allows `markdown-it-py`, PyMdown, Zensical, and extension parsers to feed one AST, but does not
define adapter ownership, dispatch order, precedence when grammars overlap, source-span mapping, or the behavior of
unclassified parser output. The named libraries do not share one token model for tables, task lists, directives,
admonitions, fences, and raw HTML.


#### Impact

The same source can produce different ASTs, be claimed by two adapters, or fall through as prose without triggering
the fail-closed validator. Diagnostics, semantic preservation, and canonical rendering will vary by adapter choice.


#### Suggestion

Define an adapter contract covering node ownership, dispatch and precedence, source spans, conflict resolution,
unknown-token rejection, and the formatter-owned AST invariants. Add a cross-adapter conformance matrix, or choose one
authoritative parsing pipeline and use the other libraries only as compatibility oracles.


#### Outcome


#### S02: Complete CommonMark/GFM conflicts with rejection rules


#### Where

Acceptance Criteria — AC04, AC10, AC11, and AC12, lines 46–53, 120–138, and 141–147


#### Issue

AC04 promises every CommonMark and GFM construct except raw HTML, but later rules reject or discard valid language
behavior. AC10 ignores ordered-list start numbers even though they affect list semantics. AC12 rejects ragged GFM body
rows instead of defining the pinned GFM row behavior. AC11 rejects arbitrary, otherwise valid CommonMark fence info
strings when their words are not recognized metadata. The bold-subject style rule also needs an explicit dialect
exception if it rejects valid list content.


#### Impact

The plan cannot both accept the complete stated language and enforce these policies. It will either reject valid source
or silently change meaning, and the compatibility corpus cannot have a coherent expected result.


#### Suggestion

Separate language support from repository style restrictions. Preserve ordered-list start semantics, specify the exact
GFM behavior for short and long body rows, and either accept arbitrary CommonMark info strings or explicitly exclude
them. List every intentional exclusion from AC04 and test it as a rejection rather than calling the language complete.


#### Outcome


#### S03: The raw-HTML boundary is not operationally defined


#### Where

Acceptance Criteria — AC02, AC04, AC06, and AC08, lines 30–35, 46–53, 82–87, and 100–107


#### Issue

AC06 names HTML blocks, tags, comments, declarations, processing instructions, CDATA, and `md_in_html`, but does not
define the lexical decision for malformed tag-like text, entities, angle-bracket link destinations, or the boundary
between an HTML block and an autolink. It also does not say whether the rule applies to frontmatter scalar strings,
which AC02 otherwise accepts independently of Markdown parsing.


#### Impact

Adapters can disagree about whether source is HTML or ordinary Markdown text. Valid links or entity text may be
rejected, raw HTML may fall through as prose, and valid frontmatter data may be incorrectly rejected. Excluding theme
and build behavior does not resolve this source-level classification.


#### Suggestion

Scope AC06 explicitly to the Markdown body and define a decision table for each forbidden HTML category. Include
accepted autolinks, angle-bracket destinations, escaped and entity text, code content, malformed tag-like text, and
frontmatter strings. Test source classification only, not generated site output.


#### Outcome


#### S04: Extension canonicalization is not specified


#### Where

Acceptance Criteria — AC05, AC07, AC13, and AC17, lines 56–79, 92–97, 150–158, and 190–195


#### Issue

The extension list names feature groups but does not define each group's grammar, canonical spelling, allowed nesting,
malformed cases, or AST fields. Footnote labels and ordering, definition-list and attribute syntax, shortcode names,
math delimiters, overlapping inline extensions, SuperFences metadata, and annotation relationships all remain
implementation-dependent. "Render in pinned source syntax" is not a canonicalization rule when a feature has multiple
valid source forms.


#### Impact

Equivalent extension inputs can produce different bytes or lose relationships, while unrecognized syntax can be
mistaken for ordinary text. Idempotence and semantic-preservation tests cannot be written from AC13. Theme and build
behavior is correctly out of scope, but the source AST contract is still incomplete.


#### Suggestion

Add one feature matrix per extension with exact syntax, nesting and precedence, AST metadata, canonical output,
invalid and unknown cases, and relationship invariants. Keep theme wrappers, anchors, tooltips, and other site effects
out of both the acceptance criteria and compatibility oracles.


#### Outcome


#### S05: Inline and width normalization is underdefined


#### Where

Acceptance Criteria — AC08, AC09, and AC10, lines 100–126


#### Issue

The plan does not name the canonical hard-break form or exact rules for entity and backslash normalization, link
destination escaping, title quoting, or the width metric. It does not define what happens to an unbreakable URL or word,
or whether heading punctuation, heading emphasis, and invalid bold-subject list items are rejected or rewritten.


#### Impact

Two implementations can satisfy the prose while producing different bytes or changing inline meaning. The deterministic
rendering, idempotence, and 120-character requirements are not testable at their boundaries.


#### Suggestion

Specify the hard-break delimiter, escape and entity canonical forms, destination and title grammar, width metric,
unbreakable-token policy, and reject-versus-rewrite behavior for every repository style restriction. Ensure the
hard-break
choice is compatible with the no-trailing-whitespace rule.


#### Outcome


#### S06: Code preservation conflicts with global whitespace


#### Where

Acceptance Criteria — AC07 and AC11, lines 92–97 and 129–138


#### Issue

AC07 requires output with no trailing whitespace, while AC11 requires preserving code line content, including trailing
spaces. A valid code payload can satisfy one rule only by violating the other. The plan also does not state how multiple
trailing payload newlines interact with the required structural newline before the closing fence.


#### Impact

The contract is impossible for some valid code blocks. An implementation must either mutate literal code or violate the
global output invariant, so code-preservation and idempotence tests have no consistent expected bytes.


#### Suggestion

Scope the no-trailing-whitespace rule to non-code structural and prose lines, or remove the code-preservation promise
and define the permitted normalization. Specify the exact treatment of trailing payload newlines.


#### Outcome


## Notes

The theme/build distinction is a sound scope boundary: the formatter should prove source parsing, AST meaning, and
canonical Markdown, not HTML, CSS, JavaScript, anchors, or theme behavior. C01 and S04 must be resolved together because
the version/configuration matrix supplies the grammar that S04 currently lacks. The frontmatter scalar-spelling
question remains output-affecting, but it is unchanged from the prior review's acknowledged compatibility unknown.
