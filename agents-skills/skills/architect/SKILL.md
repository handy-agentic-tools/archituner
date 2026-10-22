---
name: architect
description: Designs, roasts, maintains and validates a project's architecture contract - the ARCHITECTURE.md stating the ideal target shape as a layer + dependency block plus prose. Use to write, scaffold, draft, extract or map one, to ask whether a layering is the right carve, to roast an existing one, to rule on a boundary question while code is being written, or to check whether a codebase still obeys it: drift and erosion reports, boundary violations, pre-merge boundary review. Reach for it even when the user names no file - "kam patrí tento súbor", "where does this belong", "can this layer import that one", "are there circular imports", "tento kód je bordel, aká je správna štruktúra", "is this allowed". The contract is what code is judged against and is never lowered to match the code; syncing README, spec or plan to moved code is another skill's. Not DESIGN.md, which design-md-creator owns, not AGENTS.md, and it never edits code - ranking its work units and logging a ruling are other skills'.
---

# architect

**Read the `architecture-md` skill before any work below, rather than reconstructing the format from memory.** Its own opening points at the format file, whose Contents line names every section it covers.

**Keep `architecture-md` the only home of the format.** A second copy drifts from the first, and nothing tells a reader which of the two they are holding.

**Say so at the point of restating, wherever a subagent brief must restate part of it.** A brief handed no skill directory cannot reach the format file at all.

**Inline a formula or a glob shape, never a body of rules.** That bound is what keeps the exception above from legalising the drift the rule above it prevents.

**Write the contract and the reports, never application code.** Procedure 4 proves violations and carves them into work units; whoever picks a unit up writes the fix.

## What the file asserts, and how much say the tree gets in it

**Write the architecture the product should have, as a prescription.** The file states the shape the code is *meant* to have; `architecture-md` §4 states that rule and what it costs.

**Never derive a rule by asking what makes today's code legal.** §4 judges laundering by the order of reasoning, so transcribing a decomposition the user already decided is a different act from reverse-engineering one to make existing files qualify.

**Give the existing state a vote only where it has *proven* something.** Best practice and the product's problem decide the shape.

Working assumption, unmeasured: whatever is read first becomes the template, and the tree is the largest thing in context. What would settle it - drafting one repo's decomposition tree-first and docs-first, then comparing the two.

One Markdown file stating that prescription to AI coding agents. Which half wins when the block and the prose disagree is `architecture-md` §1 and §2's question, not this file's.

## Which procedure, and which mode

Four procedures. This table takes the request's wording plus the state of the file to one of them.

| Wording | File state | Procedure |
|---|---|---|
| "make / scaffold / generate / draft an ARCHITECTURE.md", "capture our layering into one", "extract the architecture" | missing or empty | 1 Design |
| the same | a non-empty file exists | 2 Roast, unless the user confirms a replacement |
| "review / lint / check / fix / roast my ARCHITECTURE.md", "is this layering the right carve" | a non-empty file exists | 2 Roast |
| the same | missing or empty | 1 Design, after saying no file was found |
| "may this layer import that one", "where does this new thing live", an implementer blocked on a case the contract does not settle | a non-empty file exists | 3 Maintain |
| "does the code still follow our architecture", "audit / verify the codebase", "drift or erosion report", "boundary violations before merge", "what work brings the code back in line" | a non-empty file exists | 4 Validate |
| the same | missing or empty | 1 Design, after saying there is nothing to audit against |
| ambiguous | missing or empty | 1 Design |
| ambiguous | a non-empty file exists | 2 Roast |

This one takes procedure 1 to one of its three modes.

| Where the decomposition comes from | Mode | Its own steps |
|---|---|---|
| best practice for this class of product and the product docs; the tree gets no vote | design autocrat | `architecture-autocrat` |
| a docs-first draft, reconciled against the tree with the burden of proof on the existing state | design democrat | `architecture-democrat` |
| an architecture the user has already decided, read out of the tree that implements it | design cartograph | `architecture-cartograph` |

**Read the repo's operational doc - AGENTS.md or CLAUDE.md - for a recorded mode on your own axis, before asking for one.** Design and maintain are two independent picks that share a vocabulary, so a bare `autocrat` names neither and a record must read `design: autocrat` or `maintain: autocrat`.

**Treat a recorded mode on your own axis as the user's standing answer.** Asking again every run is how one project ends up governed by two modes at once.

**Let the user pick the mode where none is recorded, in procedure 1 and procedure 3 alike.** A mode decides how much the tree and the implementers are allowed to settle - a call about the project, not about the task in hand.

**Never infer a mode from the file state.** What the file looks like today is the output of whichever mode last ran, so reading a mode out of it just re-runs that one.

**Record the pick as its own entry naming its axis, the moment it is made - a mode changed mid-run included.** One entry for both axes lets a maintain pick overwrite a design pick, and the next run reads a mode its own table does not list.

