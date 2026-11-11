from archituner.presentation.model.layout import NARROW_W
from archituner.presentation.model.stack_layout import NUDGE
from archituner.theme import MARKS

LINE = "/" + "/"
BLOCK = "/" + "*"


def style():
    return r"""  __B__ The phone dress. The threshold is the main column's own basis: below
     it the wide stage no longer fits beside the panel, so the page opens as
     one column and the panel falls below the drawing. The cross and the
     hint line are the phone's own controls, and the wide page hides rather
     than lacks them, so it keeps the look main approved. */
  #panel-head [data-close] { display: none; }
  .hint { display: none; }
  @media (max-width: __W__px) {
    __B__ The band the controls live in is bounded, so the drawing a phone is
     opened for starts on the first screen rather than under a wall of keys. */
    #shellbar { max-height: calc(var(--u) * 200); overflow: auto; }
    __B__ The stack's own labels answer at the dense size on a phone: the
     small type the wide header row wears is a wide screen's privilege. */
    #stack text.head { font-size: var(--type-dense); }
    __B__ The hint names what a click does, in words that name no side: a
     narrow screen has no right edge for a panel to sit beside. */
    .hint { display: block; color: var(--ink-muted); font-size: var(--type-dense); margin: var(--step-2) 0; }
    __B__ At rest the panel sits below the drawing and spans the phone, its
     padding counted inside the span it takes: a width past the phone's own
     is a sideways scroll nothing on a phone answers. Held, it rises as a
     sheet from the bottom edge over the drawing, bounded so the box the
     reader picked stays in view above it. */
    #detail { flex: 0 0 100%; box-sizing: border-box; border-left: none;
      border-top: var(--step-1) solid var(--rule); }
    #detail[data-sheet] { position: fixed; left: 0; right: 0; bottom: 0;
      max-height: calc(var(--u) * 300); overflow: auto; background: var(--surface); }
    __B__ The raised sheet leaves the flow, and the height it held under the
     drawing leaves with it: the page would end under the last box, and a
     box picked low on the column could no longer be scrolled clear of the
     sheet standing over it. The drawing's own column holds the sheet's
     bound, and one step more, as room below itself - room that grows the
     page with the drawing, so a box the reader picks can always rise above
     the sheet's top edge. */
    body:has(#detail[data-sheet]) #main { padding-bottom:
      calc(var(--u) * 300 + var(--step-4)); }
    __B__ The panel's name and its cross share one row, the cross at the far
     edge a thumb reaches: a phone has no Escape key, so closing is a
     control the sheet itself carries - and only the sheet, for at rest the
     panel is the whole project below the drawing and has nothing to close. */
    #panel-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--step-2); }
    __B__ The cross, where the sheet shows it, is a control like the page's
     others: the hand over it and the lift on hover, spelled on the shown
     state because a hidden cross owns no affordance. */
    #detail[data-sheet] #panel-head [data-close] { display: inline-block; cursor: pointer; }
    #detail[data-sheet] #panel-head [data-close]:hover { background: var(--surface-raised); }
  }
""".replace("__B__", BLOCK).replace("__W__", f"{NARROW_W}")


