# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 04**

This re-review checks the iteration-03 checklist and the revised dialect, parser-boundary, canonicalization, and
write-safety
contracts.


## Source Artifact

.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**: 1
- **Significant**: 6
- **Trivial**: 0


## Prior Review Resolution

- **C01** ⚠: Dependency versions are now named, but the enabled configurations and finite Material source grammar are
  still not enumerated.
- **S01** ⚠: The formatter-owned authority and broad dispatch order are explicit, but overlapping extension grammars and
  all precedence decisions are not.
- **S02** ⚠: Ordered starts, ragged tables, arbitrary fence info, and rejection behavior were added, but the complete
  CommonMark/GFM claim still conflicts with intentional style rejections and an incomplete task-marker rule.
- **S03** ✓: The rule is scoped to the Markdown body and now states the autolink, destination, escaped-text, code,
  malformed
  tag-like, and frontmatter boundaries.
- **S04** ⚠: Feature matrices were added, but several extension grammars, AST fields, relationships, and canonical bytes
  remain descriptive rather than executable.
- **S05** ⚠: Hard breaks, unbreakable tokens, and the width intent are specified, but escape, entity, destination,
  title,
  and width metrics still contain implementation-dependent terms.
- **S06** ✓: The no-trailing-whitespace rule now excludes code payload lines, and code trailing-newline preservation is
  explicit.


## Findings

### Summary

| Finding | Title                                            | Outcome |
| ------- | ------------------------------------------------ | ------- |
| C01     | The finite dialect matrix is still incomplete    |         |
| S01     | Overlapping extension dispatch is unresolved     |         |
| S02     | Complete CommonMark/GFM remains overstated       |         |
| S04     | Extension canonicalization is not executable     |         |
| S05     | Inline canonicalization still has vague rules    |         |
| S07     | Inserted hierarchy separators break idempotence  |         |
| S08     | The concurrent-write safety guarantee has a race |         |


### Critical

#### C01: The finite dialect matrix is still incomplete


#### Where

Acceptance Criteria — AC02 and AC05, lines 32–73; AC13–AC15, lines 159–207; Technical Notes, lines 301–307


#### Issue

The package versions are pinned, but the accepted language is not. The plan does not pin the enabled `markdown-it-py`
options or plugins, the YAML schema/parser configuration, or the exact extension configuration. The Material table has
no
source-owner column and uses terms such as “documented,” “pinned configuration,” “registered catalog,” and “where the
pinned grammar permits them.” It does not enumerate the snippet directives, shortcode catalog, Arithmatex delimiters,
SuperFences annotation syntax, Zensical grammar, or enabled Python-Markdown/PyMdown/Material extensions.


#### Impact

An implementation planner cannot determine which source bytes are accepted, rejected, or canonicalized. A dependency
version alone does not freeze plugin options, catalogs, YAML scalar resolution, or extension grammar, so the dialect and
compatibility fixtures remain non-reproducible.


#### Suggestion

Replace the broad extension rows with a finite source matrix. Each row should name the source owner, exact package and
configuration, accepted syntax, AST fields, canonical bytes, nesting and precedence, and invalid and unknown cases.
Pin the YAML schema/configuration as well, or define its scalar grammar independently of the parser. Remove references
to
external documentation or runtime catalogs as the authority.


#### Outcome


### Significant

#### S01: Overlapping extension dispatch is unresolved


#### Where

Architecture — lines 257–277; AC13–AC14, lines 159–197


#### Issue

The formatter-owned authority and a broad dispatch order are now stated, but the source grammars are not disjoint. For
example, `??? kind "title"` matches both the admonition row and the closed-details row. Inline extension groups have no
ordering within the group, and the plan does not define how SuperFences metadata is distinguished from arbitrary fence
info. “At their declared ... precedence” refers to declarations that the matrix does not provide.


#### Impact

The same bytes can still produce different node kinds, metadata, and spans. A malformed extension can be claimed by a
different adapter or fall through to prose, defeating the fail-closed and adapter-disagreement contracts.


#### Suggestion

Add one authoritative precedence table with disjoint claim predicates and tie-breakers. Resolve the admonition/details
overlap explicitly, define the fence-metadata boundary, and specify which adapter claims or rejects a partially matching
construct before ordinary parsing may run.


#### Outcome


#### S02: Complete CommonMark/GFM remains overstated


#### Where

Goal and AC04, lines 13–55; AC09–AC10, lines 106–126; AC14, lines 189–192


#### Issue

The plan still calls the baseline complete CommonMark/GFM while rejecting valid source for repository style reasons,
including headings with terminal punctuation, headings containing strong markup, and qualifying bold-subject list items.
Those are intentional source-language exclusions, but they are not listed as exclusions from the “complete” baseline.
The
task-list rule names `[ ]` and `[x]` but does not state acceptance of GFM's case-insensitive `[X]` form.


