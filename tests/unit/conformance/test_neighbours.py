import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.conformance.neighbours


def test_a_small_graph_lists_both_sides_and_their_counts():
    edges = {("cli", "run"): [{"file": "archituner/cli/__init__.py",
                               "module": "archituner.run", "line": 4}],
             ("run", "vocabulary"): [{"file": "archituner/run/machine.py",
                                      "module": "archituner.vocabulary",
                                      "line": 6}],
             ("cli", "vocabulary"): [{"file": "archituner/cli/pages.py",
                                      "module": "archituner.vocabulary",
                                      "line": 3}]}
    held = archituner.conformance.neighbours.neighbours(
        ["cli", "run", "vocabulary"], edges)
    assert held == {
        "cli": {"uses": ["run", "vocabulary"], "used_by": []},
        "run": {"uses": ["vocabulary"], "used_by": ["cli"]},
        "vocabulary": {"uses": [], "used_by": ["cli", "run"]}}
    assert len(held["cli"]["uses"]) == 2
    assert len(held["run"]["used_by"]) == 1
    assert len(held["vocabulary"]["used_by"]) == 2


def test_both_lists_follow_names_order_not_edge_insertion_order():
    edges = {("a", "m"): [{"file": "a.py", "module": "m", "line": 1}],
             ("a", "z"): [{"file": "a.py", "module": "z", "line": 2}],
             ("m", "z"): [{"file": "m.py", "module": "z", "line": 3}]}
    assert archituner.conformance.neighbours.neighbours(
        ["z", "m", "a"], edges) == {
            "z": {"uses": [], "used_by": ["m", "a"]},
            "m": {"uses": ["z"], "used_by": ["a"]},
            "a": {"uses": ["z", "m"], "used_by": []}}
    assert archituner.conformance.neighbours.neighbours(
        ["a", "m", "z"], edges) == {
            "z": {"uses": [], "used_by": ["a", "m"]},
            "m": {"uses": ["z"], "used_by": ["a"]},
            "a": {"uses": ["m", "z"], "used_by": []}}


def test_a_forbidden_import_is_still_a_use():
    edges = {("cli", "presentation"): [{"file": "archituner/cli/leak.py",
                                        "module": "archituner."
                                        "presentation.report", "line": 9}]}
    assert archituner.conformance.neighbours.neighbours(
        ["cli", "presentation"], edges) == {
            "cli": {"uses": ["presentation"], "used_by": []},
            "presentation": {"uses": [], "used_by": ["cli"]}}


def test_a_layer_using_nothing_and_used_by_nothing_holds_two_empty_lists():
    edges = {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}]}
    assert archituner.conformance.neighbours.neighbours(
        ["island", "a", "b"], edges) == {
            "island": {"uses": [], "used_by": []},
            "a": {"uses": ["b"], "used_by": []},
            "b": {"uses": [], "used_by": ["a"]}}


def test_a_self_edge_is_not_a_use():
    edges = {("a", "a"): [{"file": "pkg_a/x.py", "module": "pkg_a.y",
                           "line": 2}]}
    assert archituner.conformance.neighbours.neighbours(
        ["a", "b"], edges) == {
            "a": {"uses": [], "used_by": []},
            "b": {"uses": [], "used_by": []}}


def test_an_edge_naming_a_layer_not_in_names_is_ignored():
    edges = {("a", "ghost"): [{"file": "a.py", "module": "ghost",
                               "line": 4}],
             ("ghost", "a"): [{"file": "ghost.py", "module": "a",
                               "line": 5}],
             ("a", "b"): [{"file": "a.py", "module": "b", "line": 6}]}
    assert archituner.conformance.neighbours.neighbours(
        ["a", "b"], edges) == {
            "a": {"uses": ["b"], "used_by": []},
            "b": {"uses": [], "used_by": ["a"]}}


def main():
    failures = 0
    tests = filter(lambda item: item[0].startswith("test_"),
                   sorted(globals().items()))
    for name, test in tests:
        try:
            test()
            print(f"PASS  {name}")
        except Exception as e:
            print(f"FAIL  {name}  {type(e).__name__}: {e}")
            failures += 1
    print(f"{failures} failed" if failures else "all green")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