def script():
    return (r"""__L__ The phone's width, asked of the browser once and read by the drawing
__L__ wherever a choice hangs on it. The threshold is the model's own number,
__L__ the one the stylesheet keys the dress on, so the drawing and the dress
__L__ cannot disagree about which page is on screen. Crossing it redraws.
__L__ Asked only where a viewport answers: a page a script reads rather than
__L__ opens has no width to ask, and draws the wide stage rather than none.
const PHONE = globalThis.matchMedia
  ? globalThis.matchMedia("(max-width: __W__px)")
  : { matches: false, addEventListener() {} };
PHONE.addEventListener("change", draw);

__L__ The box the sheet rose for stays in view above it. The sheet takes its
__L__ height out of the page, so the scroll that held the box where the
__L__ reader tapped it can no longer lift the box clear on its own: the room
__L__ the stylesheet holds below the drawing is for this, and the mark the
__L__ sheet rises on is what this waits for. Only the rise - while the sheet
__L__ already stands, a box the reader tapped sits above it, or the tap
__L__ could not have reached a box under the sheet. Asked only where a page
__L__ opens: a script that reads the page without running it has no observer
__L__ to wait on, and the drawing keeps every box where the reader's own
__L__ scroll left it.
if (globalThis.MutationObserver)
  new MutationObserver(() => {
    const sheet = $("#detail");
    if (!PHONE.matches || !sheet.hasAttribute("data-sheet")) return;
    const held = $("#view .sel");
    if (!held) return;
    __L__ The lift lands the box a padding step clear of the sheet's top
    __L__ edge, a step read off the sheet's own dress rather than spelled
    __L__ here.
    const lift = held.getBoundingClientRect().bottom
      - sheet.getBoundingClientRect().top
      + parseFloat(getComputedStyle(sheet).paddingTop);
    if (lift > 0) window.scrollBy(0, lift);
  }).observe($("#detail"), { attributes: true, attributeFilter: ["data-sheet"] });

function drawColumn() {
  const g = DATA.stack_narrow;
  const shown = DATA.pairs.filter(p => p.state !== "silence" && pairVisible(p));
  __L__ The phone's stage is the stack at its own size: every drawn pair one
  __L__ right-angled wire in the one band beside the boxes - an exit dock on
  __L__ the source, its own lane, an entry dock with the arrow on the target,
  __L__ a squared hop over a standing lane - so nothing crosses unmarked on
  __L__ the way down a column a phone is wide, and no wire is merged into a
  __L__ bus the way the arcs' one lane per target was.
  let wires = "";
  const pairId = p => esc(p.source) + "->" + esc(p.target);
  shown.forEach(p => {
    const c = DATA.stack_narrow.wires[p.source + "->" + p.target];
    const mark = changing() ? moveOf(p.source, p.target) : p.state;
    const touched = !selection || selection.kind !== "layer"
      || p.source === selection.id || p.target === selection.id;
    const cls = "wire " + mark + (sel("pair", p.source + "->" + p.target) ? " sel" : "")
      + (touched ? "" : " aside");
    const away = c.x > c.l ? 1 : -1;
    __L__ The wire is one group that answers its pair everywhere on it: the
    __L__ glyph travels with the path, the arrow lands on the target's edge,
    __L__ and the glyph stands again at the middle of the wire's own lane,
    __L__ the mark a hue-blind reader reads instead.
    wires += "<g class='" + cls + "' data-pair='" + pairId(p) + "'>"
      + "<path d='M " + c.x + " " + c.a
      + c.hops_out.map(x => " H " + (x + away * g.hop) + " V " + (c.a - g.hop)
        + " H " + (x - away * g.hop) + " V " + c.a).join("")
      + " H " + c.l + " V " + c.b
      + c.hops_in.map(x => " H " + (x - away * g.hop) + " V " + (c.b - g.hop)
        + " H " + (x + away * g.hop) + " V " + c.b).join("")
      + " H " + c.x + "' marker-end='url(#" + mark + ")' data-pair='" + pairId(p) + "'>"
      + GLYPH[p.state] + "<title>" + esc(p.source) + " → " + esc(p.target)
      + ": " + esc(mark) + "</title></path>"
      + "<text x='" + c.l + "' y='" + c.my + "' text-anchor='middle'>" + GLYPH[p.state]
      + "</text></g>";
  });

  let head = "";
  ["files", "uses", "used by", "chain"].forEach((label, k) => {
    head += "<text class='head' x='" + g.centres[k] + "' y='" + g.head_y
      + "' text-anchor='middle'>" + esc(label) + "</text>";
  });

  __L__ Each box holds two rows: the name above, the four cells below, their
  __L__ heights and baselines riding the payload beside the coordinates, so
  __L__ the drawer spells no number of its own.
  let nodes = "";
  g.nodes.forEach(n => {
    const layer = DATA.layers.find(l => l.name === n.name);
    const vacant = layer.files.length === 0;
    const move = changing() ? LAYER_MOVE[n.name] : null;
    nodes += "<g class='node" + (sel("layer", n.name) ? " sel" : "") + (vacant ? " vacant" : "")
      + (move ? " " + move : "") + "' data-layer='" + esc(n.name) + "'>"
      + "<rect x='" + n.x + "' y='" + n.y + "' width='" + n.width
      + "' height='" + n.height + "'/>"
      + "<text x='" + (n.x + g.inset) + "' y='" + (n.y + g.name_base) + "'>"
      + (move ? MOVED[move] + " " : "") + esc(n.name) + "</text>";
    const vals = [layer.files.length, layer.uses.length, layer.used_by.length,
                  layer.chain === null ? "–" : layer.chain];
    vals.forEach((v, k) => {
      const x0 = n.x + n.width - g.cell * (4 - k);
      const dim = (v === 0 && k < 3) || v === "–";
      nodes += "<line x1='" + (x0 + __NUDGE__) + "' y1='" + (n.y + g.cell_top)
        + "' x2='" + (x0 + __NUDGE__) + "' y2='" + (n.y + g.cell_foot) + "'/>"
        + "<text" + (dim ? " class='dim'" : "") + " x='" + g.centres[k]
        + "' y='" + (n.y + g.val_base) + "' text-anchor='middle'>" + esc(v) + "</text>";
    });
    nodes += "</g>";
  });

  __L__ The heads twin the wide stack's own, one per stroke colour the wires
  __L__ carry: a view imports no other view, so the figure that draws them
  __L__ holds them, the way the panel's drawings hold theirs. The stage's own
  __L__ width and height are asked on the tag, so the column stands at its
  __L__ natural size rather than scaled to the screen.
  return "<svg id='stack' width='" + g.width + "' height='" + g.height
    + "' viewBox='0 0 " + g.width + " " + g.height + "'>"
    + "<defs>" + """ + " + ".join('"%s"' % (ARROW % marks) for marks in MARKS) + r""" + "</defs>" + head + wires + nodes + "</svg>";
}""").replace("__L__", LINE).replace("__W__", f"{NARROW_W}"
       ).replace("__NUDGE__", f"{NUDGE}")


ARROW = ("<marker id='%s' markerUnits='userSpaceOnUse' markerWidth='6' "
         "markerHeight='6' orient='auto' refX='6' refY='3'><path d='M "
         "0 0 L 6 3 L 0 6 Z' fill='var(%s)'/></marker>")
