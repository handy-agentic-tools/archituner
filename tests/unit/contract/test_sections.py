import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.sections import read_section_line


def layers_front():
    return {"layers": {}, "allow": [], "forbid": [], "naming": [],
            "package_root": None, "ignore": [], "limits": {},
            "overrides": [], "section": "layers"}


def test_a_dotted_name_parses_as_a_sublayer():
    front = layers_front()
    read_section_line(front, 'a: ["src_a/' + '**"]')
    read_section_line(front, 'b: ["src_b/' + '**"]')
    read_section_line(front, 'a.child: ["src_a/child/' + '**"]')
    assert "a.child" in front["layers"], front["layers"]
    assert front["layers"]["a.child"] == ["src_a/child/" + "**"], \
        front["layers"]
    assert front["layers"]["a"] == ["src_a/" + "**"], front["layers"]


def test_a_nested_layer_block_is_refused():
    front = layers_front()
    read_section_line(front, 'a: ["src_a/' + '**"]')
    try:
        read_section_line(front, "b:")
    except SystemExit as e:
        assert "nested" in str(e), str(e)
        assert "b" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the nested block parsed")


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
