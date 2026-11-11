from archituner.presentation.model.stack_layout import INSET, NUDGE
from archituner.presentation.model.stack_wires import DROP
from archituner.theme import MARKS


def style():
    return r"""  __B__ Walk row 7: the stack is the view that opens and is drawn as the main
     view. It draws at its own natural size, the width and height of its own
     stage asked on the tag itself, so a wide screen shows the drawing one to
     one and its labels hold the size their token declares rather than being
     scaled to the column down to a size no one reads. */
  #stack .node rect { fill: var(--surface); stroke: var(--rule-strong); rx: var(--radius-m); }
  #stack .node text { font-size: var(--type-dense); fill: var(--ink); }
  __B__ The header row names the columns once for the whole stack: the labels
     wear the muted ink of a zero or a dash, and the dense type - the floor no
     label on the page drops below, the small type a wide screen's privilege
     that the phone's dress already answered. */
  #stack text.head { font-size: var(--type-dense); fill: var(--ink-muted); }
  #stack .node text.dim { fill: var(--ink-muted); }
  __B__ A divider is a hairline in the rule the page already draws its lines in,
     so four cells read as one box carrying numbers, not four boxes that touch. */
  #stack .node line { stroke: var(--rule); stroke-width: var(--hair); }
  #stack .node.vacant rect { fill: var(--surface-sunken); stroke-dasharray: var(--dash-vacant); }
  #stack .node.improved rect { fill: var(--change-improved); }
  #stack .node.unchanged rect { fill: var(--change-unchanged); }
  #stack .node.regressed rect { fill: var(--change-regressed); }
  #stack .node.dropped rect { fill: var(--surface-sunken); }
  __B__ Muted ink is a colour for the page's own ground, not for an outcome fill:
     it drops to 2.7:1 on the regressed one, so a muted value on a box that says
     what moved goes back to the full ink; a vacant box's sunken ground is the
     page's own and keeps the muted dress. */
  #stack .node:not(.vacant).improved text.dim,
  #stack .node:not(.vacant).unchanged text.dim,
  #stack .node:not(.vacant).regressed text.dim,
  #stack .node:not(.vacant).dropped text.dim { fill: var(--ink); }
  #stack .node.sel rect { stroke: var(--selected); stroke-width: var(--stroke-node); }
  #stack .node.sel text:first-of-type { font-weight: bold; }
  #stack .node, #stack .wire { cursor: pointer; }
  __B__ A wire is one right-angled path per drawn pair, dressed per pair as the
     arcs it replaces were: the state's own colour, the absence's dash, the
     divergence's weight, the selection's width, and the aside faded beside a
     held layer. */
  #stack .wire path { fill: none; stroke-width: var(--stroke-mark); }
  #stack .wire.convergence path { stroke: var(--state-convergence); }
  #stack .wire.absence path { stroke: var(--state-absence); stroke-dasharray: var(--dash-absence); }
  #stack .wire.divergence path { stroke: var(--state-divergence); stroke-width: var(--stroke-emphasis); }
  #stack .wire.improved path { stroke: var(--change-improved); stroke-width: var(--stroke-emphasis); }
  #stack .wire.unchanged path { stroke: var(--change-unchanged); }
  #stack .wire.regressed path { stroke: var(--change-regressed); stroke-width: var(--stroke-emphasis); }
  #stack .wire.dropped path { stroke: var(--rule); stroke-dasharray: var(--dash-dropped); }
  #stack .wire.sel path { stroke: var(--selected); stroke-width: var(--stroke-selection); }
  #stack .wire.aside { opacity: var(--fade-aside); }
  __B__ The mark a hue-blind reader reads instead: the state's own glyph on the
     wire's own lane, at the dense size on every width, haloed in the page's
     ground so it reads over a hop it stands beside. */
  #stack .wire text { font-size: var(--type-dense); fill: var(--ink); cursor: pointer; paint-order: stroke; stroke: var(--surface); stroke-width: calc(var(--u) * 3); }
  __B__ Hover answers in the drawing's own material - weight, bold - never
     a button's dress. */
  #stack .node:hover rect { stroke-width: var(--stroke-node); }
  #stack .wire:hover path { stroke-width: var(--stroke-selection); }
  #stack .wire text:hover { font-weight: bold; }""".replace("__B__", "/" + "*")


