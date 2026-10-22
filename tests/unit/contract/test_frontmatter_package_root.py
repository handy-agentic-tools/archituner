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


def test_a_package_root_block_form_is_refused_naming_the_inline_form():
    try:
        parse_front_matter(temp_contract(
            BASE + ['package_root:', '  - "src_a"']))
    except SystemExit as e:
        assert "package_root" in str(e), str(e)
        assert "on its own line" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the block form parsed")
    try:
        parse_front_matter(temp_contract(BASE + ["package_root:"]))
    except SystemExit as e:
        assert "package_root" in str(e), str(e)
        assert "on its own line" in str(e), str(e)
    else:
        raise AssertionError("no refusal: the valueless key parsed")


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
