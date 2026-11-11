from archituner.presentation.model.layout import canvas
from archituner.presentation.model.layout import LABEL_INSET
from archituner.presentation.model.layout import labels
from archituner.presentation.model.layout import MARK_X
from archituner.presentation.model.layout import MARK_Y


def style():
    return r"""  #treemap { max-width: 100%; height: auto; }
  #treemap .region { cursor: pointer; }
  #treemap .region rect { rx: var(--radius-s); }
  #treemap .region text { font-size: var(--type-small); fill: var(--ink); pointer-events: none; }
  #treemap .region text.meta, #treemap .region tspan.meta { font-size: var(--type-micro); fill: var(--ink-muted); }
  #treemap .region.dir > rect { fill: none; stroke: var(--rule-strong); stroke-width: var(--stroke-hair); }
  #treemap .region.dir > text.dirname { font-size: var(--type-micro); fill: var(--ink-muted); }
  #treemap .region.claimed rect { fill: var(--surface-sunken); stroke: var(--surface); stroke-width: var(--stroke-hair); }
  #treemap .region.unclaimed rect { fill: var(--unclaimed); stroke: var(--surface); stroke-width: var(--stroke-hair); }
  #treemap .region.unclaimed text, #treemap .region.unclaimed text.meta { fill: var(--surface); }
  #treemap .region.moved rect { stroke: var(--surface); stroke-width: var(--stroke-hair); }
  #treemap .region.moved text.meta { fill: var(--ink); }
  #treemap .region.moved.improved rect  { fill: var(--change-improved); }
  #treemap .region.moved.unchanged rect { fill: var(--change-unchanged); }
  #treemap .region.moved.regressed rect { fill: var(--change-regressed); }
  #treemap .region.moved.dropped rect   { fill: var(--surface-sunken); }
  __B__ A region answers the pointer as a shape, not as a button: its edge
     becomes a line in the strong rule at the node's own weight, and the rule
     stands before the selection's so a held region keeps the selection's own
     outline under the pointer as well. */
  #treemap .region:hover > rect { stroke: var(--rule-strong); stroke-width: var(--stroke-node); }
  #treemap .region.sel > rect { stroke: var(--selected); stroke-width: var(--stroke-selection); }""".replace("__B__", "/" + "*")


