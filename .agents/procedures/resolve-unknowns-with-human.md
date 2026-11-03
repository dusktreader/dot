# Resolve Unknowns With Human Procedure

Resolve answerable Unknowns in a planning artifact by obtaining human decisions and updating the artifact with their
outcomes.


## Required inputs

The caller must provide:

- Path to the artifact containing Unknowns
- Artifact type, including task plan or implementation plan, and the decision context
- Current workflow state and the state to resume after resolution
- Any constraints on editing or approval state

If the artifact path, decision context, or resume state is unclear, ask the caller before proceeding.


## Resolution protocol

1. Read the artifact and identify all unresolved Unknowns. Do not edit the plan or other source artifact. Create a
   temporary status list for this procedure only: rewrite each Unknown as a short sentence under 80 characters and
   prefix already-resolved items with `SOLVED`. Do not save this shortened list into the source artifact.
2. Present the complete status list, then give the first unresolved Unknown in as much detail as needed to answer it. Do
   not expand the other unresolved Unknowns yet.
3. Wait for the human's answer to the current Unknown. Ask focused follow-up questions if the answer is ambiguous; do
   not infer an answer. Silence, unrelated responses, and approval of another artifact are not resolution.
4. Record the answer in the source artifact only as authorized by the caller. Mark the item `SOLVED` in the temporary
   status list, present the updated list, then present the next unresolved Unknown in detail. Repeat until all are
   resolved.
5. Once all Unknowns are resolved, present the full status list with every item prefixed `SOLVED`. Tell the human the
   Unknowns are resolved and request explicit approval to move to the caller's named next state. Do not advance without
   that approval.
6. Return control to the caller at the supplied resume state with the artifact path, resolved decisions, and approval
   evidence. Do not commit, publish, or perform later workflow stages.

The short status list exists only in this procedure's user-facing updates; never replace or rewrite the source plan with
it. The caller owns plan edits and determines whether material answers require agent review or another gate to be
repeated.
