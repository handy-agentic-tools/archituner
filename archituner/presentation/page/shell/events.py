LINE = "/" + "/"


SCRIPT = (r"""document.addEventListener("click", e => {
  const t = e.target.closest("[data-view],[data-pair],[data-layer],[data-file],[data-hit],"
    + "[data-isolate],[data-reset],[data-findings],[data-region],[data-reading],"
    + "[data-figure],[data-cmd]");
  if (!t) return;
  if (t.dataset.cmd) {
    asking = !asking;
    draw();
    """ + LINE +
          r""" Opened focused, because an opener that costs a click and then wants a
    """ + LINE +
          r""" second one before a key reaches the field is two interactions spent before
    """ + LINE +
          r""" the search has begun, and journey 7's whole budget is two. Closed, focus
    """ + LINE +
          r""" goes back to the control that was pressed - the redraw replaced the element
    """ + LINE +
          r""" it was on, and focus left on nothing sends a keyboard reader to the top.
    $(asking ? "#search" : "#ask button").focus();
    return;
  }
  """ + LINE +
          r""" Switching is switching, not adding: one reading replaces the other.
  if (t.dataset.reading) { reading = CHANGE ? t.dataset.reading : "state"; draw(); return; }
  """ + LINE +
          r""" A whole redraw, not the panel alone: the selection moved, so the outlines
  """ + LINE +
          r""" the last one left in the view have to go with it or the page shows a pair
  """ + LINE +
          r""" marked as selected beside a panel showing something else.
  if (t.dataset.findings) { selection = {kind: "findings", id: "all"}; draw(); return; }
  if (t.dataset.reset) {
    filters.state = new Set(STATES); filters.layer = new Set(DATA.order);
    filters.outcome = new Set(MOVES);
    filters.coverage = new Set(["mapped", "unmapped"]); filters.weight = 0;
  }
  else if (t.dataset.isolate) {
    const [axis, value] = t.dataset.isolate.split(":");
    if (axis === "coverage") {
      const set = filters.coverage;
      if (set.size === 1 && set.has(value)) set.add("mapped").add("unmapped");
      else { set.clear(); set.add(value); }
      draw();
    } else isolate(axis, value);
    return;
  }
  else if (t.dataset.view) current = t.dataset.view;
  else if (t.dataset.pair) selection = {kind: "pair", id: t.dataset.pair};
  """ + LINE +
          r""" The approved panel promises that Escape or a click on the box again
  """ + LINE +
          r""" shows the whole project, so a click on the layer already held clears the
  """ + LINE +
          r""" selection instead of setting it once more, and a click on another box
  """ + LINE +
          r""" still moves it. Only the layer box: the promise sits on the layer's panel,
  """ + LINE +
          r""" and a pair or a file has no reading in which the click that opened it
  """ + LINE +
          r""" should close it. `sel` is the reader the views already outline with, so
  """ + LINE +
          r""" the branch asks the same question the drawing asks and the two cannot
  """ + LINE +
          r""" drift apart. The redraw below is the one Escape shares, so the outlines
  """ + LINE +
          r""" the selection left in the view go with it here exactly as they go there:
  """ + LINE +
          r""" two spellings, one behaviour.
  else if (t.dataset.layer) selection = sel("layer", t.dataset.layer) ? null : {kind: "layer", id: t.dataset.layer};
  else if (t.dataset.file) selection = {kind: "file", id: t.dataset.file};
  else if (t.dataset.region) selection = {kind: "region", id: t.dataset.region};
  else if (t.dataset.figure) selection = {kind: "figure", id: t.dataset.figure};
  else if (t.dataset.hit) {
    const [kind, ...rest] = t.dataset.hit.split(":");
    selection = {kind, id: rest.join(":")};
    """ + LINE +
          r""" A hit selects what it names where the reader already is: a pair and a
    """ + LINE +
          r""" layer are drawn in the view that owns them, a file is drawn in the
    """ + LINE +
          r""" panel, so the view moves only for the first two and stays for the rest.
    current = {pair: "matrix", layer: "layers"}[kind] || current;
  }
  draw();
});
document.addEventListener("change", e => {
  const t = e.target;
  if (t.dataset && t.dataset.axis) {
    const set = filters[t.dataset.axis];
    t.checked ? set.add(t.value) : set.delete(t.value);
  } else if (t.id === "layerpick") {
    filters.layer = new Set(Array.from(t.selectedOptions).map(o => o.value));
  } else return;
  """ + LINE +
          r""" Only for the two controls above. A text field fires `change` when it loses
  """ + LINE +
          r""" focus having been edited, and the focus a search result takes is that loss:
  """ + LINE +
          r""" a redraw here rebuilt the row and destroyed the result between the reader
  """ + LINE +
          r""" pressing the mouse down and letting it up, so the hit was never clicked.
  """ + LINE +
          r""" Harmless while the field was static markup a redraw never reached.
  draw();
});
document.addEventListener("input", e => {
  if (e.target.id === "minw") { filters.weight = +e.target.value || 0; draw(); return; }
  """ + LINE +
          r""" The query is held rather than read off the field, because the field is built
  """ + LINE +
          r""" with the row and a redraw would otherwise take what the reader typed with it.
  if (e.target.id !== "search") return;
  query = e.target.value;
  $("#results").innerHTML = hits();
});

document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  """ + LINE +
          r""" uispec has the panel return to the whole project when the selection is
  """ + LINE +
          r""" cleared, and nothing on the page could clear one: every branch above assigns
  """ + LINE +
          r""" a selection and none assigns nothing. This is that path, and it adds no
  """ + LINE +
          r""" visible control to the page. The panel's builder reads the selection, so
  """ + LINE +
          r""" clearing it is what returns the panel to the overview.
  """ + LINE +
          r""" With the caret in the search field the key clears the field instead, which is
  """ + LINE +
          r""" what it means there and is the reason the branch is on the focused element
  """ + LINE +
          r""" rather than on the key alone.
  """ + LINE +
          r""" Guarded on the value, not on the field: an empty field has nothing to clear,
  """ + LINE +
          r""" and a key that does nothing there would leave a reader whose caret is in the
  """ + LINE +
          r""" search box with no way to shut the panel.
  if (e.target && e.target.id === "search" && e.target.value) {
    query = "";
    e.target.value = "";
    $("#results").innerHTML = "";
    return;
  }
  selection = null;
  draw();
});

draw();
""")