#### Impact

The fixture set cannot simultaneously prove complete GFM acceptance and the stated rejection behavior. Implementers may
either reject valid GFM unexpectedly or weaken the style contract, and task-state meaning can be lost for valid checked
markers.


#### Suggestion

Choose one contract: accept and canonicalize every valid CommonMark/GFM form, or rename the baseline as parser coverage
with an explicit list of formatter-policy exclusions and test those exclusions separately. If complete GFM is retained,
accept case-insensitive checked markers and canonicalize them to `[x]`.


#### Outcome


#### S04: Extension canonicalization is not executable


#### Where

AC08, lines 96–103; AC13–AC15, lines 159–207


#### Issue

The extension rows name intended outcomes but do not define enough source-to-source rules to produce canonical bytes.
“Canonical kind, title, and indentation,” “one term/definition layout,” “canonical delimiter spacing,” and “canonical
separators” leave multiple valid outputs. Reference definitions versus inlined references, unreferenced definitions,
footnote labels and backlinks, attribute placement, and directive or annotation definition placement are also
unresolved.


#### Impact

Equivalent extension inputs can serialize differently or lose relationships on a second parse. Idempotence and semantic
preservation cannot be tested from these contracts, even though theme and generated HTML correctly remain out of scope.


#### Suggestion

For every extension, specify the accepted source variants, AST metadata and relationship invariants, exact canonical
source
form and placement, and the behavior for unused or reordered definitions. Distinguish source meaning that is preserved
from renderer-generated behavior that is intentionally discarded.


#### Outcome


#### S05: Inline canonicalization still has vague rules


#### Where

AC08 and AC10–AC11, lines 96–144


#### Issue

“Only when needed,” “minimal canonical escape,” “when safe,” “canonical named entity,” and “angle-bracket escaping when
needed” do not define a deterministic lexical algorithm. “120 columns” and “rendered Markdown source width” do not state
whether Unicode display width, code points, tabs, escapes, or markup delimiters determine the count. These gaps remain
even
though the hard-break delimiter and overlong-token policy are now explicit.


#### Impact

Two conforming implementations can emit different escapes, link destinations, titles, or wrap points while claiming the
same semantics. Boundary cases will fail determinism and idempotence checks.


#### Suggestion

Define an escape and entity decision table, the canonical entity-name selection, destination and title escaping rules,
and
one measurable width metric with tab, Unicode, markup, and overlong-token behavior. Replace every “when needed” or
“safe”
condition with a predicate that fixtures can evaluate.


#### Outcome


#### S07: Inserted hierarchy separators break idempotence


#### Where

AC09, lines 106–113; AC19, lines 240–249; Architecture, lines 279–282


#### Issue

The renderer inserts `----` before a downward heading but canonicalizes source thematic breaks to `---`. In CommonMark,
`----` is a thematic break, and the AST has no distinct hierarchy-separator node or source marker. On the next pass the
inserted line is therefore parsed as a source thematic break and cannot be distinguished from an authored break.


#### Impact

The required second pass with identical bytes is not achievable for a document that needs an inserted separator. The
formatter will either change `----` to `---`, insert another separator, or change the meaning of an authored break.


#### Suggestion

Define a reparseable canonical rule for the separator, including how an existing break immediately before a downward
heading is classified, and make that rule agree with source-break rendering. Do not promise distinct `----` semantics
unless
the AST and second-pass classification can preserve them.


#### Outcome


#### S08: The concurrent-write safety guarantee has a race


#### Where

AC16–AC18, lines 211–237


#### Issue

The plan requires detecting a source change after preflight, but it does not define a commit-time synchronization or
compare-and-replace protocol. A file or path can change after the final identity/content check and before replacement,
including a regular-file-to-symlink or non-regular-file swap. “Read-only files” and destination-type handling also do
not
state whether the operation rejects them or merely relies on replacement failure.


#### Impact

The formatter can overwrite a concurrent edit or replace through a changed path while still claiming AC17. Atomic rename
protects readers from partial bytes, but it does not protect against lost updates or target substitution.


#### Suggestion

Specify the per-file commit protocol and its guarantee: validate through stable directory/file handles, reject type and
symlink changes, compare the snapshot immediately before replacement, and define the remaining race or a locking/CAS
mechanism. State explicit outcomes for read-only and non-regular destinations; weaken the AC if only best-effort
detection
is possible.


#### Outcome


## Notes

Iteration 02's resolved checklist remains intact where iteration 03 marked it resolved. The HTML boundary and code
whitespace contract are materially clearer. Approval still depends on turning the version and source matrix into an
authoritative finite dialect, then aligning dispatch, canonicalization, and idempotence with that dialect.
