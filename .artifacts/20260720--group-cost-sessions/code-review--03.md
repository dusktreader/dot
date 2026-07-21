# Code review: Run PR and branch-worktree policy addendum

Review of the new `run-pr` skill and revised branch-worktree policies against the requested publication and
main-integration invariants.


## Source

- `.agents/agents/principal.md`
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

- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: 51 passed.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `uv run ty check`: failed with 63 existing diagnostics in optional local tooling, cost-report code, and existing
  tests.
- `uv run pytest tests/test_validate_staged_agent_policies.py`: 51 tests passed, but the command failed its project-wide
  70% coverage gate because the focused policy tests execute no `src/dot_tools` code.
- `git diff --check`: passed.


## Issue summary

- **Critical**: 1
- **Significant**: 1
- **Trivial**: 0


## Findings

### Summary

| Finding | Title | Outcome |
|---------|-------|---------|
| C01 | `review-pr` remains an additional publishing workflow | Resolved |
| S01 | Validator does not enforce rebase and approval before main integration | Resolved |


### Critical

#### C01: `review-pr` remains an additional publishing workflow


#### Where

`.agents/skills/review-pr/SKILL.md:76-84, 147-172`


#### Issue

The review skill directs agents to push the parent feature branch after a local squash and again during its final
reply step. This conflicts with the requested invariant that only `run-pr` publishes. It also conflicts with the
revised branch workflows, which direct a ready normal branch to `run-pr` rather than implementing publication.


#### Impact

An agent handling PR comments can publish a branch without executing `run-pr`'s clean-worktree, unsafe-branch,
remote, authentication, base, and rebase checks. The policy has two publishing paths, so the final-publishing
controls are bypassable.


#### Fix

Remove parent-branch pushes from `review-pr`. After its approved squash, direct the human to invoke `run-pr`, or
otherwise incorporate the complete `run-pr` preconditions through a single shared publishing workflow. Extend the
validator inventory and tests to reject any publishing command outside `run-pr`.


#### Outcome

Resolved. `review-pr` contains no `git push` command and directs the human to invoke standalone `run-pr` after its
local squash commit. The staged-policy validator and regression test reject a `git push` command in `review-pr`.

----

### Significant

#### S01: Validator does not enforce rebase and approval before main integration


#### Where

`tools/validate_staged_agent_policies.py:18-37`


#### Issue

The branch-policy validator requires the generic phrase `stop and explicitly ask first.` and `git merge --ff-only`,
but does not require an explicit human approval, a rebase onto current main, or their ordering. The parametrized
tests at `tests/test_validate_staged_agent_policies.py:55-73` likewise mutate only the generic stop phrase and the
fast-forward command.


#### Impact

A staged policy can remove its required rebase step or replace the approval language while retaining the two checked
fragments, then pass validation. That leaves the requested no-merge-to-main safety sequence unprotected.


#### Fix

Validate an ordered main-integration statement that requires an explicit human approval, rebase of the normal branch
onto current main, and `git merge --ff-only`. Add removal and reordering mutations for all five branch workflows.


#### Outcome

Resolved. Every branch workflow now contains one ordered integration contract: explicit human approval, rebase of the
normal branch onto current main, `git merge --ff-only`, and no squash directly to main. The validator requires the
complete ordered statement, and tests remove each step and reorder the sequence across all five workflows.

----

## Skills applied

- `review-code`: global fallback.


## Decision

**RESOLVED**

C01 and S01 are resolved. `review-pr` has no publication path, and branch workflows enforce the required ordered
main-integration sequence. `run-pr` remains the standalone publication and PR workflow.
