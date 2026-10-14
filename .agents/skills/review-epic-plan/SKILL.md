---
name: review-epic-plan
description: Adversarially review an epic plan and record product-level findings.
---

# Review Epic Plan Skill

Review an `epic-plan.md` for product outcome, decomposition, MVP readiness, roadmap sequencing,
and cross-feature integrity. Record findings in a separate epic-review artifact.


## When to use

Use this skill to review an epic plan. Do not use `review-design-plan` or
`review-implementation-plan`, which assess feature-scoped artifacts.

This skill does not modify the epic plan, author child designs, or approve the plan on behalf of the human.


## Prerequisites

The prompt must include:

- Path to `epic-plan.md`
- Epic artifact directory
- Review iteration, starting at `01`
- Prior review path for a re-review

If required information is missing, ask before proceeding. Do not guess.


## Review process

1. Read `.agents/artifacts/epic-plan/description.md` and `.agents/artifacts/epic-review/description.md`.
2. Read the epic plan and any linked prior reviews. Do not edit the plan.
3. Check that the product outcome, scope, non-goals, success criteria, cross-cutting decisions,
   risks, dependencies, and closure criteria are clear without child artifacts.
4. Challenge whether T01 is the smallest useful MVP and whether each feature is independently deliverable with a clear
   outcome. Check feature boundaries, `FNN` identity consistency,
   slice membership, priorities, dependencies, and sequencing.
5. Check that `T01` and `T02+` records include their objectives, feature sets, prerequisites, states, verification,
   artifact links, and coordinator branch/worktree fields. Later slices
   must depend on accepted integrated prerequisite states.
6. Confirm deferred roadmap items remain concise briefs, unknowns are answerable, product-level
   architectural decisions are present, and implementation detail remains in feature artifacts.
7. For a re-review, resolve each prior finding as resolved, unresolved, or regressed with evidence. Report new findings
   with severity `Critical`, `Significant`, or `Minor`, location, evidence, impact, and a concrete resolution.
8. Choose `Approved` only when no unresolved material finding blocks the epic plan. Otherwise choose `Changes required`.
   An approved review unlocks the explicit human approval gate; it does not replace it.
9. Read `.agents/artifacts/epic-review/template.md.j2`, render it as `epic-review--NN.md` in the epic directory,
   and replace all template variables and sample findings with actual review content.
10. Run `dt format markdown` on the review and ensure no placeholder text remains.


## Artifact

Write `epic-review--NN.md` using a zero-padded sequence in the epic artifact directory. Supply its path and outcome to
the caller. Never imply that approval of the agent review is approval by the human.
