# Execution Review: Agent workflow staging — worktree/model-dispatch policies

## Source Artifacts

- **Implementation journal**: `.artifacts/20260715--tune-agent-workflows/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260715--tune-agent-workflows/implementation-plan.md`


## Scope

**whole-plan** — Iteration 05

This review targets the agent-policy files in `/Users/tucker.beck/agent-workflow-staging`, not the
`dot` codebase tasks recorded in the journal. The plan under review is the staged policy set itself;
the journal and implementation-plan are the scaffolding for this workflow, not the subject of code
findings. All findings apply to the staged `.agents/` and `.config/opencode/agents/` files.

No edits were made to source files or the staging area during this review.
Live policy and config are unchanged (pre-promotion state confirmed).


## Verification Evidence

```text
Validator: uv run python tools/validate_staged_agent_policies.py \
               --staging-root /Users/tucker.beck/agent-workflow-staging \
               --manifest /Users/tucker.beck/agent-workflow-staging/manifest.json
Result:    Validated complete staged policy set: /Users/tucker.beck/agent-workflow-staging

Live .agents skills:
  run-bug-fix/SKILL.md  — DIFFERS from staging (expected; staging holds new policy)
  run-fix/SKILL.md      — DIFFERS from staging (expected)
  run-hotfix/SKILL.md   — DIFFERS from staging (expected)
  principal.md          — DIFFERS from staging (expected)

Live .config/opencode/agents:
  8 unvaried files (architect-planner, architect-reviewer, engineer-executor,
  engineer-investigator, engineer-planner, engineer-reviewer, engineer-task-planner,
  principal) — NO model-specific variants present (correct; pre-promotion state)

Staged .config/opencode/agents:
  78 files: 7 specialist roles × 11 variants each + principal.md (correct count)
```


## Acceptance Criteria Verification

The plan for this staging round was expressed through the validator fixture and the diff.
Key commitments tracked here:

| Commitment                                        | Status | Evidence                                                                                                                              |
| ------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| run-bug-fix: isolated worktree lifecycle block    | ✓      | `run-bug-fix/SKILL.md:56–79`                                                                                                          |
| run-bug-fix: model-dispatch on all handoffs       | ✓      | `run-bug-fix/SKILL.md:161–163, 187–189, 218–224`                                                                                      |
| run-bug-fix: no generic specialist dispatch       | ✓      | validator `unvaried specialist dispatch` check passes                                                                                 |
| run-fix: isolated worktree lifecycle block        | ✓      | `run-fix/SKILL.md:71–93`                                                                                                              |
| run-fix: fail-closed attachment control           | ✓      | `run-fix/SKILL.md:79–81`; all four phrases present per validator                                                                      |
| run-fix: model-dispatch on all handoffs           | ✓      | `run-fix/SKILL.md:140–141, 177–184`                                                                                                   |
| run-hotfix: isolated worktree lifecycle block     | ✓      | `run-hotfix/SKILL.md:57–79`                                                                                                           |
| run-hotfix: streamlined-gate preservation         | ✓      | `run-hotfix/SKILL.md:72–73`; "principal-authored minimal plan", "one lightweight review", "no additional human approval gate" present |
| run-hotfix: no engineer-planner handoff added     | ✓      | `run-hotfix/SKILL.md:69`; explicit prohibition retained                                                                               |
| run-hotfix: model-dispatch on all handoffs        | ✓      | `run-hotfix/SKILL.md:120–122, 144–146, 151–154`                                                                                       |
| principal.md: model-selection policy present      | ✓      | `principal.md:60–124`; all 11 required model IDs present                                                                              |
| principal.md: no personal Sonnet                  | ✓      | validator check passes                                                                                                                |
| principal.md: "preferred, not exclusive" language | ✓      | `principal.md:96`                                                                                                                     |
| principal.md: no Zen in work dispatch             | ✓      | validator check passes                                                                                                                |
| principal.md: uses `github-copilot/gpt-5.6-terra` | ✓      | staged `principal.md` frontmatter `model: github-copilot/gpt-5.6-terra`                                                               |
| Variant manifest: 77 variants + principal         | ✓      | 78 entries in `.config/opencode/agents`                                                                                               |
| Variant frontmatter: name, model, mode, body      | ✓      | spot-checked `engineer-reviewer--work-sonnet.md`; validator passes all                                                                |
| No `run-implementation` references in policy text | ✓      | validator stale-reference check passes                                                                                                |
| `run-feature` replaces `run-implementation`       | ✓      | all skills updated per diff                                                                                                           |
| Manifest checksums match on-disk files            | ✓      | validator SHA-256 check passes with zero mismatches                                                                                   |
| Manifest inventory complete                       | ✓      | validator inventory check passes                                                                                                      |
| Promotion metadata present and complete           | ✓      | `approval_required`, `atomic_replacement`, `rollback_required`, `restart_required` all set                                            |
| Live .agents unchanged (pre-promotion)            | ✓      | diffs confirm live ≠ staged; live skills are pre-policy state                                                                         |
| Live .config/opencode/agents unchanged            | ✓      | only 8 unvaried definitions present; no variants                                                                                      |