def script():
    return (r"""function drawLayers() {
  __L__ Decision 12: a stack in dependency order with every drawn pair one
  __L__ right-angled wire - an exit dock on the source's edge, its own lane in
  __L__ the left band, an entry dock with the arrow on the target's edge. An
  __L__ allowed pair runs left, solid where realised and dashed where nothing
  __L__ realises it; a realised forbidden pair runs right, mirrored on the
  __L__ boxes' right edge, so a divergence is found by position alone. Silence
  __L__ is not drawn - wires for the pairs where nothing happens would bury
  __L__ the ones where something does. The layout is a function of the order
  __L__ alone, so two runs draw one picture and the change reading can be laid
  __L__ over it. None of those numbers is computed here: the geometry rides
  __L__ the payload, stack_layout having laid the stage out once. What stays
  __L__ here is what the reader does to that shape - which pairs the filters
  __L__ leave visible - not the geometry.
  const shown = DATA.pairs.filter(p => p.state !== "silence" && pairVisible(p));

  let wires = "";
  const pairId = p => esc(p.source) + "->" + esc(p.target);
  shown.forEach(p => {
    const c = DATA.stack.wires[p.source + "->" + p.target];
    __L__ Where a wire runs is the drawing's shape and stays put in both
    __L__ readings; what it is drawn in is the reading. In the change reading
    __L__ the state's own dash and weight go with it, so the wire answers one
    __L__ question.
    const mark = changing() ? moveOf(p.source, p.target) : p.state;
    __L__ uxspec: one selection, and each view renders it in that view's own
    __L__ terms. A selected LAYER is a claim about its edges too, so the wires
    __L__ that do not touch it recede - the only way a single edge can be
    __L__ followed at nineteen nodes.
    const touched = !selection || selection.kind !== "layer"
      || p.source === selection.id || p.target === selection.id;
    const cls = "wire " + mark + (sel("pair", p.source + "->" + p.target) ? " sel" : "")
      + (touched ? "" : " aside");
    __L__ The run: out of the source's edge, squared over each standing lane it
    __L__ passes - never bent through a curve - down its own lane, and in to
    __L__ the target's edge the same way. The hops arrive in the order the run
    __L__ passes them, so the path walks the band monotonically whichever side
    __L__ of the boxes the wire runs on.
    const away = c.x > c.l ? 1 : -1;
    __L__ The wire is an arrow: its head lands on the layer being used and
    __L__ spends the mark's own colour, so the divergence side keeps its band
    __L__ and its weight and still answers the one question a wire is drawn
    __L__ to answer - which layer is used here. The wire is one group that
    __L__ answers its pair everywhere on it: the glyph travels with the path
    __L__ and stands again at the middle of the lane, the mark a hue-blind
    __L__ reader reads instead.
    wires += "<g class='" + cls + "' data-pair='" + pairId(p) + "'>"
      + "<path d='M " + c.x + " " + c.a
      + c.hops_out.map(x => " H " + (x + away * DATA.stack.hop) + " V " + (c.a - DATA.stack.hop)
        + " H " + (x - away * DATA.stack.hop) + " V " + c.a).join("")
      + " H " + c.l + " V " + c.b
      + c.hops_in.map(x => " H " + (x - away * DATA.stack.hop) + " V " + (c.b - DATA.stack.hop)
        + " H " + (x + away * DATA.stack.hop) + " V " + c.b).join("")
      + " H " + c.x + "' marker-end='url(#" + mark + ")' data-pair='" + pairId(p) + "'>"
      + GLYPH[p.state] + "<title>" + esc(p.source) + " → " + esc(p.target)
      + ": " + esc(mark) + "</title></path>"
      + "<text x='" + c.l + "' y='" + c.my + "' text-anchor='middle'>" + GLYPH[p.state]
      + "</text></g>";
  });

  __L__ A header row above the stack names the four columns once, muted, each
  __L__ label centred over the cells that carry its values.
  let head = "";
  ["files", "uses", "used by", "chain"].forEach((label, k) => {
    head += "<text class='head' x='" + DATA.stack.centres[k] + "' y='" + DATA.stack.head_y
      + "' text-anchor='middle'>" + esc(label) + "</text>";
  });

  let nodes = "";
  DATA.stack.nodes.forEach(n => {
    const layer = DATA.layers.find(l => l.name === n.name);
    const vacant = layer.files.length === 0;
    const move = changing() ? LAYER_MOVE[n.name] : null;
    nodes += "<g class='node" + (sel("layer", n.name) ? " sel" : "") + (vacant ? " vacant" : "")
      + (move ? " " + move : "") + "' data-layer='" + esc(n.name) + "'>"
      + "<rect x='" + n.x + "' y='" + n.y + "' width='" + n.width
      + "' height='" + n.height + "'/>"
      + "<text x='" + (n.x + __INSET__) + "' y='" + (n.y + n.height / 2 + __DROP__) + "'>"
      + (move ? MOVED[move] + " " : "") + esc(n.name) + "</text>";
    __L__ Four equal cells at the box's right, a hairline between them, each
    __L__ value centred under its header: files, uses, used by, and the chain
    __L__ from the entry layer - a dash where no chain reaches it. A zero and a
    __L__ dash sit muted, the quietest answers.
    const vals = [layer.files.length, layer.uses.length, layer.used_by.length,
                  layer.chain === null ? "–" : layer.chain];
    vals.forEach((v, k) => {
      const x0 = n.x + n.width - DATA.stack.cell * (4 - k);
      const dim = (v === 0 && k < 3) || v === "–";
      nodes += "<line x1='" + (x0 + __NUDGE__) + "' y1='" + n.y + "' x2='" + (x0 + __NUDGE__)
        + "' y2='" + (n.y + n.height) + "'/>"
        + "<text" + (dim ? " class='dim'" : "") + " x='" + DATA.stack.centres[k]
        + "' y='" + (n.y + n.height / 2 + __DROP__) + "' text-anchor='middle'>" + esc(v) + "</text>";
    });
    nodes += "</g>";
  });

  __L__ The caption this view used to carry below the drawing is gone: the
  __L__ question it answered left the page with the other large labels and is
  __L__ the Help's to carry now.
  __L__ The stage's own width and height are asked on the tag: the drawing
  __L__ stands at its natural size and the stylesheet sizes it to nothing - a
  __L__ drawing scaled to its column scales its labels with it, and on a wide
  __L__ screen they came out tiny.
  __L__ The heads are defined beside the wires they end, one per stroke colour
  __L__ the wires carry, so no filter shows a head the reading does not explain.
  __L__ The head's path spends its mark's own token from the sheet rather than
  __L__ the tag: paint grammar resolves no var(). userSpaceOnUse sizes a head
  __L__ in the drawing's own units, never a multiple of a stroke the emphasis
  __L__ rules thicken: six user units, the reference point at the tip.
  return "<svg id='stack' width='" + DATA.stack.width + "' height='" + DATA.stack.height
    + "' viewBox='0 0 " + DATA.stack.width + " " + DATA.stack.height + "'>"
    + "<defs>" + """
            + " + ".join('"%s"' % (ARROW % marks) for marks in MARKS) +
            r""" + "</defs>" + head + wires + nodes + "</svg>";
}""").replace("__L__", "/" + "/").replace("__INSET__", f"{INSET}"
     ).replace("__DROP__", f"{DROP}").replace("__NUDGE__", f"{NUDGE}")


ARROW = ("<marker id='%s' markerUnits='userSpaceOnUse' markerWidth='6' "
         "markerHeight='6' orient='auto' refX='6' refY='3'><path d='M "
         "0 0 L 6 3 L 0 6 Z' fill='var(%s)'/></marker>")


def heads():
    return ((r"""
  __B__ The heads the wires end in, coloured: each head's path spends its
     mark's own token from a rule, so a head lands in the colour its wire is
     drawn in on both grounds - the tag's own grammar resolves no var(). */
"""
             + "".join(["  #stack #%s path { fill: var(%s); }\n" % (mark, token)
                        for mark, token in MARKS])
             ).replace("__B__", "/" + "*"))
