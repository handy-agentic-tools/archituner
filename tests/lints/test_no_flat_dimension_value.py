# covers: archituner/theme/** archituner/presentation/model/** archituner/presentation/page/views/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
HOME = os.path.join(ROOT, "archituner")
THEME = os.path.join(HOME, "theme", "__init__.py")
MODEL = os.path.join(HOME, "presentation", "model")
VIEWS = os.path.join(HOME, "presentation", "page", "views")

FLAT = re.compile(r"(?![^.\d-])(?!0?\.\d+\Z)(?!(?:var|calc|clamp|max)\()")
PAIR = re.compile(r'"([a-z0-9-]+)":\s*"([^"]*)"')
UNITED = re.compile(r"(?=.*\d)(?!.*UNIT)(?!.*['\"])")
CONSTANT = re.compile(r"^([A-Z][A-Z0-9_]*(?:\s*,\s*[A-Z][A-Z0-9_]*)*)"
                      r"\s*=\s*([^#\n]+)", re.M)
DICT = re.compile(r'(["\'][a-z0-9_]+["\'])\s*:\s*(-?\d+(?:\.\d+)?)')
OFFSET = re.compile(r"\+ (\d+(?:\.\d+)?)")
WHY = ("a dimension value stands flat where every token is computed from "
       "the one base unit: a theme entry is a var(), calc(), clamp() or "
       "max() of one, a model constant and every model geometry entry a "
       "UNIT multiple, and a view offset a splice from the model; a colour "
       "and a pure opacity number are no dimension")

THEME_TEXT = open(THEME, encoding="utf-8").read()
THEME_FINDINGS = [
    f"archituner/theme/__init__.py:"
    f"{THEME_TEXT.count(chr(10), 0, found.start()) + 1} "
    f"{found.group(1)} {found.group(2)}"
    for found in PAIR.finditer(THEME_TEXT)
    if FLAT.match(found.group(2))]
MODEL_TEXTS = [(name, open(os.path.join(MODEL, name), encoding="utf-8").read())
               for name in sorted(glob.glob("*.py", root_dir=MODEL))]
MODEL_FINDINGS = [
    f"archituner/presentation/model/{name}:"
    f"{text.count(chr(10), 0, found.start()) + 1} "
    f"{found.group(1)} = {found.group(2).strip()}"
    for name, text in MODEL_TEXTS
    for found in CONSTANT.finditer(text)
    if UNITED.match(found.group(0))]
GEOMETRY_FINDINGS = [
    f"archituner/presentation/model/{name}:"
    f"{text.count(chr(10), 0, found.start()) + 1} "
    f"{found.group(1)} holds {found.group(2)}"
    for name, text in MODEL_TEXTS
    for found in DICT.finditer(text)]
VIEW_TEXTS = [(name, open(os.path.join(VIEWS, name), encoding="utf-8").read())
              for name in sorted(glob.glob("*.py", root_dir=VIEWS))]
VIEW_FINDINGS = [
    f"archituner/presentation/page/views/{name}:"
    f"{text.count(chr(10), 0, found.start()) + 1} + {found.group(1)}"
    for name, text in VIEW_TEXTS
    for found in OFFSET.finditer(text)
    if found.group(1) not in ("0", "1")]
FINDINGS = (THEME_FINDINGS + MODEL_FINDINGS + GEOMETRY_FINDINGS
            + VIEW_FINDINGS)


def test_no_dimension_stands_flat():
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
