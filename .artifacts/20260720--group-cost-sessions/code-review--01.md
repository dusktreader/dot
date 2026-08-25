# Code review: Group OpenCode cost sessions

Review of the task-plan implementation, including session-table grouping, flat serializers, workflow setup policies,
and staged-policy validation.


## Source

- `.artifacts/20260720--group-cost-sessions/task-plan.md`
- `.artifacts/20260720--group-cost-sessions/implementation-journal.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `src/dot_tools/opencode_costs.py`
- `tests/test_cli_opencode_costs.py`
- `tests/test_opencode_costs.py`
- `tests/test_validate_staged_agent_policies.py`
- `tools/validate_staged_agent_policies.py`


## Verification evidence

- `uv run pytest --no-cov tests/test_opencode_costs.py tests/test_cli_opencode_costs.py`: 31 passed.
- `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py`: 53 passed.
- `uv run pytest`: 254 passed, with 2 existing `pytest-mock` warnings.
- `uv run ruff check src tests`: passed.
- `uv run ty check`: 58 pre-existing unrelated diagnostics, matching the journal's documented optional-local-import
  and existing-test issues. No diagnostic is in changed production hierarchy code.
- Markdown validation: the task plan passes. The edited policy files retain documented pre-existing format violations.


## Acceptance criteria

- AC01: satisfied. `table_rows` renders parent-first depth-first labels with ASCII prefixes at
  `src/dot_tools/opencode_costs.py:509`; focused and CLI tests cover child and deeper descendant output.
- AC02: satisfied. Only roots are passed through `sort_report_rows` at
  `src/dot_tools/opencode_costs.py:540`; descendants retain linked-list order.
- AC03: satisfied. JSON and CSV continue iterating flat `self.rows` at `src/dot_tools/opencode_costs.py:220` and
  `src/dot_tools/opencode_costs.py:258`; serializer assertions cover raw IDs and order.
- AC04: satisfied. Missing or unresolved parents become independent roots at
  `src/dot_tools/opencode_costs.py:519`; focused coverage retains a missing-parent row.
- AC05: satisfied. All five policies specify branch creation, immediate mirrored worktree creation, and no human
  worktree switch; parametrized validator coverage covers every policy.
- AC06: satisfied in the policy text. Each setup names its direct approval gate.
- AC07: not satisfied. The validator does not reject an added stop before the named approval gate.


## Issue summary

- Critical: 1
- Significant: 0
- Trivial: 0


## Findings

### Summary

| Finding | Title                                     | Outcome |
| ------- | ----------------------------------------- | ------- |
| C01     | Validator does not reject a pre-gate stop |         |


### Critical

#### C01: Validator does not reject a pre-gate stop

**Where:** `tools/validate_staged_agent_policies.py:263`



**Issue:**

The validator extracts setup text through `without another stop.` and checks that the required direct-progression
sentence exists, but it never detects another stop instruction before that sentence. A staged `run-task` fixture with
`STOP for human approval.` inserted immediately before `Proceed directly from setup...` returns no setup failures.
The test at `tests/test_validate_staged_agent_policies.py:186` only removes part of the required sentence; it does not
exercise the required injected pre-gate stop mutation.


**Impact:**

AC07 requires rejection of every pre-gate stop. A policy can introduce an extra human gate while retaining the required
sentence and still pass validation, defeating the workflow constraint.


**Fix:**

Add an explicit pre-gate stop detector scoped to the extracted setup contract and a parametrized mutation test for all
five workflows that injects a stop before the approval-gate sentence.


**Outcome:**

----

## Skills applied

- `review-implementation-execution`: global fallback.


## Decision

**BLOCKED — CHANGES REQUIRED**

C01 must be resolved before approval. All functional cost-report tests, the full test suite, and Ruff pass; `ty`
remains blocked only by the documented pre-existing unrelated diagnostics.
