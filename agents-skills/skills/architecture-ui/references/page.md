# The page - the detail behind its reading

Contents: the shell every view stands on · the three views · the narrow page · the filters and the search · the panel · the payload as the page draws it · the rejection page.

## What stands on every view

The shell carries the tree's own name - a directory name, never a path, because a rendered page travels - and the verdict beneath it: `CONFORMS: no forbidden pair realised`, or `DIVERGENT: N forbidden pair(s) realised`. Both grounds, light and dark, follow the browser's own scheme.

Every colour and dimension on the page is declared once as a token, and every dimension computes from one base unit: a pixel at the default font size, following the reader's font-size preference, shrinking on a narrow viewport and never growing.

The reading toggle switches the one set of views between two readings, never both on screen at once. The state reading marks each pair with what it is; the change reading marks it with what it did since the stored baseline.

The change reading needs a baseline stored beside the contract. With none stored the toggle says so and names the command that writes one - ``python3 -m archituner <contract> --baseline``, restated secondhand here; the invocation's one home is `architect-cli`.

The legend is the filter for the mark axis: one key per state in the state reading, one per outcome in the change reading - and, where pairs stood in no comparison, a not-compared key beside them - each carrying its count and isolating its mark on a click. A click on the isolated key restores all.

Beside the marks stand the unclaimed key, isolating the file axis to what no layer claims, and the findings key, opening what it counts.

The search-and-filters row sits closed at rest, so the page opens as a report and becomes an instrument on the first interaction. Its button names what the row's axes hold back while they are out of sight.

Every clickable target on the page shows the hand and answers hover in its own material. A boxed control - a legend key, a search hit, a reading toggle, the search-and-filters button, a panel tab, a tally, the reset, the sheet's cross - lifts to the raised ground; an unboxed view tab wears the active tab's underline. A shape in a drawing answers in the drawing's own material, never a button's dress: a layer box takes the node's own stroke weight, a wire the selection's width with its glyph going bold, a matrix cell a stronger border, a coverage region an edge in the strong rule - the selection's own outline holding under the pointer as well. A row the panel lists because a count drew it lifts as a band behind the row, the boxed controls' one hover spent unboxed.

No view opens with a sentence stating its question: the sentences left the page with the other large labels, and what they answered is the Help's to carry now.

## What the three views draw

| View | What it draws |
|---|---|
| layers | the stack the page opens on, dependency order top to bottom - where the program starts above the foundations - drawn at its natural size: the stage's own width and height are asked on the tag, so a wide screen shows the drawing one to one and its labels hold the size their token declares. On the wide page permitted edges run left, solid where realised and dashed where nothing realises them; realised forbidden edges run right, in a band the stage draws only when there is one, so a divergence is found by position; a pair in silence - forbidden, realised by nothing - draws no wire at all, so only the pairs where something happens get one. Each box carries its file count, the layers it uses, the layers it is used by, and its chain - the links from the chain-0 layer; a muted header row above names the four cells once - files, uses, used by, chain - and a layer with no files draws a sunken, dashed box |
| matrix | rows import columns; a cell is the pair's state, or its move in the change reading; the diagonal and the pairs the payload leaves undecided stand empty |
| coverage | the treemap: nested directory regions, area by file count, what no layer claims standing in the accent; every region selects, and in the change reading each region takes the worst move among its files |

Every drawn pair on the wide page is one right-angled wire: out of an exit dock on its source's edge, squared over each standing lane it passes, down its own lane, and into an entry dock on the target's edge, its arrow landing on the layer being used in the mark's own colour. The docks spread along the box's edge - entries above, exits below, an absence's wire entering low on its target's box - and the lanes are seated: wires whose runs would overlap hold different lanes, runs far apart share one. The state's own glyph stands at the middle of the wire's lane, haloed in the page's ground, and the wire answers its pair everywhere on it, the glyph included.

In the change reading the stack is marked with the rest: each box takes its move fill with the move glyph before its name, and each wire takes its move's own stroke while the glyph on its lane stays the state's - the wire says what the pair did, the glyph what it is. Selecting a layer recedes every wire that does not touch it, the one way to follow a single edge.

## What the narrow page draws

Under a viewport 560 px wide the stack the layers view draws is one column of boxes running down the page, each box two rows - the layer's name above, its four cells below - standing at the column's natural size. Every drawn pair is the same right-angled wire at the phone's own numbers, all of them in the one band at the boxes' left - exit dock, own lane, squared hop, entry dock with the arrow - so nothing crosses unmarked on the way down a column a phone is wide. The band the reading toggle and the legend live in is bounded to a strip that scrolls, so the drawing starts on the first screen.

