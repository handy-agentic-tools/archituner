# Procedure 4 - the detail behind its steps

Contents: the document the tool prints · splitting the semantic pass · what each coverage number is worth · the manufactured-crossing test · a unit's fields · which unit a shared file joins · ordering units · a report with no run · where the gate lives after.

## The document the tool prints

`python3 -m archituner <path>/ARCHITECTURE.md --json` prints one JSON document and nothing else, on every outcome, and the exit is the status's own: ok 0, divergent 1, rejected 2, failed_run 3.

Every key but `schema`, `crossings`, `status`, `reason` and `breaches` is the analysis itself, so the one document serves whatever reads the run. Keys print sorted, and two runs over one tree print the same bytes.

| Key | What it holds |
|---|---|
| `schema` | the document's version, `1`; a consumer gates its parse on it |
| `status` | the run's verdict - `ok`, `divergent`, `rejected` or `failed_run` - and the exit is its own: 0, 1, 2, 3 |
| `reason` | the sentence explaining the outcomes a reading never reached - a refusal's own reason, a failed run's walked count, `divergence`, `limit breach` or `divergence and limit breach` - or `null` where the counts already say it |
| `contract` | the contract file's name |
| `tree` | the analysed tree's own name |
| `baseline` | the baseline file's name |
| `order` | the layer names, in dependency order - every `allow` edge's source above its target |
| `layers` | one row per layer: its name, its globs, the paths it claims, its chain depth, the layers it uses and is used by, and the Responsibility and Rationale cells |
| `pairs` | one row per ordered pair: `source`, `target`, `kind`, `state`, the `reason` prose, the witnesses, both sides' file counts, the state the stored baseline held (`was`), and the `remedy` |
| `files` | every walked file: its path, its claiming layer or none, its module name, its imports with their targets, its importers, and its measured numbers - `size`, `defs`, `depth`, `cyclomatic`, `cognitive`, prose - beside the limits that judge them |
| `counts` | the four pair states: `convergence`, `divergence`, `absence`, `silence` |
| `coverage` | the walked tree as nested directories, each file under its claim, beside the claimed and unclaimed counts |
| `prose_percent` | the prose share of the claimed files' non-blank lines, one number over the whole tree |
| `surface` | the entry layer's public names, and what sibling trees name from this one |
| `shape` | fan-out and fan-in per layer, the longest path, and the permitted edges realised |
| `naming` | the block's naming rules, verbatim |
| `invariants` | the Invariants bullets |
| `enforcement` | the Enforcement prose |
| `findings` | every finding, each carrying its text and what produced it |
| `breaches` | the limit breaches, each carrying its file, the number and the value over the limit - enough alone to make a run `divergent` |
| `change` | the comparison against the stored baseline - improved, unchanged or regressed per pair, file and layer - or `null` with none stored |
| `regions` | the coverage tree as placed boxes - each region's `x`, `y`, `width` and `height` on a fixed canvas |
| `stack` | the layer stack's geometry - a node box per layer, and every drawn edge's arc endpoints |
| `crossings` | one entry per witness of every realised pair - convergence witnesses too, not only divergence - each carrying `file`, `line`, `module`, `source`, `target`, `kind`, `state` and `code`, the import statement's own line of source |

A run given filters carries them in a `filters` key, and narrows `crossings` and `files` to what survives them while `pairs` stays whole.

Every outcome is the document, a refusal and a failed run included: a refusal answers `rejected` at exit 2 and a failed run `failed_run` at exit 3, each with its sentence in `reason` and none of the reading's keys beside it - no measurement was made to carry.

## How to split the semantic pass across a big repo

**Split the semantic pass into one subagent per layer or area the moment a single reader cannot hold the repo.** One agent skimming everything reports whatever it opened first, and the areas it never reached leave no trace in its output.

**Hand every subagent the tool's whole JSON document, never the slice covering its own area.** That document is what stops a `WARN` duplicating a proven `FAIL`, and an import reaching out of the area is the case a trimmed document lets through.

**Give each unclaimed file to exactly one area's brief, or sweep them all in one extra subagent.** A file in two briefs comes back as two findings about one file; a file in none is the drift the whole pass exists to catch.

**Concatenate the two closing lines `architecture-audit` requires.** They are the only source for the report's `areas the semantic pass did / did not read`.

**Sum the unclaimed ratios rather than averaging them.** An average over areas hides which one was blind.

## What each coverage number is worth

**Read `counts` before the crossing list.** A low divergence count over a silent tree reads like health and means the opposite, and once that reading is in the reader's head the rest of the report argues against it.

| Number | What it is worth |
|---|---|
| `counts.divergence` | the forbidden pairs the tree realises - one number per pair, however many imports witness it; the witnesses are the `divergence`-state crossing entries, each with a file, a line and the `code` to edit |
| `counts.convergence` | the allowed pairs the tree realises; each is as checkable as a divergence, and the consumer filters by `state` rather than the tool pre-deciding |
| `counts.absence` and `counts.silence` | pairs holding no witness - allowed-but-unrealised and forbidden-but-unrealised. They prove nothing about the code: an import resolving to no walked file lands in these whatever the tree actually does |
| the length of `crossings` | the whole mechanically-proven set, both states alike |
| a layer with no walked file | its `layers` row in the document, holding an empty paths list - an empty layer's `allow` pairs read absence and its `forbid` pairs silence, so the row settles which layers are silent without matching the globs against the tree by hand |