def script():
    width, height = canvas()
    name_min, split, dirname_y, name_y, meta_y = labels()
    return (r"""function drawCov() {
  __L__ Decision 7: nested regions, area by file count, each selectable. A directory
  __L__ box holds its children, which is what tells five directories called `scripts`
  __L__ apart. What no layer claims takes the accent; claimed goes recessive.
  const boxes = DATA.regions.filter(b =>
    b.opened || (filters.coverage.has(b.layer ? "mapped" : "unmapped")
                 && (!b.layer || filters.layer.has(b.layer))));
  if (!boxes.length) return "<p class='count'>every region is filtered out</p>";
  let h = "<svg id='treemap' viewBox='0 0 __CANVAS__'>";
  boxes.forEach(b => {
    __L__ The same regions in the same places. A region carries what its claiming
    __L__ layer did; a directory box is structure and carries neither reading.
    const move = b.opened || !changing() ? null : regionMove(b.members);
    const cls = "region" + (b.opened ? " dir" : move ? " moved " + move
                            : b.layer ? " claimed" : " unclaimed")
      + (sel("region", b.id) ? " sel" : "");
    h += "<g class='" + cls + "' data-region='" + esc(b.id) + "'>"
      + "<rect x='" + b.x + "' y='" + b.y + "' width='" + b.width
      + "' height='" + b.height + "'/>";
    const label = b.name === "." ? "(root)" : b.name;
    if (b.opened) {
      if (b.width > __NAME_MIN__) h += "<text class='dirname' x='" + (b.x + __LABEL_INSET__) + "' y='"
        + (b.y + __DIRNAME_Y__) + "'>" + esc(label) + " <tspan class='meta'>" + esc(b.files) + "</tspan></text>";
    } else if (b.width > __SPLIT__ && b.height > 24) {
      h += "<text x='" + (b.x + __LABEL_INSET__) + "' y='" + (b.y + __NAME_Y__) + "'>"
        + (move ? MOVED[move] + " " : "") + esc(label) + "</text>"
        + "<text class='meta' x='" + (b.x + __LABEL_INSET__) + "' y='" + (b.y + __META_Y__) + "'>"
        + esc(b.files) + "</text>";
    } else if (move && b.width > 12 && b.height > 12) {
      __L__ Too small for a name, never too small for the mark: the hue is not the
      __L__ only thing carrying it.
      h += "<text x='" + (b.x + __MARK_X__) + "' y='" + (b.y + __MARK_Y__) + "'>" + MOVED[move] + "</text>";
    }
    h += "<title>" + esc(b.path || ".") + (b.opened ? "/"
         : " - " + (move ? move + ", " + esc(b.layer || "claimed by no layer")
                    : esc(b.layer || "unclaimed")))
      + ", " + esc(b.files) + " file(s)</title></g>";
  });
  h += "</svg>";
  __L__ The caption this view carried below the drawing at rest is gone: its question
  __L__ left with the other large labels and is the Help's to carry now. What moved,
  __L__ the tallies below still answer.
  if (changing())
    return h + "<p class='count'>" + fileTallies() + "</p>";
  return h;
}

function fileTallies() {
  __L__ The file dimension is four numbers, and a number that cannot be opened is the
  __L__ headline uxspec refuses.
  __L__ No outcome is named here. The legend a few rows up already reads each outcome
  __L__ with a count, and uispec forbids a second element on the page repeating one -
  __L__ which is what this was: two numbers under one word, one counted over pairs
  __L__ and one over files, side by side in the change reading. What is left is the
  __L__ legend's own mark, so the binding a reader needs is on screen; the word is
  __L__ still on the button's tooltip and on the heading the button opens.
  const one = (kind, id, mark, n, what) =>
    "<button class='tally' data-figure='" + esc(kind + ":" + id) + "' title='" + esc(what)
    + "'>" + esc(mark) + " " + esc(n) + "</button>";
  const since = " file(s) since the stored baseline";
  const nowhere = DATA.files.filter(f => !(f.path in CHANGE.files)).length;
  __L__ The fourth figure keeps its words, and it is the only one that may. The
  __L__ three above are keys of the legend, which is where their marks are named;
  __L__ `–` is not - the legend raises a dropped key only where the two contracts
  __L__ disagree on a layer, and this figure counts files the baseline never held,
  __L__ which happens with no dropped pair at all. A mark with no key on the page
  __L__ is the one thing the removal above may not leave behind.
  __L__ Comma-separated, not spaced: the unchanged mark is `=`, and `▲ 1 = 87` set
  __L__ between two numbers reads as an equation rather than as two figures.
  return one("fmove", "improved", MOVED.improved, CHANGE.file_counts.improved,
          "improved" + since) + ", "
    + one("fmove", "unchanged", MOVED.unchanged, CHANGE.file_counts.unchanged,
          "unchanged" + since) + ", "
    + one("fmove", "regressed", MOVED.regressed, CHANGE.file_counts.regressed,
          "regressed" + since) + ", "
    + one("fdropped", "", MOVED.dropped, nowhere, "file(s) in no comparison at all");
}""".replace("__CANVAS__", f"{width} {height}")
       .replace("__L__", "/" + "/")
       .replace("__NAME_MIN__", f"{name_min}")
       .replace("__SPLIT__", f"{split}")
       .replace("__DIRNAME_Y__", f"{dirname_y}")
       .replace("__NAME_Y__", f"{name_y}")
       .replace("__META_Y__", f"{meta_y}")
       .replace("__LABEL_INSET__", f"{LABEL_INSET}")
       .replace("__MARK_X__", f"{MARK_X}")
       .replace("__MARK_Y__", f"{MARK_Y}"))
