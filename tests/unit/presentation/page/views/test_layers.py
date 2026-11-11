import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../../../../.."))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.layers import MARKS, script, style

SHEET = '#stack .node rect { fill: var(--surface); stroke: var(--rule-strong); rx: var(--radius-m); } #stack .node text { font-size: var(--type-dense); fill: var(--ink); } #stack text.head { font-size: var(--type-dense); fill: var(--ink-muted); } #stack .node text.dim { fill: var(--ink-muted); } #stack .node line { stroke: var(--rule); stroke-width: var(--hair); } #stack .node.vacant rect { fill: var(--surface-sunken); stroke-dasharray: var(--dash-vacant); } #stack .node.improved rect { fill: var(--change-improved); } #stack .node.unchanged rect { fill: var(--change-unchanged); } #stack .node.regressed rect { fill: var(--change-regressed); } #stack .node.dropped rect { fill: var(--surface-sunken); } #stack .node:not(.vacant).improved text.dim, #stack .node:not(.vacant).unchanged text.dim, #stack .node:not(.vacant).regressed text.dim, #stack .node:not(.vacant).dropped text.dim { fill: var(--ink); } #stack .node.sel rect { stroke: var(--selected); stroke-width: var(--stroke-node); } #stack .node.sel text:first-of-type { font-weight: bold; } #stack .node, #stack .wire { cursor: pointer; } #stack .wire path { fill: none; stroke-width: var(--stroke-mark); } #stack .wire.convergence path { stroke: var(--state-convergence); } #stack .wire.absence path { stroke: var(--state-absence); stroke-dasharray: var(--dash-absence); } #stack .wire.divergence path { stroke: var(--state-divergence); stroke-width: var(--stroke-emphasis); } #stack .wire.improved path { stroke: var(--change-improved); stroke-width: var(--stroke-emphasis); } #stack .wire.unchanged path { stroke: var(--change-unchanged); } #stack .wire.regressed path { stroke: var(--change-regressed); stroke-width: var(--stroke-emphasis); } #stack .wire.dropped path { stroke: var(--rule); stroke-dasharray: var(--dash-dropped); } #stack .wire.sel path { stroke: var(--selected); stroke-width: var(--stroke-selection); } #stack .wire.aside { opacity: var(--fade-aside); } #stack .wire text { font-size: var(--type-dense); fill: var(--ink); cursor: pointer; paint-order: stroke; stroke: var(--surface); stroke-width: calc(var(--u) * 3); } #stack .node:hover rect { stroke-width: var(--stroke-node); } #stack .wire:hover path { stroke-width: var(--stroke-selection); } #stack .wire text:hover { font-weight: bold; }'

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")

RAW = (
    "data-pair='\" + p.source + \"->\" + p.target",
    "\"<title>\" + p.source + \" → \" + p.target + \": \" + mark + \"</title>",
    "text-anchor='middle'>\" + label + \"</text>\"",
    "data-layer='\" + n.name + \"'>\"",
    "text-anchor='middle'>\" + v + \"</text>",
    "+ n.name + \"</text>\"",
)

SPENT = (
    ("#stack .node.vacant rect", "stroke-dasharray", "--dash-vacant"),
    ("#stack .node.sel rect", "stroke-width", "--stroke-node"),
    ("#stack .node line", "stroke-width", "--hair"),
    ("#stack .wire path", "stroke-width", "--stroke-mark"),
    ("#stack .wire.absence path", "stroke-dasharray", "--dash-absence"),
    ("#stack .wire.divergence path", "stroke-width", "--stroke-emphasis"),
    ("#stack .wire.improved path", "stroke-width", "--stroke-emphasis"),
    ("#stack .wire.regressed path", "stroke-width", "--stroke-emphasis"),
    ("#stack .wire.dropped path", "stroke-dasharray", "--dash-dropped"),
    ("#stack .wire.sel path", "stroke-width", "--stroke-selection"),
    ("#stack .wire.aside", "opacity", "--fade-aside"),
)


def without_prose(text):
    flat = BLOCK_COMMENT.sub(" ", text)
    flat = LINE_COMMENT.sub(" ", flat)
    return WHITESPACE.sub(" ", flat).strip()


def spent_at(sheet):
    return {" ".join(selector.split()): [" ".join(one.split())
                                         for one in body.split(";")]
            for selector, body in RULE.findall(sheet)}