**Report a clean mechanical run as "nothing the tool could prove", never as "provably clean".** The second phrasing claims a coverage the numbers above do not support, and it is the claim a reader carries into the next merge.

## The manufactured-crossing test - which reported crossings are the block's defect

**File a crossing as manufactured when the file it names is claimed by the target layer's glob only because that glob is wider than the layer's `Paths` cell.** Every crossing the tool carries names a real walked file - the witness holds `file`, `line` and the `code` line it sits on - so the manufacture lives in the claim, never in the import string: the channel that once took an import naming no file in the tree is gone with the tool that had it.

**Read the crossing's file against the `## Layers` table to decide.** A file the table would not assign that layer, reached only through a glob that sweeps past its home, is a defect in the glob; the crossing is that defect made visible, one entry on every run until the glob changes.

**Pull every such crossing out of `FAIL` before the count is taken, and report it under `BLOCK DEFECTS`.** Leaving it there hands an implementer a lane that removes a legal import, and the glob manufactures it again every run.

**Send that glob to procedure 1 or 2, and carve no unit for it.** The contract is edited under review there, and a unit whose lane is `ARCHITECTURE.md` has no gate this procedure can run.

## How to fill a unit's fields

| Field | What goes in it | Why that and nothing else |
|---|---|---|
| `restores` | the boundary or invariant, quoted from ARCHITECTURE.md | the contract justifies the unit, not the auditor |
| `files` | the lane, disjoint from every other unit's | an implementer takes a lane and merges it whole |
| `shape` | what the corrected structure looks like | the reasoning that produces the diff belongs to whoever writes it |
| `may not` | the boundary the fix may not cross | almost always "do not widen the contract to make this pass" |
| `gate` | re-run procedure 4: these findings gone, none new, the UNCLAIMED count no higher | a gate nobody can run is a wish |

**Carve no unit for anything the report's `BLOCK DEFECTS` section holds.** Those are contract edits, routed to procedure 1 or 2 by the rule above; units carry code findings, and every field of this table reads a rule the code broke.

**Quote the rule into `restores` verbatim.** A paraphrase is a second copy of the contract, and the implementer then fixes the code to the paraphrase rather than to the file.

**Carry nothing into a unit beyond those five fields.** An estimate, a severity, or a sketched patch reads as the architect having approved a fix nobody reviewed.

## Which unit a file belongs to when two findings share it

**Put two findings touching the same file into one unit, with both rules quoted in `restores`.** A unit may restore more than one rule; a file may not appear in more than one lane.

**Pull every file the fix has to edit into the lane, not only the file the finding names.** Moving a module rewrites its importers, and a lane naming one file hands the implementer a change that cannot compile.

**Throw away any grouping you reached for before the file sets: severity describes the evidence, a lane describes the work.** A lane holding every `FAIL` spans every layer the scan touched, which is a repo-wide branch nobody can take.

## How to order the units

**Order units smallest commitment first, and anything needing a decision last.** The unblocked work is then already moving while the one open question is answered, instead of the whole list waiting behind it.

**Map one unit to one brief and one branch where the repo has a worker-brief convention.** The lane was built to be exactly that: a file set no other lane holds.

## What the report becomes when the tool cannot run

**Partition the failure before clearing anything.** A refusal (exit 2, its reason in the document's `reason`) is a defect in the block; a failed run (exit 3, ``failed run: N file(s) walked, none claimed by any layer`` in its `reason`) is the contract and the tree disagreeing about homes.

**Read the reason for a refusal; it names its own subject.** That is what lets procedure 4's step 3 route on it without reading anything else.

**Read the failed run's walked count.** N = 0 is a walk that found nothing at all - a non-Python tree, or a `.gitignore` that hides everything; N above it is globs that claim nothing the tree holds, which `architecture-autocrat`'s failed-run section disposes of rather than this rule.

**Treat that second case as the contract working as intended where the homes are prescribed.** A prescription names homes the tree has yet to grow, so `architecture-autocrat`'s dispositions hold rather than this rule.

**Drop the FAIL and BLOCK DEFECTS sections when the tool cannot run at all, and keep every other one.** A refusal returns before any document is built, so both have no input and a zero in either reads as a measurement never taken.

**Keep `UNITS` on such a run above all.** The semantic findings are then the whole report, and without lanes nobody can pick any of it up.

**Fill `Scan coverage` from the failed run's walked count, and from nothing on a refusal.** A refusal prints no count, so say there that the tool never reached the tree.

**Tell the semantic subagent when there is no JSON document to deduplicate against.** Every edge it then finds returns as a judgement, so the report has to say that nothing in it is mechanically proven.

## Where the gate lives after the audit

**Wire the tool into CI once the first audit lands, failing the build on any nonzero exit: `python3 -m archituner <path>/ARCHITECTURE.md --check`.** Exit 1 is a divergence or a failed run and exit 2 a refusal, and that gate, not this on-demand audit, is where enforcement actually lives.

**Keep running the full procedure periodically even with the tool in CI.** CI proves edges; the unclaimed count, the responsibility leaks and every prose invariant stay invisible to it.
