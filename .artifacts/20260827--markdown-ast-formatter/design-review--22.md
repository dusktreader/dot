# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 22**

This final review rechecks the prior delimiter and math finding plus the requested regression surface only.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

The math, table, label, metadata, nesting, dispatch, HTML, idempotence, and write contracts are specified. The
delimiter contract still has one profile-ownership and fallback ambiguity, so the plan is not approved.


## Prior Review Resolution

- **S02** ⚠: Inline and block math now have inverse left-to-right codecs, and delimiter spelling is excluded from
  normalized-AST equality. Table pipe and label escaping, opening/closing/sibling parity, and profile-span coverage
  are substantially specified. The delimiter collision predicate and the ownership and fallback behavior for `~~`
  profile spans remain inconsistent.


## Findings

### Summary

| Finding ID | Title                                                | Outcome |
| ---------- | ---------------------------------------------------- | ------- |
| S02        | Profile delimiter ownership and fallback remain open |         |


### Significant

#### S02: Profile delimiter ownership and fallback remain open


#### Where

AC07-AC08 and AC12, approximately lines 175-195, 248-255, 288-304, 419-431, and 468-484.


#### Issue

The plan defines the boundary location, delimiter runs, backslash encoding formula, and application at opening,
closing, and sibling boundaries. It does not make the complete delimiter codec executable for all profile spans:

- A collision may depend on a "legal opener or closer shape for a different node," but the per-delimiter left/right
  flanking and punctuation predicates are not enumerated.
- `~~` is named as a profile span in AC07 and AC08, while core strike also owns `~~`, the profile matrix lists only
  `~body~`, and the dispatch order places profile spans before core strike. The plan does not assign this spelling one
  owner or state the resulting precedence unambiguously.
- Core emphasis has alternate candidates and a literal fallback, but profile spans have no explicit alternate or
  semantics-preserving rule when protection cannot remove a syntax-delimiter collision.


#### Impact

Independent implementations can assign `~~x~~` to different nodes or serialize nested delimiter boundaries
differently. A fallback that emits a semantic child delimiter as literal text would change the normalized AST, breaking
the required reparse and idempotence guarantees.


#### Suggestion

Add a finite per-delimiter table covering exact opener, closer, flanking, punctuation, run, and backslash predicates.
Assign `~~` exactly one source owner and state its precedence relative to `~` in the dispatch and matrix. For every
profile delimiter, define a fixed alternate or reject a complete span whose child structure has no
semantics-preserving canonical encoding; do not silently encode semantic syntax as literal content.


#### Outcome


## Notes

The requested structural checks pass: AC01-AC17 remain present and ordered; nested blocks, heading policy, profile
precedence, one block and one inline dispatch pair, reference prepass, block-attribute post-phase, raw HTML rejection,
reparse/idempotence, and optimistic multi-file writes remain covered. No tests, builds, or linters were run.
