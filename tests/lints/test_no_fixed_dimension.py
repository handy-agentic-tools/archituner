# covers: archituner/presentation/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, "archituner", "presentation")

TAG_RADIUS = re.compile(r"\br[xy]\s*=\s*['\"][\d.]")
DECLARATION = re.compile(r"([a-z-]+)\s*:\s*([^;{}'\"]+)")
BARE = re.compile(r"(?!(?:0|auto|100vh|100%|1)\Z)-?[\d.][\d\s.]*")
FIXED = re.compile(r"\d[\d.]*(?:px|rem|em)\b")
SPARED = re.compile(r"@media|@container|@supports|0\.0625rem"
                    r"|max\(.*2px|2px.*max\("
                    r"|width: 1px|height: 1px|margin: -1px"
                    r"|clip: rect\(|clip-path: inset\(50%\)"
                    r"|white-space: nowrap|position: absolute")
WHY = ("a dimension stands fixed where every value is a token computed "
       "from the one base unit; the exceptions are the focus ring's 2px "
       "floor (WCAG 2.2), media threshold lines, the visually-hidden "
       "idiom, the base unit's own line and the structural 0, auto, "
       "100vh, 100% and 1")


def flag(rel, number, line):
    held = []
    if TAG_RADIUS.search(line):
        held.append(f"{rel}:{number} radius on the tag")
    for prop, value in DECLARATION.findall(line):
        if BARE.fullmatch(value):
            held.append(f"{rel}:{number} {prop} {value}")
    found = FIXED.search(line)
    if found and not SPARED.search(line):
        held.append(f"{rel}:{number} length {found.group()}")
    return held


def findings_on(name, text):
    rel = "archituner/presentation/" + name
    held = []
    for number, line in enumerate(text.splitlines(), 1):
        held += flag(rel, number, line)
    return held


TEXTS = [(name, open(os.path.join(PAGE, name), encoding="utf-8").read())
         for name in sorted(glob.glob(os.path.join("**", "*.py"),
                                      root_dir=PAGE, recursive=True))]
FINDINGS = [finding
            for name, text in TEXTS
            if not name.startswith("model")
            for finding in findings_on(name, text)]


def test_no_rule_or_tag_holds_a_fixed_dimension():
    assert not FINDINGS, WHY + ": " + "; ".join(FINDINGS)


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
