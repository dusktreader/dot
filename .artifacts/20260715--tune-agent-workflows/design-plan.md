# Design Plan: Tune agent workflows and report OpenCode costs

Establish a proportionate, evidence-led global agent operating model while adding local visibility into OpenCode
session costs. The workflow changes preserve human control for planned work, make low-risk work intentionally light,
and prevent active agent sessions from observing partial global-configuration updates.


## Goal

The global agent configuration will distinguish feature, task, bug-fix, follow-up-fix, hotfix, and hack work by
required planning, review, human gates, verification, and Git lifecycle. Every code-changing workflow that creates an
agent branch operates in an isolated agent worktree from the start, while hack work remains deliberately direct. The
principal will choose models and escalation paths from the project class, workflow class, complexity, and objective
evidence, rather than applying a fixed model or treating an agent's opinion as a risk decision.

The `dt` command-line tool will provide an OpenCode cost report from local session data. It will make recorded and
locally estimated costs separately auditable, support machine-readable export, and summarize usage by the dimensions
needed to identify expensive sessions and cache effectiveness.


## Acceptance Criteria

### Workflow classes

#### AC01: Feature workflow replaces the former implementation workflow

`run-feature` is the sole named full-feature workflow. It retains sequential human approvals for the design plan,
implementation plan, execution review, and manual testing before exclusively squash-merging its agent branch into the
ready-to-PR feature parent branch. References that formerly direct users to `run-implementation` direct them to
`run-feature`; the retired workflow is not presented as an available alternative.

Before creating any workflow artifact or changing code, `run-feature` creates an isolated agent worktree and branch
from the current parent branch. The human remains in the original worktree; all agent-produced artifacts and code
belong to the isolated worktree and agent branch.


#### AC02: Task workflow retains explicit controls

`run-task` produces a task plan and waits for human approval before execution. After execution, it performs final QA
once, obtains an independent agent code review, and waits for explicit human code-review approval before exclusively
squash-merging its agent branch into the ready-to-PR task parent branch. It never pushes or creates a pull request.

Before creating its task plan or changing code, `run-task` creates an isolated agent worktree and branch from the
current parent branch. The human remains in the original worktree; all agent-produced artifacts and code belong to the
isolated worktree and agent branch.


#### AC03: Bug-fix workflow preserves structured controls

`run-bug-fix` conducts an investigation and produces a bug report, then produces an implementation plan that the
human approves before execution. It executes the approved fix in its isolated agent worktree, performs one documented
final QA pass, obtains an independent agent code review, and waits for explicit human approval of that review before
exclusively squash-merging its agent branch into the ready-to-PR parent branch. It never pushes or creates a pull
request. At every investigator, planner, executor, QA-fix, and reviewer dispatch, it selects and dispatches a
model-specific specialist variant under AC10; it records the exact selected variant in the relevant implementation
journal or review context. The workflow follows the same stale-parent reconciliation and worktree-and-branch cleanup
rules in AC18 and AC19 as every branch-based workflow.


#### AC04: Hack workflow has intentionally narrow authority

`run-hack` records only a hack journal and may operate on the current branch, including the primary branch. It never
creates a branch, commit, squash merge, push, or pull request. It has no default plan, reviewer, or human gate;
the executor runs relevant verification and the principal conducts a concise diff review. It does not create or use an
agent worktree and has no Git lifecycle.


#### AC05: Hack escalation is evidence-led

The hack workflow escalates to `run-task` when objective evidence meets a defined escalation signal. Technical area
alone does not trigger escalation. Escalation uses the hard-signal list in AC09. Ambiguity remains a discretionary
prompt unless it blocks coherent work.


### Verification and review

#### AC06: Final QA has one owner and one position in the flow

Each feature and task run performs documented final QA after implementation and before reviewer handoff. Final QA
includes the project's linting, type checking, tests, and documented coverage evidence. A constrained lightweight
executor may correct straightforward QA failures; failures requiring a design or scope decision are escalated.


#### AC07: Implementation verification avoids redundant broad checks

Executors run focused tests while implementing individual work items but do not repeat whole-project linting or type
checking after every item. Reviewers consume final-QA evidence and perform only verification needed to establish a
finding or validate a material change.


#### AC08: Reviews are diff-first and findings-focused

Review instructions require reviewers to inspect the diff before expanding context, expand only as needed to assess a
specific concern, produce compact findings-focused artifacts, and avoid loading skills already available in context.
Re-review occurs only after a behavior, interface, data, security, or test change that alters an acceptance criterion
or adds a code path.


### Decision and model policy

#### AC09: Risk classification stays with the principal

