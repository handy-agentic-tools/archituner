import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.frontmatter import parse_front_matter


def temp_contract(lines):
    path = os.path.join(tempfile.mkdtemp(), "ARCHITECTURE.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("---\n" + "\n".join(lines) + "\n---\n\nBody.\n")
    return path


BASE = ["layers:",
        '  a: ["src_a/' + '**"]',
        '  b: ["src_b/' + '**"]',
        "dependencies:",
        "  allow:",
        "    - a -> b",
        "    - b -> a"]

LIMITS = ["limits:",
          "  size: 8000",
          "  defs: 8",
          "  depth: 4",
          "  cyclomatic: 30",
          "  cognitive: 50",
          "  prose_count: 0",
          "",
          "  overrides:",
          '    - "size `a`: 4000 - argv to intent to exit code"',
          '    - "cyclomatic `src_b/' + '**`: 40 - the walk tells many node '
          'kinds apart"',
          '    - "size `b`: none - the tables are generated"']


def test_the_limits_block_parses_its_defaults_wherever_it_sits():
    expected = {"size": 8000, "defs": 8, "depth": 4, "cyclomatic": 30,
                "cognitive": 50, "prose_count": 0}
    for at, lines in (("first", LIMITS + BASE),
                      ("middle", BASE[:3] + LIMITS + BASE[3:]),
                      ("last", BASE + LIMITS)):
        front = parse_front_matter(temp_contract(lines))
        assert front[6] == expected, (at, front[6])


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
