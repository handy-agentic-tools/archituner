# covers: archituner/presentation/model/stack_layout.py archituner/presentation/model/column_layout.py archituner/presentation/model/layout.py archituner/presentation/page/views/layers.py archituner/presentation/page/views/narrow.py archituner/presentation/page/shell/page.py
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PAYLOAD = "const DATA = "
DRESSES = [("the absence's dash", r"#stack \.wire\.absence", "--dash-absence"),
           ("the divergence's weight", r"#stack \.wire\.divergence",
            "--stroke-emphasis"),
           ("the selection's width", r"#stack \.wire\.sel",
            "--stroke-selection"),
           ("the aside's fade", r"#stack \.wire\.aside", "--fade-aside"),
           ("the convergence colour", r"#stack \.wire\.convergence",
            "--state-convergence"),
           ("the absence colour", r"#stack \.wire\.absence",
            "--state-absence"),
           ("the divergence colour", r"#stack \.wire\.divergence",
            "--state-divergence")]


def render():
    page = os.path.join(tempfile.mkdtemp(), "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner",
                           os.path.join(REPO, "ARCHITECTURE.md"), "-o", page],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    with open(page, encoding="utf-8") as handle:
        return handle.read()


PAGE = render()
DATA = json.loads(next(line for line in PAGE.splitlines()
                       if line.startswith(PAYLOAD))[len(PAYLOAD):].rstrip(";"))
BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")
STYLE = WHITESPACE.sub(" ", BLOCK_COMMENT.sub(" ", LINE_COMMENT.sub(
    " ", PAGE[PAGE.index("<style>") + 7:PAGE.index("</style>")]))).strip()


def block_of(needle):
    start = STYLE.index(needle)
    depth = 0
    for at, char in enumerate(STYLE[start:], start):
        depth += (char == "{") - (char == "}")
        if not depth:
            return STYLE[start:at + 1]
    raise AssertionError(f"the {needle} block never closes")


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


def scaled_of():
    return list(filter(
        lambda rule: re.search(r"[^-]width:", rule),
        re.findall(r"#stack[^{}]*\{[^{}]*\}", STYLE)))


def test_the_wide_stage_stands_at_its_natural_size_beside_the_panel():
    stack = DATA.get("stack") or {}
    assert stack.get("width") == 1004, ("issue 283: the wide stage is "
        f"{stack.get('width')} units wide, where the drawing's own natural "
        "size with no divergence drawn is 1004 - the stage is not drawn "
        "1:1 but scaled to its column")
    pad = stack["nodes"][0]["y"]
    pitch = stack["nodes"][1]["y"] - stack["nodes"][0]["y"]
    rows = len(DATA["order"])
    assert stack.get("height") == rows * pitch + pad * 2, ("issue 283: "
        f"the wide stage stands {stack.get('height')} units tall, where "
        f"the page's own {rows} rows at a {pitch} row pitch inside a "
        f"{pad} pad stand {rows * pitch + pad * 2}")
    assert not scaled_of(), ("issue 283: the stylesheet still sizes the "
        "stack to its column, so the whole drawing scales down and its "
        f"labels come out tiny on a wide screen: {scaled_of()}")


def test_the_phone_column_is_the_stack_at_its_own_size():
    narrow = DATA.get("stack_narrow") or {}
    assert narrow.get("width") == 366, ("issue 283: the phone's stage is "
        f"{narrow.get('width')} units wide, where the 390 unit screen gives "
        "it 366 - 8 unit margins, a 144 unit band and 200 unit boxes")
    nodes = narrow.get("nodes") or []
    wrong = list(filter(
        lambda n: (n["x"], n["width"], n["height"]) != (158, 200, 30), nodes))
    assert not wrong, ("issue 283: the phone's boxes are not two-row 200 "
        "unit boxes at the band's edge, the stack at its own size rather "
        "than a shrunken column: " + json.dumps(wrong))
    lanes = [w.get("l") for w in (narrow.get("wires") or {}).values()]
    assert min(lanes, default=0) >= 8, ("issue 283: a phone wire runs left "
        "of the 8 unit margin: " + json.dumps(lanes))
    assert max(lanes, default=1e9) < 158, ("issue 283: a phone wire does "
        "not run in the left band beside the boxes: " + json.dumps(lanes))


def test_no_stack_label_drops_below_the_dense_size_on_any_width():
    narrow = block_of("@media (max-width")
    ground = block_of("@media (prefers-color-scheme")
    wide = STYLE.replace(narrow, " ").replace(ground, " ")
    thin = {name: re.findall(
        r"#stack[^{}]*\{[^{}]*(?:--type-small|--type-micro)[^{}]*\}", block)
        for name, block in (("wide", wide), ("narrow", narrow))}
    assert not any(thin.values()), ("issue 283: a stack label stands in the "
        "small or micro type, under the dense size that is the floor on "
        f"every width: {json.dumps(thin)}")
    assert re.search(r"#stack text\.head[^{}]*\{[^}]*var\(--type-dense\)",
                     wide), ("issue 283: the wide header row does not wear "
        "the dense type the floor holds on every width")
    assert re.search(r"#stack \.wire text[^{}]*\{[^}]*var\(--type-dense\)",
                     wide), ("issue 283: the wire's own state mark is not "
        "dressed at the dense size the floor holds on every width")


def test_the_wire_dresses_carry_the_states_and_the_selection():
    missing = list(filter(
        lambda dress: not re.search(
            dress[1] + r"[^{}]*\{[^}]*var\(" + dress[2], STYLE),
        DRESSES))
    assert not missing, ("issue 283: the wires do not behave per pair as "
        "the arcs on main do - the state colours, the absence's dash, the "
        "divergence's weight, the selection and the aside faded beside it: "
        + "; ".join(map(lambda dress: dress[0] + " spends no var("
                        + dress[2] + ")", missing)))
    assert re.search(r"#stack[^{}]*\.wire[^{}]*\{[^}]*cursor: pointer",
                     STYLE), ("issue 283: the wires answer no pointer, so "
        "hover offers nothing where the arcs offered the pair")


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
