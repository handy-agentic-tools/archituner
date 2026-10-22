# covers: archituner/presentation/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SOURCE = os.path.join(ROOT, "archituner", "presentation")

HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{6}\b")
LENGTH_WITH_UNIT = re.compile(r"\b\d[\d.]*(?:px|rem|em)\b")
FONT_FACE = re.compile(r"\b(?:system-ui|sans-serif|serif|ui-monospace"
                       r"|monospace|SFMono-Regular|SF Mono|Menlo|Consolas"
                       r"|Liberation Mono)\b")


def literals_on(name, number, line):
    held = []
    for kind, pattern in (("colour", HEX_COLOUR),
                          ("length", LENGTH_WITH_UNIT),
                          ("face", FONT_FACE)):
        for match in pattern.findall(line):
            held.append(f"{name}:{number} {kind} {match}")
    return held


def test_no_presentation_module_holds_a_literal_value():
    held = []
    for name in sorted(glob.glob(os.path.join("**", "*.py"),
                                 root_dir=SOURCE, recursive=True)):
        with open(os.path.join(SOURCE, name), encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                held += literals_on(name, number, line)
    assert not held, (
        "presentation modules hold literal styling the theme does not exist "
        "to hold yet: " + ", ".join(held))


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            failures += outcome_of(name, test)
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(bool(failures))
