LINE = "/" + "/"


SCRIPT = ( LINE +
          r""" --- the shell: four filter axes, each stating what it hides -----------------
""" + LINE +
          r""" The default is everything visible: a reader arrives at a complete picture and
""" + LINE +
          r""" narrows it, rather than discovering something was hidden from the start.
const STATES = ["convergence", "divergence", "absence", "silence"];
const GLYPH = __GLYPH_MAP__;
const filters = {
  state: new Set(STATES),
  outcome: new Set(MOVES),
  layer: new Set(DATA.order),
  coverage: new Set(["mapped", "unmapped"]),
  weight: 0,
};

function isolate(axis, value) {
  """ + LINE +
          r""" Decision 14: clicking a legend entry shows only that state; clicking the
  """ + LINE +
          r""" isolated one again restores all four. One interaction, which is the budget.
  const all = axis === "state" ? STATES : axis === "outcome" ? MOVES : DATA.order;
  const set = filters[axis];
  if (set.size === 1 && set.has(value)) all.forEach(v => set.add(v));
  else { set.clear(); set.add(value); }
  draw();
}

""" + LINE +
          r""" The mark axis of whichever reading is on screen: one filter, read two ways,
""" + LINE +
          r""" so switching the reading switches what the axis means and never adds a second.
const onMarkAxis = p => changing()
  ? filters.outcome.has(moveOf(p.source, p.target))
  : filters.state.has(p.state);

function pairVisible(p) {
  return onMarkAxis(p)
    && filters.layer.has(p.source) && filters.layer.has(p.target)
    && p.imports.length >= filters.weight;
}

function fileVisible(f) {
  return filters.coverage.has(f.layer ? "mapped" : "unmapped")
    && (!f.layer || filters.layer.has(f.layer));
}

function hiddenCounts() {
  """ + LINE +
          r""" Per axis, not one total: a filter that hides without saying so turns a
  """ + LINE +
          r""" partial view into a false one, and a single number cannot name the cause.
  """ + LINE +
          r""" The mark axis keeps its count even though it left the filter row - the count
  """ + LINE +
          r""" goes where the axis went, to the legend. It is one figure across whichever
  """ + LINE +
          r""" reading is on screen, because the legend's own entries carry the totals per
  """ + LINE +
          r""" mark and what is missing from them is how many pairs the axis is holding
  """ + LINE +
          r""" back right now.
  const pairs = DATA.pairs, files = DATA.files;
  return {
    mark: pairs.filter(p => !onMarkAxis(p)).length,
    layer: pairs.filter(p => onMarkAxis(p)
      && !(filters.layer.has(p.source) && filters.layer.has(p.target))).length,
    coverage: files.filter(f => !filters.coverage.has(f.layer ? "mapped" : "unmapped")).length,
    weight: pairs.filter(p => onMarkAxis(p) && p.imports.length < filters.weight).length,
  };
}

function drawLegend() {
  """ + LINE +
          r""" Walk row 4: one row on the page carries a state, a count, or a way to filter
  """ + LINE +
          r""" by state, and this is that row. Decision 14 made a legend entry the filter
  """ + LINE +
          r""" itself, so every entry here is a control and every count here reaches its
  """ + LINE +
          r""" members - which is what let the counts row and the state checkboxes go.
  """ + LINE +
          r""" One legend per reading, never both: the four states, or the three outcomes
  """ + LINE +
          r""" and the pairs the two readings do not share.
  const held = hiddenCounts().mark;
  const marks = changing()
    ? OUTCOMES.map(o =>
        "<button class='key " + o + (filters.outcome.has(o) ? "" : " off")
        + "' data-isolate='outcome:" + esc(o) + "' title='show only " + esc(o) + "'>"
        + MOVED[o] + " " + o + " <span class='count'>" + CHANGE.counts[o]
        + "</span></button>").join("")
      + (CHANGE.dropped ? "<button class='key dropped"
         + (filters.outcome.has("dropped") ? "" : " off")
         + "' data-isolate='outcome:dropped' title='show only the pairs not compared'>"
         + esc(MOVED.dropped) + " not compared <span class='count'>" + esc(CHANGE.dropped)
         + "</span></button>" : "")
    : STATES.map(s =>
        "<button class='key " + s + (filters.state.has(s) ? "" : " off")
        + "' data-isolate='state:" + esc(s) + "' title='show only " + esc(s) + "'>"
        + GLYPH[s] + " " + s + " <span class='count'>" + DATA.counts[s]
        + "</span></button>").join("");
  """ + LINE +
          r""" `findings` is the one count the legend did not carry, and it carried it
  """ + LINE +
          r""" nowhere else once the counts row went. It is an entry rather than a filter:
  """ + LINE +
          r""" it opens what it counts, which is the same promise the other five make.
  $("#legend").innerHTML = marks
    + "<button class='key unclaimedkey" + (filters.coverage.has("unmapped") ? "" : " off")
    + "' data-isolate='coverage:unmapped'>unclaimed <span class='count'>"
    + DATA.files.filter(f => !f.layer).length + "</span></button>"
    + "<button class='key' data-findings='1'>findings <span class='count'>"
    + esc(DATA.findings.length) + "</span></button>"
    """ + LINE +
          r""" The axis states what it hides, in the row the axis now lives in. The
    """ + LINE +
          r""" entries' own counts are totals and do not move when one is switched off,
    """ + LINE +
          r""" so without this the mark axis would hide pairs and say nothing - which is
    """ + LINE +
          r""" the one thing uxspec names as turning a partial view into a false one.
    + (held ? " <span class='hiddencount'>" + esc(held) + " pair(s) hidden</span>" : "");
}

""" + LINE +
          r""" --- the command bar ---------------------------------------------------------
""" + LINE +
          r""" uispec: search and the layer, file and edge-weight filters are one row, closed
""" + LINE +
          r""" at rest and opened on demand. The page opens as a report and becomes an
""" + LINE +
          r""" instrument on the first interaction, so at rest it shows the reader an answer
""" + LINE +
          r""" rather than the apparatus for asking further questions.
let asking = false;
let query = "";

function hits() {
  """ + LINE +
          r""" What the query matches, rebuilt with the row rather than only on a keystroke,
  """ + LINE +
          r""" so a redraw the reader caused elsewhere - selecting one of these, switching a
  """ + LINE +
          r""" view - does not empty the results underneath them.
  """ + LINE +
          r""" Folded here rather than on the way in: what is held is what the reader typed,
  """ + LINE +
          r""" and a field redrawn from a folded copy hands them back text they did not write.
  const q = query.toLowerCase().trim();
  if (!q) return "";
  """ + LINE +
          r""" Eight is what one row can hold apart, and a row that stops at eight with
  """ + LINE +
          r""" more matched says nothing about the rest it is holding back: the row names
  """ + LINE +
          r""" how many it shows of how many matched, as a compact label beside the hits
  """ + LINE +
          r""" it is about - never a sentence of its own, the row stays one row.
  const found = INDEX.filter(i => i.text.includes(q));
  const shown = found.slice(0, 8);
  const row = shown.map(h => "<button class='hit' data-hit='"
    + esc(h.kind + ":" + h.id) + "'>[" + esc(h.kind) + "] " + esc(h.id)
    + "</button>").join(" ") || "<span class='count'>no matches</span>";
  return found.length > shown.length
    ? row + " <span class='count'>" + esc(shown.length) + " of "
      + esc(found.length) + "</span>"
    : row;
}

function drawAsk() {
  """ + LINE +
          r""" The one control that opens the row, and the only part of it on screen at
  """ + LINE +
          r""" rest. It carries what the row's own axes are holding back while they are out
  """ + LINE +
          r""" of sight: a filter that hides without saying so turns a partial view into a
  """ + LINE +
          r""" false one, and a legend key can narrow the file axis from up here with the
  """ + LINE +
          r""" row shut. Which axis is holding what is inside, one click away. The mark axis
  """ + LINE +
          r""" is the legend's own and says so there, so it is not counted again here.
  """ + LINE +
          r""" Per axis and never added up: two of these count pairs and one counts files,
  """ + LINE +
          r""" and a pair the layer axis holds may be one the weight axis holds too, so a
  """ + LINE +
          r""" single number over the three would be a figure of nothing.
  const hidden = hiddenCounts();
  const shut = [hidden.layer ? hidden.layer + " pair(s) by layer" : "",
                hidden.weight ? hidden.weight + " pair(s) by weight" : "",
                hidden.coverage ? hidden.coverage + " file(s)" : ""]
    .filter(Boolean).join(", ");
  $("#ask").innerHTML = "<button data-cmd='1'" + (asking ? " class='on'" : "")
    + " aria-expanded='" + asking + "' aria-controls='cmd'"
    + " title='search, and the layer, file and edge-weight filters'>"
    + (asking ? "hide search and filters" : "search and filters")
    + (!asking && shut ? " <span class='hiddencount'>" + esc(shut) + " hidden</span>" : "")
    + "</button>";
}

function drawCmd() {
  """ + LINE +
          r""" Walk row 3 left this row three axes: the mark axis is the legend's, and what
  """ + LINE +
          r""" is here is what no other control on the page offers. Measured in chromium on
  """ + LINE +
          r""" 2026-08-23, clicking a legend key flipped the checkbox that stood for the
  """ + LINE +
          r""" same mark - one filter wearing two coats, and the row wearing the second one
  """ + LINE +
          r""" also named every mark a second time.
  """ + LINE +
          r""" Closed is the shape the command row keeps to itself, the panel being
  """ + LINE +
          r""" always open now: the region is emptied and the marker the stylesheet
  """ + LINE +
          r""" keys the row's height on is dropped, so a shut row holds no
  """ + LINE +
          r""" control - not a clipped one, and not one the tab key can still reach.
  const bar = $("#cmd");
  bar.toggleAttribute("data-open", asking);
  if (!asking) { bar.innerHTML = ""; return; }
  const hidden = hiddenCounts();
  const note = (axis, what) => hidden[axis]
    ? " <span class='hiddencount'>" + esc(hidden[axis]) + " " + esc(what) + " hidden</span>" : "";
  """ + LINE +
          r""" A placeholder is not a name: it goes the moment the reader types, and the
  """ + LINE +
          r""" other three axes here are each labelled by the word in front of them.
  let h = "<span class='axis'><input id='search' value='" + esc(query)
    + "' aria-label='search layers, files, modules, prose'"
    + " placeholder='search layers, files, modules, prose'> "
    + "<span id='results'>" + hits() + "</span></span>";
  h += "<span class='axis'>layer: <select id='layerpick' multiple size='1'>"
    + DATA.order.map(l => "<option value='" + esc(l) + "'"
      + (filters.layer.has(l) ? " selected" : "") + ">" + esc(l) + "</option>").join("")
    + "</select>" + note("layer", "pair(s)") + "</span>";
  h += "<span class='axis'>files: " + ["mapped", "unmapped"].map(c =>
    "<label><input type='checkbox' data-axis='coverage' value='" + esc(c) + "'"
    + (filters.coverage.has(c) ? " checked" : "") + ">" + esc(c) + "</label>").join(" ")
    + note("coverage", "file(s)") + "</span>";
  h += "<span class='axis'>edge weight ≥ <input id='minw' type='number' min='0' value='"
    + esc(filters.weight) + "'>" + note("weight", "pair(s)") + "</span>";
  bar.innerHTML = h;
}

""")
