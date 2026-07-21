# Code review: Shared worktree skills

Review of the shared worktree lifecycle implementation against its task plan.


## Source

- `.agents/skills/create-agent-worktree/SKILL.md`
- `.agents/skills/cleanup-agent-worktree/SKILL.md`
- `.agents/skills/run-{feature,task,bug-fix,fix,hotfix}/SKILL.md`
- `.agents/skills/review-pr/SKILL.md`
- `tools/validate_staged_agent_policies.py`
- `tests/test_validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov`: 65 passed.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 65 passed, command failed coverage gate (0.00% < 70%).
- `node ~/.agents/tools/check-markdown-format.mjs ...`: failed. New shared skills fail H1/frontmatter and
  heading-spacing rules.
- `git diff --check`: passed.


## Issue summary

- Critical: 1
- Significant: 2
- Trivial: 0


## Findings

### Summary

| Finding | Title | Outcome |
|---------|-------|---------|
| C01 | Normal-branch cleanup has no audit branch | |
| S01 | Validator does not reject all duplicate plumbing | |
| S02 | Required Markdown validation fails | |


### C01: Normal-branch cleanup has no audit branch

**Where:** `.agents/skills/create-agent-worktree/SKILL.md:23-24`,
`.agents/skills/cleanup-agent-worktree/SKILL.md:13-20`

Creation explicitly produces no audit branch when the parent is `main` or `master`, but cleanup requires a resolved
audit branch and requires proving that it remains. All six workflows invoke cleanup in this mode. The successful-
integration cleanup path therefore cannot run for a normal branch created from `main` or `master`, violating AC02 and
AC04. Define the no-audit cleanup contract explicitly: accept the normal branch as the retained branch, or make audit
retention conditional while still validating the retained normal branch. Update callers and validator tests.


### S01: Validator does not reject all duplicate plumbing

**Where:** `tools/validate_staged_agent_policies.py:149, 359-375`,
`tests/test_validate_staged_agent_policies.py:79-83`

The duplicate regex only detects `git branch {` and `git worktree add/remove`. It misses literal branch commands,
branch suffix allocation, and other inline creation forms. The sole duplicate test adds `git worktree add` to one
workflow. Workflows can therefore reintroduce branch-allocation plumbing while the complete fixture and focused tests
still pass, leaving AC05 and AC07 incompletely enforced. Reject all workflow `git branch` creation commands and
branch-allocation/suffix patterns, while retaining explicitly allowed integration commands. Add independent mutations
for each workflow and cleanup removal.


### S02: Required Markdown validation fails

**Where:** `.agents/skills/create-agent-worktree/SKILL.md:1-6`,
`.agents/skills/cleanup-agent-worktree/SKILL.md:1-6`

The plan requires the Markdown validator to pass, but it reports errors for both new shared skills, in addition to
existing workflow errors. The documented quality gate is not met. Make the validator-compatible frontmatter and
heading layout explicit, or update the validated format and validator contract together before claiming this gate
passes.


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 must be resolved. S01 and S02 should be resolved in the same pass.
