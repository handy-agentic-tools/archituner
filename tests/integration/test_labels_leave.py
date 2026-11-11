# covers: archituner/presentation/page/views/views.py archituner/presentation/page/views/readings.py archituner/presentation/page/views/detail.py archituner/presentation/page/views/coverage.py archituner/presentation/page/views/panel.py archituner/presentation/page/shell/shell.py
import os
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

GONE = (
    "How do the layers depend on each other?",
    "Rows import columns; a cell is the pair's state",
    "Area is file count; what no layer claims",
    "Nothing to draw: the filters exclude",
    "in no comparison: the stored baseline never held these",
    "the same regions, drawn in what moved",
    "The same marks, counted over files rather than pairs",
    "change is measured against the baseline stored at",
    "pair(s) dropped from the comparison rather than ",
    "no Boundaries line reaches this pair",
    "- the baseline and this contract do not both name this pair",
    "- no file here is in the stored baseline",
    "- the worst of what its ",
    "- it left ",
    ", which is a move rather than a gain or a loss",
    "- the stored baseline never held this file",
    "<span class='small'>",
    "Click a box on the left to see that layer here.",
)

KEPT = (
    "CONFORMS: no forbidden pair realised",
    "data-reset='1'>show everything</button>",
    "since the stored baseline",
    " file(s) since the stored baseline",
    "class='tally'",
    "in no comparison",
    "aria-label='",
)


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


def render():
    contract = build()
    page = os.path.join(os.path.dirname(contract), "page.html")
    proc = subprocess.run(
        [sys.executable, "-m", "archituner", contract, "-o", page],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    with open(page, encoding="utf-8") as handle:
        return handle.read()


PAGE = render()


def test_no_label_the_owner_removed_is_left_on_the_page():
    left = [text for text in GONE if text in PAGE]
    assert not left, left


def test_the_page_still_names_the_verdict_and_its_controls():
    missing = [text for text in KEPT if text not in PAGE]
    assert not missing, missing


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
