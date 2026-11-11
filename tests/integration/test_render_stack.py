# covers: archituner/presentation/page/shell/page.py archituner/presentation/page/views/layers.py archituner/presentation/model/layout.py archituner/presentation/model/stack_layout.py
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
  forbid:
    - api -> model
    - api -> util
    - api -> web
    - core -> api
    - core -> model
    - core -> web
    - model -> api
    - model -> core
    - model -> util
    - model -> web
    - util -> api
    - util -> core
    - util -> model
    - util -> web
    - web -> api
    - web -> core
    - web -> model
    - web -> util
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
    "src/model/shape.py": "import src.api.entry\n",
    "src/util/math.py": "VALUE = 1\n",
    "src/web/page.py": "VALUE = 2\n",
}

STACK = {
    "width": 1244,
    "height": 226,
    "cell": 56,
    "head_y": 18,
    "hop": 5,
    "centres": [788, 844, 900, 956],
    "nodes": [
        {"name": "api", "x": 380, "y": 28, "width": 604, "height": 22},
        {"name": "model", "x": 380, "y": 62, "width": 604, "height": 22},
        {"name": "web", "x": 380, "y": 96, "width": 604, "height": 22},
        {"name": "core", "x": 380, "y": 130, "width": 604, "height": 22},
        {"name": "util", "x": 380, "y": 164, "width": 604, "height": 22},
    ],
    "wires": {
        "api->core": {"x": 380, "a": 39, "b": 136.5, "l": 108, "my": 91.75,
                      "hops_out": [], "hops_in": []},
        "core->util": {"x": 380, "a": 145.5, "b": 175, "l": 284,
                       "my": 164.25, "hops_out": [], "hops_in": []},
        "model->api": {"x": 984, "a": 77.5, "b": 39, "l": 1059, "my": 62.25,
                       "hops_out": [], "hops_in": []},
        "core->model": {"x": 984, "a": 141, "b": 68.5, "l": 1169,
                        "my": 108.75, "hops_out": [], "hops_in": [1059]},
    },
}

STACK_TEXT = json.dumps(STACK, sort_keys=True)

GEOMETRY_NAME = re.compile(
    r"\b(ROW|PAD|MARGIN|NODE_W|NODE_H|BAND_L|BAND_R|LEFT|STAGE_W)\b")
SPREAD = re.compile(r"\breach\b")
POSITION_LOOKUP = re.compile(r"\bindexOf\b")
BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}[^\n]*")


def code_of(drawer):
    return LINE_COMMENT.sub(" ", BLOCK_COMMENT.sub(" ", drawer))


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    for rel, text in FILES.items():
        plant(tree, rel, text)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def read_of(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def data_of(body):
    line = next(line for line in body.splitlines()
                if line.startswith("const DATA = "))
    return json.loads(line[len("const DATA = "):].rstrip(";"))


def drawer_of(body):
    start = body.index("function drawLayers() {")
    return body[start:body.index("\nfunction ", start)]


def render():
    contract = build()
    page = os.path.join(os.path.dirname(contract), "page.html")
    proc = drive(contract, "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    return read_of(page)


def test_the_stack_s_coordinates_ride_the_payload_beside_the_regions():
    data = data_of(render())
    stack = data.get("stack")
    assert stack == STACK, ("issue 283: the stage's wires are not the left "
        "band's router with divergences mirrored on the boxes' right edge "
        "- the right band is that router's exact mirror, its lanes "
        "reflected from the boxes' right edge and its entry docks in the "
        "left band's uncrossing order, per the issue's decision: ",
        STACK, stack, sorted(data))
    assert json.dumps(stack, sort_keys=True) == STACK_TEXT, (
        "the stack's numbers are not spelled the way the browser spelled "
        "them: " + json.dumps(stack, sort_keys=True))


def test_the_stack_s_drawer_declares_no_geometry_and_computes_no_coordinate():
    drawer = code_of(drawer_of(render()))
    problems = [f"{rule.pattern}: {', '.join(sorted(set(rule.findall(drawer))))}"
                for rule in (GEOMETRY_NAME, SPREAD, POSITION_LOOKUP)
                if rule.search(drawer)]
    if "DATA.stack" not in drawer:
        problems.append("the drawer reads no DATA.stack")
    assert not problems, (
        "the drawer declares the geometry it draws, where the contract holds "
        "that layout arithmetic is a module that returns coordinates: "
        + "; ".join(problems))


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                test()
                print(f"PASS  {name}")
            except Exception as e:
                print(f"FAIL  {name}  {type(e).__name__}: {e}")
                failures += 1
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(1 if failures else 0)