## Scope Verification

| File / Section                                        | Justified By                                      | Status |
| ----------------------------------------------------- | ------------------------------------------------- | ------ |
| `.agents/skills/run-bug-fix/SKILL.md`                 | Plan: worktree/model-dispatch policy for bug-fix  | ✓      |
| `.agents/skills/run-fix/SKILL.md`                     | Plan: worktree/model-dispatch policy for fix      | ✓      |
| `.agents/skills/run-hotfix/SKILL.md`                  | Plan: worktree/model-dispatch + gate preservation | ✓      |
| `.agents/skills/run-task/SKILL.md`                    | Plan: worktree/model-dispatch for task workflow   | ✓      |
| `.agents/agents/principal.md`                         | Plan: model-selection policy addition             | ✓      |
| `.agents/agents/engineer-executor.md`                 | Plan: subagent escalation-verdict prohibition     | ✓      |
| `.agents/agents/engineer-investigator.md`             | Plan: subagent escalation-verdict prohibition     | ✓      |
| `.agents/agents/engineer-reviewer.md`                 | Plan: diff-first / compact review mandate         | ✓      |
| `.agents/skills/execute-implementation-plan/SKILL.md` | Plan: QA ownership moved to orchestrator          | ✓      |
| `.agents/skills/execute-implementation-task/SKILL.md` | Plan: QA ownership moved to orchestrator          | ✓      |
| All skills: `run-implementation` → `run-feature`      | Plan: rename throughout                           | ✓      |
| `.config/opencode/agents/` — 77 variants              | Plan: model-specific dispatch variant set         | ✓      |
| `manifest.json`                                       | Plan: manifest governs promotion                  | ✓      |
| `tools/validate_staged_agent_policies.py`             | Plan: validator enforces all new invariants       | ✓      |
| `metadata/recursive-diff.txt`                         | Supporting record                                 | ✓      |
| `metadata/checksums.sha256`                           | Supporting record                                 | ✓      |


## Prior Review Resolution

No prior execution review for this staging round. This is iteration 05 per the naming
convention inherited from the project sequence; no prior findings to resolve.


## Findings

### Summary

| Finding | Title                                          | Outcome  |
| ------- | ---------------------------------------------- | -------- |
| T01     | Spurious leading space in run-hotfix lifecycle | Resolved |


### Trivial

#### T01: Spurious leading space in run-hotfix lifecycle block


#### Where

`run-hotfix/SKILL.md:74` — the prior review flagged a leading space before `independent` on the
line reading `" independent review, or any additional human approval gate"`.


#### Resolution

**Resolved.** The line now reads:

```text
independent review, or any additional human approval gate solely because isolation was added.
```

No leading space is present. Verified directly against
`/Users/tucker.beck/agent-workflow-staging/.agents/skills/run-hotfix/SKILL.md` lines 72–76.

----

## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**APPROVED**

All policy commitments verified. Validator passes clean. Worktree lifecycle blocks are present
and complete in `run-bug-fix`, `run-fix`, and `run-hotfix`. Model-dispatch is required on every
handoff in all three orchestrators and generic specialist dispatch is prohibited. The hotfix
streamlined-gate preservation and planner-handoff prohibition are intact. The principal
model-selection policy is present with all 11 required model IDs. All 77 specialist variants
plus `principal.md` are correctly formed. No stale `run-implementation` references survive.
Live `.agents` and live `.config/opencode/agents` are unchanged (pre-promotion state confirmed).

T01 (leading whitespace in run-hotfix) is resolved. No open findings remain.
