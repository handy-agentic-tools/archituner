import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.conformance.ordering

THREE_CYCLE = {
    "per_layer": [{"name": "a", "out": 1, "in": 1,
                   "out_realised": 1, "in_realised": 1},
                  {"name": "b", "out": 1, "in": 1,
                   "out_realised": 0, "in_realised": 1},
                  {"name": "c", "out": 1, "in": 1,
                   "out_realised": 1, "in_realised": 0}],
    "longest_path": 2, "permitted": 3, "realised": 2}

TAILED_CYCLE = {
    "per_layer": [{"name": "a", "out": 1, "in": 0,
                   "out_realised": 1, "in_realised": 0},
                  {"name": "b", "out": 1, "in": 2,
                   "out_realised": 1, "in_realised": 1},
                  {"name": "c", "out": 2, "in": 1,
                   "out_realised": 1, "in_realised": 1},
                  {"name": "d", "out": 0, "in": 1,
                   "out_realised": 0, "in_realised": 1}],
    "longest_path": 3, "permitted": 4, "realised": 3}


def test_an_acyclic_chain_counts_both_links():
    held = archituner.conformance.ordering.measure_shape(
        ["a", "b", "c"], {("a", "b"), ("b", "c")},
        {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}]})
    assert held == {
        "per_layer": [{"name": "a", "out": 1, "in": 0,
                       "out_realised": 1, "in_realised": 0},
                      {"name": "b", "out": 1, "in": 1,
                       "out_realised": 0, "in_realised": 1},
                      {"name": "c", "out": 0, "in": 1,
                       "out_realised": 0, "in_realised": 0}],
        "longest_path": 2, "permitted": 2, "realised": 1}


def test_a_three_cycle_ignores_the_pair_laid_against_the_order():
    pairs = {("a", "b"), ("b", "c"), ("c", "a")}
    held = archituner.conformance.ordering.measure_shape(
        ["a", "b", "c"], pairs,
        {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}],
         ("c", "a"): [{"file": "c.py", "module": "a", "line": 3}]})
    assert held == THREE_CYCLE


def test_a_mutual_pair_lays_one_link():
    held = archituner.conformance.ordering.measure_shape(
        ["a", "b"], {("a", "b"), ("b", "a")},
        {("a", "b"): [{"file": "a.py", "module": "b", "line": 2}]})
    assert held == {
        "per_layer": [{"name": "a", "out": 1, "in": 1,
                       "out_realised": 1, "in_realised": 0},
                      {"name": "b", "out": 1, "in": 1,
                       "out_realised": 0, "in_realised": 1}],
        "longest_path": 1, "permitted": 2, "realised": 1}


def test_a_cycle_with_a_tail_lays_the_chain_through_it():
    pairs = {("a", "b"), ("b", "c"), ("c", "b"), ("c", "d")}
    held = archituner.conformance.ordering.measure_shape(
        ["a", "b", "c", "d"], pairs,
        {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}],
         ("b", "c"): [{"file": "b.py", "module": "c", "line": 2}],
         ("c", "d"): [{"file": "c.py", "module": "d", "line": 3}]})
    assert held == TAILED_CYCLE


def test_the_three_cycle_measures_the_same_under_any_pair_order():
    pairs = {("a", "b"), ("b", "c"), ("c", "a")}
    edges = {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}],
             ("c", "a"): [{"file": "c.py", "module": "a", "line": 3}]}
    forms = [list(order) for order in itertools.permutations(pairs)]
    forms += [pairs, frozenset(pairs)]
    held = [archituner.conformance.ordering.measure_shape(
                ["a", "b", "c"], form, edges) for form in forms]
    assert held == [THREE_CYCLE] * len(held)


def test_the_tailed_cycle_measures_the_same_under_any_pair_order():
    pairs = {("a", "b"), ("b", "c"), ("c", "b"), ("c", "d")}
    edges = {("a", "b"): [{"file": "a.py", "module": "b", "line": 1}],
             ("b", "c"): [{"file": "b.py", "module": "c", "line": 2}],
             ("c", "d"): [{"file": "c.py", "module": "d", "line": 3}]}
    forms = [list(order) for order in itertools.permutations(pairs)]
    forms += [pairs, frozenset(pairs)]
    held = [archituner.conformance.ordering.measure_shape(
                ["a", "b", "c", "d"], form, edges) for form in forms]
    assert held == [TAILED_CYCLE] * len(held)


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
