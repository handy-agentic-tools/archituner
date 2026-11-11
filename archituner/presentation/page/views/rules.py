BLOCK = "/" + "*"


RULES = (r"""  """ + BLOCK +
          r""" Both grounds are declared, so the browser's own widgets - form controls,
     scrollbars, the canvas behind the page - follow the one in force instead of
     staying light under a dark page. */
  :root { color-scheme: light dark; }
  body { font: var(--type-body)/var(--line) var(--mono); margin: 0; display: flex;
    flex-wrap: wrap; height: 100vh; color: var(--ink); background: var(--surface); }
  #main { flex: 1 1 var(--main-w); min-width: 0; overflow: auto; padding: var(--step-4); }
  """ + BLOCK +
          r""" The panel is always open: at rest it carries the whole project, and a
     selection changes what it holds rather than whether it is there. So the two
     columns are stated once here - the main view grows from its own basis, the
     panel keeps its fixed width - and the wrap on the page lets the panel fall
     below the main column on a narrow screen rather than clip. What the panel
     draws is the panel view's own sheet, carried in beside this one; the seat
     it draws into is the shell's markup. */
  #detail { flex: 0 0 var(--panel-w); max-width: 100%; overflow: auto;
    border-left: var(--step-1) solid var(--rule); padding: var(--step-4); }
__PANEL_STYLE__
  """ + BLOCK +
          r""" uispec, "The command bar": one row, closed at rest and opened by the control
     above it. Closed by the builder emptying the region and dropping the
     marker, so with the marker gone this rule is the row's whole geometry and
     nothing shut keeps a box or a place in the tab order. */
  #cmd { height: 0; overflow: hidden; }
  #cmd[data-open] { height: auto; overflow: auto; display: flex; flex-wrap: wrap;
    align-items: center; gap: var(--step-3); padding: var(--step-3) 0; }
  #ask { margin-top: var(--step-3); }
  button { font: inherit; cursor: pointer; }
  """ + BLOCK +
          r""" Every button is the page's own: the nav tabs, a search hit and the reset
     kept the browser's widget dress - its typeface, its arrow cursor - so the
     bare rule above brings them into the mono face and gives the hand cursor
     every other control on the page already has; the tabs' own rule holds the
     spacing that keeps them apart. A tab is unboxed, so under the pointer it
     wears the active tab's underline rather than a lifted fill. */
  nav button { margin-right: var(--step-2); cursor: pointer; }
  nav button.active { font-weight: bold; text-decoration: underline; }
  nav button:hover { text-decoration: underline; }
  """ + BLOCK +
          r""" The panel's tab strip sits between the heading and the card, so its
     buttons dress as the page's own controls: the resting tab carries the page's
     ground and ink and reads bold, the set-aside one sinks. */
  #panel-tabs button { font: inherit; cursor: pointer; color: var(--ink-muted);
    background: var(--surface-sunken); border: var(--hair) solid var(--rule); }
  #panel-tabs button.on { color: var(--ink); background: var(--surface);
    border: var(--hair) solid var(--rule-strong); font-weight: bold; }
  #detail .head .label.unc { color: var(--unclaimed); }
  """ + BLOCK +
          r""" uispec region 2: the tree's name, then the verdict. Context rather than the
     answer, so it reads in the ink the page keeps for context, and verbatim -
     a directory name is an identifier and a case transform rewrites it. */
  #tree { color: var(--ink-muted); margin: var(--step-3) 0 var(--step-2); }
  """ + BLOCK +
          r""" One size, so a heading is a heading by weight, case and tracking. */
  h1 { font-size: var(--type-body); letter-spacing: var(--track-wide);
    text-transform: uppercase; margin: 0 0 var(--step-3); }
  h2 { font-size: var(--type-body); letter-spacing: var(--track-wide);
    text-transform: uppercase; color: var(--ink-muted); font-weight: bold;
    margin: var(--step-4) 0 var(--step-2); }
  #verdict.bad { color: var(--verdict-bad); }
  #verdict.good { color: var(--verdict-good); }
  table { border-collapse: collapse; }
  #matrix td, #matrix th { border: var(--hair) solid var(--rule); width: var(--cell);
    height: var(--cell-h); text-align: center; font-size: var(--type-small); cursor: pointer; }
  #matrix th { width: auto; padding: 0 var(--step-2); font-weight: normal; }
  td.convergence { background: var(--state-convergence); }
  td.divergence  { background: var(--state-divergence); }
  td.absence     { background: var(--state-absence); }
  td.silence     { background: var(--state-silence); color: var(--ink-muted); }
  """ + BLOCK +
          r""" Decision 8: the same marks in the change reading, carrying what the pair
     did instead of what it is. Never drawn beside the state reading - one mark
     answering two questions is read as the wrong one. `dropped` is not a fourth
     outcome: it is the pair the two readings do not both name. */
  td.improved    { background: var(--change-improved); }
  td.unchanged   { background: var(--change-unchanged); color: var(--ink-muted); }
  td.regressed   { background: var(--change-regressed); }
  td.dropped     { background: var(--surface-sunken); color: var(--ink-muted); }
  """ + BLOCK +
          r""" Measured 12 greyscale levels from the divergence fill, the tightest margin
     on the page; a cell that is not a pair should not sit inside the states'
     own tonal staircase at all. */
  td.diagonal    { background: var(--ink-muted); }
  td.sel { outline: var(--step-1) solid var(--selected); }
  .layerbox { border: var(--hair) solid var(--rule-strong); padding: var(--step-2) var(--step-3);
    margin: var(--step-2) 0; cursor: pointer; }
  .layerbox.sel { outline: var(--step-1) solid var(--selected); }
  """ + BLOCK +
          r""" The two shapes a reader can point at answer the pointer: a cell and a
     layerbox strengthen their border where they sit, an affordance that asks
     for the click the cursor already promised. */
  #matrix td:hover, .layerbox:hover { border-color: var(--rule-strong); }
__COVERAGE_STYLE__
  .unclaimed { color: var(--unclaimed); font-weight: bold; }
  #search { width: var(--search-w); }
  #minw { width: var(--number-w); }
  """ + BLOCK +
          r""" The command bar's controls are the page's own and wear its look: a field
     or a picker left in the browser's default style is a widget from another
     page sitting on this one, and it arrives light on the dark ground. The
     boxes take the ground's own accent, and a result button dresses like the
     keys the legend shows. */
  #search, #minw, #layerpick { font: inherit; color: var(--ink); background: var(--surface);
    border: var(--hair) solid var(--rule-strong); }
  input[type='checkbox'] { accent-color: var(--selected); }
  """ + BLOCK +
          r""" One button idiom: the legend's keys, a search hit and the two toggles
     wear one box - the page's ground and ink, the strong rule, the hairline's
     own padding - so no control keeps a dress of its own. The keys and the
     hits take a right margin; the toggles sit in the shellbar's own gap. */
  button.key, button.hit, #reading button, #ask button { font: inherit; cursor: pointer;
    color: var(--ink); border: var(--hair) solid var(--rule-strong); background: var(--surface);
    padding: var(--hair) var(--step-3); }
  button.key, button.hit { margin-right: var(--step-2); }
  .hidden { display: none; }
  """ + BLOCK +
          r""" A count rendered inside a legend key sits on a state or an outcome fill,
     and the muted ink this class used to take read 2.03:1 on the light ground
     and 1.41:1 on the dark one, as the two grounds then stood. Ink is the one
     colour already held to 4.5:1 against every fill on both grounds, so that is
     what the class takes. */
  .count { color: var(--ink); font-size: var(--type-small); }
  """ + BLOCK +
          r""" The same class also labels a zero in a table, a list entry's secondary
     line and the figure inside a heading, and every one of
     those sits on the page's own ground, where muted ink was never the defect.
     Left at ink they would read louder than the `h2` above them and than the
     tree's name at the top of the page, which is the hierarchy inverted. On the
     ground a count takes the ground's context ink, the same as `#tree`, `h2`
     and `#provenance`; only the legend's own span is on a fill. */
  p.count, td.count, li .count, h2 .count { color: var(--ink-muted); }
  .hiddencount { color: var(--unclaimed); font-size: var(--type-small); }
  button.key.convergence { background: var(--state-convergence); }
  button.key.divergence  { background: var(--state-divergence); }
  button.key.absence     { background: var(--state-absence); }
  button.key.silence     { background: var(--state-silence); }
  button.key.improved    { background: var(--change-improved); }
  button.key.unchanged   { background: var(--change-unchanged); }
  button.key.regressed   { background: var(--change-regressed); }
  button.key.dropped     { background: var(--surface-sunken); color: var(--ink-muted); }
  button.key.unclaimedkey { color: var(--unclaimed); font-weight: bold; }
  button.key.off { opacity: var(--fade-off); }
  """ + BLOCK +
          r""" One toggle, beside the legend. */
  #shellbar { display: flex; flex-wrap: wrap; align-items: center; gap: var(--step-3); }
  """ + BLOCK +
          r""" A boxed control answers the pointer by lifting off the ground it sits
     on, and the raised ground is scored against ink like every fill, on both
     grounds. The change reading's tallies are boxed controls too, so they
     join the one lift. */
  button.key:hover, button.hit:hover, #reading button:hover, #ask button:hover,
  #panel-tabs button:hover, button.tally:hover { background: var(--surface-raised); }
  #reading button.on, #ask button.on { font-weight: bold; text-decoration: underline; }
  """ + BLOCK +
          r""" Marked disabled rather than `disabled`: walk row 5 hangs the explanation on
     this button's tooltip, and chromium paints no tooltip over an actually
     disabled control and gives the keyboard no way to reach it either. The
     handler already refuses the switch when no baseline is stored, so the
     attribute was saying a second time what the code says once. */
  #reading button[aria-disabled] { color: var(--ink-muted); background: var(--surface-sunken);
    cursor: not-allowed; }
  #provenance { color: var(--ink-muted); font-size: var(--type-small);
    margin: var(--step-2) 0; }
  #provenance code { background: var(--surface-sunken); padding: 0 var(--step-1); }
  .axis { margin: var(--step-1) 0; }
__LAYERS_STYLE__
  .empty { border: var(--hair) solid var(--unclaimed); padding: var(--step-3); }
  """ + BLOCK +
          r""" The empty view's one control - the way back to a drawing - answers the
     pointer as the page's controls do: the hand over it, the lift on hover. */
  button[data-reset] { cursor: pointer; }
  button[data-reset]:hover { background: var(--surface-raised); }
  .tallies { margin: var(--step-2) 0; }
  button.tally { font: inherit; font-size: var(--type-small); background: none;
    border: var(--hair) solid var(--rule); cursor: pointer; margin-right: var(--step-2);
    padding: var(--hair) var(--step-3); color: var(--ink); }
  """ + BLOCK +
          r""" One ring for every control the keyboard can reach, in the selection's
     own colour and offset by the unit itself; the ring holds the two-pixel
     floor WCAG's focus appearance asks for, so it survives the unit shrinking
     on a narrow viewport. */
  button:focus-visible, input:focus-visible, select:focus-visible
    { outline: var(--focus-ring) solid var(--selected); outline-offset: var(--focus-gap); }
""")
