# Architecture Audit: {{ Title }}


## Scope

{{ What was audited: subsystem, layer, or full codebase. Explicit boundaries of the audit. }}


## Investigation Summary

{{
  Brief account of what was explored: key files, modules, and patterns examined. Not a full findings
  list — just enough context for the assessment to stand alone.
}}


## Current Architecture

{{
  Description of what exists: components, modules, patterns, data flows, dependencies.
  Include diagrams where useful.
}}


## Strengths

<!-- One bullet per strength. -->

- **{{ Title }}**: {{ Explanation }}


## Problem Areas

<!-- One subsection per problem area. Number them P01, P02, ... -->

### P01: {{ Title }}

- **Where**: {{ Component, module, or file }}
- **Observation**: {{ What was found }}
- **Impact**: {{ Concrete consequences: maintainability, scalability, correctness, security, etc. }}
- **Severity**: Critical | Significant | Trivial


## Recommendations

<!-- One subsection per recommendation. Number them R01, R02, ...
     Each recommendation may address one or more problem areas. -->

### R01: {{ Title }}

- **Addresses**: {{ P01, P03, ... }}
- **Recommendation**: {{ What should change and why }}
- **Effort**: Low | Medium | High
- **Risk**: Low | Medium | High


## Unknowns

{{ Ambiguities or questions that could not be resolved from the codebase alone. Omit if none. }}
