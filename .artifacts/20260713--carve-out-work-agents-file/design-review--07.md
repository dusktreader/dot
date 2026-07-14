# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 07**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0


## Prior Review Resolution

- **All prior findings** ✓: Iteration 06 closed with zero findings and an approval. No open items carry
  forward.


## Findings

### Summary

| Finding | Title | Outcome |
| ------- | ----- | ------- |

No findings.


## Notes

**Scope of this review.** This iteration reviews only the newly added `creds set` contract: AC27
(`dt creds set <key> <value>`), AC28 (`wdt creds set <key> <value>`), and all corresponding additions to the
Architecture section, Testing and validation strategy, Migration inventory, Rollout, Risks and decisions,
Technical Notes, and Unknowns. Previously approved content (AC01–AC26) is treated as locked.

**Nested credentials-only mutation is correctly specified.** AC27 states that `creds set` writes `<value>`
"to the personal credential named `<key>` in `dt`'s nested credentials sub-model (see AC17) and only that
sub-model." AC28 mirrors this for the work store. The Architecture — Credentials model subsection repeats the
constraint verbatim: "`creds set` is scoped to the credentials sub-model — it cannot address top-level or
arbitrary settings fields." The requirement is stated at design level without naming classes or fields.

**Unknown-key safety and no-mutation guarantee are fully stated.** AC27 explicitly enumerates the three
failure cases — an unknown credential name, a valid top-level settings field, and a dotted path outside the
credentials sub-model — and requires all three to exit non-zero with a diagnostic on stderr and "leave
settings on disk completely unchanged." AC28 cross-references the same failure mode by name. The Architecture
and Technical Notes sections both repeat "no on-disk mutation" for the failure path. The Testing section
requires a byte-identical settings-file check for each failure case, which makes the requirement testable.

**No value echo is correctly required throughout.** AC27 prohibits echoing `<value>` "or any derived form of
it" to stdout or stderr on success; AC28 inherits the same constraint via explicit cross-reference. AC23
requires documentation of this non-echo guarantee. The Goal paragraph and Risks section both acknowledge the
asymmetry between `creds fetch` (prints the value, accepted risk) and `creds set` (never echoes, no new
risk). The Testing section requires tests to confirm "successful invocations neither print the written value
nor any derived form of it to stdout or stderr." The requirement is fully traceable from AC through
architecture to test.

**Personal/work isolation is maintained.** AC27 scopes `dt creds set` to `dt`'s store only. AC28 scopes
`wdt creds set` to `wdt`'s store only and explicitly states "the work and personal stores remain fully
separate — `wdt creds set` cannot write into the personal store and `dt creds set` cannot write into the work
store." The Testing section adds a cross-store mutation test: "`dt creds set` never mutates `wdt`'s settings
file and vice versa." This mirrors the isolation language already established for `creds fetch` in AC16 and
AC19.

**Settings `bind` boundary is preserved.** AC27 closes with: "`creds set` is the safe individual-credential
companion to interactive/manual configuration after `configure` emits missing-credential notices; it is not a
substitute for `settings bind`, which remains the batch migration mechanism (see AC24)." The same sentence
appears in the Architecture — Credentials model subsection and the Rollout section. The Migration inventory
table and Technical Notes both list `creds set` alongside `settings bind` with the individual/batch
distinction intact and consistent.

**Agent guidance boundary is correctly drawn.** AC26 states that agent guidance "does not, by default,
instruct agents to configure or set credentials (via `creds set`, `settings bind`, or otherwise)" and that
"no new agent-facing guidance is added purely to expose the `creds set` surface." AC27 and AC28 do not
introduce any agent-facing guidance. The Testing section's manual acceptance steps for `creds set` are
operator tasks, not agent instructions. The boundary is consistent with the rest of the credential
section.

**Test coverage is adequate.** The Testing and validation strategy section lists targeted unit tests for
`creds set` covering: (1) a known key updates only the nested credentials sub-model and leaves remaining
settings byte-identical; (2) unknown key, top-level settings field, and out-of-sub-model dotted path each
exit non-zero with a stderr diagnostic and leave the settings file byte-identical; (3) no value or derived
form appears on stdout or stderr on success; and (4) cross-store isolation. Manual acceptance adds an
end-to-end spot-check: set a known credential, verify via `creds fetch`, confirm no terminal echo, then
attempt an unknown key and confirm non-zero exit with no visible settings change. Coverage maps cleanly onto
every behavioral claim in AC27–AC28.

**No invented Typerdrive APIs.** AC27 and AC28 describe `creds set` as an "application-owned sub-command"
that "reaches into each CLI's own settings model." The Architecture — Credentials model subsection explicitly
states "Neither the `fetch` nor `set` operation is a Typerdrive built-in" and that "this plan makes no claim
about a Typerdrive-provided credentials facility." The Risks section and Technical Notes both repeat that the
precise Typerdrive mechanism for nested sub-model access is deferred to implementation planning. No new
Typerdrive API surface is assumed.

**No markdown violations detected.** Line lengths are within 120 characters throughout the new content.
Headings use sentence case and correct hierarchy. Lists use `-`. No fenced code blocks are present. Separator
bars are used correctly between AC groups. Two blank lines precede all headings that follow content, except
those following separator bars (one blank line, per style guide). No bold quasi-headings stand in for
multi-sentence subsections.

**Plan is approved.** All focused review criteria for the newly added `creds set` contract are met. No prior
findings remain open, and no new findings were identified. Implementation planning may proceed.
