# covers: archituner/run/** archituner/source/**
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

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
    return run.stdout


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


def test_a_git_worktree_beside_the_tree_is_not_a_subscriber():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
    git(parent, "-C", "proj", "worktree", "add", "--detach", "../twin",
        "HEAD")
    beside = drive(contract)
    assert alone == beside, \
        "a git worktree of this repository shares the tree's git common " \
        "dir: another checkout of the same project is not a subscriber, " \
        "so the reading is the bytes of the tree alone"


def test_a_clone_beside_the_tree_is_not_a_subscriber():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
    git(parent, "clone", "-q", os.path.join(parent, "proj.git"), "twin")
    beside = drive(contract)
    assert alone == beside, \
        "a clone of this repository carries the same remote.origin.url: " \
        "another checkout of the same project is not a subscriber, so " \
        "the reading is the bytes of the tree alone"


def test_a_genuinely_different_project_beside_is_still_a_subscriber():
    parent, contract = own_project(tempfile.mkdtemp())
    alone = drive(contract)
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
    beside = drive(contract)
    assert alone != beside, \
        "a different project, owning its repository and declaring no " \
        "package root this tree declares, that imports a name this tree " \
        "exposes is a subscriber: the reading differs from the bytes of " \
        "the tree alone"


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
