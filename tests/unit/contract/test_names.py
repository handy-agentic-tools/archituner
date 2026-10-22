import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.names import refuse_undeclared_ancestors


def test_an_undeclared_parent_is_refused():
    layers = {"a": ["src_a/" + "**"], "b": ["src_b/" + "**"],
              "a.child": ["src_a/child/" + "**"], "x.child": ["src_x/" + "**"]}
    try:
        refuse_undeclared_ancestors(layers)
    except SystemExit as e:
        assert "parent" in str(e), str(e)
        assert "x" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the undeclared parent parsed")


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
