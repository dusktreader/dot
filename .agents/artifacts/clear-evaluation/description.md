# CLEAR evaluation

A CLEAR evaluation scores a prompt against the five CLEAR dimensions and produces an improved rewrite.
Reference: "GitHub Copilot Token Optimization Deep Dive," Microsoft Reactor
(<youtube.com/watch?v=HcIbvwE39NE>). Related tooling: the CATES analyzer (<github.com/microsoft/cates>).


## Template variables

| Variable | Description                              |
| -------- | ---------------------------------------- |
| `label`  | Short label or first line of the prompt  |


## Sections

### Prompt header

The label or first line of the prompt being evaluated, used as the section heading.


### CLEAR score

The total score out of 25, reported as `N/25`.


### Score table

One row per CLEAR dimension — Constrain, Lean, Explicit, Architected, Reusable — each scored 1–5
with a one-line rationale. Score each dimension independently; do not average or round across
dimensions.

| Score | Meaning                                             |
| ----- | --------------------------------------------------- |
| 5     | Fully applied; nothing to improve on this dimension |
| 4     | Applied with a minor gap                            |
| 3     | Partially applied; a clear improvement is available |
| 2     | Barely present                                      |
| 1     | Absent, or the prompt does the opposite             |

Per-dimension checks:

- **Constrain**: Is length/format/count/scope bounded? (5 = fully bounded, 1 = open-ended)
- **Lean**: Is filler/courtesy/hedging/duplication removed? (5 = zero waste, 1 = mostly padding)
- **Explicit**: Are role, task, and success criteria all concrete? (5 = all three, 1 = none)
- **Architected**: Is an output structure/sequence specified? (5 = clear schema, 1 = none)
- **Reusable**: Is it parameterized and worth saving/sharing? (5 = drop-in reusable, 1 = one-off)


### Weakest letter

The single CLEAR dimension with the highest-leverage improvement available, and a brief explanation
of why it is the weakest.


### Rewrite

The improved prompt, ready to copy. Must raise the weak dimensions without dropping real signal.
Bigger is sometimes better when the added lines are structure, not fluff.


### Rewrite score

The score of the rewrite out of 25, compared to the original, with a one-line estimate of the
token and quality change.


## Worked example

Original prompt (scores ~8/25):

```text
Hi, when you get a chance, could you please take a look at the diff below and write up a nice
description for the pull request — something that explains what we're doing and why. Make it
readable but also comprehensive. Thanks so much! [diff]
```

Weakest letters: **Lean** (all courtesy/filler) and **Explicit** ("nice", "readable" are vague).

Rewrite (scores ~22/25):

```text
Role: senior reviewer. Task: write a PR description from the diff below. Output markdown in this
order: Summary, Changes, Risks. {{diff}}
```

Same information, ~60% fewer tokens, faster first token, and a bounded, reusable shape.
