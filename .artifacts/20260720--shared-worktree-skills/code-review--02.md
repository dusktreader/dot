# Code review: Shared worktree skills

Re-review of the shared worktree lifecycle fixes for C01, S01, and S02 from iteration 01.


## Source

- `.agents/skills/create-agent-worktree/SKILL.md`
- `.agents/skills/cleanup-agent-worktree/SKILL.md`
- `.agents/skills/run-{feature,task,bug-fix,fix,hotfix}/SKILL.md`
- `.agents/skills/review-pr/SKILL.md`
- `tools/validate_staged_agent_policies.py`
- `tests/test_validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov`: 71 passed.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 71 passed, but the command fails its configured
  coverage gate because no production-module coverage is collected (0.00% < 70%).
- `~/.agents/tools/markdown-format.py check ...`: failed. The migrated workflow skills still violate the
  required Markdown format, including H1/frontmatter, heading-spacing, line-length, and unlabeled-fence errors.
- `git diff --check`: passed.


## Issue summary

- Critical: 0
- Significant: 1
- Trivial: 0


## Prior review resolution

- **C01** ✓: `cleanup-agent-worktree` explicitly handles normal branches created from `main` or `master` by reporting
  that no temporary audit branch exists. It only verifies retention when the creation result identifies an audit branch
  (`.agents/skills/cleanup-agent-worktree/SKILL.md:14-17`). All callers pass the creation result after successful
  squash.
- **S01** ✓: The validator rejects inline branch creation, worktree add/remove commands, workflow-specific audit
  suffixes, and allocation/suffix wording (`tools/validate_staged_agent_policies.py:151-156, 380-384`). Parameterized
  fixture mutations cover each of the six workflow documents independently
  (`tests/test_validate_staged_agent_policies.py:79-94`).
- **S02** ✗: The required Markdown formatter still fails for the migrated workflow skills. This remains a Significant
  finding below.


## Findings

### Summary

| Finding | Title                                    | Outcome |
| ------- | ---------------------------------------- | ------- |
| S02     | Required Markdown validation still fails |         |


### Significant

#### S02: Required Markdown validation still fails

**Where:**

`.agents/skills/run-feature/SKILL.md:1`, `.agents/skills/run-task/SKILL.md:1`,
`.agents/skills/run-bug-fix/SKILL.md:1`, `.agents/skills/run-fix/SKILL.md:1`,
`.agents/skills/run-hotfix/SKILL.md:1`, `.agents/skills/review-pr/SKILL.md:1`


**Issue:**

The task plan requires the Markdown formatter to pass for both shared skills and all six migrated workflows. The
command still reports errors in every migrated workflow skill, including frontmatter before the H1, heading spacing,
prose exceeding 120 characters, and fenced blocks with no language.


**Impact:**

The documented quality gate and AC07's complete validation requirement are not met. The shared skills format cleanly,
but the required command covers the migrated workflow files as well, so the change cannot claim full verification.


**Fix:**

Make the six workflow skill documents compatible with `markdown-format.py`, or update the formatter contract
with an approved, tested exception for skill frontmatter. Re-run the exact task-plan command until it exits zero.


**Outcome:**

Open.

----

## Skills applied

- `review-code`: global fallback
- `write-docs`: global fallback for this review artifact


## Decision

**BLOCKED - CHANGES REQUIRED**

S02 must be resolved. C01 and S01 are fully resolved. Focused validator tests pass; the normal coverage invocation
remains blocked by the repository's unrelated production-coverage configuration.
