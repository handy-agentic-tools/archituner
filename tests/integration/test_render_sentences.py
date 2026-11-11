# covers: archituner/presentation/page/shell/shell.py archituner/presentation/page/views/views.py archituner/presentation/page/views/layers.py archituner/presentation/page/views/coverage.py
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

QUESTION = (
    "How do the layers depend on each other? Top: where the program starts. "
    "Bottom: the foundations. An arrow means “uses”. Solid: it does. Dashed: "
    "it may, but doesn't. Click a box to see it on the right.")
MATRIX_ANSWER = ("Rows import columns; a cell is the pair's state; layers in "
                 "dependency order.")
COVERAGE_ANSWER = ("Area is file count; what no layer claims stands in the "
                   "accent.")
CELLS = ("In each box: files it holds · how many layers it uses · how many "
         "layers it is used by ·")

GONE = ("left of the stack: permitted, solid where realised",
        "the same stack, drawn in what moved",
        "rows import columns; layers in dependency order",
        "Each cell is what the pair did since the baseline",
        "area is file count; a box sits inside the directory that holds it")


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


def stray(texts, stray_when):
    return [text for text in texts if stray_when(text)]


PAGE = render()


def test_the_page_opens_the_view_with_its_sentence_under_the_search_row():
    marks = ('<div id="ask"></div>', '<div class="hint"></div>',
             '<div id="cmd"></div>', '<div id="view"></div>')
    order = [PAGE.find(mark) for mark in marks]
    assert -1 not in order, list(zip(marks, order))
    assert order == sorted(order), list(zip(marks, order))


def test_the_page_carries_none_of_the_sentences_the_views_opened_with():
    left = stray((QUESTION, MATRIX_ANSWER, COVERAGE_ANSWER, CELLS),
                 lambda text: text in PAGE)
    assert not left, left


def test_the_views_open_with_no_sentence_at_all():
    assert "const SENTENCE" not in PAGE, (
        "the views still build a sentence to open with")
    assert '$("#sentence")' not in PAGE, (
        "the script still writes into the sentence line")


def test_the_page_keeps_no_note_below_the_views():
    notes = GONE + ("the same regions, drawn in what moved",
                    "The same marks, counted over files rather than pairs")
    left = stray(notes, lambda text: text in PAGE)
    assert not left, left


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
