# covers: archituner/presentation/model/stack_layout.py archituner/presentation/model/column_layout.py archituner/presentation/model/layout.py archituner/presentation/page/views/layers.py archituner/presentation/page/shell/page.py
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

STAR = "*"
GLOB = STAR + STAR

CONTRACT = """---
layers:
  api:   ["src/api/{glob}"]
  core:  ["src/core/{glob}"]
  model: ["src/model/{glob}"]
  util:  ["src/util/{glob}"]
  web:   ["src/web/{glob}"]

dependencies:
  allow:
    - api -> core
    - core -> util
    - model -> util
    - web -> util
    - web -> core
  forbid:
    - api -> model
    - api -> util
    - api -> web
    - core -> api
    - core -> model
    - core -> web
    - model -> api
    - model -> core
    - model -> web
    - util -> api
    - util -> core
    - util -> model
    - util -> web
    - web -> api
    - web -> model
---

## Boundaries

- `core -> *`: a stage never reaches back to the thing that constructed it, and never draws.
- `model -> *`: a representation computes nothing and depends on nothing.
- `util -> *`: a helper is reached, it never reaches.
- `web -> *`: a page is reached, it never reaches.
- `api -> model`: a representation is not the invocation's to draw.
- `api -> util`: the invocation reaches no helper past the stage it holds.
- `api -> web`: the invocation draws no page.
""".format(glob=GLOB)

FILES = {
    "src/api/entry.py": "import src.core.base\n",
    "src/core/base.py": "import src.model.shape\nimport src.util.math\n",
    "src/model/shape.py": "import src.util.math\nimport src.core.base\n",
    "src/util/math.py": "VALUE = 1\n",
    "src/web/page.py": "import src.util.math\n",
}

STACK = {
    "width": 1244, "height": 226, "cell": 56, "head_y": 18, "hop": 5,
    "centres": [788, 844, 900, 956],
    "nodes": [
        {"name": "api", "x": 380, "y": 28, "width": 604, "height": 22},
        {"name": "model", "x": 380, "y": 62, "width": 604, "height": 22},
        {"name": "web", "x": 380, "y": 96, "width": 604, "height": 22},
        {"name": "core", "x": 380, "y": 130, "width": 604, "height": 22},
        {"name": "util", "x": 380, "y": 164, "width": 604, "height": 22},
    ],
    "wires": {
        "api->core": {"x": 380, "a": 39, "b": 135, "l": 55.2, "my": 91,
                      "hops_out": [],
                      "hops_in": [125.60000000000001, 196,
                                  266.40000000000003]},
        "core->model": {"x": 984, "a": 145.5, "b": 68.5, "l": 1059,
                        "my": 111, "hops_out": [], "hops_in": []},
        "core->util": {"x": 380, "a": 140.5, "b": 169, "l": 336.8,
                       "my": 158.75, "hops_out": [], "hops_in": []},
        "model->core": {"x": 984, "a": 77.5, "b": 136.5, "l": 1169,
                        "my": 111, "hops_out": [1059], "hops_in": [1059]},
        "model->util": {"x": 380, "a": 73, "b": 181, "l": 125.60000000000001,
                        "my": 131, "hops_out": [], "hops_in": []},
        "web->core": {"x": 380, "a": 111.5, "b": 146, "l": 266.40000000000003,
                      "my": 132.75, "hops_out": [], "hops_in": [336.8]},
        "web->util": {"x": 380, "a": 102.5, "b": 175, "l": 196,
                      "my": 142.75, "hops_out": [], "hops_in": []},
    },
}

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")


def without_prose(text):
    flat = BLOCK_COMMENT.sub(" ", text)
    flat = LINE_COMMENT.sub(" ", flat)
    return WHITESPACE.sub(" ", flat).strip()


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def render(with_divergence):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    files = dict(FILES)
    if not with_divergence:
        files["src/model/shape.py"] = "import src.util.math\n"
        files["src/core/base.py"] = "import src.util.math\n"
    for rel, text in files.items():
        plant(tree, rel, text)
    page = os.path.join(tree, "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner",
                           os.path.join(tree, "ARCHITECTURE.md"), "-o", page],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    with open(page, encoding="utf-8") as handle:
        return handle.read()


