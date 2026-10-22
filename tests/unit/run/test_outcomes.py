import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.outcomes import page_lines
from archituner.run.outcomes import quoted_lines

READING = {"contract": "ARCHITECTURE.md",
           "layers": [{"name": "api"}, {"name": "core"}, {"name": "model"}],
           "files": [{"path": "api_entry.py", "layer": "api"},
                     {"path": "core_base.py", "layer": "core"},
                     {"path": "stray.py", "layer": None}],
           "findings": [],
           "counts": {"convergence": 1, "divergence": 0, "absence": 2,
                      "silence": 3},
           "change": None}


def test_quoted_lines_carry_each_witness_row_stripped_and_once():
    tree = tempfile.mkdtemp()
    with open(os.path.join(tree, "one.py"), "w", encoding="utf-8") as handle:
        handle.write("alpha\nbeta\ngamma\n")
    os.makedirs(os.path.join(tree, "sub"))
    with open(os.path.join(tree, "sub", "two.py"), "w",
              encoding="utf-8") as handle:
        handle.write(" first\nsecond\n")
    witnesses = [{"file": "one.py", "line": 2}, {"file": "one.py", "line": 1},
                 {"file": "one.py", "line": 1},
                 {"file": "sub/two.py", "line": 1}]
    assert quoted_lines(tree, witnesses) == {
        ("one.py", 1): "alpha", ("one.py", 2): "beta",
        ("sub/two.py", 1): "first"}


def test_the_page_lines_are_the_tallies_of_the_reading_and_its_artifact():
    assert page_lines(READING, "c.md", "p.html") == [
        "c.md",
        "  layers 3  files 3  unclaimed 1",
        "  convergence 1  divergence 0  absence 2  silence 3",
        "  findings 0",
        "  -> p.html"]


def test_a_stored_change_adds_its_comparison_line():
    reading = dict(READING, change={"counts": {"improved": 0, "regressed": 1,
                                               "unchanged": 5}})
    lines = page_lines(reading, "c.md", "p.html")
    assert lines[-2:] == ["  vs baseline: improved 0  regressed 1",
                          "  -> p.html"]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
