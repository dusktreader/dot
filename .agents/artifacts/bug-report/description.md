# Bug Report

A structured account of a confirmed bug: what is wrong, how to reproduce it, what causes it,
what it affects, and how to fix it. Produced at the end of bug investigation, before planning
begins.


## Template Variables

| Variable  | Description                                              |
| --------- | -------------------------------------------------------- |
| `title`   | Short descriptive title for the bug                      |


## Sections


### Description

Observed behavior versus expected behavior. Specific about what is wrong and under what
conditions it occurs.


### Reproduction Steps

A numbered list of steps sufficient to reproduce the bug consistently. Includes enough detail
that someone unfamiliar with the system can follow them.


### Root Cause

What causes the bug, based on investigation findings. Includes `file:line` references for
every element. Each element is labeled as confirmed (directly observed in the code) or
inferred (a conclusion drawn from observations).


### Blast Radius

A bulleted list of affected components, behaviors, or downstream systems. One bullet per
affected area. Helps the planner understand the scope of the fix.


### Proposed Approach

A high-level description of how to fix the bug — enough for a planner to begin. Not an
implementation plan. May include constraints or risks worth noting.


### Unknowns

Anything unresolved from the investigation that the planner needs to address. Omit this
section if there are none.
