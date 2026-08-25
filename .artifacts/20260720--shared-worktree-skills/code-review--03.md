# Code review: Shared worktree skills

Final re-review of the shared-worktree lifecycle migration after the iteration 02 fixes.


## Source

- `.agents/skills/create-agent-worktree/SKILL.md`
- `.agents/skills/cleanup-agent-worktree/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/review-pr/SKILL.md`
- `tools/validate_staged_agent_policies.py`
- `tests/test_validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov`: 71 passed.
- `~/.agents/tools/markdown-format.py check .agents/skills/run-feature/SKILL.md
  .agents/skills/run-task/SKILL.md .agents/skills/run-bug-fix/SKILL.md .agents/skills/run-fix/SKILL.md
  .agents/skills/run-hotfix/SKILL.md .agents/skills/review-pr/SKILL.md`: passed for all six files.
- `git diff --check`: passed.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 71 tests passed, but the repository coverage gate fails
  because this tooling-only test module collects no coverage for the configured `src/dot_tools` target (0.00% < 70%).


## Issue summary

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior review resolution

- **C01** ✓: `cleanup-agent-worktree` distinguishes normal branches created directly from `main` or `master` from audit
  branches, verifies audit-branch retention only when one was created, and all six callers pass the creation result.
- **S01** ✓: The validator and parameterized tests require both shared-skill references. They reject workflow-local
  branch, worktree, audit-branch, and suffix-allocation plumbing for every migrated workflow.
- **S02** ✓: The required formatter passes for `run-feature`, `run-task`, `run-bug-fix`, `run-fix`, `run-hotfix`, and
  `review-pr`.


## Findings

### Summary

No findings.


## Skills applied

- `review-code`: global fallback
- `write-docs`: global fallback


## Decision

**APPROVED**

All requested quality gates pass. The coverage-enabled focused test command remains unavailable because its configured
production coverage target is unrelated to the policy validator tests.
