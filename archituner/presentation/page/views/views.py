LINE = "/" + "/"


SCRIPT = (r"""function emptyState() {
  """ + LINE +
          r""" The button is what is actionable and stays; the sentence that named which
  """ + LINE +
          r""" filter emptied the view left with the other large labels and is the
  """ + LINE +
          r""" Help's to carry now. The filters are still walked, because they are the
  """ + LINE +
          r""" page's own test for whether there is anything to draw.
  """ + LINE +
          r""" The mark axis is not blamed here: since walk row 3 took its checkboxes away
  """ + LINE +
          r""" the only things that write it are the legend's isolate and the reset, and
  """ + LINE +
          r""" neither can leave it empty.
  const blame = [];
  if (!filters.layer.size) blame.push("every layer");
  if (!filters.coverage.size) blame.push("both file-coverage values");
  if (filters.weight > Math.max(0, ...DATA.pairs.map(p => p.imports.length)))
    blame.push("edge weight ≥ " + filters.weight + ", above every realised pair");
  return blame.length
    ? "<p class='empty'><button data-reset='1'>show everything</button></p>"
    : "";
}

function drawMatrix() {
  let h = "<table id='matrix'><tr><th></th>";
  DATA.order.forEach(t => h += "<th>" + esc(t) + "</th>");
  h += "</tr>";
  DATA.order.forEach(s => {
    h += "<tr><th>" + esc(s) + "</th>";
    DATA.order.forEach(t => {
      if (s === t) { h += "<td class='diagonal'></td>"; return; }
      const p = pairAt[s + "->" + t];
      """ + LINE +
          r""" A pair the payload leaves undecided still owns its cell: the grid counts
      """ + LINE +
          r""" layer pairs, not decided ones, so the cell stands empty the way the
      """ + LINE +
          r""" diagonal's does rather than the drawing stopping where the payload does.
      if (!p) { h += "<td></td>"; return; }
      """ + LINE +
          r""" The same grid either way: what the cell carries is the reading, and the
      """ + LINE +
          r""" reading is one at a time.
      const mark = changing() ? moveOf(s, t) : p.state;
      const glyph = changing() ? MOVED[mark] : GLYPH[p.state];
      const cls = mark + (pairVisible(p) ? "" : " hidden")
        + (sel("pair", s + "->" + t) ? " sel" : "");
      h += "<td class='" + cls + "' data-pair='" + esc(s) + "->" + esc(t) + "' title='"
        + esc(s) + " → " + esc(t) + ": " + esc(mark) + "'>" + esc(glyph) + "</td>";
    });
    h += "</tr>";
  });
  h += "</table>";
  return h;
}

__LAYERS_SCRIPT__

__NARROW_SCRIPT__

function drawFindings() {
  """ + LINE +
          r""" Fact above, what produced it muted below - the same two-line shape a pair's
  """ + LINE +
          r""" realising imports use, because a finding a reader cannot trace back to a
  """ + LINE +
          r""" contract line or an import is a claim the page is making on its own.
  if (!DATA.findings.length) return "<p class='count'>no findings</p>";
  return "<ul>" + DATA.findings.map(f => "<li>" + esc(f.text)
    + "<br><span class='count'>from " + esc(f.produced_by) + "</span></li>").join("") + "</ul>";
}

__COVERAGE_SCRIPT__

function figureMembers(kind, id) {
  """ + LINE +
          r""" What a figure counts, as the files it counts - so the detail panel can list
  """ + LINE +
          r""" them and the reader can go on to any one of them. The pair figures went
  """ + LINE +
          r""" with the view that drew them; a count that opens nothing has no button.
  if (kind === "fmove")
    return {title: id + " since the stored baseline",
            files: DATA.files.filter(f => CHANGE.files[f.path] === id).map(f => f.path)};
  if (kind === "fdropped")
    return {title: "in no comparison",
            files: DATA.files.filter(f => !(f.path in CHANGE.files)).map(f => f.path)};
}

function sel(kind, id) { return selection && selection.kind === kind && selection.id === id; }

function drawHint() {
  """ + LINE +
          r""" The panel's promise, in words that name no side: a narrow screen has
  """ + LINE +
          r""" no edge for a panel to sit beside, so the click itself is what the
  """ + LINE +
          r""" words explain. The wide page hides the line, and the hint stays one
  """ + LINE +
          r""" line that answers the selection on screen.
  $(".hint").textContent = selection && selection.kind === "layer"
    ? "Click the box again to see the whole project."
    : "Click a box to see that layer.";
}

function draw() {
  $("#nav").innerHTML = views.map(v =>
    "<button class='" + (v === current ? "active" : "") + "' data-view='" + esc(v) + "'>"
    + esc(v) + "</button>").join("");
  const empty = emptyState();
  """ + LINE +
          r""" The layers view draws the phone's column under the width threshold the
  """ + LINE +
          r""" stylesheet keys the phone dress on: one reading, one figure per width,
  """ + LINE +
          r""" chosen at draw time so a resize crosses with one redraw.
  $("#view").innerHTML = empty || {matrix: drawMatrix,
    layers: PHONE.matches ? drawColumn : drawLayers,
    coverage: drawCov}[current]();
  drawTree();
  verdict();
  drawReading();
  drawLegend();
  drawAsk();
  drawCmd();
  drawHint();
  drawDetail();
}

""")
