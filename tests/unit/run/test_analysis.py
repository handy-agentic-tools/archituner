import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.analysis import analyse

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

STORED = {
    "files": {"api_entry.py": "api", "core_backbone.py": "core",
              "model_shape.py": "model"},
    "layers": ["api", "core", "model"],
    "pairs": {"api -> core": "convergence", "api -> model": "absence",
              "core -> model": "absence", "core -> api": "silence",
              "model -> api": "silence", "model -> core": "silence"},
}


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(stray=False):
    tree = os.path.join(tempfile.mkdtemp(), "scratch")
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", "import core_backbone\n")
    plant(tree, "core_backbone.py", "VALUE = 1\n")
    plant(tree, "model_shape.py", "VALUE = 2\n")
    if stray:
        plant(tree, "stray.py", "VALUE = 3\n")
    return tree, os.path.join(tree, "ARCHITECTURE.md")


def pair(reading, source, target):
    return next(p for p in reading["pairs"]
                if (p["source"], p["target"]) == (source, target))


def test_the_reading_names_the_contract_and_the_tree_for_a_reader_afar():
    tree, contract = build()
    reading = analyse(contract)
    assert (reading["contract"], reading["tree"]) == ("ARCHITECTURE.md",
                                                      "scratch")


def test_the_layers_travel_in_dependency_order_with_their_rows():
    tree, contract = build()
    reading = analyse(contract)
    rows = reading["layers"]
    assert (reading["order"], rows[0]["name"], rows[1]["name"],
            rows[2]["name"], rows[0]["globs"], rows[0]["files"],
            rows[0]["responsibility"], rows[0]["rationale"]) == (
        ["api", "core", "model"], "api", "core", "model", ["api_*"],
        ["api_entry.py"], "", "")


def test_the_pairs_carry_the_boundary_reason_and_the_witness():
    tree, contract = build()
    reading = analyse(contract)
    kept = pair(reading, "core", "api")
    assert (kept["reason"], kept["imports"], kept["was"]) == (
        "a stage never reaches back to the thing that constructed it.", [],
        None)
    assert pair(reading, "api", "core")["imports"] == [
        {"file": "api_entry.py", "module": "core_backbone", "line": 1}]


def test_the_counts_and_the_coverage_tally_the_walk():
    tree, contract = build(stray=True)
    reading = analyse(contract)
    records = reading["files"]
    assert (records[0]["path"], records[1]["path"], records[2]["path"],
            records[3]["path"]) == ("api_entry.py", "core_backbone.py",
                                    "model_shape.py", "stray.py")
    assert (records[-1]["layer"], reading["counts"],
            reading["coverage"]["claimed"], reading["coverage"]["unclaimed"],
            reading["coverage"]["tree"]["files"]) == (
        None, {"convergence": 1, "divergence": 0, "absence": 2, "silence": 3},
        3, 1, 4)


def test_a_stored_reading_answers_what_each_pair_was():
    tree, contract = build()
    reading = analyse(contract, STORED)
    stored = dict(STORED, pairs=dict(STORED["pairs"],
                                     **{"core -> api": "divergence"}))
    changed = analyse(contract, stored)
    assert (pair(reading, "api", "core")["state"],
            pair(reading, "api", "core")["was"],
            pair(changed, "core", "api")["state"],
            pair(changed, "core", "api")["was"]) == (
        "convergence", "convergence", "silence", "divergence")


def test_a_quiet_reading_answers_the_silence_of_every_side_question():
    tree, contract = build()
    reading = analyse(contract)
    assert (reading["findings"], reading["breaches"],
            reading["prose_percent"], reading["naming"],
            reading["invariants"], reading["enforcement"],
            reading["surface"]["cross_contract"],
            reading["shape"]["permitted"],
            reading["shape"]["realised"]) == (
        [], [], 0.0, [], [], "", None, 3, 1)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
