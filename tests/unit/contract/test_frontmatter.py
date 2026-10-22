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


def test_ignore_is_a_top_level_list_of_globs():
    front = parse_front_matter(
        temp_contract(BASE + ['ignore: ["gen_*.py", out/' + '**]']))
    assert front[5] == ["gen_*.py", "out/" + "**"], front[5]


def test_ignore_sits_beside_package_root():
    both = ['package_root: src_a'] + BASE + ['ignore: ["gen_*.py"]']
    front = parse_front_matter(temp_contract(both))
    assert front[4] == "src_a", front[4]
    assert front[5] == ["gen_*.py"], front[5]
    flipped = ['ignore: ["gen_*.py"]'] + BASE + ['package_root: src_a']
    front = parse_front_matter(temp_contract(flipped))
    assert front[4] == "src_a", front[4]
    assert front[5] == ["gen_*.py"], front[5]


def test_ignore_parses_wherever_it_sits_in_the_front_matter():
    first = ['ignore: ["gen_*.py"]'] + BASE
    middle = BASE[:3] + ['ignore: ["gen_*.py"]'] + BASE[3:]
    last = BASE + ['ignore: ["gen_*.py"]']
    for lines in (first, middle, last):
        front = parse_front_matter(temp_contract(lines))
        assert front[5] == ["gen_*.py"], (lines[0], front[5])


def test_ignore_absent_or_empty_reads_as_empty():
    front = parse_front_matter(temp_contract(BASE))
    assert front[5] == [], front[5]
    front = parse_front_matter(temp_contract(BASE + ["ignore: []"]))
    assert front[5] == [], front[5]


def test_an_indented_ignore_never_parses():
    front = parse_front_matter(
        temp_contract(BASE + ['  ignore: ["gen_*.py"]']))
    assert set(front[0]) == {"a", "b"}, front[0]
    assert front[5] == [], front[5]


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
