# Changelog

## Unreleased

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
