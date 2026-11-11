from archituner.presentation.model.figures import chain_column
from archituner.presentation.model.figures import NAME_BASE
from archituner.presentation.model.figures import NAME_INSET
from archituner.presentation.model.figures import relied_on

LINE = "/" + "/"
BLOCK = "/" + "*"


SCRIPT = (r"""function drawOverview() {
  const o = DATA.overview; const f = o.chain.figure, r = o.relied.figure;
  """ + LINE +
          r""" One box serves both drawings, so the pair of them is written once: the
  """ + LINE +
          r""" chain column and the relied-on bus spend the same box and the same
  """ + LINE +
          r""" segment. The head rides the line whose end it marks, as the sketch's
  """ + LINE +
          r""" own arrowheads do.
  const pbox = b => "<rect class='box' x='" + b.x + "' y='" + b.y
    + "' width='" + b.width + "' height='" + b.height + "'/>"
    + "<text x='" + (b.x + __NAME_INSET__) + "' y='" + (b.y + __NAME_BASE__) + "'>" + esc(b.name) + "</text>";
  const seg = (d, head) => "<path class='ln' d='" + d + "'" + (head
    ? " marker-end='url(#phead)'" : "") + "/>";
  """ + LINE +
          r""" The meter the owner kept. Its fill is the share of the allowed
  """ + LINE +
          r""" connections the code really uses, and the width travels in the payload
  """ + LINE +
          r""" beside the count it is the share of, so the two cannot drift apart.
  let h = "<div class='block'><div class='head'>"
    + "<span class='label'>Connections in use</span><span>"
    + esc(o.connections.count) + "</span></div>"
    + "<div class='bar'><span style='width:" + o.connections.width
    + "%'></span></div></div>";
  """ + LINE +
          r""" Drawings 1:1, never stretched past the width they travelled in, so the
  """ + LINE +
          r""" text in them stays the dense size. The head is declared once, on the
  """ + LINE +
          r""" first drawing; a marker is named in the document, not owned by one svg.
  """ + LINE +
          r""" The caption under each drawing left with the other large labels; its
  """ + LINE +
          r""" words still name the drawing, on the svg's own aria-label, where they
  """ + LINE +
          r""" cost the layout nothing and a screen reader reads them whole.
  h += "<div class='block'><div class='head'><span class='label'>Longest chain"
    + "</span><span>" + esc(o.chain.count) + "</span></div>"
    + "<svg width='" + f.width + "' height='" + f.height
    + "' viewBox='0 0 " + f.width + " " + f.height
    + "' role='img' aria-label='" + esc(o.chain.caption) + "'><defs>"
    + "<marker id='phead' markerUnits='userSpaceOnUse' markerWidth='6' markerHeight='6' orient='auto' refX='6' refY='3'><path d='M 0 0 L 6 3 L 0 6 Z' fill='var(--rule-strong)'/></marker>"
    + "</defs>" + f.boxes.map(pbox).join("")
    + f.arrows.map(a => seg("M " + a.x + " " + a.y1 + " V " + a.y2, true)).join("")
    + "</svg></div>";
  """ + LINE +
          r""" The bus: every user joins one line and the line carries a single arrow
  """ + LINE +
          r""" into the layer, so nothing crosses on the way down.
  h += "<div class='block'><div class='head'><span class='label'>Most relied on"
    + "</span><span>" + esc(o.relied.count) + "</span></div>"
    + "<svg width='" + r.width + "' height='" + r.height
    + "' viewBox='0 0 " + r.width + " " + r.height
    + "' role='img' aria-label='" + esc(o.relied.caption) + "'>"
    + r.users.map(pbox).join("")
    + r.joins.map(j => seg("M " + j.x1 + " " + j.y + " H " + j.x2)).join("")
    + seg("M " + r.bus.x + " " + r.bus.y1 + " V " + r.bus.y2)
    + seg("M " + r.arrow.x1 + " " + r.arrow.y + " H " + r.arrow.x2, true)
    + pbox(r.layer)
    + "</svg></div>";
  return h;
}
""" + LINE +
          r""" The strip the sketch puts under the panel's heading: one tab per
  """ + LINE +
          r""" card, overview and all files, and one card drawn at a time. The
  """ + LINE +
          r""" choice belongs to the state it was made at, so it is kept beside
  """ + LINE +
          r""" that state: the same state redrawn keeps it, a new state resets it,
  """ + LINE +
          r""" and a selection empties the strip, its card being the selection's.
const PANEL_TABS = [["overview", "overview"], ["files", "all files"]];
let panelTab = PANEL_TABS[0][0], panelState = null;
function drawPanelTabs() {
  if (panelState !== selection) { panelState = selection; panelTab = PANEL_TABS[0][0]; }
  $("#panel-tabs").innerHTML = selection ? "" : PANEL_TABS.map(t =>
    "<button role='tab' data-panel-tab='" + esc(t[0]) + "' aria-selected='"
    + (panelTab === t[0]) + "'" + (panelTab === t[0] ? " class='on'" : "")
    + ">" + t[1] + (t[0] === "files"
      ? " <span class='count'>" + esc(DATA.files.length) + "</span>" : "")
    + "</button>").join("");
}

""").replace("__NAME_INSET__", f"{NAME_INSET}"
          ).replace("__NAME_BASE__", f"{NAME_BASE}")


