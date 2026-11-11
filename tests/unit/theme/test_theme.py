import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
import archituner
from archituner import theme
from archituner import vocabulary

CONTRACT = os.path.join(ROOT, "ARCHITECTURE.md")

PAGE = archituner.render(archituner.analyse(CONTRACT))

GLYPHS = {"convergence": "✓", "divergence": "✗",
          "absence": "○", "silence": "·"}
MOVED = {"improved": "▲", "unchanged": "=",
         "regressed": "▼", "dropped": "–"}

MARKS = {"convergence": "--state-convergence",
         "absence": "--state-absence",
         "divergence": "--state-divergence",
         "improved": "--change-improved",
         "unchanged": "--change-unchanged",
         "regressed": "--change-regressed",
         "dropped": "--rule"}

UNITED = {
    "stroke-hair": "var(--u)",
    "stroke-mark": "calc(var(--u) * 1.5)",
    "stroke-node": "calc(var(--u) * 2)",
    "stroke-emphasis": "calc(var(--u) * 2.5)",
    "stroke-selection": "calc(var(--u) * 3)",
    "dash-vacant": "calc(var(--u) * 3) calc(var(--u) * 2)",
    "dash-absence": "calc(var(--u) * 4) calc(var(--u) * 3)",
    "dash-dropped": "calc(var(--u) * 1) calc(var(--u) * 3)",
    "fade-aside": ".18",
    "fade-off": ".35",
}

HELD = {name: theme.LIGHT.get(name) for name in UNITED}
RESTATED = sorted(UNITED.keys() & theme.DARK.keys())

UNSPENT = sorted(filter(
    lambda mark: f"#stack #{mark} path {{ fill: var({MARKS[mark]}); }}" not in PAGE,
    MARKS))
HELD_MARKS = dict(theme.MARKS)
MARKS_PROBLEMS = []
if (HELD_MARKS, UNSPENT) != (MARKS, []):
    MARKS_PROBLEMS = [f"the theme holds {HELD_MARKS} against the table {MARKS}, "
                      f"and the sheet leaves {UNSPENT} without a head rule"]


def folded(value):
    return " ".join(value.split())


def spelled(mapping):
    return "{" + ", ".join(f'{key}: "{mark}"' for key, mark in mapping.items()) + "}"


def declarations(block):
    return dict(map(lambda pair: (pair[0], folded(pair[1])),
                    re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block)))


def grounds(style):
    light = re.search(r":root\s*\{([^{}]*)\}", style).group(1)
    dark_at = style.index("prefers-color-scheme: dark")
    dark = re.search(r":root\s*\{([^{}]*)\}", style[dark_at:]).group(1)
    return light, dark


def spell_report(name, value, declared):
    spelled_out = declared.get("--" + name)
    if spelled_out not in (None, folded(value)):
        return (f"--{name}: the theme holds {value!r}, "
                f"the page spells {spelled_out!r}")
    return None


def ground_problems(ground, held, declared):
    missing = list(filter(lambda name: declared.get("--" + name) is None,
                          held))
    off = list(filter(None, map(
        lambda item: spell_report(item[0], item[1], declared),
        held.items())))
    extra = sorted(set(declared) - set(map(lambda name: "--" + name, held)))
    problems = []
    if missing:
        problems.append(f"the {ground} block declares no "
                        + ", ".join(missing))
    problems += off
    if extra:
        problems.append(f"the {ground} block holds values the theme "
                        f"does not: " + ", ".join(extra))
    return problems


def state_report(state):
    held = vocabulary.STATE_COLOURS[state]
    if theme.LIGHT.get("state-" + state) != held:
        return (f"STATE_COLOURS[{state!r}] is "
                f"{held!r} but the light ground holds "
                f"{theme.LIGHT.get('state-' + state)!r}")
    return None


def state_problems():
    keyed = tuple(vocabulary.STATE_COLOURS)
    if keyed != vocabulary.STATES:
        return [f"STATE_COLOURS is keyed "
                f"{keyed}, not by "
                f"vocabulary.STATES"]
    return list(filter(None, map(state_report, vocabulary.STATES)))


def table_problems(module, name, table):
    problems = []
    if spelled(getattr(module, name)) != spelled(table):
        problems.append(f"{name} spells {spelled(getattr(module, name))}, "
                        f"not {spelled(table)}")
    needle = f"const {name} = " + spelled(table)
    if needle not in PAGE:
        problems.append(f"the script carries no {needle}")
    return problems


def test_the_rendered_css_matches_the_theme():
    style = PAGE[PAGE.index("<style>"):PAGE.index("</style>")]
    light_block, dark_block = grounds(style)
    problems = ground_problems("light", theme.LIGHT,
                               declarations(light_block))
    problems += ground_problems("dark", theme.DARK, declarations(dark_block))
    problems += state_problems()
    problems += table_problems(vocabulary, "GLYPH", GLYPHS)
    problems += table_problems(theme, "MOVED", MOVED)
    problems += MARKS_PROBLEMS
    assert not problems, (
        f"the rendered css does not match the theme: " + "; ".join(problems))


def test_the_svg_tokens_ride_the_unit_and_the_fades_stay_numbers():
    assert (HELD, RESTATED) == (UNITED, []), (
        "the theme does not compute the svg strokes and dashes from the "
        f"one base unit - the light ground holds {HELD} against the table "
        f"{UNITED}, and the dark ground restates {RESTATED}; a flat "
        "number in a dimension entry is the defect the fixed-value lint "
        "flags, and the two fades stay the pure numbers they are")


def test_the_state_marks_live_in_vocabulary_and_not_in_the_theme():
    assert (vocabulary.GLYPH, vocabulary.STATE_COLOURS,
            hasattr(theme, "GLYPH"), hasattr(theme, "STATE_COLOURS"),
            theme.MOVED == MOVED) == (
        GLYPHS, {"convergence": "#7cc093", "divergence": "#d37269",
                 "absence": "#f7cb64", "silence": "#ededed"},
        False, False, True)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
