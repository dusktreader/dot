---
name: run-fix
description: Extends an existing implementation project with a scoped fix. Use when a human identifies a gap or missed requirement post-implementation. Never trigger automatically.
---

# Run Fix Skill

Extend an existing implementation project with a scoped fix plan. This skill is always triggered
by a human identifying a specific gap — never by an agent acting on its own initiative.

The fix lives in the same project directory as the original implementation. It adds new artifacts
without modifying the original design plan, implementation plan, or journal.


## When to use

Use this skill when, after a `run-implementation` project is complete, a human identifies a
missed requirement or incorrect behaviour that needs a targeted fix — through code review, UAT,
or manual testing feedback.

This is a standalone skill triggered directly by humans. It always operates within an existing
project directory created by `run-implementation`.

Do not use when:
- The gap is discovered during a PR review → use `review-pr` instead
- The bug is unrelated to an existing implementation project → use `run-bug-fix` or
  `run-hotfix` instead
- The change is a new feature rather than a fix → start a new `run-implementation` project
- No agent triggered this — this skill must never be triggered automatically


## Prerequisites

Your prompt must include:

- Path to the existing project directory (`.agents/work/{project}/`)
- A clear description of the gap or missed requirement to fix

If either is missing, ask before proceeding. Do not guess.


## When to use this skill

Use this skill when, after implementation is complete, a human identifies something that was
missed — through code review, UAT, or operational feedback. Examples:

- An AC was not met
- A key design constraint was not implemented correctly
- A behaviour is wrong in a way that requires targeted changes

Do NOT use this skill to:
- Add new features (start a new project with `run-implementation` instead)
- Make broad architectural changes (those require a new design plan)
- Fix things proactively — only when a human explicitly requests it


## Artifacts

All artifacts are written to the existing project directory alongside the original artifacts.

| Artifact                                        | Description                                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `implementation-plan--fix-{N}.md`               | Scoped fix plan (N = zero-padded 2 digits: 01, 02, ...)                                   |
| `implementation-review--fix-{N}--{M}.md`        | Fix plan review (N = fix number, M = zero-padded iteration: 01, 02, ...)                  |
| `implementation-journal--fix-{N}.md`            | Execution journal for the fix                                                             |
| `execution-review--fix-{N}--whole-plan--{M}.md` | Execution review (N = fix number, M = zero-padded iteration: 01, 02, ...)                 |

Use the next available N by checking what fix artifacts already exist in the project directory.


## Git workflow

This skill manages its own git commits throughout the workflow. The `--agents` branch should
already exist from the original `run-implementation` run. If it does not, create it from the
current branch following the same rules in `run-implementation`.

Extract the Jira ID from the parent branch name using the same rules as `run-implementation`.

### Commits after each approved stage

After the human approves each stage, commit and push:

```shell
git add -A
git commit -m "<message>"
git push origin {branch}--agents
```

Stage-specific commit types:
- **After fix plan approved**: `docs(<jira-id>): add fix-{N} plan for {project-name}`
- **After fix execution approved**: `fix(<jira-id>): apply fix-{N} for {project-name}`

### Final squash onto parent branch

After the human approves the fix execution and the CHANGELOG is updated, squash all new
`--agents` commits (those not already on the parent branch) onto the parent branch:

1. Propose a squash commit message to the human. **Wait for explicit approval.**
2. Once approved:
   ```shell
   git switch {parent-branch}
   git merge --squash {parent-branch}--agents
   git commit -m "<approved message>"
   ```
3. Do NOT delete the `--agents` branch.
4. Do NOT push the parent branch — that is the human's decision.


## Process

### 1. Plan

Read the existing `implementation-plan.md` and `design-plan.md` to understand the project context.

Dispatch an `engineer-planner` subagent to create `implementation-plan--fix-{N}.md`. The prompt
must include:
- The specific gap or missed requirement
- Path to the existing project directory
- Instruction to scope the plan narrowly — only what is needed to address the gap, nothing more
- Instruction to read `.agents/artifacts/implementation-plan/description.md` for section definitions,
  render `.agents/artifacts/implementation-plan/template.md.j2` to produce the initial file, and replace
  all dummy content with real content. The rendered file must contain no placeholder text when submitted.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the
fix plan path, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Apply significant and critical findings using judgment. If a finding is genuinely ambiguous —
  where the correct resolution depends on information only the human has — flag it inline and
  note what you need. Do not stop the workflow for findings you can resolve yourself.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `architect-reviewer` at M+1 if changes were substantial. Repeat until the
  agent reviewer approves.

**STOP — end your turn here.**
The fix plan is ready for human review. Present it to the human. Do not summarize the agent
findings — the human will read the plan directly. Wait for the human to ask questions, request
revisions, or give approval. Do not proceed until the human explicitly approves.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the fix plan to the human in this turn
- [ ] I have NOT dispatched an executor agent or started any execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit and push (see Git workflow — "After fix plan approved").


### 2. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the
fix plan path. The journal is `implementation-journal--fix-{N}.md`.

Then dispatch an `engineer-reviewer` subagent with the `review-implementation-execution` skill,
the fix journal path, scope `whole-plan`, and iteration `01`. The review artifact is
`execution-review--fix-{N}--whole-plan--01.md`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Dispatch an `engineer-executor` to fix significant and critical findings. Flag genuinely
  ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `engineer-reviewer` at M+1 if changes were substantial. Repeat until the
  agent reviewer approves.

If a `CHANGELOG.md` exists in the repo root, add an entry under `## Unreleased` summarising
what was fixed. Use the fix plan's Goal as the basis. Follow the existing entry style in the
file.

**STOP — end your turn here.**
The execution is ready for human review. Present the execution review to the human. Wait for the
human to ask questions, request revisions, or give approval. Do not proceed until the human
explicitly approves.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the execution review to the human in this turn
- [ ] I have NOT started the squash or any post-execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit and push (see Git workflow — "After fix execution approved"), then perform
the final squash onto the parent branch.


### 3. Report

Report completion with the paths to all new artifacts, a summary of what was changed, and the
squash commit SHA on the parent branch.
