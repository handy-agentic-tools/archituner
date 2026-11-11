# covers: archituner/presentation/page/** archituner/presentation/model/figures.py
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

STAR = "**"

CONTRACT = (
    "---\n"
    "layers:\n"
    "  app:  [\"src/app/" + STAR + "\"]\n"
    "  web:  [\"src/web/" + STAR + "\"]\n"
    "  data: [\"src/data/" + STAR + "\"]\n"
    "  util: [\"src/util/" + STAR + "\"]\n"
    "\n"
    "dependencies:\n"
    "  allow:\n"
    "    - app -> web\n"
    "    - app -> data\n"
    "    - web -> data\n"
    "    - web -> util\n"
    "    - data -> util\n"
    "  forbid:\n"
    "    - app -> util\n"
    "    - web -> app\n"
    "    - data -> app\n"
    "    - data -> web\n"
    "    - util -> app\n"
    "    - util -> web\n"
    "    - util -> data\n"
    "---\n"
    "\n"
    "## Boundaries\n"
    "\n"
    "- `app -> util`: a stage never reaches past the one that serves it.\n"
    "- `web -> app`: a stage never reaches back to the thing that "
    "constructed it.\n"
    "- `data -> app`: a store never reaches back to the thing that "
    "constructed it.\n"
    "- `data -> web`: a store never reaches sideways to a stage beside it.\n"
    "- `util -> app`: a helper never reaches back to the thing that "
    "constructed it.\n"
    "- `util -> web`: a helper never reaches sideways to a stage beside it.\n"
    "- `util -> data`: a helper never reaches down to the store that calls "
    "it.\n"
)

FILES = (("src/app/__main__.py", "import src.web.view\n"),
         ("src/web/view.py",
          "import src.data.store\nimport src.util.help\n"),
         ("src/data/store.py", "import src.util.help\n"),
         ("src/util/help.py", "VALUE = 1\n"),
         ("src/loose/wild.py", "VALUE = 2\n"))

WORDS = ("Whole project",
         "Connections in use", "4 of 5 allowed",
         "Longest chain", "3 links",
         "Most relied on", "util · used by 2",
         'role="tablist"', 'data-panel-tab=', 'aria-selected=',
         "all files", "overview", "imported by", "DATA.files.length",
         "src/app/__main__.py", "src/web/view.py", "src/data/store.py",
         "src/util/help.py", "src/loose/wild.py")

GONE = ("Click a box on the left to see that layer here.",
        "<span class='small'>")


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    for rel, text in FILES:
        plant(tree, rel, text)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def page_of(contract):
    page = os.path.join(os.path.dirname(contract), "page.html")
    proc = drive(contract, "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    with open(page, encoding="utf-8") as handle:
        return handle.read()


def payload_of(body):
    line = next(one for one in body.splitlines()
                if one.startswith("const DATA = "))
    return json.loads(line[len("const DATA = "):].rstrip(";"))


def reading_of(contract):
    proc = drive(contract, "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    return json.loads(proc.stdout)


def test_the_cold_page_names_the_whole_project_overview():
    page = page_of(build())
    missing = [word for word in WORDS if word not in page]
    assert not missing, "the page at rest shows no: " + ", ".join(missing)
    assert all(text not in page for text in GONE), GONE


def test_every_count_the_overview_shows_resolves_to_the_reading():
    contract = build()
    overview = payload_of(page_of(contract))["overview"]
    reading = reading_of(contract)
    shape = reading["shape"]
    assert overview["connections"] == {
        "count": (str(shape["realised"]) + " of "
                  + str(shape["permitted"]) + " allowed"),
        "width": (shape["realised"] * 100 // shape["permitted"])
    }, overview["connections"]
    chain = shape["longest_chain"]
    assert (overview["chain"]["count"],
            [b["name"] for b in overview["chain"]["figure"]["boxes"]]) == \
        (str(len(chain) - 1) + " links", chain), overview["chain"]
    relied = max(reading["layers"], key=lambda one: len(one["used_by"]))
    assert overview["relied"]["count"] == (
        relied["name"] + " · used by " + str(len(relied["used_by"]))
    ), overview["relied"]
    assert [u["name"] for u in overview["relied"]["figure"]["users"]] == \
        relied["used_by"], overview["relied"]["figure"]
    assert overview["relied"]["figure"]["layer"]["name"] == relied["name"], \
        overview["relied"]["figure"]


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
