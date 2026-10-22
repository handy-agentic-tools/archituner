# Procedure 1, autocrat - the tree gets no vote

The user does not trust the current architecture, calls it a mess worth refactoring, and wants the ideal shape on a green field. Every step below runs above the four `architect` shares across the three modes.

## What this mode settles before the shared four

1. **Read the product docs, not the tree.** What the product does, and what it must survive - a provider change, a second surface, data outliving the code.
2. **Get both from the user where the repo carries no product docs, before drafting anything.** The tree does not answer them, and in this mode it is not permitted to try.
3. **Stop and say the mode has no input where the product's problem still cannot be stated.** Best practice is indexed by the class of product, so a draft with the class unknown is a generic layering wearing the user's name.
4. **Take the complaint apart into the incidents behind it.** A change that touched nine files, a test nobody could write, a vendor swap that never happened - those are what the new carve must make cheap, and a draft that does not is a reshuffle.
5. **Draft the decomposition from best practice for this class of product, without opening a single source file.** The dependency direction, the outside edge held behind ports, where the value must stay testable.

## What the tree is not allowed to contribute

**Give the tree no vote on the decomposition, at any point in this mode.** The user's verdict is that the current architecture is a mess, so anything read out of it arrives as a template for the shape they asked to leave behind.

**Never design the negation of the tree either.** An inverted decomposition is still derived from the one the user dislikes: it carries the same carve, mirrored, and now with no reason behind any line of it.

**Take a constraint the outside world imposes from the product docs and the user, never from the tree.** A platform rule or a vendor's imposed shape is a fact about the product, which steps 1 and 2 already reach.

**Put design democrat to the user rather than reading the tree here.** The mode is the user's call, so a design that quietly took the tree's evidence is running a mode nobody chose and the repo's record names the wrong one.

## Where the green-field design leaves a file homeless

**Read the gap between the draft's layers and the files that exist as the migration, whole.** This mode's homeless set is large by construction, and its size measures the refactor the user asked for rather than an error in the carve.

**Never let that size become the argument for bending the file.** The pressure to widen a glob or invent a layer scales with the number of strays, and `architecture-md` §4 names the moves that pressure produces and refuses each one.

**Keep the not-claimed line of `## Enforcement` for paths the architecture excludes on purpose, never for a source file that has a home and is not in it.** Relabelling a stray as out of scope retires the finding that would have moved it.

**Leave the homeless set to procedure 4 to report, and write no migration into ARCHITECTURE.md.** A transcribed migration is stale the moment the first file moves, while the audit regenerates it on demand.

## Where this mode hands off

**Say at handoff that no part of the repo satisfies this file yet.** A green-field contract read as a description is read as broken, and the first audit is too late for the user to learn that the whole gap was the plan.

**Say which of the prescribed homes exist yet.** That decides what procedure 2's mechanical half can see at all.

**Say that the tool's counts speak only for the homes that exist.** One surviving home with one walked file gives a run whose every convergence sits inside that layer alone, saying nothing about the rest.

**Hand the settled decomposition to `architect`'s four shared steps and run them from there.** They are what turns a decomposition into a format-valid file, and nothing above them produces one.
