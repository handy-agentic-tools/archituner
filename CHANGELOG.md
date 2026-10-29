# Changelog

## Unreleased

- Every dimension on the page is a token computed from one base unit: the type, the spacing, the strokes, the dashes and the corners all derive from it, so the page follows the browser's font-size setting and shrinks on a narrow viewport; every control answers the keyboard with one focus ring and the pointer with a hover, the buttons share one idiom, and the page a refused contract earns wears the page's own typeface.
- When a search finds more records than the eight its row shows, the row says how many: the results row ends with "8 of N", so the cap at eight no longer reads as the whole match.
- The `architecture-ui` and `architect-cli` skills follow the page on main: the page is written only with `-o`, the views are the layers stack, the pair matrix and the coverage treemap with the panel beside them, and a bare run is the check.
- All large explanatory labels are gone from the page: the sentence that opened each view, the empty-state sentence, the provenance and dropped-pair lines, the coverage caption and tally sentence, the panel hint and panel captions, and every move explanation leave the page for the Help; the verdict headline, control names, values, aria-labels and tooltips stay.
- A name holding an apostrophe, an ampersand, a less-than or a quote no longer truncates the page: every measured name reaches its attribute and its text through one escape, so the page shows it whole and a click on it selects what it names.
- The `files` view is gone from the page: the panel's all files tab carries the list, and search still reaches every file.
- The `surface` view is gone from the page: the views are layers, matrix and coverage, and `--json` prints the same bytes as before.
- The `shape` view is gone from the page: the whole-project numbers it showed - the longest chain, connections in use, the layer the most others rely on - are in the panel on the right.

## 0.1.1 - 2026-10-28

A patch release: two fixes to the check.

- `--file` reads a leading `./`, repeated slashes, an absolute path inside the tree and a directory with or without its trailing slash as the file or files they name, and a path that is neither on disk nor in git's `HEAD` or index is a finding, so a typo no longer passes the gate.
- The sibling scan no longer counts another checkout of the same project as a subscriber: a tree sharing the git common dir, the `remote.origin.url`, or a package root of this tree's contract is skipped.

## 0.1.0 - 2026-10-22

The first public release: archituner as a command-line tool for people and their coding agents.

### The check
- `archituner ARCHITECTURE.md` checks your code against the plan and exits 1 on any finding: an import across a forbidden pair, a limit breach, a glob that matches nothing, an `ignore` finding, a sublayer finding.
- Every deviation names the import lines, quotes the plan's reason for the rule, and gives the fix.
- `--file` checks only the files you name, so a pull request is judged on what it changed.

### The reading
- `--report` prints the whole reading: verdict, the four marks per pair of floors, the matrix, deviations, files no floor claims, per-file figures.
- `--report --format md` prints the same as Markdown, for a chat with your agent or a pull request comment.
- `--json` gives the whole reading as one document for agents and scripts, with each floor's `uses`, `used_by` and `chain`, and the longest chain of imports.
- `--baseline` stores a reading; later runs show what moved since.

### The plan
- `ARCHITECTURE.md`: floors as path globs, every ordered pair allowed or forbidden, a reason for every forbidden pair, a `limits` block for size, definitions, depth, cyclomatic and cognitive complexity and prose, `ignore`, sublayers.

### The agent skills
- Plugin `architect` (marketplace `archituner`) with seven skills that design, survey, review, hold and run the plan: `architect`, `architect-cli`, `architecture-md`, `architecture-cartograph`, `architecture-audit`, `architecture-democrat`, `architecture-autocrat`.