Subagents report objective facts and evidence without risk verdicts. The principal classifies risk and independently
escalates work on narrowly defined hard signals: user-facing or system compatibility changes, safety-boundary
changes, durable state with nontrivial recovery, release or production behavior changes, substantive design choices,
materially unbounded scope, or inability to establish coherent focused verification. Evidence-based conflict with
existing patterns, QA exposing a design flaw, and material scope expansion are also hard signals.


#### AC10: Model selection follows project class and evidence

Work-project agent dispatches use only GitHub Copilot provider model IDs: `github-copilot/gpt-5.6-luna` for economy
work, `github-copilot/gpt-5.6-terra` for capable or premium work, and `github-copilot/gpt-5.6-sol` for exceptional
escalation. Personal-project dispatches may select only from the curated OpenCode Zen provider menu:
`opencode/deepseek-v4-flash` for low-cost work, `opencode/kimi-k2.7-code` for bounded code work,
`opencode/claude-sonnet-5` for non-trivial review or execution, `opencode/gpt-5.6-terra` for difficult reasoning,
and `opencode/gpt-5.6-sol` as last resort. Zen free models are not default choices. The principal recommends a model
from this menu, may escalate independently, and asks Tucker only for a genuinely unresolved material workflow or
cost tradeoff.

Every branch-based workflow selects and dispatches a model-specific specialist variant, rather than a generic role,
for each applicable investigator, planner, executor, QA-fix, and reviewer handoff. The principal applies this policy
at every handoff, selects an appropriate GitHub Copilot variant for work projects and an approved personal variant for
personal projects, and records the exact selected variant in the relevant implementation journal or review context.


### OpenCode cost reporting

#### AC11: A single scoped cost-reporting command is available

`dt opencode costs` reports from local OpenCode SQLite session data. It accepts `--since`, `--until`, `--directory`,
`--agent`, and `--model` filters, plus a `--format` selection of `table`, `json`, or `csv`; table is the default.
Output goes to standard output by default, and `--file` writes the same selected format only when its parent
directory already exists.


#### AC12: Reports make cost provenance and usage dimensions clear

Every report clearly separates OpenCode-recorded cost from locally estimated cost. It includes token totals, cache
ratio, project directory, root session tree, agent, model, date, and outlier indicators. Filtered, empty,
unavailable, and malformed local-data cases return an actionable result without modifying the source database.


#### AC13: Estimates use the selected published estimator faithfully

The local estimate follows the pricing semantics in `opencode-token-costs/estimate_opencode_costs.py` and
`opencode-token-costs/pricing.csv` from Eric Butler's `Eric-Butler_mcgraw/dotfiles` repository at the source revision
captured during implementation. The command vendors or faithfully adapts that logic without representing an estimate
as an OpenCode-recorded charge. Unsupported models, incomplete token data, and estimator-version limitations remain
visible in the report rather than being silently converted to zero or an invented price.


#### AC14: Local database failures are actionable and read-only

When the local OpenCode database is absent, locked, unreadable, or malformed, `dt opencode costs` exits non-zero and
identifies the path and failure reason. It does not create or modify the database.


### Safe promotion

#### AC15: Global configuration changes are staged before activation

Changes to the live global agent and skill configuration are developed in a timestamped temporary staging area,
validated and independently reviewed there, and presented for explicit human approval. Active configuration remains
unchanged throughout staging.


#### AC16: Promotion is atomic and followed by a restart

After explicit approval, the complete staged global-configuration set is promoted atomically so sessions observe
either the prior complete set or the approved complete set. OpenCode is restarted after live promotion. Promotion
failure preserves or restores the prior live configuration and reports the failure clearly.


### Isolated-worktree integration

#### AC17: Branch-based workflows isolate all agent-owned work

`run-feature`, `run-task`, `run-bug-fix`, `run-fix`, and `run-hotfix` create an isolated agent worktree and branch
from the current parent branch before creating artifacts or changing code. The human remains in the original worktree;
all agent-produced artifacts and code belong to the agent worktree and agent branch. Every human gate after workspace
creation identifies the agent worktree path and branch so the human can inspect the complete agent-owned state without
leaving or altering the original worktree. `run-hack` remains direct and does not create an agent worktree.


#### AC18: Parent reconciliation rejects stale state

Before exclusive squash integration, each branch-based workflow verifies that the parent worktree branch still matches
the base recorded when its agent worktree was created. Parent drift stops the workflow and is reported to the human;
the workflow does not assume the parent state is stable. Only with explicit human approval may reconciliation discard
the agent worktree and local audit branch, then restart from the updated parent. The workflow never silently rebases,
merges, discards, overwrites, or otherwise changes human work.


