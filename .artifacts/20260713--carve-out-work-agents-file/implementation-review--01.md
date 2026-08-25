# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 01**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 5
- **Trivial**:     3


## Findings

### Summary

| Finding | Title                                                              | Outcome |
| ------- | ------------------------------------------------------------------ | ------- |
| C01     | Migration guide uses wrong `settings bind` syntax                  |         |
| S01     | `wdt settings set` is a hallucinated Typerdrive command            |         |
| S02     | `_seed_secrets()` assumes unreachable Typerdrive context           |         |
| S03     | Flat `WorkSettings` schema conflicts with nested `Settings` design |         |
| S04     | Design plan AC22 (risk documentation) has no covering task         |         |
| S05     | Task 02 and Task 01 each contain duplicate steps                   |         |
| T01     | `Unknowns` contradicts Task 04's own research step                 |         |
| T02     | `## Technical Notes` section is empty                              |         |
| T03     | Shell rc code fence uses `bash` instead of `shell`                 |         |


### Critical

#### C01: Migration guide uses wrong `settings bind` syntax


#### Where

Execution — Task 13 — Steps — lines 934–937


#### Issue

Task 13 step 5 provides a sample `dt settings bind` command:

```text
dt settings bind jira_base_url "https://fusion.jira.com"
```

This syntax is incorrect. `dt settings bind` accepts named options keyed on the top-level
`Settings` fields. The existing `Settings` model wraps Jira credentials inside a `JiraInfo`
nested model, so the actual bind command is `dt settings bind --jira-info '{"base_url": ...,
"api_key": ..., "cloud_id": ...}'` (or equivalent). The flat-key invocation the guide shows
does not correspond to any command Typerdrive generates from the current schema.

The migration guide is the operator's reference for a one-shot, high-stakes credential
cutover. Incorrect command examples will cause the operator to fail validation gating and
risk deleting the legacy credential file prematurely.


#### Impact

The migration step will fail on execution. If the operator does not notice the discrepancy
and proceeds to the deletion step, credentials are lost with no fallback.


#### Suggestion

Before Task 13 is executed, confirm the exact `dt settings bind` invocation by running
`dt settings bind --help` and documenting the required option shape. Update the sample
command in step 5 to match. If `WorkSettings` uses a different (flat) schema from
`Settings`, document both bind syntaxes separately and call out the difference explicitly.

Alternatively, if `WorkSettings` is intentionally flat (see S03), ensure the migration
guide uses the flat invocation only for `wdt settings bind`, and uses the nested invocation
for `dt settings bind`.


#### Outcome


----

### Significant

#### S01: `wdt settings set` is a hallucinated Typerdrive command


#### Where

Execution — Task 04 — Acceptance Criteria — line 363; Task 05 — AC05 — line 435


#### Issue

AC08 of Task 04 and AC05 of Task 05 direct operators to use `wdt settings set <field>
<value>`. Typerdrive does not expose a `settings set` command. The auto-generated settings
sub-commands are `bind`, `update`, `unset`, `reset`, and `show`. There is no `set`.

AC08 reads: "`wdt settings set <field> <value>` updates a setting in the work secret store".
AC05 of Task 05 reads: "Configure it via: `wdt settings set <key> <value>`".


#### Impact

Operators and agents following these ACs will find the command does not exist. Notices
printed by `wdt configure` will direct users to a non-existent interface, making secret
population impossible via the documented path.


#### Suggestion

Replace all references to `wdt settings set` with `wdt settings update --<field> <value>`
(for updating a single field) or `wdt settings bind --<field> <value>` (for binding
interactively). Verify the exact option shape after `WorkSettings` is defined.


#### Outcome


----

#### S02: `_seed_secrets()` assumes unreachable Typerdrive context


#### Where

Execution — Task 05 — Steps — line 445


#### Issue

Task 05 step 1 instructs `WorkInstaller._seed_secrets()` to "load the current settings via
typerdrive" and "save the updated settings". However, `WorkInstaller` is a plain Python
class instantiated outside the CLI framework. Typerdrive's `SettingsManager` requires an
initialized `TyperdriveConfig` — created by the CLI's Typer context when `attach_settings`
or `add_settings_subcommand` wires things up — to know the application config directory and
settings path.

