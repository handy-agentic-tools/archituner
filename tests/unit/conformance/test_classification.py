import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.conformance.classification

SUB_ORDER = ["a.child", "a.child2", "a", "b"]
SUB_PAIRS = {("a", "b"): "allow", ("b", "a"): "allow",
             ("a.child", "a.child2"): "allow",
             ("a.child2", "a.child"): "allow"}
SUB_EDGES = {("a", "b"): ({"file": "src/pkg_a/child/c.py",
                           "module": "pkg_b.b", "line": 1},),
             ("a.child2", "a.child"): ({"file": "src/pkg_a/child2/d.py",
                                        "module": "src.pkg_a.child.c",
                                        "line": 1},)}
SUB_HELD = {"a.child": 1, "a.child2": 1, "a": 1, "b": 1}

FLAT_ORDER = ["a", "b"]
FLAT_PAIRS = {("a", "b"): "allow", ("b", "a"): "allow"}
FLAT_EDGES = {("a", "b"): ({"file": "src_a/x.py",
                            "module": "src_b.b", "line": 1},)}
FLAT_HELD = {"a": 1, "b": 1}


def test_a_sublayer_contract_classifies_without_a_missing_pair():
    table, _ = archituner.conformance.classification.pair_readings(
        SUB_ORDER, SUB_PAIRS, SUB_EDGES, {}, SUB_HELD)
    rows = [(row["source"], row["target"]) for row in table]
    assert rows == [("a.child", "a.child2"), ("a.child2", "a.child"),
                    ("a", "b"), ("b", "a")], rows
    assert all(source != target for source, target in rows), rows


def test_the_table_holds_exactly_the_decided_pairs():
    table, _ = archituner.conformance.classification.pair_readings(
        SUB_ORDER, SUB_PAIRS, SUB_EDGES, {}, SUB_HELD)
    rows = [(row["source"], row["target"]) for row in table]
    assert sorted(rows) == sorted([("a", "b"), ("b", "a"),
                                   ("a.child", "a.child2"),
                                   ("a.child2", "a.child")]), rows


def test_a_flat_contract_classifies_the_same_rows():
    table, _ = archituner.conformance.classification.pair_readings(
        FLAT_ORDER, FLAT_PAIRS, FLAT_EDGES, {}, FLAT_HELD)
    assert [(row["source"], row["target"]) for row in table] == \
        [("a", "b"), ("b", "a")]
    assert [row["state"] for row in table] == ["convergence", "absence"]


def run_one(pair):
    name, test = pair
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    entries = sorted(filter(lambda item: item[0].startswith("test_"),
                            globals().items()))
    failures = sum(map(run_one, entries))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
