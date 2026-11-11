# Changelog

## Unreleased

## 0.2.0 - 2026-11-11

A minor release: the interactive page ships, written with `-o`.

- `archituner ARCHITECTURE.md -o <file>` writes the whole reading as one self-contained page and prints the counts on stdout; the page opens on the layers stack, the pair matrix and the coverage treemap are the other views, and a panel beside them carries the all files tab and the whole-project numbers - the longest chain, the connections in use, the layer the most others rely on; search still reaches every file, `-o` accepts the narrowing flags and ignores them, a bare run stays the check, and `--json` prints the same bytes as before.
- The layers stack draws right-angled wires: every drawn pair is one orthogonal path - an exit dock on its source's edge, its own seated lane, squared hops over the standing lanes, an entry dock with the arrow in the mark's own colour, and the state's glyph at the middle of the lane, the wire answering its pair everywhere on it - divergences mirrored in a right band drawn only when one is, the change reading's wire in its move's own stroke, and no curved arc at any width; the stage draws at its natural size on every width, so its labels hold the dense size on every screen, and the phone's column carries the same wires in one band beside two-row boxes.
- The page opens for a phone: under the main column's own width the stack is one column of two-row boxes with the uses arrows as one bus in the left gutter, the legend and controls bands are bounded so the drawing starts on the first screen, the panel rises as a sheet from the bottom edge carrying its own close cross and the picked box lifted above it, and a hint names what a click does in words that name no side; the wide page keeps the layout it had.
- Every dimension on the page is a token computed from one base unit: the type, the spacing, the strokes, the dashes and the corners all derive from it, so the page follows the browser's font-size setting and shrinks on a narrow viewport; every clickable target answers the pointer with a hover, and the native controls show a focus ring; the buttons share one idiom, and the page a refused contract earns carries the two grounds and wears the page's own typeface.
- The legend holds a not-compared key, the stack a header row and vacant boxes, the change reading's marks sit on the stack and a coverage region names its worst move, every selection's panel opens with the move, and the coverage view carries its own empty line beside the reset.
- When a search finds more records than the eight its row shows, the row says how many: the results row ends with "8 of N", so the cap at eight no longer reads as the whole match; Escape clears the search field first.
- All large explanatory labels are gone from the page: the sentence that opened each view, the empty-state sentence, the provenance and dropped-pair lines, the coverage caption and tally sentence, the panel hint and panel captions, and every move explanation leave the page for the Help; the verdict headline, control names, values, aria-labels and tooltips stay.
- A name holding an apostrophe, an ampersand, a less-than or a quote no longer truncates the page: every measured name reaches its attribute and its text through one escape, so the page shows it whole and a click on it selects what it names.
- A sibling project's contract that vanishes or cannot be read no longer crashes `--check`; it is treated as no sibling.
- The sibling scan no longer crashes `--check` on a sibling whose files cannot be read, or whose contract or `.gitignore` cannot be decoded: such a sibling is treated as not there, and the siblings beside it still contribute.

## 0.1.3 - 2026-11-07

A patch release: the check gets stricter.

- A Python file no layer claims now fails `--check` when it sits in a directory holding a claimed file, imports a claimed file or is imported by one, so a project that passed on 0.1.2 can fail on 0.1.3: the check names the file, and the way out is claiming it into a layer or listing it under `ignore` in ARCHITECTURE.md to declare it an exception.

## 0.1.2 - 2026-10-30

A patch release: one fix to the check.

- An import of a module that is not in the tree no longer counts as an edge to its parent package, so a guarded import of a package a release leaves out is not a divergence.

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
