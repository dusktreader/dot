# CLEAR prompt evaluator

Score a prompt against CLEAR, improve signal per token, and apply the approved rewrite. Use the canonical definitions in
`~/.agents/artifacts/clear-evaluation/description.md` and `~/.agents/artifacts/clear-evaluation/template.md.j2`.

Mnemonic: cap it, lose it, explain it, architect it, reuse it.


## Five dimensions

Score every dimension independently from 1 to 5. Do not average or round scores.

| Letter | Dimension    | Check                                               |
| ------ | ------------ | --------------------------------------------------- |
| C      | Constrain    | Is length, format, count, and scope bounded?       |
| L      | Lean         | Is filler, courtesy, hedging, and duplication removed? |
| E      | Explicit     | Are role, task, and success criteria concrete?     |
| A      | Architected  | Is the output structure or sequence specified?     |
| R      | Reusable     | Is the prompt parameterized and worth saving or sharing? |

Use this scale: 5 means fully applied with nothing to improve, 4 a minor gap, 3 a clear partial improvement, 2 barely
present, and 1 absent or counterproductive.


## Phase 1: Autonomous iteration

Read the prompt and initialize a human-readable Markdown ledger next to the temporary rewrite. For a file target, use
`$OPENCODE_TMPDIR/<original-filename>.ledger.md` beside `$OPENCODE_TMPDIR/<original-filename>`, where
`$OPENCODE_TMPDIR` is `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode`. For a prompt not sourced from a file,
use `$OPENCODE_TMPDIR/clear-evaluation-ledger.md` beside `$OPENCODE_TMPDIR/clear-evaluation-rewrite.md`. Do not modify
the original during this phase.

The ledger uses exactly one `## Iteration N` heading per autonomous iteration. Iteration 0 is the unchanged baseline. It
contains only its score table, `TOTAL: X/25`, and `STATUS: BASELINE`.
It has no rewrite fields. Its score table has exactly five rows.
All use `Prompt=original`, one each for C, L, E, A, and R.

Iterations 1 through 10 are the only autonomous iterations. Each has exactly ten score-table rows: five with
`Prompt=current` and five with `Prompt=rewrite`, one each for C, L, E, A, and R. Every table uses exactly the columns
`Prompt`, `Dimension`, `Score`, and `Rationale`.
Use the same dimension names, score fields, and rationale fields in every row. Do not add summary rows to these tables.

Each iteration 1 through 10 also records `CURRENT TOTAL: X/25`, `REWRITE TOTAL: Y/25`, `STATUS: Continue` or
`STATUS: Stop`, the weakest dimension and why it is the highest-leverage fix, whitespace-delimited token counts for both
prompts, `TOKEN CHANGE: rewrite tokens - current tokens`, `QUALITY CHANGE: rewrite total - current total`, and full
`text` fences for the current and rewritten prompts.

Use this deterministic loop:

1. Score the current prompt independently and compute its total.
2. Select the weakest dimension. Rewrite to improve it without dropping real signal, then count whitespace-delimited
   tokens for both prompts.
3. Score the rewrite independently, record the complete ten-row iteration, and calculate the token and quality changes.
4. If the rewrite is `25/25`, record `Stop`, then record the exact line `BEST: iteration N, score 25/25` and state that
   this is the selected rewrite for Phase 2. Set the final ledger status to
   `TERMINATED: perfect score after iteration N`.
5. If the rewrite is below `25/25` and the iteration is below 10, record `Continue` and use that rewrite as the next
   current prompt.
6. If iteration 10 is below `25/25`, record `Stop`, choose the highest-scoring rewrite from iterations 1 through 10,
   breaking ties in favor of the latest iteration, and record `BEST: iteration N, score X/25`. State that it is the
   selected rewrite for Phase 2, record the remaining gaps, and set the final ledger status to
   `TERMINATED: iteration budget exhausted at iteration 10`.

Do not stop for good-enough quality, an estimate that improvement is unlikely, a self-imposed ceiling, or token cost.
Only a perfect rewrite or iteration 10 can stop Phase 1. Phase 2 is blocked until the ledger contains one of the two
exact terminal statuses. The ledger is a working record, not a replacement for the final CLEAR output block. For a file
target, write each rewrite to the temporary rewrite path and keep the original unchanged until approval.


## Phase 2: Human review

Present the final CLEAR output block with the prompt label, score table and rationales, weakest letter, and full best
rewrite. Include the rewrite score, token and quality change, remaining gaps when applicable, and both temporary paths.
Use the existing CLEAR artifact format. Do not treat the ledger as the final output block.

Stop and wait for explicit human approval. For every requested post-Phase-1 change, append a ledger entry labelled
exactly `## Human revision N`. Compare the revision with the immediately preceding presented candidate.

For Human revision 1, that candidate is the Phase 1 selected rewrite.
Score all five dimensions for both candidates using the same `Dimension`, `Score`, and `Rationale` fields. Record
`PRECEDING TOTAL: X/25` and `REVISED TOTAL: Y/25`.
Calculate whitespace-delimited token counts for both and record `TOKEN CHANGE` and
`QUALITY CHANGE: revised total - preceding total`.
Include the full preceding and revised prompts in separate fenced `text` blocks. Human revisions do not consume the
autonomous iteration count or alter the terminal status.
Update the temporary rewrite and re-present the result for explicit approval. Do not proceed without approval.


## Phase 3: Apply on approval

After explicit approval, replace the original file with the approved temporary rewrite and remove the temporary rewrite
and ledger. If the prompt was not sourced from a file, output the approved rewrite directly. Preserve the final CLEAR
output block in the response.
