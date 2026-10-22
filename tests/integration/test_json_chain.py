# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/** archituner/report/report.py archituner/vocabulary/**
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
    - isle -> leaf
  forbid:
    - entry -> leaf
    - entry -> isle
    - mid -> entry
    - mid -> leaf
    - mid -> isle
    - leaf -> entry
    - leaf -> mid
    - leaf -> isle
    - isle -> entry
    - isle -> mid
---

## Boundaries

- `entry -> *`: the entry reaches nowhere beside its one allowed hop.
- `mid -> *`: a hub is imported and never reaches back or sideways.
- `leaf -> *`: a leaf computes and depends on nothing.
- `isle -> *`: nothing reaches the isle, so it may only feed the leaf.
"""

ENTRY_MAIN = "MAIN = 1\n"
ENTRY_GATE = "import mid_hub\n"
MID_HUB = "import leaf_final\n"
LEAF_FINAL = "LEAF = 1\n"
ISLE_HUT = "import leaf_final\n"

CHAIN = {"entry": 0, "mid": 1, "leaf": 2, "isle": None}
LONGEST_CHAIN = ["entry", "mid", "leaf"]


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


def drive(contract):
    return subprocess.run([sys.executable, "-m", "archituner", contract,
                           "--json"], cwd=REPO, capture_output=True,
                          text=True, timeout=120)


def test_a_planted_tree_s_layers_carry_their_chain_from_its_entry_layer():
    with tempfile.TemporaryDirectory() as tree:
        proc = drive(build(tree))
    assert proc.returncode in (0, 1), (proc.returncode, proc.stdout,
                                       proc.stderr)
    document = json.loads(proc.stdout)
    chains = {row["name"]: row["chain"] for row in document["layers"]}
    assert chains == CHAIN, chains
    assert document["shape"]["longest_chain"] == LONGEST_CHAIN, \
        document["shape"]


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
