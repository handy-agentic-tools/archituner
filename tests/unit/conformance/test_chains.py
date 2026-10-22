import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.conformance.chains


def test_a_straight_chain_counts_its_links():
    edges = {("a", "b"): [{"file": "pkg_a/x.py", "module": "pkg_b.y",
                           "line": 3}],
             ("b", "c"): [{"file": "pkg_b/y.py", "module": "pkg_c.z",
                           "line": 7}]}
    assert archituner.conformance.chains.chains(
        ["a", "b", "c"], edges, "a") == {
            "chain": {"a": 0, "b": 1, "c": 2},
            "longest_chain": ["a", "b", "c"]}


def test_a_diamond_takes_the_longest_side():
    edges = {("entry", "short"): [{"file": "e.py", "module": "s",
                                   "line": 1}],
             ("entry", "mid"): [{"file": "e.py", "module": "m",
                                 "line": 2}],
             ("mid", "deep"): [{"file": "m.py", "module": "d",
                                "line": 3}],
             ("deep", "sink"): [{"file": "d.py", "module": "k",
                                 "line": 4}],
             ("short", "sink"): [{"file": "s.py", "module": "k",
                                  "line": 5}]}
    assert archituner.conformance.chains.chains(
        ["entry", "short", "mid", "deep", "sink"], edges, "entry") == {
            "chain": {"entry": 0, "short": 1, "mid": 1, "deep": 2,
                      "sink": 3},
            "longest_chain": ["entry", "mid", "deep", "sink"]}


def test_a_layer_reached_only_from_a_test_layer_is_none():
    edges = {("cli", "run"): [{"file": "cli.py", "module": "run",
                               "line": 1}],
             ("tests_unit", "vocabulary"): [{"file": "test_v.py",
                                             "module": "vocabulary",
                                             "line": 2}]}
    assert archituner.conformance.chains.chains(
        ["cli", "run", "tests_unit", "vocabulary"], edges, "cli") == {
            "chain": {"cli": 0, "run": 1, "tests_unit": None,
                      "vocabulary": None},
            "longest_chain": ["cli", "run"]}


def test_the_entry_layer_sits_at_zero():
    assert archituner.conformance.chains.chains(
        ["solo", "far"], {}, "solo") == {
            "chain": {"solo": 0, "far": None},
            "longest_chain": ["solo"]}


def test_no_entry_layer_leaves_every_chain_none():
    edges = {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}]}
    assert archituner.conformance.chains.chains(
        ["a", "b"], edges, None) == {
            "chain": {"a": None, "b": None},
            "longest_chain": []}


def test_a_cycle_terminates():
    edges = {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}],
             ("b", "c"): [{"file": "b.py", "module": "c", "line": 2}],
             ("c", "a"): [{"file": "c.py", "module": "a", "line": 3}]}
    assert archituner.conformance.chains.chains(
        ["a", "b", "c"], edges, "a") == {
            "chain": {"a": 0, "b": 1, "c": 2},
            "longest_chain": ["a", "b", "c"]}


def test_an_equal_tie_takes_the_first_in_names_order():
    edges = {("entry", "left"): [{"file": "e.py", "module": "l",
                                  "line": 1}],
             ("entry", "right"): [{"file": "e.py", "module": "r",
                                   "line": 2}],
             ("left", "sink"): [{"file": "l.py", "module": "k",
                                 "line": 3}],
             ("right", "sink"): [{"file": "r.py", "module": "k",
                                  "line": 4}]}
    assert archituner.conformance.chains.chains(
        ["entry", "left", "right", "sink"], edges, "entry") == {
            "chain": {"entry": 0, "left": 1, "right": 1, "sink": 2},
            "longest_chain": ["entry", "left", "sink"]}
    assert archituner.conformance.chains.chains(
        ["entry", "right", "left", "sink"], edges, "entry") == {
            "chain": {"entry": 0, "right": 1, "left": 1, "sink": 2},
            "longest_chain": ["entry", "right", "sink"]}


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
