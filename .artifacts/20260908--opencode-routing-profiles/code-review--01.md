# Code Review: isolated OpenCode routing profiles

**Iteration 01**

The implementation was reviewed against the approved task plan, execution journal, final QA evidence, and the
personal and optional work-dot repository diffs. The initial review findings were resolved or recorded as follow-up
work. A human-requested change then made `light` the default tier for both profiles, with an explicit launcher seam for
specific `standard` cases. The launcher was then migrated into `dt` and `wdt` CLI subcommands, with `oc` and `woc`
aliases. The resulting blockers received focused re-reviews.


## Source

Personal repository:

- `.agents/agents/principal.md`
- `.agents/skills/run-bug-fix/SKILL.md`
- `.agents/skills/run-feature/SKILL.md`
- `.agents/skills/run-fix/SKILL.md`
- `.agents/skills/run-hack/SKILL.md`
- `.agents/skills/run-hotfix/SKILL.md`
- `.agents/skills/run-task/SKILL.md`
- `.config/opencode/agents/architect-planner.md`
- `.config/opencode/agents/architect-reviewer.md`
- `.config/opencode/agents/engineer-executor.md`
- `.config/opencode/agents/engineer-investigator.md`
- `.config/opencode/agents/engineer-planner.md`
- `.config/opencode/agents/engineer-reviewer.md`
- `.config/opencode/agents/engineer-task-planner.md`
- `.config/opencode/agents/principal.md`
- `.config/opencode/opencode.json`
- `.config/opencode/package.json`
- `.config/opencode/plugins/router-metadata.js`
- `.config/opencode/profiles/personal.json`
- `.config/litellm/opencode-tab.yaml`
- `src/dot_tools/opencode_profile.py`
- `src/dot_tools/cli/opencode.py`
- `.dotrc`
- `uninstall.sh`
- `etc/install.yaml`
- `tools/validate_opencode_profiles.py`
- `tools/validate_staged_agent_policies.py`
- `tests/test_opencode_profiles.py`
- `tests/test_router_metadata.js`
- `tests/test_validate_staged_agent_policies.py`
- `README.md`
- `.gitignore`
- Deleted profile-specific agent files under `.config/opencode/agents/`

Work repository:

- `.config/litellm/opencode-mhe.yaml`
- `.config/opencode/profiles/work.json`
- `src/work_tools/opencode_profile.py`
- `src/work_tools/cli/opencode.py`
- `src/work_tools/cli/main.py`
- `.workrc`
- `etc/install.yaml`
- `tests/test_opencode_profiles.py`
- `README.md`
- `.gitignore`
- Preserved pre-existing `.workrc`


## Verification Evidence

| Command                                                                                                                  | Result                                                                 |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `uv run pytest tests/test_opencode_profiles.py tests/test_validate_staged_agent_policies.py --no-cov -q` in personal dot | 100 passed                                                             |
| `uv run pytest tests/test_opencode_profiles.py --no-cov -q` in work-dot                                                  | 22 passed                                                              |
| `uv run pytest --no-cov -q` in work-dot                                                                                  | 45 passed                                                              |
| `uv run pytest -q` in personal dot                                                                                       | 409 passed, 1 known baseline failure                                   |
| Focused `uv run ruff check ...` in both repositories                                                                     | Passed                                                                 |
| `uv run ty check`                                                                                                        | 78 known baseline diagnostics, no routing-specific diagnostic isolated |
| `zsh -n .dotrc`                                                                                                          | Passed                                                                 |
| `zsh -n .workrc`                                                                                                         | Passed                                                                 |
| Offline profile validator                                                                                                | Passed for personal and optional work profiles                         |
| `node --check .config/opencode/plugins/router-metadata.js`                                                               | Passed                                                                 |
| `node --test tests/test_router_metadata.js`                                                                              | 9 passed                                                               |
| `git diff --check` in both repositories                                                                                  | Passed                                                                 |

The personal baseline failure expects `@opencode-ai/plugin` version `1.18.14`, while the tracked package specifies


## Issue Summary

- **Critical**: 4 initial findings, all resolved
- **Significant**: 5 findings, deferred as follow-up work
- **Trivial**: 1 finding, accepted without change


## Findings

### Summary

| Finding | Title                                                          | Outcome                             |
| ------- | -------------------------------------------------------------- | ----------------------------------- |
| C01     | Launcher can adopt an unrelated healthy router                 | Resolved                            |
| C02     | Workflow policies dispatch deleted model-specific names        | Resolved                            |
| C03     | Staged validator lost existing safety coverage                 | Resolved                            |
| C04     | Work profile did not enforce its account boundary              | Resolved with documented limitation |
| S01     | Personal fallback is broader than quota-only behavior          | Follow-up                           |
| S02     | Premium tier has no operational selection path                 | Resolved                            |
| S03     | Behavioral test coverage remains incomplete                    | Follow-up                           |
| S04     | Offline validator does not provide schema validation           | Follow-up                           |
| S05     | Work profile does not install or verify the shared plugin      | Follow-up                           |
| S06     | Authentication and troubleshooting documentation is incomplete | Follow-up                           |
| T01     | Unused LiteLLM tag prefix configuration                        | Accepted                            |


