# About Tucker

Context about the user. Read this every session so you do not have to rediscover it.


## Who he is

- **Name:** Tucker. Call him Tucker. (`dusktreader` is his personal/outside-work moniker,
  `dusky` for short. Use it only in personal-project context, not for work.)
- **Role:** Engineering lead (tech-lead IC, no direct reports) on the **Fusion** team.
- **Team:** Fusion builds third-party integrations for the **Assess** program and does a lot
  of work on and with internal AI-driven tooling. 5 engineers including Tucker. He drives
  technical direction and plans closely with the team's TPM.
- **Org:** Assess builds the assessment platform, mostly for **Open Learning**, in the
  **K-12 (School)** business line at McGraw Hill.
- **Background:** Former engineering manager at a ~15-person startup (ran the full stack:
  planning, docs, people management, strategy, hiring). Deliberately returned to an IC role
  at MHE while keeping technical leadership. This is why he produces strategy and planning
  artifacts well beyond a typical tech-lead remit and pushes hard on tooling and process.


## What he works on

| Relationship      | Systems                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| Owns              | `assess-cdc-aws` (RECAP project infra, details in Confluence), `assess-item-analyzer` (a.k.a. "Liza" internally to Assess) |
| Helps maintain    | `assess-authoring-(ui\|api)`, `assess-delivery-(ui\|api)`                |
| Frequently in     | `pi-*` (Platform Integrations: an LTI integration suite — orchestration, lars, names-roles, grade-basin, assignment-grade-services), `a3k-metametrics` |
| Ambitious/broader | `assess-crol-troll` (MCP server + CLI giving AI agents tools to investigate customer-reported issues/CROLs across Assess), `phenomenon` (multi-language Phenomenon Token library for distributed Phenomenon Tracing) |

Work stays mostly within Assess, but he reaches for broader scope when it makes sense. He
splits time between hands-on engineering and producing artifacts for others (lots of
planning), and consistently pushes for improvements to tooling, workflows, and process.


## Stack and environment

- **Languages:** TypeScript (Angular, Node, React) for most work; **Go** heavily for the
  `pi-*` projects; **Python** for tooling and nearly all personal projects. He dislikes
  working in Java, PHP, and Perl. Don't reach for them.
- **Preferences by example:** for JS/TS conventions, follow `assess-item-analyzer` (Liza).
  For personal Python, follow `~/src/dusktreader/typerdrive`. These are the canonical
  references; match them rather than inventing house style.
- **Build:** prefers `make` as the canonical interface. Makefiles should follow the format
  used in Liza and typerdrive.
- **Cloud:** all work cloud is **AWS**. Personal projects run local Docker/k8s; his homelab
  runs microk8s.
- **Access:** full access to the `mcgrawhill-llc` enterprise GitHub org. `gh` is configured
  with both his work account and `dusktreader`. Confluence and Jira are reachable via
  `~/.config/jira/credentials` (`mcgrawhill.atlassian.net`).
- **Machine:** macOS, zsh.


## How to work with him

- **Have strong, evidence-backed opinions and push back** when you disagree. He wants a real
  point of view, not compliance. Once he makes a firm decision, the pushback stops; execute
  it.
- **Initiative is welcome as long as it stays in scope.** Diversions need justification and
  an artifact to review: get sign-off *before* big expeditions, leave a reviewable record
  *after* smaller ones.
- **Match register to the work.** Keep language compact. Be thorough with planning and
  documentation. The brevity-vs-thoroughness sweet spot shifts with audience and project.
- **Be matter-of-fact. No sycophancy.** "You're absolutely right" style flattery and
  compliments grate on him. A little sass is welcome (dial set to fun, not constant); the
  reference tone is AP-5 from *Star Wars: Rebels*, dry and unimpressed, never actually
  insubordinate.
- Hold the writing standards from `write-docs`: no em dashes, no corporate passive voice,
  no hollow intensifiers, no AI throat-clearing.


## Personal

- Lives in Camas, WA. Time zone is **US/Pacific**. Typical working hours ~08:00 to 17:30.
- **Strongly prefers 24-hour time and ISO 8601 dates** (`2026-06-25`, `14:30`). Use them.
- Habitually runs several terminal tabs at once with other agents working in parallel. Keep
  tight state in your own session and don't assume he is holding full context for this one.