**Keep one home for both entries where AGENTS.md and CLAUDE.md both exist.** One states them and the other links to it, so the read above finds one answer rather than two.

This one takes procedure 3 to one of its two modes.

| Mode | Who may propose a solution | Its own channel |
|---|---|---|
| maintain autocrat · propose this one first | nobody - the architect reads no code and only rules, while implementers ask questions and report defects | `architecture-autocrat` |
| maintain democrat | the implementer proposes and the architect weighs it against the contract | `architecture-democrat` |

**Propose maintain autocrat first.** Its democrat has the architect weighing an implementer's reasoning about code, which is worth reading only from implementers who know what they are doing.

## Which artifact each procedure produces

| Procedure | Deliverable |
|---|---|
| 1 Design | a format-valid `ARCHITECTURE.md` - or the file plus the findings the author declined - and the pair arithmetic `architecture-md` §1 defines, so an incomplete matrix is visible at handoff rather than at the next audit |
| 2 Roast | the merged findings report |
| 3 Maintain | one ruling per question, plus the ARCHITECTURE.md edit; the decision-log entry is the owner's alone, on their explicit go-ahead |
| 4 Validate | the audit report, and the disjoint work units its findings carve into |

## 1 Design - the steps every mode shares

**Read the mode's own reference file first.** It carries every step above these four, all of them settled before the coverage questions are walked.

1. **Walk every coverage question in `architecture-md` §2 with the user, plus which dependencies are *forbidden* and *why*.** The code answers none of these, and nobody volunteers them - to whoever built the system they are too obvious to say out loud.
2. **Settle each layer whole before moving to the next: its block entry, its `## Layers` row, and its relation to every other layer.** §1 ties the glob to the `Paths` cell and §2 ties the Responsibility cell to the block, so none of the three settles alone.
3. **Assemble the rest of the body per `architecture-md`, stating a reason for every deviation from the best-practice shape for this class of product.** `architecture-md` §4 says which cell that reason goes in, whatever pulled the design away from that shape.
4. **Run procedure 2 on the output.** A design nobody roasted is a draft.

## 2 Roast - who reviews the design, and on what brief

**Read the `architecture-audit` skill before the first spawn.** It carries the merge, the declines, the offer to apply, the re-spawn and the exit condition, plus the fallback where no subagent is available.

**Spawn two reviewers as two agents, never one agent running both lenses.** The two lenses are SHAPE and MECHANICS.

**Pin the two reviewer spawns to `agent-tier: standard`.** A reviewer reads and judges; [tiers.yaml](../../tiers.yaml) owns what the tier resolves to per provider, so no provider's model is named here.

**Hand each lens `architecture-autocrat`'s reviewer brief, its lens name, the ARCHITECTURE.md path and the repo root.** The brief reaches the invocation home `architect-cli` and the format skill `architecture-md` by name.

Working assumption, unmeasured: one reader holding both checklists finds whichever class it looked for first. What would settle it - running the lenses single-agent and two-agent over one file, then comparing the findings.

**Say in the report wherever the review ran degraded, and what that costs the finding set.** The mechanical run being unavailable and the lenses sharing one agent are two cases of it, not the only two.

## 3 Maintain - how an implementer's question becomes a ruling

The channel between the architect who owns the contract and the implementers writing code against it. An implementer hits a case the contract does not settle - may this layer import that one, where does this new thing live - and the architect rules.

**Read the chosen mode's own channel file before ruling on anything.** It carries what may enter the channel and what the architect may open, neither of which this section states.

**Bounce a question whose answer the file already carries, in either mode.** Stated outright or reached by inverting a rule that is - either way the contract answered it first, and answering makes the architect a lookup for a file the asker holds.

**Require of every question that it say what the asker read and quote the contradiction or the hole.** Nothing else separates a gap in the contract from a gap in the reading, and the architect's only other way to tell is to redo that reading.

**Treat an admitted question as a claim about the contract, never as a mandate to edit it.** The asker is claiming that two rules collide or that none covers the case, and a claim is tested rather than conceded.

**Let that test decide whether the file changes, never the question's arrival.** A surviving claim names a collision or a hole the file carries, and both owe an edit; the entry is the owner's alone, on their explicit go-ahead; one that fails means the file settled it already.

**Treat a case you had to reason your way to as a change, not as something the file carried.** That reasoning is what the file lacks, and calling it a reading leaves the file as unable to settle the next instance as it was before.

**Edit nothing and log nothing on a failed claim.** The file already said it, so an edit would restate a rule it carries and an entry would record a question in a log that holds decisions.

**Put all five statements below in every ruling, whichever mode produced it.** The implementer is blocked while it is written, so a ruling needing a follow-up round trip costs more than the question it answered.

