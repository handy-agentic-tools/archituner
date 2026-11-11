# covers: archituner/run/** archituner/source/** archituner/contract/**
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
GONE = "/nonexistent/target"

CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

dependencies:
  allow:
    - api -> core
    - api -> model
    - core -> model
  forbid:
    - core -> api
    - model -> api
    - model -> core
---

## Boundaries

- `model -> *`: a representation computes nothing and depends on nothing.
- `core -> api`: a stage never reaches back to the thing that constructed it.
"""

OTHER_CONTRACT = """---
layers:
  zeta: ["zeta_*"]
  eta:  ["eta_*"]

dependencies:
  allow:
    - zeta -> eta
  forbid:
    - eta -> zeta
---

## Boundaries

- `eta -> zeta`: a consumer never reaches back to the thing that constructed it.
"""

API_ENTRY = "import core_base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
API_EDGE = "import core_\n"
OTHER_EDGE = "import core_\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def git(parent, *args):
    subprocess.run(["git", *args], cwd=parent, check=True,
                   capture_output=True, timeout=120)


def drive(contract):
    run = subprocess.run(
        [sys.executable, "-m", "archituner", contract, "--json"],
        cwd=REPO, capture_output=True, timeout=120)
    assert b'"cross_contract"' in run.stdout, run.stderr
    return run


def own_project(parent):
    tree = os.path.join(parent, "proj")
    os.makedirs(tree)
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "api_edge.py", API_EDGE)
    plant(tree, "core_base.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    git(parent, "-C", "proj", "init", "-q")
    git(parent, "-C", "proj", "config", "user.email", "unit@example.com")
    git(parent, "-C", "proj", "config", "user.name", "unit")
    git(parent, "-C", "proj", "add", "-A")
    git(parent, "-C", "proj", "commit", "-qm", "proj")
    git(parent, "clone", "-q", "--bare", "proj", "proj.git")
    git(parent, "-C", "proj", "remote", "add", "origin",
        os.path.join(parent, "proj.git"))
    return parent, os.path.join(tree, "ARCHITECTURE.md")


def subscriber(parent):
    tree = os.path.join(parent, "other")
    os.makedirs(tree)
    plant(tree, "ARCHITECTURE.md", OTHER_CONTRACT)
    plant(tree, "edge.py", OTHER_EDGE)
    plant(tree, "zeta_thing.py", "VALUE = 1\n")
    git(parent, "-C", "other", "init", "-q")
    git(parent, "-C", "other", "config", "user.email", "unit@example.com")
    git(parent, "-C", "other", "config", "user.name", "unit")
    git(parent, "-C", "other", "add", "-A")
    git(parent, "-C", "other", "commit", "-qm", "other")


def test_a_sibling_with_an_undecodable_contract_leaves_the_reading_unchanged():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
    sibling = os.path.join(parent, "bad")
    os.makedirs(sibling)
    with open(os.path.join(sibling, "ARCHITECTURE.md"), "wb") as handle:
        handle.write(b"\xff\xfe\xfa\n")
    beside = drive(contract)
    assert beside.returncode == alone.returncode == 0, beside.stderr
    assert beside.stdout == alone.stdout, \
        "a sibling whose contract cannot be decoded contributes nothing, " \
        "as if it were not there: the reading is the bytes of the tree " \
        "alone"
    assert b"Traceback" not in beside.stderr, beside.stderr


def test_a_sibling_with_an_unreadable_module_leaves_the_reading_unchanged():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
    subscriber(parent)
    os.symlink(GONE, os.path.join(parent, "other", "gone.py"))
    beside = drive(contract)
    assert beside.returncode == alone.returncode == 0, beside.stderr
    assert beside.stdout == alone.stdout, \
        "a sibling whose module cannot be read contributes nothing, as " \
        "if it were not there: the reading is the bytes of the tree " \
        "alone, not of the sibling minus that one file"
    assert b"Traceback" not in beside.stderr, beside.stderr


def test_a_sibling_with_an_unreadable_gitignore_leaves_the_reading_unchanged():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
    subscriber(parent)
    os.symlink(parent, os.path.join(parent, "other", ".gitignore"))
    beside = drive(contract)
    assert beside.returncode == alone.returncode == 0, beside.stderr
    assert beside.stdout == alone.stdout, \
        "a sibling whose gitignore cannot be read contributes nothing, " \
        "as if it were not there: the reading is the bytes of the tree " \
        "alone"
    assert b"Traceback" not in beside.stderr, beside.stderr


def test_a_good_subscriber_beside_a_broken_sibling_still_contributes():
    parent, contract = own_project(tempfile.mkdtemp())
    subscriber(parent)
    good = drive(contract)
    sibling = os.path.join(parent, "broken")
    os.makedirs(sibling)
    plant(sibling, "ARCHITECTURE.md", OTHER_CONTRACT)
    plant(sibling, "stray.py", "import core_\n")
    os.symlink(GONE, os.path.join(sibling, "gone.py"))
    both = drive(contract)
    assert both.returncode == good.returncode == 0, both.stderr
    assert both.stdout == good.stdout, \
        "a sibling whose module cannot be read contributes nothing: the " \
        "subscriber beside it still contributes exactly as before"
    assert b'"contract": "other"' in good.stdout, good.stdout
    assert b"Traceback" not in both.stderr, both.stderr


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