### Critical

#### C01: Launcher can adopt an unrelated healthy router


#### Where

`bin/opencode-tab:81-100` and `~/src/mhe/work-dot/bin/opencode-mhe:81-100`


#### Issue

The launchers originally trusted any healthy process listening on the profile port.


#### Impact

An unrelated local process could receive requests and profile credentials, violating account and profile isolation.


#### Fix

Reuse now requires a live recorded PID whose command matches the profile-specific LiteLLM config, loopback host, and
port. Occupied unrelated ports fail closed, and stop only kills a matching recorded PID. Tests cover unrelated
listeners,
matching PIDs, and safe stop behavior.


#### Outcome

Resolved. The focused re-review found no remaining critical issue.


#### C02: Workflow policies dispatch deleted model-specific names


#### Where

`.agents/skills/run-feature/SKILL.md`, `.agents/skills/run-bug-fix/SKILL.md`, `.agents/skills/run-fix/SKILL.md`, and
`.agents/skills/run-hotfix/SKILL.md`


#### Issue

Several workflow policies still named deleted personal/work/model specialist variants.


#### Impact

The workflows could request agents that no longer exist and bypass the generic routing contract.


#### Fix

Dispatch prose now uses shared role names through the active profile launcher, with profile and tier selection recorded
separately. The staged validator rejects model-specific dispatch names and regression tests cover the invariant.


#### Outcome

Resolved. A repository search found no remaining model-specific dispatch references in the changed policy files.


#### C03: Staged validator lost existing safety coverage


#### Where

`tools/validate_staged_agent_policies.py` and `tests/test_validate_staged_agent_policies.py`


#### Issue

The first implementation replaced, rather than extended, checks for several workflows and shared Git lifecycle rules.


#### Impact

Unsafe workflow policy regressions could pass validation.


#### Fix

Lifecycle, worktree, publication, branch integration, retained branch, promotion, principal ownership, and review-pr
checks were restored alongside generic role, profile, and tier checks. Regression tests cover omitted controls.


#### Outcome

Resolved. The staged-policy suite passed 71 tests during the fix pass and remains included in the final 80 focused
tests.


#### C04: Work profile did not enforce its account boundary


#### Where

`~/src/mhe/work-dot/bin/opencode-mhe:143-155`


#### Issue

Separate token directories alone could not detect a wrong first-run GitHub account.


#### Impact

The work launcher could use a personal or otherwise incorrect Copilot login.


#### Fix

Normal work launch now requires an owner-controlled work token directory and an exact `TuckerBeck_mcgraw` account
marker. Missing or mismatched markers fail closed, with tests and setup documentation.


#### Outcome

Resolved with a documented limitation. The marker is an offline assertion seam and cannot prove provider identity
without contacting the provider, which was prohibited for this task.


### Significant

#### S01: Personal fallback is broader than quota-only behavior


#### Where

`.config/litellm/opencode-tab.yaml:42-51`


#### Issue

The configured LiteLLM fallback applies to general provider failures, not a conclusively identified Copilot quota error.


#### Impact

Personal requests may reach Zen during authentication, outage, or other upstream failures.


#### Fix

Deferred. The limitation is documented, the fallback remains personal-only and light-only, and work cannot reach it.


#### Outcome

Follow-up. A controlled provider response or a narrower provider error mechanism is required to change this safely.


#### S02: Premium and standard tiers lacked an operational selection path


#### Where

`.config/opencode/plugins/router-metadata.js:30-35` and the shared agent definitions


#### Issue

Premium and standard were represented in router aliases and policy prose, but no profile-independent explicit
per-invocation selection path was available.


#### Impact

The principal could not reliably select a specific standard or premium route without encoding model families in role
names or relying on unsupported task arguments.


#### Fix

The launchers now accept `--tier light|standard|premium`, default to light, select the matching alias through
`OPENCODE_CONFIG_CONTENT`, and set validated `OPENCODE_ROUTING_TIER` metadata. Premium still requires
`OPENCODE_PREMIUM_APPROVED=1`.


#### Outcome

Resolved. Ordinary and review dispatches use light, specific standard cases use the explicit launcher flag, and premium
remains behind explicit human approval.


#### S03: Behavioral test coverage remains incomplete


#### Where

`tests/test_opencode_profiles.py` and `tests/test_router_metadata.js`


#### Issue

The implementation tests launcher safety and helper functions, but do not exercise every plugin hook and all session
variants end to end.


#### Impact

Regressions in plugin lifecycle handling, resumed sessions, or argument/environment construction could escape tests.


#### Fix

Deferred. Add direct hook lifecycle tests and broader subprocess seams without contacting providers.


#### Outcome

Follow-up. The critical launcher and account-boundary behaviors are covered by the final focused tests.


#### S04: Offline validator does not provide schema validation


#### Where

