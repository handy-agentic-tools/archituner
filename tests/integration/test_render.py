# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/presentation/page/shell/page.py archituner/presentation/rejection/rejection.py
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
    '  api:   ["src/api/' + STAR + '"]\n'
    '  core:  ["src/core/' + STAR + '"]\n'
    '  model: ["src/model/' + STAR + '"]\n'
    "\n"
    "dependencies:\n"
    "  allow:\n"
    "    - api -> core\n"
    "    - api -> model\n"
    "    - core -> model\n"
    "  forbid:\n"
    "    - core -> api\n"
    "    - model -> api\n"
    "    - model -> core\n"
    "---\n"
    "\n"
    "## Boundaries\n"
    "\n"
    "- `model -> *`: a representation computes nothing and depends on nothing.\n"
    "- `core -> api`: a stage never reaches back to the thing that "
    "constructed it.\n"
)

BROKEN_CONTRACT = "layers:\n  api: [\"src/" + STAR + "\"]\n"

API_ENTRY = "import src.core.base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_broken():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", BROKEN_CONTRACT)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def read_of(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_the_default_action_writes_one_self_contained_page():
    contract = build()
    page = os.path.join(os.path.dirname(contract), "page.html")
    proc = drive(contract, "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert os.path.isfile(page), proc.stdout
    body = read_of(page)
    assert body.startswith("<!doctype html>"), body[:40]
    assert "const DATA" in body, "the reading is not inlined"
    assert "src/core/base.py" in body, "the tree's own files are not drawn"
    assert "<script src=" not in body and "<link " not in body, \
        "the page fetches at view time"
    assert "  layers 3  files 6  unclaimed 0" in proc.stdout.splitlines(), \
        proc.stdout
    assert "  convergence 1  divergence 0  absence 2  silence 3" \
        in proc.stdout.splitlines(), proc.stdout
    assert proc.stdout.splitlines()[-1] == f"  -> {page}", proc.stdout


def test_a_rerun_over_one_unchanged_tree_regenerates_the_same_bytes():
    contract = build()
    page = os.path.join(os.path.dirname(contract), "page.html")
    drive(contract, "-o", page)
    first = read_of(page)
    proc = drive(contract, "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert read_of(page) == first, "the rerun moved bytes"


def test_a_refused_contract_renders_the_rejection_page():
    contract = build_broken()
    page = os.path.join(os.path.dirname(contract), "page.html")
    proc = drive(contract, "-o", page)
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert os.path.isfile(page), proc.stdout
    body = read_of(page)
    assert body.startswith("<!doctype html>"), body[:40]
    assert "Contract rejected" in body, body[:200]
    reason = proc.stdout.splitlines()[0].replace(
        contract, os.path.basename(contract))
    assert reason and reason in body, (reason, body[:200])
    assert contract not in body, \
        "the rejection page shows the contract's absolute path"
    assert proc.stdout.splitlines()[-1] == f"  -> {page}", proc.stdout


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
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
