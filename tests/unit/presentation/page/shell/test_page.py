import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, ROOT)
import archituner
from archituner.theme import DARK
from archituner.theme import LIGHT

CONTRACT = os.path.join(ROOT, "ARCHITECTURE.md")

PAGE = archituner.render(archituner.analyse(CONTRACT))

PAYLOAD = "const DATA = "
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
BARE_NUMBER = re.compile(r"(?<![\w.])(?=[-0.]*[1-9])-?\d*\.?\d+(?![\w.%])")

COLOURS = set(map("--{}".format, DARK))
SHARED = set(map("--{}".format, set(LIGHT) - set(DARK)))


def stylesheet_past_the_token_blocks():
    css = PAGE[PAGE.index("<style>"):PAGE.index("</style>")]
    past = css[css.index("}", css.index(":root {")):]
    dark = past.index(":root {", past.index("prefers-color-scheme: dark"))
    past = past[past.index("}", dark):]
    return re.sub(r"/\*.*?\*/", " ", past, flags=re.S)


def leak_of(selector, decl):
    prop, _, value = decl.partition(":")
    if "var(" in decl or prop.strip() == "flex":
        return None
    bare = BARE_NUMBER.findall(value)
    if not bare:
        return None
    return f"{prop.strip()}: {' '.join(bare)}  ({selector.strip()})"


def leaks():
    past = stylesheet_past_the_token_blocks()
    return list(filter(None, [leak_of(selector, " ".join(decl.split()))
                              for selector, body in RULE.findall(past)
                              for decl in body.split(";")]))


def test_no_unitless_literal_in_a_style_rule():
    leaked = leaks()
    assert not leaked, (
        f"{len(leaked)} unitless declaration(s) the unit-suffixed gate walks "
        f"past: " + "; ".join(leaked))


def payloadless_body():
    return "\n".join(filter(lambda line: not line.startswith(PAYLOAD),
                            PAGE.splitlines()))


def token_keys(body):
    return sorted(set(re.findall(r"var\((--[\w-]+)\)", body)))


def grounds_declared():
    style = PAGE[PAGE.index("<style>"):PAGE.index("</style>")]
    blocks = re.findall(r":root\s*\{([^{}]*)\}", style)
    return list(filter(None, map(
        lambda block: set(re.findall(r"(--[\w-]+)\s*:", block)), blocks)))


def test_both_grounds_are_complete_in_colours_and_dimensions_once():
    keys = token_keys(payloadless_body())
    grounds = grounds_declared()
    assert keys, "the rendered page reads no token"
    assert len(grounds) == 2, (
        f"expected both grounds' :root blocks, found {len(grounds)}")
    assert not (COLOURS - grounds[0]) | (COLOURS - grounds[1]), (
        "a fill has to read against its own ground's ink, so both grounds "
        "carry the theme's whole colour set; one misses: "
        + ", ".join(sorted((COLOURS - grounds[0]) | (COLOURS - grounds[1]))))
    assert not (SHARED - grounds[0]) | (SHARED & grounds[1]), (
        "the theme carries the sizes, the faces and the numbers once, and "
        "the base ground alone declares them; it misses, or the dark "
        "ground restates: "
        + ", ".join(sorted((SHARED - grounds[0]) | (SHARED & grounds[1]))))
    assert not set(keys) - grounds[0] - grounds[1], (
        "the page reads a token no ground declares: "
        + ", ".join(sorted(set(keys) - grounds[0] - grounds[1])))


def chosen_tests():
    return filter(lambda pair: pair[0].startswith("test_"),
                  sorted(globals().items()))


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


def report(failures):
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    report(sum(map(lambda pair: outcome_of(*pair), chosen_tests())))