`tools/validate_opencode_profiles.py:26-59`


#### Issue

The validator checks parseability, aliases, tags, profile boundaries, and credential-looking values but not complete
LiteLLM or OpenCode schema validity.


#### Impact

Some operational configuration errors could pass offline validation.


#### Fix

Deferred. Add provider-free schema or startup validation when a stable supported validation interface is selected.


#### Outcome

Follow-up. Current offline validation passes and no provider calls were made.


#### S05: Work profile does not install or verify the shared plugin


#### Where

`~/src/mhe/work-dot/etc/install.yaml` and `.config/opencode/plugins/router-metadata.js`


#### Issue

Work-dot reuses the plugin installed by personal dot but does not verify that prerequisite at install or launch time.


#### Impact

An independently installed work layer could run without routing headers.


#### Fix

Deferred. Add a documented prerequisite plus a launcher-time fail-closed check, or another non-duplicating shared
installation mechanism.


#### Outcome

Follow-up. Work-owned configuration remains optional and does not duplicate the personal plugin.


#### S06: Authentication and troubleshooting documentation is incomplete


#### Where

`README.md` in both repositories


#### Issue

The documentation describes profile commands, state paths, account boundaries, and limitations but lacks complete
first-run authentication, stale-token remediation, and shared-plugin prerequisite instructions.


#### Fix

Deferred. Expand setup and troubleshooting documentation in follow-up work.


#### Outcome

Follow-up. The current documentation explicitly warns about `gh auth switch`, work-marker setup, and provider identity
limits.


### Trivial

#### T01: Unused LiteLLM tag prefix configuration


#### Where

`.config/litellm/opencode-tab.yaml:45` and the corresponding work configuration


#### Issue

The routers configure `tag_routing_prefix: "route:"`, while the plugin emits raw required tags.


#### Fix

No change. LiteLLM accepts the required raw tags used by the implementation.


#### Outcome

Accepted as non-blocking. Remove the unused setting or exercise it consistently in a later cleanup.


## Latest Review Resolution

The light-default adjustment, CLI migration, and follow-up fixes were re-reviewed after focused QA. The review checklist
confirmed:

- Both profile overlays and launchers default to `light`, and both light routes select Luna.
- Personal and work light deployments include `capability:tools`, so principal tool routing has a matching deployment.
- `--tier standard` selects the standard alias for one invocation and passes remaining OpenCode arguments unchanged.
- Invalid capability and tier metadata, unapproved premium routing, unknown-agent light fallback, and run-hack
  model-specific dispatch names are covered by tests.
- Generic workflow dispatch, staged-policy safety checks, profile isolation, work account gating, and work Zen exclusion
  remain intact.
- `dt opencode launch/status/stop` and `wdt opencode launch/status/stop` preserve lifecycle safety, while `oc` and `woc`
  provide the documented shell aliases.
- Explicit CLI premium selection works without the automated principal approval marker.
- Work strips personal provider credentials, requires the shared routing plugin for launch, and leaves status/stop
  available for cleanup.
- New router startup failure cleanup, uninstall cleanup, and strict bare-or-absolute `litellm` executable matching are
  covered by tests.
- The personal and work LiteLLM config files are now named `personal.yaml` and `work.yaml`. Both are passed explicitly
  to LiteLLM with `--config`; the historical `opencode-tab` and `opencode-mhe` profile identifiers remain unchanged.
- Operational profile documentation was removed from both repository READMEs. The relevant personal and work setup,
  isolation, tier, prerequisite, and troubleshooting guidance now appears in `dt opencode launch --help` and
  `wdt opencode launch --help`.
- OpenCode agent adapters now use `prompt: "{file:~/.agents/agents/<role>.md}"` and retain only OpenCode discovery
  metadata. Redundant agent-level model, variant, capability, and tier options were removed; the routing plugin and
  launcher remain the single routing authority.
- The active model remains `personal/light` or `work/light`, while the principal agent defaults to OpenCode variant
  `xhigh` and `default_agent: principal` in generated runtime configuration.

The final re-review found no Critical, Significant, or Trivial findings and approved the implementation. The config
filename cleanup and README/help-text documentation cleanup were also re-reviewed and found no findings. The remaining
follow-up findings concern broader provider behavior, schema validation, and documentation depth rather than the
requested tier-default or CLI migration changes.


## Skills Applied

- `customize-opencode`: global built-in
- `execute-implementation-plan`: global fallback, applied by the execution workflow
- `review-code`: global fallback, applied by the independent review


## Decision

**APPROVED**

All critical findings are resolved and the focused quality gates pass. The five remaining significant findings are
recorded as follow-up work and do not block this bounded task. The CLI migration's review blockers are resolved,
including work credential stripping, strict router executable matching, failed-start cleanup, the shared-plugin
prerequisite, uninstall cleanup, and explicit CLI premium behavior. The known personal package-version baseline failure,
existing `ty` diagnostics, stale global `dt` executable during QA, and provider-specific limitations are documented and
are not regressions from the final fixes.
