# covers: archituner/presentation/**
import glob
import operator
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SOURCE = os.path.join(ROOT, "archituner", "presentation")

MARKUP = re.compile(r"<(?:!doctype|div|svg|g|rect|path|text|table|tr|td|th"
                    r"|p|ul|li|h1|h2|button|nav|meta|title|style|script"
                    r"|input|select|label|span|code|br)\b")

DECLARATION = re.compile(r"^[ \t]*(?:const|let|var)[ \t]+(.*)$", re.M)
ASSIGNMENT = re.compile(r"([A-Za-z_$][\w$]*)\s*=\s*(.+?)\s*;?\s*$")
NONZERO_NUMBER = re.compile(r"(?=[^1-9]*[1-9])-?\d*\.?\d+$")
QUOTE = re.compile(r"['\"]")
FEED = r"\b{}\b"


def rows_of(text):
    return [(text.count("\n", 0, m.start()) + 1, piece.group(1),
             piece.group(2))
            for m in DECLARATION.finditer(text)
            for piece in filter(None, map(ASSIGNMENT.match,
                                          map(str.strip,
                                              m.group(1).split(","))))]


def fed_row(row, numeric):
    if QUOTE.search(row[2]) or row[1] in numeric:
        return None
    feeds = sorted(filter(
        lambda name: re.search(FEED.format(re.escape(name)), row[2]),
        numeric))
    return ((row[1], f"{row[1]} = {row[2]}  (from {', '.join(feeds)})")
            if feeds else None)


def declared_quantities(text):
    rows = rows_of(text)
    seeded = list(filter(lambda row: NONZERO_NUMBER.match(row[2]), rows))
    numeric = set(map(operator.itemgetter(1), seeded))
    declared = list(map(lambda row: (row[0], f"{row[1]} = {row[2]}"),
                        seeded))
    grown = True
    while grown:
        grown = False
        for row in rows:
            fed = fed_row(row, numeric)
            if fed:
                numeric.add(fed[0])
                declared.append((row[0], fed[1]))
                grown = True
    return declared


TEXTS = list(map(lambda name: (name, open(os.path.join(
    SOURCE, name), encoding="utf-8").read()),
    sorted(glob.glob(os.path.join("**", "*.py"), root_dir=SOURCE,
                     recursive=True))))

FINDINGS = [f"{name}:{number} {spelling}"
            for name, text in filter(lambda pair: MARKUP.search(pair[1]),
                                     TEXTS)
            for number, spelling in declared_quantities(text)]


def test_no_view_emits_its_own_geometry():
    assert not FINDINGS, ("a view declares the geometry it draws, where the "
                          "contract holds that layout arithmetic is a module "
                          "that returns coordinates: " + "; ".join(FINDINGS))


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
