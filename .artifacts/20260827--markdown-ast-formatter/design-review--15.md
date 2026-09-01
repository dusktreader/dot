# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 15 re-reviews the design plan against iteration 14, limited to prior findings and the requested ownership,
serialization, round-trip, policy, idempotence, and write-safety checks.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 4
- **Trivial**:     0

The structural heading and AC numbering defects are fixed. Raw HTML rejection, block-math attribute placement,
definition-list framing, idempotence intent, and write safety are also explicit. The plan still has gaps in complete
CommonMark underscore ownership, exact canonical bytes, fence delimiter safety, and executable policy predicates.


## Prior Review Resolution

- **C01** ✓: `Table serialization details` is `#####` content under AC07, and `Block profile` plus `Inline and fence
  profile`
  are `#####` content under AC12.
- **S01** ⚠: The explicit dispatch pair and pre/post phases remove the former lifecycle duplication, but exclusive
  ownership still drops valid CommonMark underscore delimiter runs.
- **S02** ⚠: Core escaping and delimiter intent are more detailed, but exact context-sensitive bytes and inline-math
  serialization remain unspecified.
- **S03** ⚠: Metadata splitting and annotation productions are substantially complete, but the fallback tilde fence
  rule does not state the required minimum fence length.
- **S04** ✓: Definition-list term, entry, continuation, termination, EOF, and canonical inverse rules are now explicit.
- **S05** ⚠: Source provenance and several terminal-character cases are named, but terminal and sentence predicates are
  still not fully executable.


## Findings

### Summary

| Finding | Title                                     | Outcome |
| ------- | ----------------------------------------- | ------- |
| S01     | Complete CommonMark underscore ownership  |         |
| S02     | Exact canonical bytes remain incomplete   |         |
| S03     | Fallback fence delimiter can be invalid   |         |
| S05     | Policy terminal predicates remain partial |         |


### Significant

#### S01: Complete CommonMark underscore ownership


#### Where

AC04 and AC12 ownership rules, the Betterem row, and inline dispatch, approximately lines 55-64, 321-324, 363-364,
and 409-412.


#### Issue

The plan makes Betterem and core emphasis disjoint by assigning `_` and `__` to Betterem and `*` and `**` to core.
Betterem accepts only identical, non-overlong simple spans. Valid CommonMark underscore delimiter runs outside that
subset, such as `___foo___` and mixed nested runs, therefore have no semantic owner. Treating those sources as ordinary
baseline text does not provide complete CommonMark parsing because the core underscore productions have been excluded.


#### Impact

The claimed complete CommonMark/GFM profile can silently lose valid emphasis and strong node structure. Canonical output
for those inputs can be semantically different even though the source is accepted, and the one-owner invariant is not
actually compatible with the stated baseline.


#### Suggestion

Assign all CommonMark underscore delimiter-run semantics to core, then make Betterem's additional behavior disjoint from
that grammar. Alternatively, make Betterem implement the full baseline underscore grammar before claiming exclusive
ownership. State longest-delimiter precedence for the remaining overlapping `^`/`^^` and `~`/`~~` productions as well.


#### Outcome


#### S02: Exact canonical bytes remain incomplete


#### Where

AC07-AC08 core inline serialization and the Math, Mark/caret/tilde, and Attributes rows, approximately lines 154-234,
361-364, and 377-412.


#### Issue

The plan still describes delimiter collision handling only as escaping a literal delimiter "when it would merge" with a
run. It does not define the collision predicate, escape count, or the context-sensitive output for a source-escaped
delimiter, a literal backslash, and nested or adjacent emphasis. Source escape provenance alone does not say how the
canonical serializer prevents a previously escaped `*` or `_` from becoming an active opener on reparse. Inline math
accepts both `$...$` and `\(...\)` but does not state its canonical delimiter and body production. These omissions leave
exact core and extension bytes open to independent interpretations.


#### Impact

Two conforming implementations can emit different bytes or canonical output that reparses into different inline nodes.
That directly defeats the exact-byte and idempotence guarantees for escaped, nested, adjacent, and math-containing
content.


#### Suggestion

Define a context-sensitive canonical production for every core and extension inline node. Specify the delimiter-run
collision algorithm, literal-backslash and source-escape emission rules, and the exact inline-math spelling. Include
canonical-byte examples with nested and adjacent delimiters, escaped punctuation, entities, and both math delimiters.


#### Outcome


#### S03: Fallback fence delimiter can be invalid


#### Where

AC11 fence delimiter selection, approximately lines 306-309.


#### Issue

The backtick fallback explicitly has a minimum length of three, but the tilde fallback is described only as longer than
the longest payload tilde run. When backticks are unavailable because the normalized info contains a backtick and the
payload contains no tilde run, that rule permits a one- or two-tilde delimiter. Such a delimiter is not a valid fenced
code opener.


#### Impact

Fences with valid metadata or annotation relationships can serialize to source that does not reparse as a fence. The
metadata and annotation round-trip guarantee then fails for a valid edge case.


#### Suggestion

Specify the fallback as a tilde fence of length `max(3, longest payload tilde run + 1)`, and state that delimiter
selection occurs after marker restoration and normalized info construction.


#### Outcome


#### S05: Policy terminal predicates remain partial


#### Where

AC09-AC10 heading and bold-subject policies, approximately lines 255-282.


#### Issue

The plan names a normalized inline AST and source escape provenance, but it still delegates the decision to a "final
semantic rendered character" and says there is "no second sentence" without defining those operations. It does not give
terminal behavior for empty or boundary-only nodes, recursive emphasis, inline code, autolinks, images with empty
alt-text, or soft and hard breaks in the policy representation. The same omission leaves the bold-subject sentence count
and the placement of its terminator non-executable.


#### Impact

Fixtures can disagree about whether escaped or entity-derived punctuation terminates a heading or item sentence, and
whether an item with nested or empty inline nodes satisfies the bold-subject policy. Implementations can accept
different
documents while claiming the same policy exclusions.


#### Suggestion

Define a total terminal-character function over every inline node kind, including an explicit empty result and recursive
boundary behavior. Define sentence terminators as a finite scan over that representation, including the exact handling
of
source escapes, entity decoding, links, images, code, math, extension atoms, and soft or hard breaks.


#### Outcome


## Notes

The three supporting headings are actually `#####` and are structurally owned by AC07 or AC12. AC01 through AC17 are
contiguous. The plan contains one explicit block-dispatch lifecycle and one explicit inline-dispatch lifecycle; the
reference prepass and block-attribute post-phase are named separately rather than duplicated as dispatches.

Raw HTML classification and rejection, block-math attributes on the following same-prefix line, the definition-list
inverse grammar, positional `----` handling, normalized-fence idempotence intent, and optimistic write safety remain
consistent with the requested contract. No tests, builds, or linters were run.
