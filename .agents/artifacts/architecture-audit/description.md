# Architecture Audit

A structured assessment of a codebase's architecture: what exists, what is working well,
where the problems are, and what should change. Produced from investigation findings
synthesized by an architect.


## Template Variables

| Variable  | Description                                              |
| --------- | -------------------------------------------------------- |
| `title`   | Short descriptive title for the audit scope              |


## Sections

### Scope

What was audited: the subsystem, layer, or full codebase. States the explicit boundaries
of the audit so readers know what is and is not covered.


### Investigation Summary

A brief account of what was explored during investigation: key files, modules, and patterns
examined. Not a findings list — just enough context for the assessment to stand alone without
having read the investigation artifacts.


### Current Architecture

A description of what currently exists: components, modules, patterns, data flows, external
dependencies. May include diagrams. Factual and neutral — this section describes, it does not
evaluate.


### Strengths

A bulleted list of things working well. One bullet per strength. Each bullet is a bold title
followed by a brief explanation.


### Problem Areas

One `### P{NN}: title` subsection per identified problem, numbered `P01`, `P02`, etc.

Each problem area contains:
- **Where**: the component, module, or file where the problem manifests
- **Observation**: what was found — specific and factual
- **Impact**: concrete consequences: maintainability, scalability, correctness, security, etc.
- **Severity**: Critical | Significant | Trivial


### Recommendations

One `### R{NN}: title` subsection per recommendation, numbered `R01`, `R02`, etc. A single
recommendation may address multiple problem areas.

Each recommendation contains:
- **Addresses**: the problem area IDs this recommendation resolves (e.g. P01, P03)
- **Recommendation**: what should change and why
- **Effort**: Low | Medium | High
- **Risk**: Low | Medium | High


### Unknowns

Ambiguities or questions that could not be resolved from the codebase alone. Omit this
section if there are none.