def data_of(body):
    line = next(line for line in body.splitlines()
                if line.startswith("const DATA = "))
    return json.loads(line[len("const DATA = "):].rstrip(";"))


def drawer_of(kind, body):
    flat = without_prose(body)
    start = flat.index(f"function {kind}() {{")
    nxt = flat.find("function ", start + 10)
    return flat[start:nxt] if nxt != -1 else flat[start:]


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


PAGE = render(True)
DATA = data_of(PAGE)


def test_the_stage_lays_one_right_angled_wire_per_drawn_pair():
    stack = DATA.get("stack")
    assert stack == STACK, ("issue 283: the wide stage does not lay every "
        "drawn pair as one right-angled wire - an exit dock on the source's "
        "left edge, its own vertical lane in the left band, an entry dock "
        "with the arrow on the target's left edge, the mark at the middle "
        "of the lane and a hop where a horizontal run passes another wire's "
        "lane - allowed pairs left, divergences mirrored on the boxes' "
        "right edge - the right band is the left band's exact mirror, its "
        "lanes reflected from the boxes' right edge and its entry docks in "
        "the left band's uncrossing order, per the issue's decision - the "
        "right band widening the stage only then: "
        + json.dumps(stack, sort_keys=True))


def test_the_stage_keeps_no_right_band_without_a_drawn_divergence():
    narrow = data_of(render(False)).get("stack") or {}
    assert narrow.get("width") == 1004, ("issue 283: without a divergence "
        f"drawn the stage is {narrow.get('width')} units wide, where the "
        "boxes' right edge ends it at 1004 - the right band is drawn only "
        "when a divergence is: " + json.dumps(narrow.get("width")))


def test_the_wide_drawer_draws_straight_runs_and_the_state_mark():
    body = drawer_of("drawLayers", PAGE)
    pieces = ("DATA.stack.wires", "hops_out", "hops_in", '" H "', '" V "')
    missing = list(filter(lambda piece: piece not in body, pieces))
    bent = re.search(r" Q | C ", body)
    assert not missing and not bent, ("issue 283: the wide drawer does not "
        "draw each pair as one right-angled path - missing: "
        + json.dumps(missing)
        + ("; the pair still bends through a curve" if bent else ""))
    assert re.search(r"<text x='\" \+ \w+\.l \+ \"' y='\" \+ \w+\.my \+ \"' "
                     r"text-anchor='middle'>\" \+ GLYPH\[", body), ("issue "
        "283: the wide drawer sets no state mark on the wire's own lane - "
        "the glyph each state carries must stand at the middle of the "
        "vertical run at the dense size, on every width")
    assert re.search(r"marker-end", body) and re.search(r"<title>", body) \
        and re.search(r"data-pair=", body), ("issue 283: the wire carries "
        "no arrow, tooltip or pair mark, so hover lands and lands nothing "
        "like the arcs it replaces")


def test_the_drawing_is_left_at_its_natural_size():
    rules = re.findall(r"#stack[^{}]*\{[^{}]*\}", PAGE)
    scaled = list(filter(lambda rule: re.search(r"[^-]width:", rule), rules))
    assert not scaled, ("issue 283: the stylesheet still sizes the stack to "
        f"its column, so the whole drawing scales down and its labels "
        f"shrink: {scaled}")
    tag = re.search(r"<svg id='stack'[^>]*>", without_prose(PAGE))
    assert tag and re.search(r"width='\" \+ DATA\.stack\.width", tag.group(0)) \
        and re.search(r"height='\" \+ DATA\.stack\.height", tag.group(0)), \
        ("issue 283: the stack's svg carries no width and height of its "
         "stage, so the drawing cannot stand at 1:1: "
         + (tag.group(0) if tag else "no svg"))


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
