---
name: architecture-ui
description: Reads the HTML page a run of the architect tool draws with `-o` - the layers stack, the pair matrix and the coverage treemap, with its filters, search and the panel beside them. Use it on a question about archituner.html or what the page shows - "open the architecture page", "čo ukazuje stránka". A release 2 skill: it needs the page, which release 1 does not ship. Rendering the page is this skill's; the other runs and their exits are architect-cli's; the contract is architecture-md's.
---

# architecture-ui

## What this skill owns

**This skill is a release 2 skill: it reads the HTML page, which release 1 does not ship.** A reader holding release 1 has no page to open, and the answer to a question about one is that sentence, never a guess at a drawing that is not there.

**Read `references/page.md` before describing what the page shows, rather than reconstructing it from memory.** Its Contents line names every section it covers.

**Keep this skill the one home of the page's reading.** A second home drifts from the first, and nothing tells a reader which of the two they are holding.

The run's other modes - the check, the report, the JSON document - are `architect-cli`'s to invoke and to read, and the contract the page reads is `architecture-md`'s. This skill owns what the page draws, the run that draws it, and how it is read.

## How the page is produced

```bash
python3 -m archituner <path>/ARCHITECTURE.md -o <path>/out.html
```

**The page is written by a run `-o` names a file for - a mode of its own, spelled beside no other mode flag.** The run writes the page to that path, prints its own counts beside it, and exits 0 whatever the verdict: a drawing, not a gate.

**The narrowing flags - `--layer`, `--state`, `--file`, `--min-weight` - are accepted beside `-o` and change nothing: the page always draws the whole reading.**

A run naming no mode flag writes no page at all - it is the check gate, `architect-cli`'s to read.

A contract the tool refuses writes a rejection page to the same path and exits 2. `references/page.md` carries what that page says.

**Treat the block above as the one home of the render invocation.** `architect-cli` spells every other mode and leaves `-o` to this skill, so the spelling lives here and nowhere else.

## Which reference file covers what

| File | Covers |
|---|---|
| `references/page.md` | the shell every view stands on, the three views, the narrow page, the filters and the search, the panel beside the views, the payload as the page draws it, and the rejection page |
