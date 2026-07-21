# Task journal: Share agent worktree skills

Execution record for the approved shared agent-worktree skills task.


## Source plan

`.artifacts/20260720--shared-worktree-skills/task-plan.md`


## Status

**Complete**: Implemented the shared worktree lifecycle skills, migrated all six workflows, and updated validation.


## Review follow-up

Resolved code review `C01`, `S01`, and `S02`. Cleanup now consumes the creation result: it removes and verifies the
agent worktree in every mode, verifies an audit branch only when creation returned one, and otherwise reports that no
temporary audit branch was created for a normal branch started from `main` or `master`. The policy validator now rejects
literal branch commands, worktree setup and removal, audit branch allocation, and suffix allocation in each migrated
workflow. Reformatted the six migrated workflow skills without changing their workflow requirements or shared-skill
references. They now begin with an H1 and pass the Markdown formatter.

Validation completed:

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov`: 71 passed.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `node ~/.agents/tools/check-markdown-format.mjs .agents/skills/run-feature/SKILL.md
   .agents/skills/run-task/SKILL.md .agents/skills/run-bug-fix/SKILL.md .agents/skills/run-fix/SKILL.md
   .agents/skills/run-hotfix/SKILL.md .agents/skills/review-pr/SKILL.md`: passed.
- `git diff --check`: passed.


## Tasks

### Task 01: Add shared lifecycle validation

#### Status

**Complete**


#### Overview

Updated staged-policy test fixtures and validator rules for the shared skills, required workflow references, contracts,
and prohibited inline worktree plumbing.


#### Files modified

- UPDATED: `tests/test_validate_staged_agent_policies.py`
- UPDATED: `tools/validate_staged_agent_policies.py`


#### Validation

`uv run pytest tests/test_validate_staged_agent_policies.py --no-cov` passed: 65 tests.


### Task 02: Create shared worktree skills

#### Status

**Complete**


#### Overview

Added central creation and successful-integration cleanup skill contracts.


#### Files modified

- CREATED: `.agents/skills/create-agent-worktree/SKILL.md`
- CREATED: `.agents/skills/cleanup-agent-worktree/SKILL.md`


#### Validation

The validator tests cover required inputs, collision suffix policy, exact path policy, cleanup verification, and audit
branch retention.


### Task 03: Migrate branch-based workflows

#### Status

**Complete**


#### Overview

Replaced inline branch allocation, worktree creation, and successful cleanup mechanics with shared skill invocations
while retaining workflow-specific gates, artifacts, QA, review, squash, and publication policies.


#### Files modified

- UPDATED: `.agents/skills/run-feature/SKILL.md`
- UPDATED: `.agents/skills/run-task/SKILL.md`
- UPDATED: `.agents/skills/run-bug-fix/SKILL.md`
- UPDATED: `.agents/skills/run-fix/SKILL.md`
- UPDATED: `.agents/skills/run-hotfix/SKILL.md`
- UPDATED: `.agents/skills/review-pr/SKILL.md`


#### Validation

The complete staged-policy fixture validates successfully. `uv run ruff check tools/validate_staged_agent_policies.py
tests/test_validate_staged_agent_policies.py` passed.


## QA notes

Code review `S02` is resolved. The six migrated workflow skills pass the required Markdown validator after removing
frontmatter that preceded the H1, correcting heading spacing and prose wrapping, and labeling text fences. No workflow
requirements or shared-skill references changed.
