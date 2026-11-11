BLOCK = "/" + "*"


GROUND = (r"""  """ + BLOCK +
          r""" Decision 13: the page's whole visual vocabulary, declared once. Every rule
     below reads a token; a colour or a dimension written literally in a rule is
     a defect, because that is the one place a value can drift unseen. */
  :root {
    --ink:            __light-ink__;
    --ink-muted:      __light-ink-muted__;
    --surface:        __light-surface__;
    --surface-sunken: __light-surface-sunken__;
    --rule:           __light-rule__;
    --rule-strong:    __light-rule-strong__;

    """ + BLOCK +
          r""" One hue per conformance state. Four states, four fills, and each carries a
       glyph as well, so the reading survives greyscale. */
    --state-convergence: __light-state-convergence__;
    --state-divergence:  __light-state-divergence__;
    --state-absence:     __light-state-absence__;
    --state-silence:     __light-state-silence__;

    """ + BLOCK +
          r""" One per change outcome: two poles and a neutral middle, so better and
       worse are opposite rather than merely different. */
    --change-improved:  __light-change-improved__;
    --change-unchanged: __light-change-unchanged__;
    --change-regressed: __light-change-regressed__;

    """ + BLOCK +
          r""" What no layer claims. The accent, and the only accent - a hue no state
       and no outcome uses, because the legend puts it beside them and an orange
       there is a second divergence to the eye. */
    --unclaimed:      __light-unclaimed__;
    --selected:       __light-selected__;

    """ + BLOCK +
          r""" The verdict's own two colours, per ground. They were the state fills put
       through `filter: brightness()`, which reads the ground it is on: the same
       filter that darkens a red to legible on white drives it into the
       background on black. */
    --verdict-bad:  __light-verdict-bad__;
    --verdict-good: __light-verdict-good__;

    """ + BLOCK +
          r""" The one base unit every dimension on the page computes from. At the
       browser's default font size it resolves to exactly one pixel, so the
       ladder below holds the pixels the page was approved at; it follows the
       reader's font-size preference, and on a viewport narrower than the
       clamp's lower cross it shrinks with the width - the floor keeps the
       micro type readable - while it never grows, density on a large
       monitor being the point of the tool. */
    --u: __light-u__;

    --step-1: __light-step-1__;  --step-2: __light-step-2__;  --step-3: __light-step-3__;  --step-4: __light-step-4__;

    """ + BLOCK +
          r""" A hairline is not a spacing step: it is the unit itself, the thinnest a
       border can be and stay one device pixel. */
    --hair: __light-hair__;

    """ + BLOCK +
          r""" Two sizes below the body step, for the grid and the treemap, where the
       label has to fit a cell rather than a line of prose. */
    --type-micro: __light-type-micro__;  --type-dense: __light-type-dense__;

    """ + BLOCK +
          r""" The four fixed extents on the page. Everything else is content-sized,
       and these are the ones a density pass has to reach. The main column's
       basis joined them when the panel opened for good beside it. */
    --cell-h: __light-cell-h__;  --main-w: __light-main-w__;  --panel-w: __light-panel-w__;  --search-w: __light-search-w__;  --number-w: __light-number-w__;
    --type-small: __light-type-small__;  --type-body: __light-type-body__;
    --cell: __light-cell__;

    """ + BLOCK +
          r""" Decision 29: terminal inspired. One stack, nothing fetched over the
       network, so the page stays self-contained. One size does the work and
       hierarchy comes from weight, case and colour - the head and hero
       aliases are gone, and every heading reads the body step. */
    --mono: __light-mono__;
    --line: __light-line__;
    --track-wide: __light-track-wide__;

    """ + BLOCK +
          r""" The strokes, the dashes and the two fades, every dimension among them
       a calc() off the unit: in SVG a CSS length is a user unit, so one
       ladder weights the drawings and the rules. The two fades are numbers,
       not dimensions, and stay flat. */
    --stroke-hair: __light-stroke-hair__;  --stroke-mark: __light-stroke-mark__;  --stroke-node: __light-stroke-node__;
    --stroke-emphasis: __light-stroke-emphasis__;  --stroke-selection: __light-stroke-selection__;
    --dash-vacant: __light-dash-vacant__;  --dash-absence: __light-dash-absence__;  --dash-dropped: __light-dash-dropped__;

    """ + BLOCK +
          r""" The corners, the keyboard's ring and the ground a control lifts to.
       The radii join the ladder, so a corner is a multiple like every other
       dimension; the ring holds the two-pixel floor WCAG asks for under the
       unit on a narrow viewport; the raised ground is scored against ink
       like every fill. */
    --radius-s: __light-radius-s__;  --radius-m: __light-radius-m__;
    --focus-ring: __light-focus-ring__;  --focus-gap: __light-focus-gap__;
    --surface-raised: __light-surface-raised__;
    --fade-aside: __light-fade-aside__;  --fade-off: __light-fade-off__;
  }

  """ + BLOCK +
          r""" The second ground, searched rather than eyeballed. Ten values moved and
     were scored against the thresholds the suite encodes, with the suite's own
     arithmetic: OKLab 15 between any two state fills, 8 under both dichromat
     simulations, 4.5:1 for ink on every fill and every surface, 15 between the
     accent and anything carrying hue. The seven fills, the accent and the two
     inks are the ten. The rest are step 1's and were held where they stood -
     the two grounds, the two rules, the selection outline, the verdict's pair -
     so nothing here claims they were derived. One of them is worth naming:
     `selected` is scored by nothing at all, and its outline runs as low as
     1.6:1 against the fill it is drawn on. This step neither opened that nor
     closed it.

     Which hue means which state does not move. Every value the search moved
     lands within 0.6 degrees of the light ground's own angle, measured on the
     hex that ships rather than on the number that produced it: at the chroma a
     dark fill can carry, one 8-bit step is worth one to three degrees, so those
     are not the same claim. An earlier cut of this block held the angle before
     rounding and shipped absence seven degrees warm.

     What moves is lightness, and the ink moves with it. Every fill has to clear
     4.5:1 against ink, which caps the top of the staircase, so the band the
     ladder lives in is exactly as wide as the ink is bright. The value here is
     the one that gives this ladder the room the approved one has: 0.285 of
     OKLab L against the light ground's 0.286. Dimming it is paid for directly -
     nine 8-bit levels down leaves 1.0% headroom and fifteen has no solution at
     all. That figure is not the suite's alone: it is the suite's floors plus
     five this step added and a hue band held on the shipped hex.

     The staircase falls to silence rather than rising to it: silence is the
     state nearest the page's own ground on either ground, and on black that is
     the bottom rung. Its rungs are 0.052 / 0.110 / 0.123 in OKLab L, bottom
     heavy because the ink caps the top and nothing caps the bottom. */
  @media (prefers-color-scheme: dark) {
    :root {
      --ink:            __dark-ink__;
      --ink-muted:      __dark-ink-muted__;
      --surface:        __dark-surface__;
      --surface-sunken: __dark-surface-sunken__;
      --rule:           __dark-rule__;
      --rule-strong:    __dark-rule-strong__;

      --state-convergence: __dark-state-convergence__;
      --state-divergence:  __dark-state-divergence__;
      --state-absence:     __dark-state-absence__;
      --state-silence:     __dark-state-silence__;

      --change-improved:  __dark-change-improved__;
      --change-unchanged: __dark-change-unchanged__;
      --change-regressed: __dark-change-regressed__;

      """ + BLOCK +
          r""" Bright, where the light ground's accent is deep: the treemap sets the
         page's own surface as the label on an unclaimed region, so the accent
         is the ground that label has to read against. */
      --unclaimed:      __dark-unclaimed__;
      --selected:       __dark-selected__;

      --verdict-bad:  __dark-verdict-bad__;
      --verdict-good: __dark-verdict-good__;

      """ + BLOCK +
          r""" The hover ground, the one dimension-bearing value this ground
         restates: every size, type and stroke token is shared, and a lifted
         control's fill has to read against this ground's own ink. */
      --surface-raised: __dark-surface-raised__;
    }
  }
""")
