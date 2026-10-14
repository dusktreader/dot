# Design Plan: Add epic workflow

Add a workflow for coordinating a multi-feature project from product framing through an MVP and later roadmap tranches.
It must preserve the standalone feature workflow while providing one durable record of the
total initiative, its minimum useful release, and its discrete feature boundaries.


## Goal

`run-epic` enables an agent and human to plan, sequence, and progressively deliver a new project or significant
expansion that contains several independently deliverable features. It begins with an epic plan that states the overall
outcome, the smallest useful MVP, the value and boundary of every identified feature, and the roadmap after MVP.

The workflow must make the MVP the first delivery objective. Before implementation begins, every feature committed to
the MVP receives a complete design and review. Later roadmap features remain concise briefs until they enter a human
approved planning tranche, preventing speculative detailed designs from being treated as commitments.


## Acceptance Criteria

### Epic planning

#### AC01: Epic has a complete product-level record

An epic plan describes the intended outcome, success criteria, scope, non-goals, cross-cutting decisions, risks,
dependencies, MVP boundary, and closure criteria in a form that is understandable without detailed feature artifacts.


#### AC02: Features have durable, traceable identities

Every feature uses a stable `FNN` identifier in the epic plan and throughout its detailed artifacts. The epic plan shows
each feature's outcome, priority, MVP or roadmap tranche, dependencies,
state, and link to its separate artifact directory.


#### AC03: Epic is approved before feature planning

The epic plan receives independent agent review and explicit human approval before the workflow creates child feature
design plans. Material changes to the product outcome, MVP boundary, feature
sequence, or cross-cutting decisions require renewed approval.


### MVP design readiness

#### AC04: MVP designs are complete before implementation

Every feature in the committed MVP has an individually reviewed design plan before any MVP implementation plan or code
work begins. The workflow presents the complete MVP design set for
explicit human approval before implementation planning starts.


#### AC05: Design changes preserve approval integrity

Before execution, a material change to an MVP feature's approved design intent, boundary, dependencies, sequencing, or
acceptance criteria requires revision of affected designs and renewed MVP design-set approval. After execution begins,
approved feature plans remain immutable. A human-approved departure is recorded as a feature-specific deviation and,
when it affects MVP scope, dependencies, sequencing, success criteria, or another feature, an epic-wide deviation.
Affected unfinished dependent work pauses until that epic record assesses the impact and the human supplies any required
renewed approval; the changed outcome is verified through feature QA and integrated MVP verification.


#### AC06: Detailed artifacts remain feature-scoped

The epic plan contains concise feature briefs and links, not embedded feature design plans, implementation plans,
reviews, journals, deviations, or QA records. Each feature record is identifiable
from its `FNN` identifier without relying on a branch name.


### Delivery and roadmap progression

#### AC07: Standalone feature workflow remains available

A direct `run-feature` request continues to own its feature-specific planning, implementation, review, QA, worktree,
branch, and publication handoff. Epic coordination does not require a feature to become part of an epic.


#### AC08: MVP and roadmap gates are explicit

The MVP is tranche `T01`. Its completion requires a recorded pass or failure for every epic success criterion and
explicit human acceptance. Any unmet criterion blocks MVP closure and roadmap implementation until affected feature work
satisfies its existing review and QA controls. Deferred features remain roadmap briefs until the human approves a later
tranche, at which point that tranche receives the same design-readiness controls before implementation.


#### AC09: Each feature has a human verification gate

After a feature passes its agent review and feature QA, the human verifies that feature before the epic begins the next
feature. A failed verification returns only the affected feature to its existing QA and deviation controls.


#### AC10: Workflow ownership is safe and auditable

The epic workflow uses one selected epic branch and worktree through each tranche, executes feature lifecycles
sequentially in that workspace, does not create nested worktrees, does not bypass feature-level
approval or QA, and never publishes or creates pull requests automatically.


#### AC11: Tranches are explicit and independently deliverable

The epic plan records `T01` as the MVP and every later approved tranche as `T02`, `T03`, and so on. Each tranche lists
its objective, included `FNN` features, dependencies, delivery state, verification result, artifact links, and its
coordinator-owned branch and worktree. A tranche begins only from the accepted integrated product state of all its
prerequisite tranches. Each uses the same design, feature-verification, integrated-verification,
failed-verification, explicit acceptance, cleanup, and publication-handoff controls.


## Architecture

The epic plan is the product-level coordination artifact. It contains an identifier-based feature register and separates
the committed MVP from the deferred roadmap. A feature register entry is a concise contract: what the feature achieves,
its dependencies and delivery state, and where its detailed artifact set lives.

Feature artifacts form the detailed layer. A feature's design, implementation plan, reviews, implementation journal,
plan deviations, and QA journal stay in a separate artifact directory bearing the same `FNN` identifier used by the epic
register. This permits complete feature history without turning the epic plan into a monolithic specification.

A shared internal lifecycle supplies feature-level design, planning, execution, review, and QA controls. `run-feature`
remains its standalone public entry point. Before MVP design-set approval, `run-epic` invokes the lifecycle's feature
design and review stages in the selected epic workspace. After the complete design set is reviewed and approved, epic
mode resumes those same feature records at implementation planning without standalone worktree setup. The epic
coordinator owns product framing, design-set readiness, roadmap progression, and integrated MVP validation; it does not
replace child artifact ownership or approval records.

The epic records a tranche register. `T01` is the MVP; each approved roadmap tranche receives the next identifier and
its own coordinator-owned branch and worktree. A later tranche starts only from the accepted integrated product state of
its prerequisite tranches; if that state is unavailable, the tranche remains blocked. Within a tranche, the epic
executes each feature lifecycle sequentially in that workspace, so feature integration is continuous and the tranche is
validated as one product. The tranche branch is the only branch handed to `run-pr` after integrated human acceptance.

Feature-level deviations retain the exact departure from the approved feature plans and its verification. An epic-wide
deviation record links the affected feature deviations and assesses the impact on MVP scope, dependencies, sequencing,
and success criteria. It is the authority for pausing dependent unfinished work and requesting a renewed MVP design-set
approval.

The human verifies each completed feature before the coordinator begins the next one. After all MVP features are
verified, the human performs a full integrated MVP verification against every epic success criterion. A failed feature
or MVP verification returns the affected work to its existing QA and deviation controls; no roadmap implementation
begins until the MVP receives explicit human acceptance.


## Unknowns

No unresolved design decisions remain.


## Technical Notes

- Epic review uses its own canonical artifact contract because it assesses product decomposition, MVP minimality,
  sequencing, and cross-feature concerns rather than a single feature's technical design.
- The workflow records an epic directory and a distinct identifier-bearing directory for every feature. The epic
  register links those directories so feature state remains visible at the product level.
- Approval records distinguish an individual feature design review, the human-approved MVP design set, each
  feature's implementation approval and QA, and the human acceptance of the integrated MVP.