def spend_problem(rules, selector, prop, token):
    held = rules.get(selector)
    if held is None:
        return f"no rule names {selector}"
    if f"{prop}: var({token})" not in held:
        return f"{selector} holds {held}; {prop} spends no var({token})"


RULES = spent_at(without_prose(style()))


def test_the_stack_s_rules_hold_byte_for_byte():
    flat = without_prose(style())
    assert flat == SHEET, flat


def test_the_stack_writes_no_value_into_its_markup_without_the_escape():
    flat = without_prose(script())
    left = list(filter(lambda one: one in flat, RAW))
    assert not left, ("a value is concatenated into the markup raw, and a "
                      "name holding an apostrophe truncates the attribute "
                      "it is written into: " + " | ".join(left))


def test_the_stack_s_rules_spend_the_unitless_tokens_by_name():
    problems = list(filter(None, map(lambda row: spend_problem(RULES, *row),
                                     SPENT)))
    assert not problems, (
        "the stack's rules do not spend the unitless tokens by name: "
        + "; ".join(problems))


def test_the_selected_name_is_bold():
    RULES["#stack .node.sel text:first-of-type"].index("font-weight: bold")


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", REPO + "/ARCHITECTURE.md",
         "--check", "--file", "archituner/presentation/page/views/layers.py"],
        capture_output=True, text=True, cwd=REPO)


def test_the_layers_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


MARKER = re.compile(r"<marker\b.*?</marker>")

HEAD = (r"<marker\b(?:(?!</marker>).)*%s(?:(?!</marker>).)*var\(%s\)(?:(?!</marker>).)*</marker>")
HEADS = tuple(map(re.compile, map(HEAD.__mod__, MARKS)))


def test_every_wire_ends_in_a_head_at_the_used_layer():
    tag = re.search(r'wires \+= "<g class.*?</g>', without_prose(script()))
    assert tag, ("issue 283: the drawer lays no wire group per drawn pair, "
                 "so no arrow ends in a head at the used layer")
    re.search(r"d='M \" \+ \w+\.x \+ \" \" \+ \w+\.a", tag.group(0)).group(0)
    re.search(r'" V "', tag.group(0)).group(0)
    re.search(r"marker-end", tag.group(0)).group(0)


def test_the_stack_defines_its_heads_in_its_svg_sized_under_the_dense_text():
    flat = without_prose(script())
    one = re.search(r"<svg id='stack'.*?<marker\b.*?</marker>", flat).group(0)
    re.search(r"markerUnits='userSpaceOnUse'", one).group(0)
    re.search(r"markerWidth='6'", one).group(0)
    re.search(r"markerHeight='6'", one).group(0)
    re.search(r"orient='auto'", one).group(0)


def test_each_mark_s_head_spends_that_mark_s_own_stroke_token():
    flat = without_prose(script())
    assert all(map(lambda head: head.search(flat), HEADS)), \
        re.findall(MARKER, flat)


def test_the_header_row_hangs_muted_over_the_four_columns():
    flat = without_prose(script())
    row = re.search(r'let head = ""; \["files", "uses", "used by", "chain"\]'
                    r".*?DATA\.stack\.centres\[k\].*?DATA\.stack\.head_y", flat)
    assert row, "the drawer hangs no header row"


def test_each_box_stamps_the_reading_s_numbers_in_four_equal_cells():
    flat = without_prose(script())
    re.search(r'const vals = \[layer\.files\.length, layer\.uses\.length, '
              r'layer\.used_by\.length, layer\.chain === null \? "–" : '
              r'layer\.chain\];.*?forEach.*?<line x1=\'.*?'
              r"DATA\.stack\.centres\[k\]", flat).group(0)


def test_zeros_and_the_dash_sit_muted_and_the_vacancy_note_is_gone():
    flat = without_prose(script())
    re.search(r"const dim = \(v === 0 && k < 3\) \|\| v === \"–\".*?"
              r"\(dim \? \" class=\'dim\'\"", flat).group(0)
    re.search(r'\A(?:(?!"vacant" : layer\.files\.length).)*\Z',
              flat).group(0)
    RULES["#stack .node text.dim"]


if __name__ == "__main__":
    for name, test in filter(lambda pair: pair[0].startswith("test_"),
                             sorted(globals().items())):
        test()
        print(f"PASS  {name}")
    print("all green")
