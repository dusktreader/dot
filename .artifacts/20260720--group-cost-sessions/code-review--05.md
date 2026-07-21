# Code review: Agent task worktree branch and PR policy extension

Re-review after `code-review--04.md` and C01 remediation. This review verifies temporary branch exclusion,
workflow naming, review publication boundaries, and local main-integration ordering.


## Source

- `.agents/artifacts/pr-review/description.md`
- `.agents/skills/review-pr/SKILL.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/run-pr/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `tests/test_validate_staged_agent_policies.py`
- `tools/validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: passed, 80 tests.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `uv run python tools/validate_staged_agent_policies.py --help`: passed.
- `git diff --check`: passed.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 80 tests passed, but the command failed the
  project-wide 70% coverage gate because focused policy tests execute no `src/dot_tools` code.
- `uv run ty check`: failed with 63 existing diagnostics in optional local tooling, cost-report code, and tests.


## Issue summary

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior review resolution

- **C01** ✓: `run-pr` rejects a branch containing the reserved `--agents` token when it is followed by a hyphen or
  the branch-name end. This covers both `{parent-branch}--agents` and all
  `{parent-branch}--agents-{workflow}` temporary forms, including `--agents-review-{N}`.


## Findings

### Summary

No findings.


## Skills applied

- `review-code`: global fallback.


## Decision

**APPROVED**

`run-pr` rejects all reserved temporary `--agents-*` names. Every workflow temporary branch uses the same
`{parent-branch}--agents-{workflow}` convention. `review-pr` contains no `git push` command and delegates
publication to `run-pr`. The five branch workflows preserve explicit approval, rebase onto current main, and then
`git merge --ff-only` in that order. Focused tests and lint pass; the coverage-gated focused invocation and project
type checker remain blocked by unrelated project-wide conditions.
