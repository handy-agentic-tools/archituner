# Procedure 2 - the roast loop

Procedure 2 is a loop, not a pass. `architect` owns each spawn and `architecture-autocrat`'s reviewer brief owns the shape of the report it comes back with; this file owns the round those reports enter, and how many rounds there are.

## What one round runs, and in what order

The first spawn has already happened when you reach this list. Each item decides what the next one reads, so the order is not a presentation choice.

1. **Merge the two lens reports into one before reading either for anything else.** Both lenses read one file, so a defect both reach arrives twice, and nothing downstream has a single subject until they are one report.
2. **Carry every earlier decline onto the finding it closes, in this step and nowhere else.** `architecture-autocrat`'s reviewer brief bars a lens from recording one, so a declined `Warning` comes back as fresh text every round unless the merge closes it here.
3. **Stop where the merged report leaves no `Error` unfixed and no `Warning` neither fixed nor declined.** The test reads the merge and only the merge: half of what closes it, the declines, exists nowhere before step 2.
4. **Offer the merged findings to the author and apply only what they pick.** The author owns the file and the intent behind it, and applying the set unasked makes the next round a review of your own edits.
5. **Stop where the author applies nothing, naming every `Error` left open and every `Warning` neither fixed nor declined.** They have seen this set and not acted, so re-offering it unchanged asks one question twice.
6. **Stop and say so where three rounds leave the `Error` count non-zero and no lower.** Each fix is landing the next defect, so the round is not what needs changing: name what is producing them and put that to the author.
7. **Re-spawn both lenses on the applied state, then repeat from step 1.** A fix is itself a diff and lands its own defects, so the deliverable is format-valid only of a state a review has seen.

**Hand a re-spawned lens the file and nothing from the round that produced it.** A lens told what was fixed or declined is reading the author's frame, and its report then confirms the last round instead of testing the new state.

**Hand back the merged report the loop exited on, never a union of the rounds.** What the earlier rounds closed is fixed text by now, and a union reports it against a file that no longer carries it.

## What closes a finding, and what only looks like it

**Treat every `Error` and every `Warning` as blocking until it is fixed, dropped or declined.** A finding is a claim about the file rather than advice about it, and step 3 is counting the ones still open.

**Let a `Not a rule` finding hold nothing open.** That verdict says no consumer acts on the input, so there is no rule for a fix to restore; `architecture-md` §3 says what to report instead.

**Drop a finding only against evidence about the artifact that raised it: the file's text, the format rule it cites, or the run the lens showed.** A prose defence citing nothing argues that the author meant it, which is a decline and not a drop.

**Carry no drop forward, and read one the next round re-files as the file's text inviting it.** A decline records standing intent; a drop answered one report, and a second lens reaching it from the same sentence is evidence about the sentence.

**Take the user in the session as the author, and say so where they did not write the file.** Every `Warning` closes on intent, so a loop with nobody holding it cannot close, and a user who inherited the file is deciding what it means now.

**Record a decline as the author's own written reason for leaving a `Warning` standing.** The verdict turns on intent only they hold, so their sentence is what closes it and silence closes nothing.

**Never decline an `Error`.** `architecture-md` §3 rule 5 says why nothing is left for the author's intent to settle, so the loop cannot close over one.

## What runs the lenses when a spawn or the tool is unavailable

**Spawn both lenses even when the tool cannot run.** `architecture-autocrat`'s reviewer brief says which of its checks survive with no run, and which it must report unrun.

**With no subagent available, work `architecture-autocrat`'s reviewer brief yourself, one lens per pass.** The independence the two-agent split buys is lost either way, and holding both checklists in one pass loses the split as well.

**Run the loop above unchanged in either case.** A fallback changes who holds a lens, never what the merge, the decline or the exit condition are.
