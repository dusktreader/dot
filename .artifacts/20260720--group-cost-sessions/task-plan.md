# Task plan: Group OpenCode cost sessions

Render `dt opencode costs` table rows as session trees while keeping the existing columns and flat JSON and CSV
contracts intact. Update every branch-based workflow policy and its staged-policy validator to require safe,
branch-mirrored agent worktrees. This task does not change the OpenCode database schema, CLI options, or serialized
report formats.


## Project commands

### Run focused cost-report tests

Command:

```shell
uv run pytest tests/test_opencode_costs.py tests/test_cli_opencode_costs.py
```

Expected output:

```text
All selected tests pass.
```


### Run staged-policy validator tests

Command:

```shell
uv run pytest tests/test_validate_staged_agent_policies.py
```

Expected output:

```text
All selected tests pass.
```


### Run repository quality checks

Command:

```shell
uv run pytest && uv run ruff check src tests && uv run ty check
```

Expected output:

```text
The full test suite, Ruff, and ty complete without errors.
```


## Project standards

- [Repository guide](../../.dot_agents/dot.md)
- [Python style guide](../../.agents/instructions/python.md)
- [Markdown style guide](../../.agents/instructions/markdown.md)
- [`pyproject.toml`](../../pyproject.toml)


## Steps

1. Add focused `Report.build` and table-rendering tests in `tests/test_opencode_costs.py` for a root, child, and
   deeper descendant. Assert that table `Session` values use tree prefixes, retain the current columns, and emit each
   parent immediately before its descendants.
2. Add sorting coverage that uses multiple root groups and a requested sort key. Assert that sorting reorders root
   groups only, preserves depth-first parent/child order inside each group, and keeps unresolved or rootless sessions
   visible as independent rows. Extend existing JSON and CSV assertions to prove their flat session IDs and row
   ordering are unchanged by table-only tree decoration.
3. Refactor `src/dot_tools/opencode_costs.py` so report construction preserves the flat row order for JSON and CSV,
   while table rendering derives a hierarchy from `session_id`, `parent_session`, and `root_session`. Apply requested
   sort keys to root groups, then render every group depth-first with each parent followed by its children; decorate
   only the table `Session` cell with ASCII tree prefixes and leave the remaining table columns unchanged.
4. Add CLI coverage in `tests/test_cli_opencode_costs.py` using a mocked parent-child session set to confirm default
   terminal and `--file` table output show the tree prefixes and retain their existing ANSI-free file behavior.
5. Update only `.agents/skills/run-feature/SKILL.md`, `.agents/skills/run-task/SKILL.md`,
   `.agents/skills/run-bug-fix/SKILL.md`, `.agents/skills/run-fix/SKILL.md`, and
   `.agents/skills/run-hotfix/SKILL.md` in this worktree. In each setup, require agent worktrees under
   `<repo-root>/.worktrees/<agent-branch>` with a path that exactly mirrors the full agent branch path; create the
   parent branch with `git branch`, immediately create the agent worktree with `git worktree add`, and explicitly
   prohibit `git switch` in the human worktree. Direct each workflow immediately to its defined approval gate after
   setup, with no additional stop before that gate.
6. Extend `tools/validate_staged_agent_policies.py` with explicit setup controls for every branch-based skill:
   `run-feature`, `run-task`, `run-bug-fix`, `run-fix`, and `run-hotfix`. Require `.worktrees`, agent-branch path
   mirroring, the `git branch` then immediate `git worktree add` sequence, the human-worktree `git switch`
   prohibition, and direct progression without a stop before the defined approval gate. Scope the `git switch`
   rejection to setup policy language so existing permitted Git examples outside setup are not misclassified.
7. Extend `tests/test_validate_staged_agent_policies.py` to cover each branch-based skill independently. Mutate each
   staged fixture for every required phrase/control, including an injected setup `git switch` and an extra pre-gate
   stop, and assert the validator returns an actionable failure for every violation. Confirm every unmodified staged
   fixture remains valid.
8. Run the focused cost-report and validator tests, then the repository quality checks. Run the Markdown formatter
   validator on this plan and any edited Markdown policy file before review.
9. Scope extension: add standalone `run-pr`, make it the principal's final publishing workflow, and replace the branch
    workflow policy with normal-branch and temporary-audit-branch modes. Validate no-PR/no-main integration controls.
10. Scope addendum: restore the detailed baseline workflow skills and policy validator before applying these additive
    publication, branch-mode, review-pr, and validation changes; do not alter cost-report source, tests, or task
    artifact hierarchy.


## Acceptance criteria

- AC01: Table output renders each root session followed by its children and deeper descendants, with ASCII tree
  prefixes in the `Session` cell and no added, removed, or renamed table columns.
- AC02: A requested `--sort` order ranks root groups by the selected sort keys while descendants remain in depth-first
  parent/child order within their own root group.
- AC03: JSON and CSV preserve their flat row objects, fields, raw session IDs, and existing sort behavior; they do
  not contain table tree prefixes.
- AC04: Rootless, missing-parent, or otherwise unresolved ancestry rows remain represented in table output rather
  than being omitted during hierarchy construction.
- AC05: Each branch-based skill (`run-feature`, `run-task`, `run-bug-fix`, `run-fix`, and `run-hotfix`) requires
  `<repo-root>/.worktrees/<agent-branch>` exactly mirroring the agent branch path, creates the parent branch with
  `git branch` immediately before `git worktree add`, and prohibits `git switch` in the human worktree.
- AC06: Each branch-based skill proceeds directly from setup without a stop until its defined approval gate.
- AC07: `tools/validate_staged_agent_policies.py` rejects every staged branch-based policy missing any required
   worktree path, mirroring, setup-sequence, direct-progression, pre-gate-stop, or `git switch` prohibition control,
   and all validator tests pass.
- AC08: `run-pr` is the only publishing workflow; branch workflows and `review-pr` keep their existing detailed gates
  while deferring publication to it.
