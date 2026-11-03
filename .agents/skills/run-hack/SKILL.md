# Run Hack Skill

Make a low-risk change directly on the current worktree with the smallest useful record and verification. Do not create
a worktree or run a Git lifecycle.


## When to use

Use this workflow for a bounded, reversible change where the current branch is the intended destination, including
`main`. Do not use it when objective evidence requires a fuller workflow.


## Scope and escalation

Resolve bounded ambiguity using judgment when the change remains low-risk, reversible, and within scope. Escalate only
when ambiguity prevents coherent execution or an objective escalation signal applies.

Escalate to `run-task` when the change adds or changes a public interface, data schema or migration, security boundary,
externally observable behavior, or a new code path with meaningful failure modes, or when the scope is no longer
bounded. A technical category alone is not an escalation signal when the change is demonstrably unchanged, isolated, and
reversible.


## Prerequisites

The prompt must describe a bounded change and its expected outcome. If either is unclear, ask before proceeding.


## Workflow phases

### Setup

Stay in the selected current worktree and branch. Invoke `.agents/procedures/use-artifact-dir.md` with
`branch_type=chore`, the task summary, and ticket if provided. Set `hack_journal_path` to the next unused
`hack-journal--{task-slug}--NN.md` in the returned directory, where `task-slug` is a short lowercase kebab-case task
summary and `NN` is a zero-padded sequence starting at `01`.


### Hack lifecycle

1. The principal selects the active profile and tier, dispatches the shared `engineer-executor` role with
   `hack_journal_path`, and records the profile and tier.
2. The selected variant makes the focused change and records the files and intent in `hack_journal_path`.
3. The principal selects the active review profile and tier, dispatches the shared `engineer-reviewer` role, and
   performs a concise diff-first review. Resolve findings and repeat review after changes.


### QA

After implementation and review are complete, run the project-documented tests and quality checks relevant to the
change. Record exact commands and results in `hack_journal_path`. Resolve failures and rerun affected checks before
completion. If no automated check applies, record why and perform a suitable manual check.


### Human review

Present a concise diff summary and the QA commands and results. Ask the human to accept the change or request revisions.
Questions and silence are not acceptance. If revisions are requested, implement them in **Hack lifecycle**, repeat
review and QA, and return to this gate.


### Completion

After explicit human acceptance, report the `hack_journal_path`, change summary, and verification results. Leave the
current branch intact. Never create or switch branches or worktrees, commit or squash, push, or create a pull request.
