from archituner.vocabulary import STATE_COLOURS as STATE_FILL
from archituner.vocabulary import STATES


LIGHT = {
    "ink": "#1a1a1a",
    "ink-muted": "#5c5c5c",
    "surface": "#ffffff",
    "surface-sunken": "#f4f4f4",
    "rule": "#b8b8b8",
    "rule-strong": "#7a7a7a",

    "state-convergence": STATE_FILL["convergence"],
    "state-divergence": STATE_FILL["divergence"],
    "state-absence": STATE_FILL["absence"],
    "state-silence": STATE_FILL["silence"],

    "change-improved": "#8ed3ad",
    "change-unchanged": "#e0e0e0",
    "change-regressed": "#df8ba3",

    "unclaimed": "#933bb0",
    "selected": "#0a58ca",

    "verdict-bad": "#8f342a",
    "verdict-good": "#2f6b45",

    "u": "clamp(0.8px, 0.0625rem, 0.18vw)",

    "step-1": "calc(var(--u) * 2)",
    "step-2": "calc(var(--u) * 4)",
    "step-3": "calc(var(--u) * 8)",
    "step-4": "calc(var(--u) * 12)",

    "hair": "var(--u)",

    "type-micro": "calc(var(--u) * 10)",
    "type-dense": "calc(var(--u) * 12)",

    "cell-h": "calc(var(--u) * 22)",
    "main-w": "calc(var(--u) * 560)",
    "panel-w": "calc(var(--u) * 320)",
    "search-w": "calc(var(--u) * 260)",
    "number-w": "calc(var(--type-body) * 3.5)",

    "type-small": "calc(var(--u) * 11)",
    "type-body": "calc(var(--u) * 13)",

    "cell": "calc(var(--u) * 26)",

    "mono": 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, '
            '"Liberation Mono", monospace',

    "line": "calc(var(--type-body) * 1.5)",
    "track-wide": "calc(var(--type-body) * 0.08)",

    "stroke-hair": "var(--u)",
    "stroke-mark": "calc(var(--u) * 1.5)",
    "stroke-node": "calc(var(--u) * 2)",
    "stroke-emphasis": "calc(var(--u) * 2.5)",
    "stroke-selection": "calc(var(--u) * 3)",

    "dash-vacant": "calc(var(--u) * 3) calc(var(--u) * 2)",
    "dash-absence": "calc(var(--u) * 4) calc(var(--u) * 3)",
    "dash-dropped": "calc(var(--u) * 1) calc(var(--u) * 3)",

    "radius-s": "calc(var(--u) * 3)",
    "radius-m": "calc(var(--u) * 3)",
    "focus-ring": "max(calc(var(--u) * 2), 2px)",
    "focus-gap": "var(--u)",
    "surface-raised": "#e8e8e8",

    "fade-aside": ".18",
    "fade-off": ".35",
}

DARK = {
    "ink": "#efefef",
    "ink-muted": "#aaaaaa",
    "surface": "#14161a",
    "surface-sunken": "#1c1f25",
    "rule": "#333941",
    "rule-strong": "#5a626c",

    "state-convergence": "#157241",
    "state-divergence": "#ae4b45",
    "state-absence": "#543e00",
    "state-silence": "#1d232d",

    "change-improved": "#196140",
    "change-unchanged": "#2b323b",
    "change-regressed": "#964961",

    "unclaimed": "#db82fb",
    "selected": "#4a8fe0",

    "verdict-bad": "#e8837a",
    "verdict-good": "#7cc093",

    "surface-raised": "#262a31",
}


def _covering_states(ground, name):
    missing = sorted(set(STATES) - {key.removeprefix("state-")
                                    for key in ground})
    if missing:
        raise ValueError(f"the {name} ground declares no fill for "
                        + ", ".join(missing))


_covering_states(LIGHT, "light")
_covering_states(DARK, "dark")

MOVED = {"improved": "▲", "unchanged": "=",
         "regressed": "▼", "dropped": "–"}

MARKS = (("convergence", "--state-convergence"),
         ("absence", "--state-absence"),
         ("divergence", "--state-divergence"),
         ("improved", "--change-improved"),
         ("unchanged", "--change-unchanged"),
         ("regressed", "--change-regressed"),
         ("dropped", "--rule"))

REFUSAL = {
    "light": {"scheme": "light", "ink": LIGHT["ink"],
              "surface": LIGHT["surface"],
              "sunken": LIGHT["surface-sunken"],
              "accent": LIGHT["verdict-bad"],
              "u": LIGHT["u"], "mono": LIGHT["mono"],
              "type-body": LIGHT["type-body"], "face": "var(--mono)",
              "line": LIGHT["line"], "pad": "calc(var(--u) * 24)",
              "head": "calc(var(--u) * 24)",
              "code-pad": "calc(var(--u) * 2) calc(var(--u) * 6)"},
    "dark": {"scheme": "dark", "ink": DARK["ink"], "surface": DARK["surface"],
             "sunken": DARK["surface-sunken"], "accent": DARK["verdict-bad"],
             "u": LIGHT["u"], "mono": LIGHT["mono"],
             "type-body": LIGHT["type-body"], "face": "var(--mono)",
             "line": LIGHT["line"], "pad": "calc(var(--u) * 24)",
             "head": "calc(var(--u) * 24)",
             "code-pad": "calc(var(--u) * 2) calc(var(--u) * 6)"},
}
