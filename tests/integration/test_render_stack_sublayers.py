# covers: archituner/presentation/**
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

STAR = "*"
GLOB = STAR + STAR

CONTRACT = """---
package_root: "."

layers:
  cut_detection.corner: ["src/corner/{glob}"]
  cut_detection.path_nib: ["src/nib/{glob}"]
  core: ["src/core/{glob}"]
  cut_detection: ["src/cut/{glob}"]
  util: ["src/util/{glob}"]

dependencies:
  allow:
    - core -> cut_detection
    - cut_detection -> util
    - core -> util
    - cut_detection.path_nib -> cut_detection.corner
  forbid:
    - cut_detection -> core
    - util -> core
    - util -> cut_detection
    - cut_detection.corner -> cut_detection.path_nib
---

## Boundaries

- `util -> *`: a helper is reached, it never reaches.
- `cut_detection -> core`: a stage never reaches back to the thing that constructed it.
""".format(glob=GLOB)

FILES = {
    "src/core/base.py": "import src.cut.main\n",
    "src/cut/main.py": "import src.util.help\n",
    "src/nib/nib.py": "VALUE = 1\n",
    "src/corner/corner.py": "VALUE = 2\n",
    "src/util/help.py": "VALUE = 3\n",
}

TOPOLOGICAL = ["cut_detection.path_nib", "core", "cut_detection.corner",
               "cut_detection", "util"]

DISPLAY = ["core", "cut_detection", "cut_detection.corner",
           "cut_detection.path_nib", "util"]

PARENT = {"cut_detection.corner": "cut_detection",
          "cut_detection.path_nib": "cut_detection"}

WIDE = {"row": 34, "pad": 28, "node_h": 22}


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
    return tree


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def payload_of():
    tree = build()
    page = os.path.join(tree, "page.html")
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    with open(page, encoding="utf-8") as handle:
        body = handle.read()
    line = next(line for line in body.splitlines()
                if line.startswith("const DATA = "))
    return json.loads(line[len("const DATA = "):].rstrip(";"))


def rows_of(figure):
    return [node["name"] for node in figure["nodes"]]


def by_name(figure):
    return {node["name"]: node for node in figure["nodes"]}


def stack_of():
    return payload_of()["stack"]


def check_display_rows(rows):
    assert rows == DISPLAY, ("issue 338: the stack's rows are the dependency "
        "order whole, so a sublayer lands wherever its allowed pairs put it "
        "instead of directly below its parent, in the wide stack and in the "
        "narrow column alike: ", DISPLAY, rows)


def check_indented(figure):
    nodes = by_name(figure)
    for sub, parent in PARENT.items():
        assert nodes[sub]["x"] > nodes[parent]["x"], ("issue 338: the "
            "sublayer " + sub + " is not indented one step under its parent, "
            "so its row does not read as part of that parent: ",
            nodes[parent]["x"], nodes[sub]["x"])
    assert (nodes["cut_detection.corner"]["x"]
            == nodes["cut_detection.path_nib"]["x"]), ("issue 338: one "
            "parent's sublayers are not indented by the same step: ",
            nodes["cut_detection.corner"]["x"],
            nodes["cut_detection.path_nib"]["x"])


def test_the_wide_stack_places_each_sublayer_directly_below_its_parent():
    check_display_rows(rows_of(stack_of()))


def test_the_wide_stack_s_rows_sit_at_the_heights_the_new_order_gives():
    heights = [node["y"] for node in stack_of()["nodes"]]
    assert heights == [WIDE["pad"] + i * WIDE["row"]
                       for i in range(len(DISPLAY))], ("issue 338: a "
        "sublayer's row does not follow the display order, so the rows the "
        "stack draws are not the rows the new order gives: ", heights)


def test_the_wide_stack_indents_each_sublayer_one_step_under_its_parent():
    check_indented(stack_of())


def test_the_narrow_column_places_each_sublayer_below_its_parent_indented():
    figure = payload_of()["stack_narrow"]
    check_display_rows(rows_of(figure))
    check_indented(figure)


def test_the_wires_land_on_the_rows_the_new_order_gives():
    wire = stack_of()["wires"]["core->cut_detection"]
    top = WIDE["pad"] + DISPLAY.index("cut_detection") * WIDE["row"]
    assert top <= wire["b"] <= top + WIDE["node_h"], ("issue 338: a wire's "
        "entry dock does not land on the row the new order gives its "
        "target, so the arcs do not follow the new rows: ",
        top, wire["b"])
    home = WIDE["pad"] + DISPLAY.index("core") * WIDE["row"]
    assert home <= wire["a"] <= home + WIDE["node_h"], ("issue 338: a "
        "wire's exit dock does not leave from the row the new order gives "
        "its source: ", home, wire["a"])


def test_the_json_order_keeps_the_dependency_order_it_has_today():
    tree = build()
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--json")
    assert proc.returncode in (0, 1), (proc.returncode, proc.stdout,
                                       proc.stderr)
    document = json.loads(proc.stdout)
    assert document["order"] == TOPOLOGICAL, ("issue 338: the boundary is "
        "the display order alone, so the JSON order must stay the "
        "dependency order: ", TOPOLOGICAL, document["order"])


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