The panel stands below the drawing at rest; a selection raises it as a sheet from the page's bottom edge, and the box the selection named scrolls to stand above the sheet's top edge. The close button is the sheet's own - at rest the panel is the whole project below the drawing and has nothing to close.

A hint names what a click does, in words that name no side: `Click a box to see that layer.`, and with a layer selected `Click the box again to see the whole project.` The wide page hides the hint and keeps the layout it had.

## How the filters and the search narrow the page

Four axes narrow the drawing. The mark axis lives in the legend, spelled above.

The row carries the other three: the layer multi-select over the dependency order, the files axis of mapped and unmapped, and the edge weight - a floor on the witnesses a pair must carry to draw.

**A filter that hides says so.** The legend states the pairs the mark axis holds back, and each axis in the row states its own hidden count - per axis, never as one total.

A filter that empties a view is answered by the reset alone, `show everything`: the sentence that named which filter emptied it left with the other large labels. The coverage view is the exception: it can empty while every axis still holds a value - the files axis on `mapped` alone, on a tree where no file is claimed - and it then answers with its own line, `every region is filtered out`, carrying no reset.

The search covers layers, files, modules and prose - a layer's name, Responsibility and Rationale; a file's path and module; a pair's ends and Boundaries reason.

It answers with up to eight hits - where more matched, a compact label beside them names how many it shows of how many matched - and a hit selects what it names: a pair or a layer moves to the view that draws it, and a file opens in the panel.

## What the panel holds

On the wide page the panel stands open beside the views; nothing on the page opens or closes it. At rest its name is the whole project's, its body one of two cards chosen by the tab strip beneath the name.

A selection replaces both with its own name and its own detail, and every path to a selection does the same.

The overview card carries the project's own numbers: connections in use - the share of the allowed connections the code really uses - the longest chain, and the most relied on, the last two as figures beside their counts.

The all files card carries every walked file, one group per layer in the order the layers depend in, the files no layer claims standing last under the accent. A row reads the file's path, its imports and its importers.

A row a count lists - a figure's files, a region's members, this card's own - answers the pointer where it sits, and a click on it selects the file it names.

| Selection | What the panel holds |
|---|---|
| a pair | its state or its move, the Boundaries reason, the imports realising it, and the remedy |
| a layer | its move across its own pairs, in the change reading, its globs, its Responsibility and Rationale cells, and its file count |
| a file | its move, in the change reading, its claiming layer or none, its imports with their targets, and its importers |
| a coverage region | its move, in the change reading, its claiming layer or none, its file count, and its member files |
| a figure | the files it counts - the move tallies the coverage view carries in the change reading |
| the findings | every finding beside the naming rules and the invariants, stated and never checked |

Escape and a click on the layer box already selected return the panel to the whole project - the promise that box's panel makes. A click on any other box moves the selection. Escape with the caret in the search field clears the query first, and clears the selection only from an empty field.

## What the payload holds as the page draws it

The page draws the run's own reading - the same keys, holding the same values, the `--json` document travels, so a reader and a consumer never hold two readings of one run. `architect-cli`'s reference names what each of those keys holds.

The page is one self-contained file - styles and script inline, the system's own monospace face, nothing fetched over the network - which is why a rendered page travels.

The four below exist for the drawing alone - they never travel in the document - and the page is their reader.

| Key | What the page draws from it |
|---|---|
| `regions` | where the coverage view places every region on its canvas - each box's place and size, its claiming layer, its file count and its members |
| `stack` | the wide stage's geometry - a node box per layer, and every wire's run: its dock at each end, its lane, its hops and the glyph's place on its lane |
| `stack_narrow` | the narrow stage's geometry - the same wires at the phone's own numbers, a node box per layer with its two rows' metrics beside the coordinates |
| `overview` | the panel's whole-project card - the connections share, and the longest chain and the most relied on as figures, each with its count |

## What a refused contract draws

A contract the tool refuses gets a page of its own: `Contract rejected`, the refusal's own reason, the contract's name, and the sentence saying nothing was measured, so no view can be drawn. It follows the browser's scheme on both grounds, dressed from the same tokens as the page.

The exit is the refusal's own, 2, and `architect-cli`'s partition of refusals is what routes it.
