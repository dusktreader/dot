# Code review: Restored branch and PR policy changes

This re-review assesses the restored workflow policies, their staged-policy validator, and the hierarchy cost changes.


## Source

- `.agents/agents/principal.md`
- `.agents/artifacts/pr-review/description.md`
- `.agents/skills/review-pr/SKILL.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/run-pr/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `src/dot_tools/opencode_costs.py`
- `tests/test_cli_opencode_costs.py`
- `tests/test_opencode_costs.py`
- `tests/test_validate_staged_agent_policies.py`
- `tools/validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: passed, 32 tests.
- `uv run pytest --no-cov tests/test_opencode_costs.py tests/test_cli_opencode_costs.py`: passed, 33 tests.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py
  src/dot_tools/opencode_costs.py tests/test_opencode_costs.py tests/test_cli_opencode_costs.py`: passed.
- `git diff --check`: passed.
- The documented single-color ANSI test passes. The terminal renderer applies expected styles and file output remains
  ANSI-free. It is not a policy-review finding.


## Issue summary

- **Critical**: 0
- **Significant**: 2
- **Trivial**: 0


## Prior review resolution

`code-review--05.md` approved the pre-restoration state. The restored detailed workflows supersede that content, so its
approval cannot establish that the current setup and validation contracts remain enforced.


## Findings

### Summary

| Finding | Title                                                        | Outcome  |
| ------- | ------------------------------------------------------------ | -------- |
| S01     | Workflow setup does not consistently implement branch modes  | Resolved |
| S02     | Validator replaces required policy checks with weaker checks | Resolved |


### Significant

#### S01: Workflow setup does not consistently implement branch modes

**Where:**

`.agents/skills/run-feature/SKILL.md:90`, `.agents/skills/run-task/SKILL.md:137`,
`.agents/skills/run-bug-fix/SKILL.md:104`, `.agents/skills/run-fix/SKILL.md:98`, and
`.agents/skills/run-hotfix/SKILL.md:106`


**Issue:**

The shared contract says all five workflows create a normal branch from `main` or `master` with `git branch`, then add
an agent worktree at the exact mirrored path. It also says an existing normal branch uses a local audit branch. The
detailed setup instructions do not implement that contract consistently: `run-task`, `run-bug-fix`, and `run-hotfix`
create the temporary branch with `git worktree add -b`; `run-feature` uses it for the temporary mode; and `run-fix`
has no setup step for either mode and instead assumes a prior `--agents` branch.


**Impact:**

An agent following the actionable setup sections can create branches through a different command and sequencing than
the required policy, or cannot establish a required worktree at all. The promised two-mode, branch-then-worktree
safety contract is therefore not reliable across the five workflows.


**Fix:**

Give every workflow an explicit setup procedure for both modes. In each procedure, create the selected branch with
`git branch`, immediately add `<repo-root>/.worktrees/<agent-branch>` with `git worktree add`, and keep `git switch`
prohibited in the human worktree. Preserve the existing workflow-specific gates around that shared setup.


**Outcome:**

Resolved. Each workflow now records the parent state, uses `git branch` for normal and temporary modes, then immediately
uses `git worktree add <repo-root>/.worktrees/<agent-branch> {agent-branch}`. Temporary names follow
`{parent-branch}--agents-{workflow}`, `git switch` remains prohibited in the human worktree, and each setup proceeds
directly to its defined approval gate.

----

### Significant

#### S02: Validator replaces required policy checks with weaker checks

**Where:**

`tools/validate_staged_agent_policies.py:128-141` and
`tests/test_validate_staged_agent_policies.py:202-244`


**Issue:**

The restoration replaces targeted branch-policy and ordered main-integration checks with independent substring checks in
`_BRANCH_CONTRACT`. The validator no longer requires the branch-then-immediate-worktree sequence, exact path mirroring
language, or direct progression to the approval gate. It also accepts the main-integration phrases in any order. The
replacement tests only remove `git merge --ff-only`, append `git switch` outside setup, and cover one publication
workflow, so they do not detect these regressions.


**Impact:**

Policies that violate the required worktree setup, add a pre-gate stop, or re-order approval, rebase, and
fast-forward integration can validate successfully. This weakens the validator instead of extending it and permits
drift from the documented safety contract.


**Fix:**

Retain the existing targeted controls and add the restored-policy checks alongside them. Test each of the five
workflow fixtures independently for both branch modes, exact mirrored path, `git branch` followed immediately by
`git worktree add`, setup-scoped `git switch` rejection, no pre-gate stop, no publication mechanics, and the ordered
approval, rebase, then fast-forward integration contract.


**Outcome:**

Resolved. The validator retains the existing branch-contract checks and adds ordered setup, direct-progression,
pre-gate-stop, and approval-rebase-fast-forward controls. Parametrized regressions cover all five workflows.

----

## Skills applied

- `review-code`: global fallback.
- `write-docs`: global fallback for the review artifact.


## Decision

**APPROVED**

S01 and S02 are resolved. `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py` reports `47 passed`;
Ruff and `git diff --check` pass.
