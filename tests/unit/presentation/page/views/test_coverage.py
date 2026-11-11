import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
import archituner.presentation.page.views.coverage as coverage
from archituner.presentation.page.views.coverage import script
from archituner.presentation.page.views.coverage import style

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "page", "views",
                        "coverage.py")

SHEET = '#treemap { max-width: 100%; height: auto; } #treemap .region { cursor: pointer; } #treemap .region rect { rx: var(--radius-s); } #treemap .region text { font-size: var(--type-small); fill: var(--ink); pointer-events: none; } #treemap .region text.meta, #treemap .region tspan.meta { font-size: var(--type-micro); fill: var(--ink-muted); } #treemap .region.dir > rect { fill: none; stroke: var(--rule-strong); stroke-width: var(--stroke-hair); } #treemap .region.dir > text.dirname { font-size: var(--type-micro); fill: var(--ink-muted); } #treemap .region.claimed rect { fill: var(--surface-sunken); stroke: var(--surface); stroke-width: var(--stroke-hair); } #treemap .region.unclaimed rect { fill: var(--unclaimed); stroke: var(--surface); stroke-width: var(--stroke-hair); } #treemap .region.unclaimed text, #treemap .region.unclaimed text.meta { fill: var(--surface); } #treemap .region.moved rect { stroke: var(--surface); stroke-width: var(--stroke-hair); } #treemap .region.moved text.meta { fill: var(--ink); } #treemap .region.moved.improved rect { fill: var(--change-improved); } #treemap .region.moved.unchanged rect { fill: var(--change-unchanged); } #treemap .region.moved.regressed rect { fill: var(--change-regressed); } #treemap .region.moved.dropped rect { fill: var(--surface-sunken); } #treemap .region:hover > rect { stroke: var(--rule-strong); stroke-width: var(--stroke-node); } #treemap .region.sel > rect { stroke: var(--selected); stroke-width: var(--stroke-selection); }'

RAW = (
    "data-region='\" + b.id + \"'>\"",
    "\" <tspan class='meta'>\" + b.files + \"</tspan>",
    "\"'>\" + b.files + \"</text>\"",
    "data-figure='\" + kind + \":\" + id + \"' title='\"",
    "title='\" + what + \"'>\"",
    "'>\" + mark + \" \" + n + \"</button>",
)

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")

SPENT = (
    ("#treemap .region.dir > rect", "stroke-width", "--stroke-hair"),
    ("#treemap .region.claimed rect", "stroke-width", "--stroke-hair"),
    ("#treemap .region.unclaimed rect", "stroke-width", "--stroke-hair"),
    ("#treemap .region.moved rect", "stroke-width", "--stroke-hair"),
    ("#treemap .region.sel > rect", "stroke-width", "--stroke-selection"),
)


def spent_at(sheet):
    return {" ".join(selector.split()): [" ".join(one.split())
                                         for one in body.split(";")]
            for selector, body in RULE.findall(sheet)}


def spend_problem(rules, selector, prop, token):
    held = rules.get(selector)
    if held is None:
        return f"no rule names {selector}"
    if f"{prop}: var({token})" not in held:
        return (f"{selector} holds {'; '.join(filter(None, held))}; "
                f"{prop} spends no var({token})")


def without_prose(text):
    return WHITESPACE.sub(" ", LINE_COMMENT.sub(" ",
        BLOCK_COMMENT.sub(" ", text))).strip()


def test_the_treemap_s_rules_hold_byte_for_byte():
    assert without_prose(style()) == SHEET, without_prose(style())


def test_the_treemap_writes_no_value_into_its_markup_without_the_escape():
    flat = WHITESPACE.sub(" ", LINE_COMMENT.sub(" ", BLOCK_COMMENT.sub(
        " ", script()))).strip()
    left = list(filter(lambda one: one in flat, RAW))
    assert not left, ("a value is concatenated into the markup raw, and a "
                      "name holding an apostrophe truncates the attribute "
                      "it is written into: " + " | ".join(left))


def test_the_treemap_s_rules_spend_the_unitless_tokens_by_name():
    rules = spent_at(style())
    problems = list(filter(None, map(lambda row: spend_problem(rules, *row),
                                     SPENT)))
    assert not problems, (
        "the treemap's rules do not spend the unitless tokens by name: "
        + "; ".join(problems))


def test_the_treemap_s_drawer_names_a_box_by_the_layout_s_answers():
    was = getattr(coverage, "labels", None)
    coverage.labels = lambda: (50, 60, 21, 23, 35)
    drawn = script()
    coverage.labels = was
    moved = ("b.width > 50", "b.width > 60", "(b.y + 21)", "(b.y + 23)",
             "(b.y + 35)")
    assert not list(filter(lambda mark: mark not in drawn, moved)), (
        "with the layout answering moved numbers the drawer keeps the ones "
        "it spells: no " + ", ".join(moved) + " is drawn, so the floors and "
        "baselines arrive from no labels() seam the way the canvas arrives "
        "- they are spelled on this side")


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_coverage_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
