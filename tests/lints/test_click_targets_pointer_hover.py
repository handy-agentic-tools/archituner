# covers: archituner/presentation/page/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, "archituner", "presentation", "page")

CLOSEST = re.compile(r"closest\(([^)]*)\)")
ATTRIBUTE = re.compile(r"\[data-([a-z][a-z0-9-]*)\]")

TEXTS = [open(os.path.join(PAGE, name), encoding="utf-8").read()
         for name in sorted(glob.glob(os.path.join("**", "*.py"),
                                      root_dir=PAGE, recursive=True))]
SHEET = "".join(TEXTS)

DELEGATION = {
    "view": ["nav button"],
    "pair": ["#matrix td", "#stack .wire", "#detail li[data-pair]"],
    "layer": ["#stack .node"],
    "file": ["#detail li[data-file]"],
    "hit": ["button.hit"],
    "isolate": ["button.key"],
    "reset": ["button[data-reset]"],
    "findings": ["button.key"],
    "region": ["#treemap .region"],
    "reading": ["#reading button"],
    "figure": ["button.tally"],
    "cmd": ["#ask button"],
    "panel-tab": ["#panel-tabs button"],
    "close": ["#panel-head [data-close]"],
}

MARK = ["#stack .wire text"]
TARGETS = [s for names in DELEGATION.values() for s in names] + MARK


def delegated():
    bound = set()
    for text in TEXTS:
        bound |= set(ATTRIBUTE.findall("".join(CLOSEST.findall(text))))
    return bound


def undress(selector):
    cursor = re.search(re.escape(selector)
                       + r"(?![\w.:\[#>~+])[^{}]*\{[^{}]*"
                         r"cursor\s*:\s*pointer", SHEET)
    hover = re.search(re.escape(selector) + r":hover(?![\w-])", SHEET)
    return [name for name, held in
            (("cursor: pointer", cursor), ("a :hover rule", hover))
            if not held]


def test_every_delegated_attribute_maps_to_a_target():
    bound = delegated()
    assert bound, ("the page scripts hold no click delegation to read, "
                   "so the lint measures nothing")
    unmapped = sorted(bound - set(DELEGATION))
    assert not unmapped, ("the page delegates a click on a data attribute "
                          "the lint maps no target for: data-"
                          + ", data-".join(unmapped))


def test_every_click_target_shows_the_pointer_and_a_hover():
    missing = [(selector, undress(selector)) for selector in TARGETS]
    undressed = [selector + " (" + ", ".join(gaps) + ")"
                 for selector, gaps in missing if gaps]
    assert not undressed, ("clickable targets drawn without the pointer "
                           "and the hover the delegation promises: "
                           + "; ".join(undressed))


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