Calling `SettingsManager(WorkSettings)` directly inside `WorkInstaller._seed_secrets()`
will fail unless the Typerdrive config context has been established. The plan does not
address how to initialize this context from within `WorkInstaller`, nor does it show the
call site in `cli/main.py` that initializes the context before constructing `WorkInstaller`.


#### Impact

`_seed_secrets()` as described will raise `SettingsInitError` or similar at runtime when
called from `WorkInstaller.install_dot()`, because no Typerdrive context exists. The
configure command will fail and the entire seeding contract collapses.


#### Suggestion

Either: (a) pass the initialized `SettingsManager` instance into `WorkInstaller` from the
CLI layer (where context is available), or (b) call `set_typerdrive_config(...)` with the
correct app name before constructing `SettingsManager` inside `WorkInstaller`. Option (b)
requires understanding the exact config initialization pattern; it should be researched in
Task 04 step 5 and documented in Task 05's Technical Notes. Add an AC to Task 05 confirming
that seeding works when invoked from the `wdt configure` command (not just in isolation).


#### Outcome


----

#### S03: Flat `WorkSettings` schema conflicts with nested `Settings` design


#### Where

Execution — Task 04 — Acceptance Criteria — line 352; Task 04 Steps — line 374


#### Issue

Task 04 defines `WorkSettings` with flat fields: `jira_api_key`, `jira_base_url`,
`jira_cloud_id`, `confluence_api_key`, `datadog_api_key`. The existing `Settings` in `dot`
uses a nested model: `jira_info: JiraInfo` where `JiraInfo` groups `base_url`, `api_key`,
and `cloud_id`. The plan does not justify or even acknowledge this divergence.

The design plan (AC18) states every `wdt secrets` sub-command must have the "same contract"
as its `dt secrets` counterpart. If the schemas differ structurally, the `fetch` keys will
differ between CLIs (`jira_api_key` vs `jira_info.api_key` or a nested path), which
violates the spirit of AC18 and confuses operators who use both CLIs.

Additionally, `WorkSettings` introduces Confluence and Datadog fields that `Settings`
doesn't have — this may be intentional but is not discussed. If `dt settings` also needs
a `secrets fetch` command (as implied by the design plan AC17), what fields does `Settings`
expose? The plan omits a `dt secrets` command entirely.


#### Impact

The flat-vs-nested inconsistency will surface in two places: the `settings bind` syntax
differs between CLIs (C01 above), and any documentation or agent guidance that treats both
CLIs symmetrically will be wrong. The absence of a `dt secrets fetch` task means design
plan AC17 is unimplemented.


#### Suggestion

Add a task (or extend Task 04) to implement `dt secrets fetch` in the `dot` repo, covering
AC17. Explicitly document the chosen schema shape for `WorkSettings` and explain why it
diverges from `Settings` if it does. If the schemas are intentionally different, document
how `secrets fetch` key names map across the two CLIs.


#### Outcome


----

#### S04: Design plan AC22 has no covering task


#### Where

Design plan — AC22; Implementation plan — Execution section (all tasks)


#### Issue

Design plan AC22 requires: "Documentation for the `secrets fetch` command in each CLI
states plainly that the command prints a secret to stdout, that this is intentional for
scripting, and that callers are responsible for not logging or echoing the output."

No task in the implementation plan adds this risk disclosure to the `secrets fetch` help
text or to any documentation. Tasks 10, 13, and 14 update agent instructions and migration
docs but none require a `secrets fetch --help` text that acknowledges the stdout-printing
risk.


#### Impact

AC22 of the approved design plan is unimplemented. The risk disclosure is intentionally
part of the design and was called out as explicit in the Risks and decisions section. Its
absence means the accepted design is not fully delivered.


#### Suggestion

