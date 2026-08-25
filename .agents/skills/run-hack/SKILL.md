---
name: run-hack
description: Makes a low-risk current-branch change with a hack journal and focused verification.
---

# Run Hack Skill

Make a low-risk change directly on the current branch with the smallest useful record and verification. This workflow
uses
no agent worktree and no Git lifecycle. It uses no worktree and does not create one.


## When to use

Use this workflow for a bounded, reversible change where the current branch is the intended destination. It operates on
the current branch, including `main`.

Do not use it when objective evidence requires a fuller workflow.


## Artifacts

Create only one artifact: `.artifacts/{YYYYMMDD}--{project-name}/hack-journal.md`.


## Prohibitions

This workflow never creates or switches branches, never creates a worktree, never commits or squashes, never pushes, and
never creates a PR. It
has no plan, reviewer, or human gate by default.


## Process

1. The principal selects the executor model using the principal's Model selection policy, chooses and dispatches the
   exact `engineer-executor--{work|personal}-{suffix}` variant, and records the exact variant agent name.
2. The selected variant makes the focused change and records the files, intent, and relevant verification in
   `hack-journal.md`.
3. Run relevant verification for the changed behavior.
4. The principal selects a review model using the Model selection policy, chooses and dispatches the exact
   `engineer-reviewer--{work|personal}-{suffix}` variant, and performs a concise diff-first review.

Ambiguity is discretionary. It does not cause escalation unless it blocks coherent work. Resolve bounded ambiguity
using judgment when the change remains low-risk, reversible, and within scope; escalate only when the ambiguity
prevents coherent execution or an objective escalation signal applies.

Escalate to `run-task` only on objective signals: the change adds or changes a public interface, data schema or
migration, security boundary, externally observable behavior, a new code path with meaningful failure modes, or the
scope is no longer bounded. A technical category alone is not an escalation signal when the change is demonstrably
unchanged, isolated, and reversible. Do not escalate merely because a language, framework, or subsystem is technical.
