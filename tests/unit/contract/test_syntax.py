import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.syntax import parse_override


def test_an_override_entry_not_in_its_one_shape_is_refused():
    try:
        parse_override("size `a`: 4000")
    except SystemExit as e:
        assert "4000" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the reasonless entry parsed")
    try:
        parse_override("size `a`: forty - why")
    except SystemExit as e:
        assert "forty" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the countless entry parsed")


def test_an_override_whose_selector_reaches_no_file_parses_anyway():
    override = parse_override(
        "size `src_x/" + "**`: 12 - parked outside the tree")
    assert override == ("size", "src_x/" + "**", 12,
                        "parked outside the tree"), override


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
