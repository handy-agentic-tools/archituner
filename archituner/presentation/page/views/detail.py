LINE = "/" + "/"


SCRIPT = (r"""function drawDetail() {
  const d = $("#panel-body"), n = $("#panel-name");
  drawPanelTabs();
  """ + LINE +
          r""" The sheet's mark, set beside the selection that raises it: the
  """ + LINE +
          r""" stylesheet keys the raised dress on it, so a held box lifts the
  """ + LINE +
          r""" panel over the drawing on a phone and a cleared one settles it
  """ + LINE +
          r""" back below, the one spelling of that move for every selection.
  $("#detail").toggleAttribute("data-sheet", !!selection);
  """ + LINE +
          r""" The panel is one seat the shell holds open: a name over a body. At rest
  """ + LINE +
          r""" the name is the whole project's and the body is the overview the panel
  """ + LINE +
          r""" view draws; a selection replaces both with its own name and its own
  """ + LINE +
          r""" detail. Every path to a selection ends in this function, so one call
  """ + LINE +
          r""" moves the seat whole and a name from one selection cannot sit over the
  """ + LINE +
          r""" body of another.
  if (!selection) { n.innerHTML = "Whole project"; d.innerHTML = panelTab === "files" ? drawAllFiles() : drawOverview(); return; }
  if (selection.kind === "findings") {
    """ + LINE +
          r""" The contract's own prose sits here beside the tool's findings, which is
    """ + LINE +
          r""" where techspec asks for it; where it finally lives is O2's to answer.
    n.innerHTML = "findings <span class='count'>" + esc(DATA.findings.length) + "</span>";
    d.innerHTML = drawFindings()
      + "<h2>naming rules <span class='count'>stated, never checked</span></h2>"
      + (DATA.naming.length ? "<ul>" + DATA.naming.map(n => "<li>" + esc(n) + "</li>").join("") + "</ul>"
         : "<p class='count'>none stated</p>")
      + "<h2>invariants <span class='count'>" + esc(DATA.invariants.length)
      + ", stated, never checked</span></h2>"
      + (DATA.invariants.length ? "<ul>" + DATA.invariants.map(i => "<li>" + esc(i) + "</li>").join("")
         + "</ul>" : "<p class='count'>none stated</p>");
    return;
  }
  if (selection.kind === "pair") {
    const p = pairAt[selection.id];
    const move = changing() ? moveOf(p.source, p.target) : null;
    n.innerHTML = esc(p.source) + " → " + esc(p.target);
    d.innerHTML = (move
       ? "<p><b>" + MOVED[move] + " " + move + "</b> " + (move === "dropped"
          ? "" : "since the stored baseline") + "</p>"
       : "<p><b>" + esc(p.state) + "</b> (" + esc(p.kind) + ")</p>")
      + (p.reason ? "<p>" + esc(p.reason) + "</p>" : "")
      + (p.imports.length ? "<h2>realised by</h2><ul>" + p.imports.map(i =>
          "<li>" + esc(i.file) + "<br><span class='count'>imports " + esc(i.module) + "</span></li>").join("") + "</ul>"
         : "<p class='count'>no import realises this pair</p>")
      """ + LINE +
          r""" Beside the state and the witnesses, in the two-line shape a finding
      """ + LINE +
          r""" uses: what to do above, what it was drawn from muted below. A pair the
      """ + LINE +
          r""" reading proposes nothing for shows nothing - the page has none of its
      """ + LINE +
          r""" own to offer.
      + (p.remedy ? "<h2>remedy</h2><ul><li>" + esc(p.remedy.text)
          + "<br><span class='count'>from " + esc(p.remedy.produced_by)
          + "</span></li></ul>" : "");
  } else if (selection.kind === "layer") {
    const l = DATA.layers.find(x => x.name === selection.id);
    n.innerHTML = esc(l.name);
    d.innerHTML = (changing() ? "<p><b>" + MOVED[LAYER_MOVE[l.name]] + " " + LAYER_MOVE[l.name]
         + "</b> across its own pairs since the stored baseline</p>" : "")
      + "<p class='count'>" + l.globs.join("<br>") + "</p>"
      + (l.responsibility ? "<p><b>Responsibility.</b> " + esc(l.responsibility) + "</p>" : "<p class='count'>no Layers table row</p>")
      + (l.rationale ? "<p><b>Rationale.</b> " + esc(l.rationale) + "</p>" : "")
      + "<p>" + esc(l.files.length) + " file(s)</p>";
  } else if (selection.kind === "figure") {
    const [kind, id] = selection.id.split(/:(.*)/);
    const found = figureMembers(kind, id);
    n.innerHTML = found.title;
    d.innerHTML = (found.files
      ? "<p class='count'>" + esc(found.files.length) + " file(s)</p><ul>"
        + found.files.map(m => "<li data-file='" + esc(m) + "'>" + esc(m) + "</li>").join("") + "</ul>"
      : "<p class='count'>" + esc(found.pairs.length) + " pair(s)</p><ul>"
        + found.pairs.map(p => "<li data-pair='" + esc(p.source) + "->" + esc(p.target) + "'>"
            + esc(p.source) + " → " + esc(p.target) + " <span class='count'>" + esc(p.state) + "</span></li>").join("")
        + "</ul>");
  } else if (selection.kind === "region") {
    const box = DATA.regions.find(b => b.id === selection.id);
    const boxMove = changing() && !box.opened ? regionMove(box.members) : null;
    n.innerHTML = esc((box.path || ".") + (box.opened ? "/" : ""));
    d.innerHTML = (boxMove ? "<p><b>" + MOVED[boxMove] + " " + boxMove + "</b></p>" : "")
      + "<p>" + (box.opened ? "directory"
                 : box.layer ? "claimed by <b>" + esc(box.layer) + "</b>"
                 : "<span class='unclaimed'>no layer claims these</span>") + "</p>"
      + "<p>" + esc(box.files) + " file(s)</p>"
      + (box.members.length
         ? "<ul>" + box.members.map(m => "<li data-file='" + esc(m) + "'>" + esc(m) + "</li>").join("") + "</ul>"
         : "<p class='count'>counted from the boxes inside it</p>");
  } else if (selection.kind === "file") {
    const f = DATA.files.find(x => x.path === selection.id);
    n.innerHTML = esc(f.path);
    d.innerHTML = (changing() ? "<p><b>" + MOVED[fileMove(f)] + " " + fileMove(f) + "</b> "
         + (fileMove(f) === "dropped" || relocation(f.path)
            ? "" : "since the stored baseline") + "</p>" : "")
      + "<p>layer: " + (f.layer ? esc(f.layer) : "<span class='unclaimed'>unclaimed</span>") + "</p>"
      + "<h2>imports</h2><ul>" + (f.imports.map(i => "<li>" + esc(i.module)
        + " <span class='count'>" + (i.layer ? esc(i.layer) : "unclaimed") + "</span></li>").join("") || "<li class='count'>nothing inside the tree</li>") + "</ul>"
      + "<h2>imported by</h2><ul>" + (f.importers.map(i => "<li>" + esc(i) + "</li>").join("") || "<li class='count'>nothing</li>") + "</ul>";
  }
}

const INDEX = [];
DATA.layers.forEach(l => INDEX.push({kind: "layer", id: l.name,
  text: (l.name + " " + l.responsibility + " " + l.rationale).toLowerCase()}));
DATA.files.forEach(f => INDEX.push({kind: "file", id: f.path,
  text: (f.path + " " + (f.module || "")).toLowerCase()}));
DATA.pairs.forEach(p => INDEX.push({kind: "pair", id: p.source + "->" + p.target,
  text: (p.source + " -> " + p.target + " " + p.reason).toLowerCase()}));
""" + LINE +
          r""" The all-files card: one group per layer in the order the layers
  """ + LINE +
          r""" depend in, with the files no layer claims standing last under the
  """ + LINE +
          r""" accent, the way the coverage view groups them. A row reads the
  """ + LINE +
          r""" file's own records - its path, the imports it holds, the importers
  """ + LINE +
          r""" that reach it - so a count here is the count its own page shows.
function drawAllFiles() {
  let h = "";
  DATA.order.concat(["unclaimed"]).forEach(layer => {
    const rows = DATA.files.filter(f =>
      layer === "unclaimed" ? !f.layer : f.layer === layer);
    if (!rows.length) return;
    h += "<div class='block'><div class='head'><span class='label"
      + (layer === "unclaimed" ? " unc" : "") + "'>"
      + (layer === "unclaimed" ? "unclaimed" : esc(layer)) + "</span></div>"
      + "<ul class='flist'><li class='h'><span>file</span>"
      + "<span class='n'>imports</span><span class='n'>imported by</span></li>"
      + rows.map(f => "<li data-file='" + esc(f.path) + "'><span class='p'>"
        + esc(f.path) + "</span><span class='n'>" + esc(f.imports.length)
        + "</span><span class='n'>" + esc(f.importers.length) + "</span></li>").join("")
      + "</ul></div>";
  });
  return h;
}
""" + LINE +
          r""" One click moves one card in: the tab's own name rides the button,
  """ + LINE +
          r""" and the redraw is the panel's own, so the strip re-dresses and the
  """ + LINE +
          r""" card is drawn by the same path every redraw takes.
document.addEventListener("click", e => {
  const t = e.target.closest("[data-panel-tab]");
  if (!t) return;
  panelTab = t.dataset.panelTab;
  drawDetail();
});

""" + LINE +
          r""" The cross the sheet carries: a phone has no Escape key, so the closing
""" + LINE +
          r""" Escape does is a control of the panel's own. It clears the selection
""" + LINE +
          r""" and redraws, exactly the branch Escape takes - one behaviour, two
""" + LINE +
          r""" spellings, the same promise kept on every width.
document.addEventListener("click", e => {
  const t = e.target.closest("[data-close]");
  if (!t || !t.dataset.close) return;
  selection = null;
  draw();
});

""")
