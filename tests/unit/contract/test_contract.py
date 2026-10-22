import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract import read_contract
from archituner.vocabulary import Contract


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

IGNORE_BLOCK = ['ignore:',
                '  - "plans/repro_*.py"',
                '  - gen_*.py']


def parsed_or_fail(lines):
    try:
        return read_contract(temp_contract(lines))
    except SystemExit as e:
        raise AssertionError(f"refused: {e}")


def refusal_of(lines):
    try:
        read_contract(temp_contract(lines))
    except SystemExit as e:
        return str(e)
    raise AssertionError("no refusal: the contract parsed")


def test_a_contract_value_defaults_to_no_ignored_globs():
    contract = Contract(path="ARCHITECTURE.md", layers={}, pairs={},
                        naming=[], package_root=None, body="", findings=[])
    assert contract.ignore == [], contract.ignore


def test_ignore_block_list_parses_like_the_inline_form():
    inline = parsed_or_fail(BASE + ['ignore: ["plans/repro_*.py", gen_*.py]'])
    block = parsed_or_fail(BASE + IGNORE_BLOCK)
    for contract in (inline, block):
        assert contract.ignore == ["plans/repro_*.py", "gen_*.py"], \
            contract.ignore
        assert set(contract.pairs) == {("a", "b"), ("b", "a")}, contract.pairs
    assert inline.ignore == block.ignore, (inline.ignore, block.ignore)
    for at, lines in (("first", IGNORE_BLOCK + BASE),
                      ("middle", BASE[:3] + IGNORE_BLOCK + BASE[3:]),
                      ("last", BASE + IGNORE_BLOCK)):
        contract = parsed_or_fail(lines)
        assert contract.ignore == ["plans/repro_*.py", "gen_*.py"], \
            (at, contract.ignore)


def test_a_contract_value_defaults_to_no_limits():
    contract = Contract(path="ARCHITECTURE.md", layers={}, pairs={},
                        naming=[], package_root=None, body="", findings=[])
    assert contract.limits == {}, contract.limits
    assert contract.overrides == [], contract.overrides


def test_an_override_naming_a_number_whose_default_is_absent_is_refused():
    lines = BASE + ["limits:",
                    "  size: 8000",
                    "",
                    "  overrides:",
                    '    - "cyclomatic `a`: 40 - the walk tells many node '
                    'kinds apart"']
    refusal = refusal_of(lines)
    assert "cyclomatic" in refusal, refusal


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
