# Investigation Report

A structured answer to a specific investigation question about a codebase. Records what was
observed, what was inferred, and what conclusion can be drawn. Produced by an investigator
and returned to the caller — not written as a persistent file artifact in most workflows.


## Template Variables

| Variable  | Description                                              |
| --------- | -------------------------------------------------------- |
| `title`   | Short descriptive title for the investigation            |


## Sections


### Question

The investigation question, verbatim or faithfully restated in the investigator's own words.


### Findings

A collection of evidence gathered during investigation. Each item is prefixed with one of
two labels:

- **Observed** (`file:line`): something directly seen in the code. Every observed item
  includes a `file:line` citation.
- **Inferred**: a conclusion drawn from one or more observations. Does not require a
  citation but should reference the observations it is based on.

**Formatting**: use a flat bulleted list only when there are 5 or fewer items and each fits
on a single line. Otherwise use `### ` subsections — one per finding — with a descriptive
title of the form `Observed (file:line): brief summary` or `Inferred: brief summary`, and
the detail as a short paragraph.


### Conclusion

A single direct answer to the question. If the answer is uncertain, states the uncertainty
and explains why. If the question cannot be answered from the codebase alone, says so
explicitly rather than speculating.


### Open Questions

Anything that could not be determined from the codebase and why. Omit this section entirely
if there are none.