Add an AC to Task 04 (or a note in Task 10's documentation step): "The `secrets fetch`
help text includes a plain statement that the command prints a secret value to stdout, that
this is intentional for scripting, and that callers must not log or echo the output."
Mirror the same AC in `work-dot`'s Task 04 equivalent.


#### Outcome


----

#### S05: Task 01 and Task 02 contain duplicate steps


#### Where

Execution — Task 01 — Steps — lines 193–195; Task 02 — Steps — lines 239, 254, 257


#### Issue

Task 01 steps 4 and 5 both write to `work-dot/pyproject.toml`. Step 4 creates it with the
entry point, dependencies, and project name. Step 5 then creates it again with lint and test
settings. The steps should be a single unified step or the second step should say "add to
the `pyproject.toml` created in step 4".

Task 02 step 2 creates `work-dot/src/work_tools/cli/main.py`, and step 4 also says "Create
`work-dot/src/work_tools/cli/main.py`". Step 4 is a pure duplicate of step 2, with step 3
and the placeholder-import note in between.


#### Impact

An implementer executing either task literally will either overwrite their own work or be
confused about which step is authoritative. Step duplication in Task 01 risks producing an
incomplete `pyproject.toml` (missing either entry point or tool config).


#### Suggestion

In Task 01, merge steps 4 and 5 into a single step covering the full `pyproject.toml`
content. In Task 02, remove the duplicate step 4 and replace it with "Run `uv sync` and
verify `wdt --help` displays the expected output", which is what step 4 likely intended.


#### Outcome


----

### Trivial

#### T01: `Unknowns` section contradicts Task 04's own research step


#### Where

Unknowns — line 1079; Task 04 — Steps — line 388


#### Issue

The `## Unknowns` section states: "None. All open questions from the design plan were
resolved before this implementation plan was written." Yet Task 04 step 5 reads: "Research
and document Typerdrive's settings API: how settings are persisted (file path), how multiple
CLIs can have separate stores. This research must be completed during this task."

If the API surface is unknown enough to require mid-task research, it is a legitimate
unknown and belongs in the `## Unknowns` section. The contradiction obscures a real
open question from plan reviewers.


#### Suggestion

Either move the Typerdrive API research question into `## Unknowns` (with a note that it
is resolved in-task) or rewrite Task 04 step 5 to indicate that the API surface was
verified during planning and state the confirmed details inline in the Technical Notes.


#### Outcome


----

#### T02: `## Technical Notes` section is empty


#### Where

Technical Notes — line 1092


#### Issue

The `## Technical Notes` heading at the end of the document has no content. Per the
implementation plan description, this section holds "additional technical context for the
implementation." An empty section is noise; it should either be populated or removed.


#### Suggestion

Either add relevant cross-task technical notes (e.g., the Typerdrive config path
conventions, the `extra_dotfiles` dedup contract, the exit code conventions already stated
in the Technical Notes subsection) or remove the empty heading entirely.


#### Outcome


----

#### T03: Shell rc code fence uses `bash` language hint


#### Where

Execution — Task 09 — Steps — line 692


#### Issue

The fenced code block for `work-dot/.dot_work_rc` content uses ` ```bash `. The project
markdown style guide requires `shell` for shell commands and scripts, not `bash`.


#### Suggestion

Change ` ```bash ` to ` ```shell `.


#### Outcome


----

## Notes

C01 and S03 are closely related: the correct `dt settings bind` syntax depends on the
`Settings` schema, and the correct `wdt settings bind` syntax depends on the `WorkSettings`
schema. Resolving S03 (clarifying the schema design) will inform the fix for C01 (the
migration guide). Address S03 first.

S02 (Typerdrive context initialization) is the highest-risk implementation trap in the
plan. The seeding mechanism is plausible at a design level but the CLI context requirement
is a runtime constraint that will block Task 05 if not addressed in Task 04's research step.
If the reviewer accepts moving the Typerdrive research into `## Unknowns`, the resolution
of that unknown should explicitly answer the context-initialization question.

S04 (missing AC22 coverage) requires no human input — the design plan is clear and the fix
is a one-line AC addition. It can be resolved without discussion.
