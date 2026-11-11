# covers: archituner/presentation/page/views/** archituner/presentation/page/shell/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, "archituner", "presentation", "page")
ATTRIBUTE = re.compile(
    r"""(?:data-[a-z-]+|value|title|aria-label)='[^"]*"\s*\+([^+]+?)\s*(?:\+|\n)""")
TEXT = re.compile(r"""[^-]>\s*"\s*\+([^+]+?)\s*(?:\+\s*"|\n)""")
INTERPOLATION = re.compile(ATTRIBUTE.pattern + "|" + TEXT.pattern)
CALL = re.compile(r"[A-Za-z_$][\w$.]*\(")
BUILT = ("(", '"', "'", "MOVED[", "GLYPH[", "DATA.counts[", "CHANGE.counts[") \
    + tuple("0123456789")


def sources():
    return sorted(glob.glob(os.path.join("**", "*.py"), root_dir=PAGE,
                            recursive=True))


def findings():
    held = set()
    for name in sources():
        with open(os.path.join(PAGE, name), encoding="utf-8") as handle:
            text = handle.read()
        for match in INTERPOLATION.finditer(text):
            piece = (match.group(1) or match.group(2)).strip()
            if not (piece.startswith(BUILT) or CALL.match(piece)):
                held.add("%s:%d %s %s" % (
                    name, text.count("\n", 0, match.start()) + 1,
                    ("attribute", "text")[match.group(1) is None], piece))
    return sorted(held)


def test_the_page_homes_hold_the_modules_the_rule_judges():
    assert sources() != [], PAGE


def test_every_interpolated_value_reaches_the_markup_through_the_escape():
    assert findings() == [], (
        "values reach the page markup without the escape: "
        + ", ".join(findings()))


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    TESTS = (test_the_page_homes_hold_the_modules_the_rule_judges,
             test_every_interpolated_value_reaches_the_markup_through_the_escape)
    failures = 0
    for test in TESTS:
        failures += outcome_of(test.__name__, test)
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(min(failures, 1))
