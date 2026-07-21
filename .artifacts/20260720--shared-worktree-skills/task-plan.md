# Task plan: Share agent worktree skills

Extract branch allocation, isolated-worktree creation, and post-integration cleanup from the branch-based workflow
skills into two reusable skills. Preserve every workflow's established artifacts, human gates, review scope,
integration policy, and publication boundary; this task changes only how those workflows obtain and clean up their
agent worktrees.


## Project commands

### Run shared-policy validator tests

Command:

```shell
uv run pytest tests/test_validate_staged_agent_policies.py
```

Expected output:

```text
All validator tests pass, including shared-skill reference, duplicate-plumbing, numbered-branch, and cleanup checks.
```


### Run staged-policy validator

Command:

```shell
uv run python tools/validate_staged_agent_policies.py \
  --staging-root <staging-root> \
  --manifest <staging-root>/manifest.json
```

Expected output:

```text
Validated complete staged policy set: <staging-root>
```


### Validate edited Markdown

Command:

```shell
node ~/.agents/tools/check-markdown-format.mjs \
  .agents/skills/create-agent-worktree/SKILL.md \
  .agents/skills/cleanup-agent-worktree/SKILL.md \
  .agents/skills/run-feature/SKILL.md \
  .agents/skills/run-task/SKILL.md \
  .agents/skills/run-bug-fix/SKILL.md \
  .agents/skills/run-fix/SKILL.md \
  .agents/skills/run-hotfix/SKILL.md \
  .agents/skills/review-pr/SKILL.md
```

Expected output:

```text
The Markdown validator completes without formatting errors.
```


## Project standards

- [Repository guide](../../.dot_agents/dot.md)
- [Markdown style guide](../../.agents/instructions/markdown.md)
- [File editing safety](../../.agents/instructions/editing.md)
- [`tools/validate_staged_agent_policies.py`](../../tools/validate_staged_agent_policies.py)
- [`tests/test_validate_staged_agent_policies.py`](../../tests/test_validate_staged_agent_policies.py)


## Steps

1. Add tests in `tests/test_validate_staged_agent_policies.py` that first demonstrate failure when each branch-based
   workflow omits either shared skill reference, embeds creation or cleanup Git plumbing, or retains an obsolete
   workflow-specific branch-allocation rule. Cover `run-feature`, `run-task`, `run-bug-fix`, `run-fix`, `run-hotfix`,
   and `review-pr` independently. Add fixture mutations for a missing shared-skill file, a missing required reference,
   and a workflow that invokes the wrong shared skill at setup or cleanup.
2. Add allocation and cleanup boundary tests for the new shared skills. Assert the creation policy records the parent
   worktree, branch, and immutable base before work; uses the normal branch directly when the parent is `main` or
   `master`; allocates `{parent}--agents-{workflow}` for an existing normal branch; and selects the next unused
   zero-padded suffix such as `-02` when the unnumbered audit branch is retained. Assert the resulting worktree path is
   exactly `<repo-root>/.worktrees/<agent-branch>` and the human worktree is never switched.
3. Add cleanup-policy tests that require `git worktree remove` for the exact agent path, validation that the path is
   absent from `git worktree list`, and validation that the audit branch remains in `git branch --list`. Verify the
   validator rejects automatic `git branch -d` or `git branch -D` cleanup and any wording that allows deleting an audit
   branch without an explicit human request. Retain tests for declined, abandoned, and stale-parent outcomes so they
   continue to preserve both the agent worktree and audit branch until explicit human cleanup.
4. Create `.agents/skills/create-agent-worktree/SKILL.md` as the sole setup authority. Define required inputs for the
   repository root, parent worktree, parent branch, immutable parent base, workflow identifier, and normal-branch
   naming data when the parent is `main` or `master`. Specify branch selection, collision detection against local
   branches and worktrees, `git branch` followed by `git worktree add`, the exact mirrored path contract, and the
   prohibition on `git switch` or other mutation of the human worktree. Require the caller to receive and record the
   resolved agent branch and worktree path before it creates artifacts or dispatches work.
