# Code review: Branch and PR policy fixes

This re-review confirms that the fixes for S01 and S02 retain the detailed workflow content while enforcing the
branch-setup and main-integration ordering contracts.


## Source

- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `tools/validate_staged_agent_policies.py`
- `tests/test_validate_staged_agent_policies.py`
- `.artifacts/20260720--group-cost-sessions/code-review--06.md`


## Verification evidence

- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: passed, 47 tests.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `git diff --check`: passed.
- Build: skipped, policy-only documentation and validator review.
- Coverage: skipped, no coverage command was provided for the validator suite.


## Issue summary

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior review resolution

- **S01** ✓ Fully resolved: all five workflows retain their detailed stages and gates while each setup creates the
  selected branch with `git branch`, then immediately creates its exact mirrored agent worktree. See
  `run-feature/SKILL.md:152`, `run-task/SKILL.md:121`, `run-bug-fix/SKILL.md:101`, `run-fix/SKILL.md:114`, and
  `run-hotfix/SKILL.md:105`.
- **S02** ✓ Fully resolved: the validator requires the ordered branch-to-worktree setup, rejects setup stops before
  the defined gate, and requires approval, rebase, then fast-forward integration ordering. Parametrized tests cover
  each control across all five workflows. See `validate_staged_agent_policies.py:351` and
  `test_validate_staged_agent_policies.py:233`.


## Findings

### Summary

No findings.


## Skills applied

- `review-code`: global fallback.
- `write-docs`: global fallback.


## Decision

**APPROVED**

S01 and S02 are fully resolved. The detailed workflow content remains present, and all targeted quality gates pass.
