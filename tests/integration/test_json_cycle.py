# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/** archituner/report/* archituner/vocabulary/**
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CONTRACT = """---
layers:
  entry: ["__main__.py", "entry_*"]
  mid:   ["mid_*"]
  leaf:  ["leaf_*"]
  isle:  ["isle_*"]

dependencies:
  allow:
    - entry -> mid
    - mid -> leaf
    - leaf -> isle
    - isle -> entry
  forbid:
    - entry -> leaf
    - entry -> isle
    - mid -> entry
    - mid -> isle
    - leaf -> entry
    - leaf -> mid
    - isle -> mid
    - isle -> leaf
---

## Boundaries

- `entry -> *`: the entry reaches the hub and nothing beside it.
- `mid -> *`: the hub feeds the leaf and never reaches back.
- `leaf -> *`: the leaf feeds the isle and never reaches back.
- `isle -> *`: the isle closes the cycle back into the entry.
"""

ENTRY_MAIN = "MAIN = 1\n"
ENTRY_GATE = "import mid_hub\n"
MID_HUB = "import leaf_final\n"
LEAF_FINAL = "import isle_hut\n"
ISLE_HUT = "import entry_gate\n"

SEEDS = (0, 1, 2, 3)
LONGEST_PATH = 3


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(tree):
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "__main__.py", ENTRY_MAIN)
    plant(tree, "entry_gate.py", ENTRY_GATE)
    plant(tree, "mid_hub.py", MID_HUB)
    plant(tree, "leaf_final.py", LEAF_FINAL)
    plant(tree, "isle_hut.py", ISLE_HUT)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(contract, seed):
    return subprocess.run([sys.executable, "-m", "archituner", contract,
                           "--json"], cwd=REPO, capture_output=True,
                          text=True, timeout=120,
                          env=dict(os.environ, PYTHONHASHSEED=str(seed)))


def test_a_cyclic_allow_set_measures_one_longest_path_under_every_seed():
    with tempfile.TemporaryDirectory() as tree:
        runs = [drive(build(tree), seed) for seed in SEEDS]
    for run in runs:
        assert run.returncode in (0, 1), (run.returncode, run.stdout,
                                          run.stderr)
    documents = [json.loads(run.stdout) for run in runs]
    for document in documents:
        assert document["shape"]["longest_path"] == LONGEST_PATH, \
            document["shape"]
    assert runs[0].stdout == runs[1].stdout == runs[2].stdout \
        == runs[3].stdout


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