- [ ] **The rule, stated so it places every later file of this kind** - one naming only the file at hand is a diff wearing prose, and the next file of that kind asks again.
- [ ] **The layer or boundary it follows from** - without it the implementer cannot tell a ruling from a preference, nor carry it to a case that shifts slightly.
- [ ] **Where the work the rule displaces now lives** - `architecture-md` §2 has what a boundary with no destination costs; here it costs the implementer a second stop at the same point.
- [ ] **Whether the contract changed** - it decides whether the implementer re-reads `ARCHITECTURE.md` before resuming, or simply resumes.
- [ ] **Which adjacent case the ruling does not reach** - said plainly, so the next one arrives as a question rather than as an extrapolation.

1. **Take one question at a time, and answer the one asked.** An implementer blocked on a boundary is blocked now, and a bundled answer to four arrives after three of them were guessed.
2. **Rule from the contract and the product, never from the branch that raised the question.** Deciding a case by what its code already does is `architecture-md` §4's laundering with a second person holding the pen.
3. **Write a ruling that changes the contract into ARCHITECTURE.md.** A ruling living only in the thread binds the one agent that heard it; it enters the file as its own rule, carrying no link out - not to the question, the issue or the log (`architecture-md` §4).
4. **Send back the rule and its reason, never the diff.** A rule naming the layer and the reason places every later file of that kind; a diff places one, and the implementer owns the code.
5. **Hand the ruling and the alternatives it rejected to the decision log's owner, and write no entry.** An entry is the owner's alone, written on their explicit go-ahead; the rule above already exempts a failed claim from both.

## 4 Validate - what checks the code, and in what order

Drift is the expected output, and a clean run is the unusual result.

**Read every violation as evidence about the code, never as a defect in the contract - except the ones step 5 pulls.** A rule that looks wrong goes to procedure 3 as a question.

**Never widen a glob or drop an edge because something crossed it.** `architecture-md` §4 names that move and refuses it; taken here it turns a finding into a rule and makes the misplacement permanent.

**Read the `architect-cli` skill before step 1.** Its own opening points at the reference file, whose Contents line names every section it covers, and they bite from the scan onward rather than only at the semantic pass.

Each `crossings` entry in the document the tool prints is one import that crossed a declared pair, carrying `file`, `line`, `module`, both layer names as `source` and `target`, the pair's `kind` and `state`, and `code` - the import statement's own line of source.

1. **Locate `ARCHITECTURE.md`.** No file → stop and route to procedure 1, because there is nothing to audit against. The contract governs its own directory, so where the file is decides what tree it reads - there is no root to confirm.
2. **Run the tool.**
   ```bash
   python3 -m archituner <path>/ARCHITECTURE.md --json
   ```
   The invocation's one home is `architect-cli`; this step and `architecture-autocrat`'s `agents/reviewer.md` restate it, and every site carries the note. Every outcome is one document carrying `status`, and the exit is the status's own - ok 0, divergent 1, rejected 2, failed_run 3; the document's shape is the key table `architect-cli`'s reference opens with.
3. **Stop on a refusal (exit 2) and route to procedure 2.** The document's `reason` names the structural defect, so no rule was read at all - there is nothing to audit against and no section of this report takes a defect in the block. Procedure 2 is where a block is graded and fixed.
4. **Read a failed run (exit 3, its `reason` ``failed run: N file(s) walked, none claimed by any layer``) through `architect-cli`'s partition.** The walked count separates a tree with nothing to claim from one whose globs claim nothing it holds; both are the contract and the tree disagreeing about homes.
5. **Pull every `crossings` entry failing `architect-cli`'s manufactured-crossing test, before any of them reaches `FAIL`.** A crossing failing it is a defect in the globs, not in the code.
6. **Report every pulled crossing under `BLOCK DEFECTS`, naming the glob that claimed it.** The template below defines that section and every other one. Editing the block here would leave the later steps merging a document computed against globs that no longer exist.
7. **Spawn a `general-purpose` subagent on `architecture-audit`'s semantic pass prompt, handing it the ARCHITECTURE.md path, the repo root and the tool's JSON document.** Every finding it returns is a `WARN` - a judgement that may be a false positive.
8. **Merge the surviving `FAIL` set and the `WARN` set into one finding set.** A `FAIL` wins wherever the semantic pass names something the document already proved, and the duplicate `WARN` is dropped.
9. **Carve that set into units by the file set each touches, never by severity.** A lane is a set of files no other lane holds, and two sharing a file collide at merge. Block defects are contract edits and `architect-cli` routes them elsewhere.

**Pin the semantic pass to `agent-tier: standard` as well.** The pass reads and judges like a reviewer does, and the same matrix owns the resolution.

A source file no layer glob claims is a first-class finding, and it belongs to the semantic pass - the tool can form no crossing on an unclaimed file, so none of its traffic reaches the document.

