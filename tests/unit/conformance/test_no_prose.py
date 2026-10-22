import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.conformance.no_prose

SHEBANG = "#!/usr/bin/env python3\n"
COVERS = "# covers: archituner/" + "**\n"


def test_the_covers_directive_on_the_first_line_is_not_refused():
    found = archituner.conformance.no_prose.findings(
        (COVERS + "x = 1\n").encode())
    assert found == [], found


def test_the_covers_directive_after_a_shebang_is_not_refused():
    found = archituner.conformance.no_prose.findings(
        (SHEBANG + COVERS + "x = 1\n").encode())
    assert found == [], found


def test_the_covers_directive_on_line_2_without_a_shebang_is_refused():
    found = archituner.conformance.no_prose.findings(
        ("x = 1\n" + COVERS).encode())
    assert [row for row, _ in found] == [2], found


def test_the_covers_directive_on_line_5_is_refused():
    found = archituner.conformance.no_prose.findings(
        ("x = 1\ny = 2\nz = 3\nw = 4\n" + COVERS).encode())
    assert [row for row, _ in found] == [5], found


def test_the_shebang_itself_stays_exempt():
    found = archituner.conformance.no_prose.findings(
        (SHEBANG + "x = 1\n").encode())
    assert found == [], found


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