5. Create `.agents/skills/cleanup-agent-worktree/SKILL.md` as the sole successful-integration cleanup authority.
   Require its caller to provide the resolved audit branch and agent worktree path. Remove only that worktree after the
   workflow's existing stale-parent check, approved squash, and any workflow-specific completion gate have succeeded;
   verify removal with `git worktree list`; verify audit retention with `git branch --list`; and state that audit branch
   deletion is forbidden unless the human explicitly requests it. State that declined, abandoned, and regeneration
   paths remain caller-controlled and do not trigger automatic cleanup.
6. Refactor `run-feature`, `run-task`, `run-bug-fix`, `run-fix`, `run-hotfix`, and `review-pr` to invoke
   `create-agent-worktree` before their first artifact or investigation action and invoke `cleanup-agent-worktree` only
   after their already-defined successful squash path. Replace inline `git branch`, suffix allocation, `git worktree
   add`, `git worktree remove`, and audit-branch retention commands with concise references to the shared skills plus
   workflow-specific input values such as `feature`, `task`, `bug-fix`, `fix`, `hotfix`, and `review`. Preserve every
   existing human gate, artifact rule, model-dispatch rule, stale-parent stop, squash-only integration rule, and
   `run-pr` publication handoff.
7. Update `tools/validate_staged_agent_policies.py` so the six workflows must reference both shared skills at their
   appropriate lifecycle points and the two shared skill files must be present and satisfy their contracts. Replace
   workflow-specific string checks for branch creation, worktree addition, numbered audit allocation, and removal with
   shared-skill checks. Reject duplicated worktree plumbing in workflow documents while retaining validation of their
   detailed gates, temporary-branch non-publication, main/master policy, stale-parent handling, and retained-audit
   branch policy.
8. Run the focused validator tests, then validate the complete staged policy tree. Run the Markdown formatter over the
   two new shared skills and all six migrated workflow skills. Confirm the validator's complete fixture passes and that
   intentional failure fixtures produce actionable messages naming the missing shared reference or prohibited duplicate
   plumbing.


## Acceptance criteria

- AC01: `.agents/skills/create-agent-worktree/SKILL.md` centralizes branch selection and isolated-worktree creation for
  `run-feature`, `run-task`, `run-bug-fix`, `run-fix`, `run-hotfix`, and `review-pr`.
- AC02: When invoked from `main` or `master`, the creation skill creates and uses the normal parent branch directly;
  when invoked from an existing normal branch, it allocates `{parent}--agents-{workflow}` or the next available
  zero-padded suffix when a retained audit branch already occupies that name.
- AC03: The creation skill uses exactly `<repo-root>/.worktrees/<agent-branch>` and never switches or otherwise alters
  the human worktree.
- AC04: `.agents/skills/cleanup-agent-worktree/SKILL.md` removes only the successful-run agent worktree, proves its
  absence through `git worktree list`, proves the audit branch remains through `git branch --list`, and never deletes
  that audit branch without an explicit human request.
- AC05: Each migrated workflow references the shared creation and cleanup skills at the correct lifecycle boundaries
  and contains no duplicated branch allocation, worktree creation, collision-suffix, removal, or audit-retention
  plumbing.
- AC06: The migrated workflows retain their existing workflow-specific artifacts, detailed approval gates, model and
  review policy, stale-parent stop, integration rule, and `run-pr` publication boundary.
- AC07: `tools/validate_staged_agent_policies.py` and `tests/test_validate_staged_agent_policies.py` reject missing
  shared-skill references, missing shared-skill contracts, duplicate workflow plumbing, unsafe cleanup, incorrect
  temporary suffix allocation, and human-worktree switching; the complete fixture passes.


## Technical notes

Treat the normal branch produced from `main` or `master` as the agent branch, not as an audit branch. Audit-branch
retention and numbered suffix allocation apply only when a workflow starts from an existing normal parent branch.
Workflow callers remain responsible for their domain-specific ticket, slug, review-cycle, artifact, gate, and squash
decisions; the shared skills own only the common Git worktree lifecycle.
