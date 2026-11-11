# covers: archituner/presentation/**
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PAYLOAD = "const DATA = "

CONTROLS = ("data-view", "search and filters", "unclaimed <span")


def render():
    page = os.path.join(tempfile.mkdtemp(), "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner",
                           os.path.join(REPO, "ARCHITECTURE.md"), "-o", page],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    with open(page, "rb") as handle:
        return handle.read()


PAGE = render()
TEXT = PAGE.decode("utf-8")
STYLE = TEXT[TEXT.index("<style>") + 7:TEXT.index("</style>")]
SCRIPT = TEXT[TEXT.index("<script>") + 8:TEXT.index("</script>")]


def block_of(work, needle):
    start = work.index(needle)
    open_at = work.index("{", start)
    depth = 0
    for at, char in enumerate(work[open_at:], open_at):
        depth += (char == "{") - (char == "}")
        if not depth:
            return start, at + 1
    raise AssertionError(f"the {needle} block never closes")


def narrow_of():
    work = re.sub(r"/\*.*?\*/", lambda mark: " " * len(mark.group()),
                  STYLE, flags=re.S)
    assert "@media (max-width" in work, ("the page draws one layout for "
        "every width: no width threshold carries the narrow layout, so "
        "the narrow dress has nothing to live in")
    start, end = block_of(work, "@media (max-width")
    ground_end = block_of(work, "@media (prefers-color-scheme")[1]
    return work[start:end], work[:start] + work[end:], ground_end


def data_of():
    line = next(filter(lambda line: line.startswith(PAYLOAD),
                       TEXT.splitlines()))
    return json.loads(line[len(PAYLOAD):].rstrip(";"))


def figure_of(data):
    figure = data.get("stack_narrow")
    assert figure, ("the payload carries no narrow figure of the stack "
        "beside the wide one: at a phone's width the page draws the one "
        "wide stage scaled down, and no numbers say how the column is "
        "drawn")
    return figure


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


def test_the_narrow_layout_lives_behind_one_width_threshold():
    work = re.sub(r"/\*.*?\*/", lambda mark: " " * len(mark.group()),
                  STYLE, flags=re.S)
    count = work.count("@media (max-width")
    assert count == 1, (f"the page draws one layout for every width: "
        f"{count} width thresholds carry the narrow layout, so at a "
        "phone's width the stack is the wide stage drawn scaled down")
    narrow, _, ground_end = narrow_of()
    assert ground_end < work.index("@media (max-width"), ("the narrow "
        "block sits inside a ground block, so the narrow layout holds on "
        "one ground alone")
    spill = list(filter(lambda value: float(value) > 390, re.findall(
        r"(?<![\w-])width:\s*calc\(var\(--u\) \* ([\d.]+)\)", narrow)))
    assert not spill, ("the narrow block declares a width past the 390 "
        f"units a phone is wide, so the page scrolls sideways: {spill}")
    missing = list(filter(lambda mark: mark not in TEXT, CONTROLS))
    assert not missing, ("the narrow page drops a control the issue keeps "
        f"for the narrow screen too: {missing}")
    thin = re.findall(r"[^{}]+\{[^{}]*--type-(?:small|micro)[^{}]*\}", narrow)
    assert re.search(r"#stack text\.head[^{}]*\{[^}]*var\(--type-dense\)",
                     narrow) and not thin, ("the narrow block leaves a "
        "stack label in the small or micro type, under the dense size "
        f"--type-dense answers, 12 units, that no stack label drops "
        f"below: {thin}")


def test_the_payload_carries_a_narrow_figure_of_the_stack():
    data = data_of()
    narrow, wide = figure_of(data), data["stack"]
    missing = sorted((wide.keys() - {"head_y"}) - narrow.keys())
    assert not missing, ("the narrow figure answers fewer faces than the "
        f"wide one: {missing}")
    assert narrow["width"] <= 390, (f"the narrow stage is "
        f"{narrow['width']} units wide, past the 390 a phone spans, so "
        "the column itself would scroll sideways")


def test_the_narrow_figure_is_one_column_of_two_row_boxes():
    data = data_of()
    narrow = figure_of(data)
    names = list(map(lambda node: node["name"], narrow["nodes"]))
    assert names == data["order"], ("the narrow figure is not one column "
        "of every layer the page's own order carries, in dependency "
        "order: " + json.dumps(names))
    wide_row = data["stack"]["nodes"][0]["height"]
    shallow = list(filter(lambda node: node["height"] <= wide_row,
                          narrow["nodes"]))
    assert not shallow, (f"a narrow box stands {wide_row} units tall, the "
        "wide box's own one row, and holds neither the name above nor the "
        "four cells below: " + json.dumps(shallow))
    half = narrow["width"] / 2
    squeezed = list(filter(lambda node: node["width"] <= half,
                           narrow["nodes"]))
    assert not squeezed, ("a narrow box spans less than half the column, "
        "so the figure is a grid of cards rather than one column: "
        + json.dumps(squeezed))
    gutter = min(map(lambda node: node["x"], narrow["nodes"]))
    stray = list(filter(
        lambda wire: wire.get("l", narrow["width"]) >= gutter,
        narrow.get("wires", {"": {}}).values()))
    assert not stray, ("a narrow arrow does not run in the left gutter "
        "beside the boxes, a missing wires figure reading as stray under "
        "issue 283: " + json.dumps(stray))
    edge = gutter + narrow["nodes"][0]["width"]
    outside = list(filter(lambda centre: not gutter <= centre <= edge,
                          narrow["centres"]))
    assert not outside and len(narrow["centres"]) == 4, ("the four cell "
        "headers do not stand over the box's four cells: "
        + json.dumps(narrow["centres"]))
    assert "stack_narrow" in SCRIPT, ("the drawer draws the wide stack "
        "only: the narrow figure rides no drawing")


def test_the_first_screen_shows_the_drawing_not_only_controls():
    narrow, _, _ = narrow_of()
    band = re.findall(r"#(?:shellbar|legend)[^{}]*\{[^{}]*\}", narrow)
    capped = list(filter(lambda rule: re.search(
        r"(?:max-)?height:\s*calc\(\s*var\(--u\)\s*\*\s*([\d.]+)", rule),
        band))
    assert capped, ("the narrow block bounds no view bar and legend rule "
        "with a height in the page's own units: at a phone's width the "
        "wide band wraps into a wall of keys, the controls alone take the "
        "first screen, and nothing says how much of the 844 a phone is "
        "tall stays for the drawing")
    tall = list(filter(lambda rule: float(re.search(
        r"(?:max-)?height:\s*calc\(\s*var\(--u\)\s*\*\s*([\d.]+)",
        rule).group(1)) > 240, capped))
    assert not tall, ("a view bar or legend bound stands past 240 units, "
        "so the band alone eats more than 604 of the 844 units a phone's "
        f"first screen is tall and the drawing starts below it: {tall}")


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