#### AC19: Agent worktree lifecycle preserves auditable outcomes

Agent worktrees and branches for every branch-based workflow persist through human gates. After a successful squash
merge, the workflow removes the agent worktree but preserves the local agent branch for audit. If a human declines
integration or a run is abandoned, the workflow preserves both worktree and branch until the human explicitly removes
them.


#### AC20: Follow-up fixes remain attached to their project

`run-fix` reads the existing implementation project's context and adds its fix artifacts at that project's established
path within the agent worktree. It does not create or modify fix artifacts in the human worktree, and it retains the
workflow's scoped-fix approvals and review. At every investigator, planner, executor, QA-fix, and reviewer dispatch,
it selects and dispatches a model-specific specialist variant under AC10 and records the exact selected variant in the
relevant implementation journal or review context.


#### AC21: Hotfixes retain streamlined controls while isolated

`run-hotfix` uses an agent worktree despite its urgency. Its brief investigation, principal-authored minimal plan,
direct execution, single lightweight review, and existing approval thresholds remain unchanged; isolation adds no new
approval or review gate. Each applicable investigator, executor, QA-fix, and reviewer dispatch follows the shared
model-specific specialist-variant selection and recording requirement in AC10.


## Architecture

The global operating model has four coordinated policy layers. The workflow layer selects feature, task, bug-fix,
follow-up-fix, hotfix, or hack behavior and its artifacts, gates, verification, review, and Git authority. Feature,
task, bug-fix, follow-up-fix, and hotfix runs establish a distinct agent-owned workspace from the ready-to-PR parent
branch's recorded starting point before producing any artifact or code. They integrate exclusively by squash merge
into that parent branch; the agent branch and all workflow artifacts remain in the agent workspace until that
integration succeeds. A follow-up fix attaches its new artifacts to the existing project's path as represented in that
workspace. Hack runs retain their direct, no-lifecycle behavior. The decision layer gives the principal ownership of
model selection, escalation, and risk classification, while making specialist reports factual inputs. The
verification-and-review layer separates focused implementation tests, one final QA pass, and diff-first independent
review. The promotion layer isolates edits from the live configuration until validation, review, and explicit approval
complete.

Human gates after workspace creation expose the agent workspace identity so approval applies to inspectable, isolated
work rather than an implicit branch context. This includes hotfix gates without changing that workflow's intentionally
streamlined approval model. Integration treats the recorded parent base as a freshness boundary: a changed parent
branch stops the workflow and requires explicit human approval before reconciliation discards the isolated worktree and
local audit branch and restarts from the updated parent. The workflow never assumes that parent state is stable or
silently rebases, merges, discards, overwrites, or otherwise changes human work. This prevents the workflow from
presenting stale agent work as safely integrable and preserves the human's original worktree as the integration
authority. Agent worktrees persist through those gates, are removed only after successful squash integration, and leave
their local branches intact for audit. A declined or abandoned run retains both its worktree and branch until the human
explicitly removes them.

The principal makes every specialist handoff using a model-specific variant selected under the project-class policy.
This shared dispatch rule applies to every applicable investigator, planner, executor, QA-fix, and reviewer handoff in
each branch-based workflow. Work handoffs use appropriate GitHub Copilot variants, while personal handoffs use only
approved personal variants. The implementation journal records each selected variant, and review contexts record the
variant used for their reviewer handoff, preserving an auditable link between the policy decision and each result.

The cost-reporting capability is a read-only reporting pipeline. It reads local OpenCode session records, reconstructs
session ancestry and reporting dimensions, preserves provider-recorded cost as source data, and computes a distinct
local estimate through the selected estimator. A reporting view applies requested filters, calculates token and cache
measures, identifies outliers against the selected population, groups results, and renders one consistent dataset to
the selected output format.

The `dt` command namespace treats OpenCode as a command family so future OpenCode inspection or maintenance commands
can share a coherent entry point without changing the cost report's contract.


## Technical Notes

- The repository installs the global agent configuration into the home-directory agent location, so promotion must
  account for its linked deployment rather than assume configuration is private to this checkout. The directory symlinks
  point at this repository, so validated staged files can be copied into the repository's corresponding directories.
- Existing workflow references span orchestrators, sub-skills, and agent descriptions. The rename is a compatibility
  migration across that policy graph, not merely a directory rename.
- Local OpenCode database schema must be inspected during implementation and captured in tests and user-facing help.
  The report must tolerate schema evolution and missing optional fields.
- Cost data is local operational metadata. The command must not contact an external billing service or mutate session
  data to produce a report.
- The cost report is personal tooling, but its global workflow policy must be usable in both work and personal
  projects without allowing a work dispatch to select a Zen model.