## What the roast report and the audit report must each contain

**Rank both reports worst first.** A reader acts on the first item either way, so any other order picks that item for them.

Procedure 2's merged findings report: one entry per finding, carrying the five fields `architecture-autocrat`'s reviewer brief requires and graded on `architecture-md` §3's `Error` / `Warning` / `Not a rule`, with every earlier decline carried onto the finding it closes.

Procedure 4's audit report, always this structure, `FAIL` before `WARN`, so the reader sees proofs first and guesses second:

```
# Architecture audit: <repo>

## FAIL - mechanically proven (N)
Divergences the tool's document carries and step 5 did not pull. High confidence.
- path/to/file.py:42  web -> domain   `import { User } from '../models/user'`
  why forbidden: <reason from ARCHITECTURE.md Boundaries, if present>

## BLOCK DEFECTS - crossings step 5 pulled (P)
Globs claiming files the `## Layers` table would not assign that layer. Each is a defect in the
contract, not drift in the code, and the tool reports it as proven on every run until the glob
changes. These carve into no work unit - they go to procedure 1 or 2, where the contract is edited.
- app/**   drew the crossing at app/models/lead.py:1 into this layer; the layer's Paths cell is
  app/models, so this glob claims three sibling layers' files as well

## WARN - semantic judgement (M)
Soft drift a reviewer flagged. Verify each - may be a false positive.
- <file>:<line>  <category>: <one-line what's wrong>  (invariant/boundary: <which stated rule>)  [confidence: high|med|low]
  why: <one sentence - what intent this breaks and how>

## UNCLAIMED - outside every layer's home (K of T source files)
Drift against a target-state contract. The tool can form no crossing on any of it, so it proves
nothing about their imports either.
- <file>   suggests: <layer>   why: <one sentence from its contents, not its path>

## UNITS - what this carves into
- U1 · <short name>
  restores: <rule, quoted from ARCHITECTURE.md>
  files:    <the lane - disjoint from every other unit>
  shape:    <what the corrected structure looks like>
  may not:  <the boundary the fix may not cross>
  gate:     <what re-running procedure 4 must show>

## Scan coverage
- pair states: convergence <c>  divergence <d>  absence <a>  silence <s> - quoted from the
  document's `counts`; an absence or a silence pair holds no witness, so it proves nothing
  about the code either way
- crossings: the document's <N> entries - one per witness, where `counts` is one per pair -
  <P> of the divergence crossings pulled at step 5, so `FAIL` above is the divergence
  crossings minus <P>
- what the tool cannot see: non-Python source, anything the tree's `.gitignore` hides, dynamic
  imports (`importlib`, `__import__`, string-built paths) - the semantic pass and the UNCLAIMED
  list are the only coverage over those
- areas the semantic pass did / did not read
```

**Keep the WARN and UNCLAIMED rows identical to the ones `architecture-audit` requires the pass to emit; both sites carry the note.** The pass writes them and this template only receives them, so a field added on one side and not the other is dropped at the merge.

**Take both UNCLAIMED numbers from the semantic pass's closing count, never from the tool.** That count already subtracts what `## Enforcement` declares out of scope, and the tool walks Python only where the pass covers every text source file.

**Report coverage beside every count.** A `FAIL` count on its own invites the misreading that a low number means health, while the mechanical pass gets blinder as drift grows.

**Quote the counts the document carries rather than recomputing any of them.** A recomputed count is a second call site for a number the tool owns, and `architecture-md` §1 says what the counts do not mean.

**Never merge the two categories.** A `FAIL` that survived step 5 is defensible against pushback, and a `WARN` is a lead.

**Say plainly wherever the mechanical layer could not run.** Leaning on the semantic pass instead implies a coverage nobody achieved.

## Which reference file covers what

| File | Covers |
|---|---|
| `architecture-md` | the format, and the only home of it - its own skill, not a file here |
| `architecture-autocrat` | the autocrat's three files - procedure 1's design mode with the tree given no vote, procedure 3's channel where the architect reads no code, and procedure 2's reviewer brief - its own skill, not files here |
| `architecture-democrat` | procedure 1's democrat mode - the docs-first draft, and the reconciliation that puts the burden of proof on the existing state |
| `architecture-cartograph` | procedure 1's cartograph mode - reading a decomposition the user has already decided out of the tree that implements it - its own skill, not a file here |
| `architecture-audit` | procedure 2's loop - the merge, the declines, the offer to apply, the re-spawn and the exit - plus procedure 4's semantic subagent prompt; its own skill, not files here |
| `architecture-democrat` | procedure 3's other channel, where implementers propose and the architect weighs |
| `architect-cli` | procedure 4's detail - the document's shape, the manufactured-crossing test, the per-area fan-out, the fields each unit carries, and what the coverage numbers are worth - its own skill, not a file here |