def overview(reading):
    shape = reading["shape"]
    chain = shape["longest_chain"]
    relied = max(reading["layers"], key=lambda layer: len(layer["used_by"]))
    links = [chain[at] + " uses " + chain[at + 1]
             for at in range(min(2, len(chain) - 1))]
    return {
        "connections": {
            "count": (str(shape["realised"]) + " of "
                      + str(shape["permitted"]) + " allowed"),
            "width": (shape["realised"] * 100 // shape["permitted"]
                      if shape["permitted"] else 0)},
        "chain": {
            "count": (str(len(chain) - 1) + " links" if chain else "–"),
            "figure": chain_column(chain, None),
            "caption": ("each arrow is a link: " + ", ".join(links)
                        + ", and so on down to the foundation"
                        if chain else "")},
        "relied": {
            "count": (relied["name"] + " · used by "
                      + str(len(relied["used_by"]))),
            "figure": relied_on(relied["used_by"], relied["name"]),
            "caption": ("a change in " + relied["name"]
                        + " reaches every layer on the left")}}


def style():
    return r"""  #detail .block { display: grid; gap: var(--step-2); }
  #detail .head { display: flex; flex-wrap: wrap; gap: var(--step-1) var(--step-3); align-items: baseline; }
  #detail .head .label { color: var(--ink-muted); }
  #detail .bar { height: var(--step-3); background: var(--surface-sunken); border: var(--hair) solid var(--rule); }
  #detail .bar > span { display: block; height: 100%; background: var(--state-convergence); }
  #detail svg { display: block; max-width: 100%; height: auto; }
  #detail svg text { font-family: var(--mono); font-size: var(--type-dense); fill: var(--ink); }
  #detail svg .box { fill: var(--surface); stroke: var(--rule-strong); stroke-width: var(--hair); rx: var(--radius-s); }
  #detail svg .ln { stroke: var(--rule-strong); stroke-width: var(--hair); fill: none; }
  #detail .small, #detail .hint { color: var(--ink-muted); font-size: var(--type-small); }
  #detail .hint { border-top: var(--hair) solid var(--rule); padding-top: var(--step-3); }
  __B__ The card the files tab draws is one row per file on a grid that wraps
     a path however long it grew, the counts right-aligned in the context
     ink. A row the panel lists because a figure, a region or that card
     counts it answers the pointer where it sits: the hand over it, and on
     hover the row lifts to the raised ground - the boxed controls' one
     hover, spent as a band behind the row rather than as a box. */
  #detail .flist { list-style: none; margin: 0; padding: 0; }
  #detail .flist li { display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto; gap: var(--step-3);
    padding: var(--step-1) 0; border-bottom: var(--hair) solid var(--rule);
    font-size: var(--type-dense); }
  #detail .flist li span.p { overflow-wrap: anywhere; }
  #detail .flist li span.n { color: var(--ink-muted); text-align: right; }
  #detail li[data-pair], #detail li[data-file] { cursor: pointer; }
  #detail li[data-pair]:hover, #detail li[data-file]:hover { background: var(--surface-raised); }
""".replace("__B__", BLOCK)


def script():
    return SCRIPT
