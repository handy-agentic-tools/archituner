import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.pairs import decide_pairs


def test_a_non_sibling_edge_is_refused():
    layers = {"a": ["src_a/" + "**"], "b": ["src_b/" + "**"],
              "a.child": ["src_a/child/" + "**"]}
    try:
        decide_pairs(layers, ["a -> b", "b -> a", "a.child -> b"], [], [])
    except SystemExit as e:
        assert "sibling" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the non-sibling edge parsed")
    try:
        decide_pairs(layers, ["a -> b", "b -> a", "a -> a.child"], [], [])
    except SystemExit as e:
        assert "sibling" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the ancestor edge parsed")


def test_totality_is_judged_per_sibling_set():
    layers = {"a": ["src_a/" + "**"], "b": ["src_b/" + "**"],
              "a.child": ["src_a/child/" + "**"],
              "a.child2": ["src_a/child2/" + "**"]}
    allow = ["a -> b", "b -> a", "a.child -> a.child2",
             "a.child2 -> a.child"]
    try:
        pairs = decide_pairs(layers, allow, [], [])
    except SystemExit as e:
        raise AssertionError(f"refused: {e}")
    assert set(pairs) == {("a", "b"), ("b", "a"),
                          ("a.child", "a.child2"),
                          ("a.child2", "a.child")}, pairs
    assert set(pairs.values()) == {"allow"}, pairs


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
