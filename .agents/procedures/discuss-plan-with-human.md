# Discuss Plan With Human Procedure

Present a review-ready plan to the human, resolve feedback, and obtain explicit approval of an exact revision.


## Required inputs

The caller must provide:

- Path to the plan under review
- Plan type, including task plan or implementation plan, and review purpose
- Related agent review and blocker-check artifacts, when available
- Current workflow state and the state to resume after approval
- Constraints on changes, such as whether the plan is already immutable or approval is for a coordinated set
- Whether this gate concerns one plan or a coordinated set of plans

If any input is missing or ambiguous, ask the caller before presenting the plan.


## Review protocol

1. Present the plan path, concise summary, agent-review outcome, unresolved findings, and focused verification evidence.
2. Invite the human to review, ask questions, or request revisions. Do not treat questions, silence, `feedback
   complete`, or agent-review approval as approval.
3. If revisions are requested, update only the requested plan content, then return control to the caller to run required
   agent review before presenting the revised candidate again. The caller controls blocker-check placement according to
   the workflow.
4. Obtain explicit human approval of the exact plan revision or coordinated set. Record the approved revision or set
   membership and approval evidence for the caller.
5. Return control to the caller at the supplied resume state. Do not perform later workflow stages.

Do not commit, publish, or modify code as part of this procedure. Never imply the human approved a revision they have
not explicitly approved.
