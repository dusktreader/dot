# Code review: Agent task worktree branch and PR policy extension

Re-review of the policy extension after `code-review--03.md`, focused on publication ownership,
main-integration ordering, and normal versus temporary agent-branch behavior.


## Source

- `.agents/agents/principal.md`
- `.agents/skills/review-pr/SKILL.md`
- `.agents/skills/run-pr/SKILL.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `tests/test_validate_staged_agent_policies.py`
- `tools/validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: passed, 72 tests.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `git diff --check`: passed.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 72 tests passed, but the command failed the
  project-wide 70% coverage gate because focused policy tests execute no `src/dot_tools` code.
- `uv run ty check`: failed with 63 existing diagnostics in optional local tooling, cost-report code, and tests.


## Issue summary

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior review resolution

- **C01** ✓: `review-pr` no longer contains a `git push` command and directs publication through `run-pr`.
- **S01** ✓: Every branch workflow contains the ordered contract: explicit approval, rebase onto current main,
  then `git merge --ff-only`. The validator and mutation tests enforce it.


## Findings

### Summary

| Finding | Title                                                       | Outcome |
| ------- | ----------------------------------------------------------- | ------- |
| C01     | `run-pr` can publish the temporary `review-pr` audit branch | Open    |


### Critical

#### C01: `run-pr` can publish the temporary `review-pr` audit branch

**Where**

`.agents/skills/review-pr/SKILL.md:66`, `.agents/skills/run-pr/SKILL.md:8`,
`tools/validate_staged_agent_policies.py:40`, `tests/test_validate_staged_agent_policies.py:79`


**Issue**

`review-pr` creates a local-only audit branch named `{parent-branch}--agents-review-{N}`. `run-pr` rejects only
branches ending in `--agents`, so an explicit `run-pr` invocation on that temporary branch passes its branch-name
precondition and can push it and create a pull request. The validator and its tests preserve the same incomplete
suffix rule.


**Impact**

The policy's claim that only `run-pr` publishes remains technically true, but `run-pr` can publish an audit branch
that `review-pr` declares local-only. This breaks the required normal versus `--agents` branch separation and allows
a PR from review commits rather than the intended squash on the normal parent branch.


**Fix**

Make `run-pr` reject any temporary agent branch, including names containing `--agents` such as
`--agents-review-{N}`, and add validator mutations that prove both the policy and rejection coverage. Alternatively,
rename the review branch to the exact reserved `--agents` suffix, but retain a test preventing publication of all
temporary agent branch forms.


**Outcome**

Open.

----

## Skills applied

- `review-code`: global fallback.


## Decision

**BLOCKED - CHANGES REQUIRED**

C01 must be resolved before approval. Focused policy tests and lint pass; the focused coverage command and the
project type checker remain blocked by unrelated project-wide gates and existing diagnostics.
