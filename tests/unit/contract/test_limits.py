import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.limits import read_limits_line

DEFAULTS = ["  size: 8000", "  defs: 8", "  depth: 4", "  cyclomatic: 30",
            "  cognitive: 50", "  prose_count: 0"]

OVERRIDES_BLOCK = ["  overrides:",
                   '    - "size `a`: 4000 - argv to intent to exit code"',
                   '    - "cyclomatic `src_b/' + '**`: 40 - the walk tells '
                   'many node kinds apart"',
                   '    - "size `b`: none - the tables are generated"']

INLINE = ['overrides: ["size `a`: 4000 - argv to intent to exit code", '
          '"cyclomatic `src_b/' + '**`: 40 - the walk tells many node '
          'kinds apart", '
          '"size `b`: none - the tables are generated"]']

OVERRIDES = [("size", "a", 4000, "argv to intent to exit code"),
             ("cyclomatic", "src_b/" + "**", 40,
              "the walk tells many node kinds apart"),
             ("size", "b", None, "the tables are generated")]


def read_block(lines):
    section, limits, overrides = "limits", {}, []
    for stripped in filter(None, map(str.strip, lines)):
        section, overrides = read_limits_line(section, stripped,
                                              limits, overrides)
    return limits, overrides


def refusal_of(stripped, limits):
    try:
        read_limits_line("limits", stripped, limits, [])
    except SystemExit as e:
        return str(e)
    raise AssertionError("no refusal: the line parsed")


def test_overrides_parse_in_both_list_forms():
    block_limits, block_overrides = read_block(
        DEFAULTS + [""] + OVERRIDES_BLOCK)
    inline_limits, inline_overrides = read_block(DEFAULTS + [""] + INLINE)
    assert block_overrides == OVERRIDES, block_overrides
    assert inline_overrides == OVERRIDES, inline_overrides
    assert inline_limits == block_limits, (inline_limits, block_limits)


def test_a_limits_key_naming_an_unmeasured_number_is_refused():
    refusal = refusal_of("fanout: 5", {"size": 8000})
    assert "fanout" in refusal, refusal


def test_a_default_that_is_not_a_plain_count_is_refused():
    refusal = refusal_of("size: none", {})
    assert "none" in refusal, refusal
    assert "size" in refusal, refusal
    refusal = refusal_of("depth: many", {})
    assert "many" in refusal, refusal
    assert "depth" in refusal, refusal
    refusal = refusal_of("size: -3", {})
    assert "size" in refusal, refusal


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
