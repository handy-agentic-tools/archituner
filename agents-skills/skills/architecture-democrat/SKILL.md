---
name: architecture-democrat
description: Shapes the architecture contract together with the team - a design mode where a docs-first draft is contested by the tree, burden of proof on the existing state, and a maintain mode where the implementer proposes and the architect weighs. Use it when the user asks for the team's say - 'shape it with the team', 'nech to tím navrhne' - or when the repo's record names design: democrat or maintain: democrat. The format is architecture-md's; procedures and every other mode are architect's.
---

# architecture-democrat

## What this skill owns

**Shape the architecture contract together with the team, at the two points that shape gets settled.** The design mode and the maintain channel are one call about how much say the team gets, and that call is this skill's one job.

Design: the contract is drafted docs-first and the tree contests the draft, the burden of proof on the existing state. Maintain: the implementer sends a proposed rule with the question, and the architect weighs it.

Both procedures - and the shared steps each mode plugs into - live in `architect`, which loads this skill for its democrat modes.

## How this skill reaches the format and the procedures

**Reach the format through the `architecture-md` skill, section number kept - `architecture-md` §4 - and never through a reconstruction from memory.** A name resolves to that skill wherever it is installed, and a reconstruction drifts as the stale instance.

**Take the procedure's shared steps from `architect`, and return the mode's output to them.** Design's four shared steps and maintain's five ruling statements hold in every mode of their procedure; each file below builds on them, never restating them.

**Route a request that names no democrat mode to `architect`.** Its tables take the request's wording and the file state to a procedure and a mode, and this skill picks up only the two rows that chose democrat.

## Which reference file covers which mode

| File | Covers |
|---|---|
| `references/design-democrat.md` | procedure 1's design mode - the docs-first draft, the contest the tree gives it, and the reconciliation that puts the burden of proof on the existing state |
| `references/maintain-democrat.md` | procedure 3's maintain channel - what a proposal must carry, how the architect weighs it, and what an accepted or rejected one is owed |

**Read the chosen mode's file before shaping anything in it.** Each carries every step of its own mode; this SKILL.md only routes.
