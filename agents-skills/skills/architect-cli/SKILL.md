---
name: architect-cli
description: Runs the architect tool against an ARCHITECTURE.md and reads what it prints - the --json document, the --check gate, the --report reading, the --baseline comparison. Load it whenever a line names python3 -m archituner: wiring the tool into CI, running a ready gate, asking what an exit means or what a key holds - "čo vypísal architect". The contract format is architecture-md's, the HTML page architecture-ui's; this skill owns the invocation and the reading.
---

# architect-cli

## What this skill owns

**Read `references/validate.md` before reading anything the tool prints, rather than reconstructing the document's shape from memory.** Its Contents line names every section it covers.

**Keep this skill the one home of the invocation and the reading.** A second home drifts from the first, and nothing tells a reader which of the two they are holding.

`python3 -m archituner` takes one argument, the contract file, and governs the tree that file's own directory sits in - so the path a command names settles what gets read, and there is no root to confirm.

The contract's format is `architecture-md`'s, and the audit procedure the tool serves is `architect`'s procedure 4. An implementer holding a work unit loads this skill to run the tool, and nothing else.

## Which flag, and what it prints

```bash
python3 -m archituner <path>/ARCHITECTURE.md --json
python3 -m archituner <path>/ARCHITECTURE.md --check
python3 -m archituner <path>/ARCHITECTURE.md --report
python3 -m archituner <path>/ARCHITECTURE.md --baseline
```

**Keep these spellings identical to the `--json` line `references/validate.md` opens with.** Two spellings of one command drift, and a reader comparing two runs is then reading answers to two different questions.

**Spell a mode flag, or none and read the check.** A bare `python3 -m archituner <path>/ARCHITECTURE.md` is the check gate - the same lines, the same exits, as `--check` - and the HTML page is drawn by a run `-o` names a file for, `architecture-ui`'s to spell and to read.

| Flag | What it prints | Exit |
|---|---|---|
| `--json` | one JSON document, on every outcome alike - the key table `references/validate.md` opens with names what it holds | the status's own: ok 0, divergent 1, rejected 2, failed_run 3 |
| `--check` | the divergences and the limit breaches, or `no divergence` on a clean run | 0 clean, 1 a divergence, a limit breach or a failed run, 2 a refusal |
| `--report` | the whole reading as lines a person reads - the counts, the findings, the limit breaches, the matrix, the divergences, the files | 0 ok, 1 a divergence, a limit breach or a failed run, 2 a refusal |
| `--report --format md` | the same reading as Markdown - `#` sections and a matrix table, colour off | the same exits as `--report` |
| `--baseline` | `baseline written: <path>`, having written the baseline file beside the contract | 0 written, 1 a failed run, 2 a refusal |

**Read the exit as the verdict and the text as its evidence.** The statuses carry their own subject in `reason`, so a refusal or a failed run names what went wrong before anything else is read.

## How a run is narrowed

`--check`, `--report` and `--json` alike take the four filters below; `--json` echoes them in its `filters` key, and `--report` names them in its `filters:` summary line.

| Filter | What it narrows |
|---|---|
| `--state s ...` | the pairs to the states named - `convergence`, `divergence`, `absence`, `silence` |
| `--layer l ...` | the pairs to those with both ends among the layers named |
| `--file p ...` | the crossings and the limit breaches to the files named, by exact path |
| `--min-weight n` | the pairs to those carried by n witnesses or more |

```bash
python3 -m archituner <path>/ARCHITECTURE.md --check --file <path> <path>
```

**Read a narrowed run's verdict over what survives the narrowing.** The status is computed on the pairs and breaches left, so a filter can quiet a divergence the unfiltered run states.

**Take any flag this file does not name from the tool's own `--help`, never from memory.** The usage line there owns the spellings, and the five spellings above are the ones a consumer reads.

## How the other skills reach this one

**Let `architect` own what the reading becomes.** Its procedure 4 loads this skill for the mechanical pass and decides what the document means - the audit report, the work units, the block defects. The judgement stays `architect`'s; the mechanical detail behind each - a unit's fields, the fan-out, the report template - lives in `references/validate.md`.

**Inline into a brief only the command and the exit map, marked secondhand at the point of restating.** A brief handed no skill directory cannot reach this skill at all, so its wording is all the reader gets.
