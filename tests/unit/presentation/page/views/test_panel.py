import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
import archituner.presentation.page.views.panel as panel

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "page", "views",
                        "panel.py")

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")


def box(name, x, y, width, height):
    return {"name": name, "x": x, "y": y, "width": width, "height": height}


def join(x1, x2, y):
    return {"x1": x1, "x2": x2, "y": y}


def line(x, y1, y2):
    return {"x": x, "y1": y1, "y2": y2}


READING = {"shape": {"realised": 20, "permitted": 24,
                     "longest_chain": ["cli", "run", "presentation", "theme",
                                       "vocabulary"]},
           "layers": [{"name": "cli", "used_by": []},
                      {"name": "run", "used_by": ["cli"]},
                      {"name": "presentation", "used_by": ["run"]},
                      {"name": "theme", "used_by": ["run", "presentation"]},
                      {"name": "vocabulary",
                       "used_by": ["tests_unit", "run", "presentation",
                                   "conformance", "contract", "source",
                                   "theme"]}]}

CHAIN = {"width": 160, "height": 150, "on": None,
         "boxes": [box("cli",0,0,140,20), box("run",0,32,140,20),
                   box("presentation",0,64,140,20), box("theme",0,96,140,20),
                   box("vocabulary",0,128,140,20)],
         "arrows": [line(70,21,32), line(70,53,64), line(70,85,96),
                    line(70,117,128)]}

BUS = {"width": 280, "height": 172,
       "users": [box("tests_unit",0,0,110,20), box("run",0,25,110,20),
                 box("presentation",0,50,110,20),
                 box("conformance",0,75,110,20), box("contract",0,100,110,20),
                 box("source",0,125,110,20), box("theme",0,150,110,20)],
       "joins": [join(110,130,10), join(110,130,35), join(110,130,60),
                 join(110,130,85), join(110,130,110), join(110,130,135),
                 join(110,130,160)],
       "bus": line(130,10,160), "arrow": join(130,160,85),
       "layer": box("vocabulary",160,75,110,20)}

OVERVIEW = {"connections": {"count": "20 of 24 allowed", "width": 83},
            "chain": {"count": "4 links", "figure": CHAIN,
                      "caption": "each arrow is a link: cli uses run, run "
                                 "uses presentation, and so on down to the "
                                 "foundation"},
            "relied": {"count": "vocabulary · used by 7", "figure": BUS,
                       "caption": "a change in vocabulary reaches every "
                                  "layer on the left"}}

SMALL_READING = {"shape": {"realised": 4, "permitted": 5,
                           "longest_chain": ["app", "web", "data", "util"]},
                 "layers": [{"name": "app", "used_by": []},
                            {"name": "web", "used_by": ["app"]},
                            {"name": "data", "used_by": ["web"]},
                            {"name": "util", "used_by": ["web", "data"]}]}

SMALL_CHAIN = {"width": 160, "height": 118, "on": None,
               "boxes": [box("app",0,0,140,20), box("web",0,32,140,20),
                         box("data",0,64,140,20), box("util",0,96,140,20)],
               "arrows": [line(70,21,32), line(70,53,64), line(70,85,96)]}

SMALL_BUS = {"width": 280, "height": 47,
             "users": [box("web",0,0,110,20), box("data",0,25,110,20)],
             "joins": [join(110,130,10), join(110,130,35)],
             "bus": line(130,10,35), "arrow": join(130,160,10),
             "layer": box("util",160,0,110,20)}

SMALL_OVERVIEW = {"connections": {"count": "4 of 5 allowed", "width": 80},
                  "chain": {"count": "3 links", "figure": SMALL_CHAIN,
                            "caption": "each arrow is a link: app uses web, "
                                       "web uses data, and so on down to the "
                                       "foundation"},
                  "relied": {"count": "util · used by 2",
                             "figure": SMALL_BUS,
                             "caption": "a change in util reaches every "
                                        "layer on the left"}}

SHEET = '#detail .block { display: grid; gap: var(--step-2); } #detail .head { display: flex; flex-wrap: wrap; gap: var(--step-1) var(--step-3); align-items: baseline; } #detail .head .label { color: var(--ink-muted); } #detail .bar { height: var(--step-3); background: var(--surface-sunken); border: var(--hair) solid var(--rule); } #detail .bar > span { display: block; height: 100%; background: var(--state-convergence); } #detail svg { display: block; max-width: 100%; height: auto; } #detail svg text { font-family: var(--mono); font-size: var(--type-dense); fill: var(--ink); } #detail svg .box { fill: var(--surface); stroke: var(--rule-strong); stroke-width: var(--hair); rx: var(--radius-s); } #detail svg .ln { stroke: var(--rule-strong); stroke-width: var(--hair); fill: none; } #detail .small, #detail .hint { color: var(--ink-muted); font-size: var(--type-small); } #detail .hint { border-top: var(--hair) solid var(--rule); padding-top: var(--step-3); } #detail .flist { list-style: none; margin: 0; padding: 0; } #detail .flist li { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: var(--step-3); padding: var(--step-1) 0; border-bottom: var(--hair) solid var(--rule); font-size: var(--type-dense); } #detail .flist li span.p { overflow-wrap: anywhere; } #detail .flist li span.n { color: var(--ink-muted); text-align: right; } #detail li[data-pair], #detail li[data-file] { cursor: pointer; } #detail li[data-pair]:hover, #detail li[data-file]:hover { background: var(--surface-raised); }'

RAW = (
    "'>\" + b.name + \"</text>",
    "</span><span>\" + o.connections.count + \"</span></div>",
    "</span><span>\" + o.chain.count",
    "aria-label='\" + o.chain.caption",
    "class='small'>\" + o.chain.caption + \"</span>",
    "</span><span>\" + o.relied.count",
    "aria-label='\" + o.relied.caption",
    "class='small'>\" + o.relied.caption + \"</span>",
    "data-panel-tab='\" + t[0]",
    "class='count'>\" + DATA.files.length + \"</span>",
)


def flat_of(text):
    flat = BLOCK_COMMENT.sub(" ", text)
    flat = LINE_COMMENT.sub(" ", flat)
    return WHITESPACE.sub(" ", flat).strip()


def test_the_whole_project_overview_lands_in_the_panel_module():
    assert panel.overview(READING) == OVERVIEW, panel.overview(READING)


def test_the_overview_is_taken_from_the_reading_it_is_handed():
    assert panel.overview(SMALL_READING) == SMALL_OVERVIEW, \
        panel.overview(SMALL_READING)


def test_the_overview_writes_no_value_into_its_markup_without_the_escape():
    flat = flat_of(panel.script())
    left = list(filter(lambda one: one in flat, RAW))
    assert not left, ("a value is concatenated into the markup raw, and a "
                      "name holding an apostrophe truncates the attribute "
                      "it is written into: " + " | ".join(left))


def without_prose(text):
    return WHITESPACE.sub(" ", LINE_COMMENT.sub(" ",
        BLOCK_COMMENT.sub(" ", text))).strip()


def test_the_panel_s_rules_hold_byte_for_byte():
    assert without_prose(panel.style()) == SHEET, without_prose(panel.style())


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_panel_module_sits_within_its_limits():
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
