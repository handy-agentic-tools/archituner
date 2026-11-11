import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from archituner.presentation.rejection import render_rejection
from archituner.theme import REFUSAL

import functools
import operator
from itertools import chain

CONTRACT = "ARCHITECTURE.md"
REASON = "the contract names a layer no glob claims"
ARTIFACT = render_rejection(CONTRACT, REASON)
STYLE = ARTIFACT[ARTIFACT.index("<style>"):ARTIFACT.index("</style>")]

DARK_AT = STYLE.index("prefers-color-scheme: dark")
DECLARATIONS = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
DECLARED = {"light": dict(DECLARATIONS.findall(STYLE[:DARK_AT])),
            "dark": dict(DECLARATIONS.findall(STYLE[DARK_AT:]))}
PAST = STYLE[STYLE.index("}", STYLE.index(":root {", DARK_AT)):]

UNSPENT = re.compile(r"[^;{}]*var\([^()]*\)[^;{}]*")
LITERAL = re.compile(r"#[0-9a-fA-F]{6}\b"
                     r"|\b\d[\d.]*(?:px|rem|em|vh)\b"
                     r"|\b(?:system-ui|sans-serif|serif|monospace"
                     r"|ui-monospace)\b")
LEAKS = LITERAL.findall(UNSPENT.sub(" ", PAST))


def spelled(ground):
    return dict(map(lambda item: ("--" + item[0], item[1]),
                    REFUSAL[ground].items()))


UNITED = {"scheme": "light", "ink": "#1a1a1a", "surface": "#ffffff",
          "sunken": "#f4f4f4", "accent": "#8f342a",
          "u": "clamp(0.8px, 0.0625rem, 0.18vw)",
          "mono": 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, '
                  'Consolas, "Liberation Mono", monospace',
          "type-body": "calc(var(--u) * 13)",
          "face": "var(--mono)", "line": "calc(var(--type-body) * 1.5)",
          "pad": "calc(var(--u) * 24)", "head": "calc(var(--u) * 24)",
          "code-pad": "calc(var(--u) * 2) calc(var(--u) * 6)"}
GROUNDLESS = ("scheme", "u", "mono", "type-body", "face", "line", "pad",
              "head", "code-pad")
DARK_KEEP = ("dark",) + tuple(map(UNITED.get, GROUNDLESS[1:]))
COLOURS = ("ink", "surface", "sunken", "accent")
GROUND_VALUES = tuple(map(str, chain(map(REFUSAL["light"].get, COLOURS),
                                     map(REFUSAL["dark"].get, COLOURS))))
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")

WEIGHTS = (0.2126, 0.7152, 0.0722)
CHANNEL = list(map(lambda value: [value / 255 / 12.92,
                                  ((value / 255 + 0.055) / 1.055) ** 2.4]
                   [value > 10], range(256)))


def luminous(colour):
    return sum(map(operator.mul, WEIGHTS,
                   map(CHANNEL.__getitem__,
                       map(functools.partial(int, base=16),
                           (colour[1:3], colour[3:5], colour[5:7])))))


def contrast(one, other):
    lower, higher = sorted((luminous(one), luminous(other)))
    return (higher + 0.05) / (lower + 0.05)


FLOOR = 4.5
SCORED = (("light", "ink", "surface"), ("light", "ink", "sunken"),
          ("light", "accent", "surface"),
          ("dark", "ink", "surface"), ("dark", "ink", "sunken"),
          ("dark", "accent", "surface"))


def scored(triple):
    ground, name, back = triple
    ratio = contrast(REFUSAL[ground][name], REFUSAL[ground][back])
    return None if ratio >= FLOOR else (
        f"{ground} {name} on {back} scores {ratio:.2f} to 1, under the "
        f"{FLOOR} the palette validator holds")


SPENT = (r"h1\s*\{[^}]*color:\s*var\(--accent\)",
         r"h1\s*\{[^}]*font-size:\s*var\(--head\)",
         r"body\s*\{[^}]*padding:\s*var\(--pad\)",
         r"code\s*\{[^}]*background:\s*var\(--sunken\)",
         r"code\s*\{[^}]*padding:\s*var\(--code-pad\)")
ALL_SPENT = all(map(lambda pattern: re.search(pattern, PAST), SPENT))


def test_no_rule_past_the_token_blocks_holds_a_literal():
    assert not LEAKS, (
        "the rejection artifact holds literal styling past the token "
        "blocks, where every rule spends var(--...) only: "
        + ", ".join(LEAKS))


def test_the_token_blocks_spell_the_theme_and_nothing_else():
    assert DECLARED == {"light": spelled("light"),
                        "dark": spelled("dark")}, (
        "the token blocks spell " + str(DECLARED) + ", not the theme's own "
        "two grounds, so the artifact holds a value REFUSAL does not")


def test_the_refusal_theme_reads_the_page_s_ladder():
    assert REFUSAL["light"] == UNITED, (
        "REFUSAL's light ground is " + str(REFUSAL["light"]) + ", not the "
        "page's own ladder the refusal page joins, computed from the one "
        "base unit and faced like the page: " + str(UNITED))


def test_the_refusal_theme_holds_one_scheme_face_and_scale_on_both_grounds():
    held = tuple(map(REFUSAL["dark"].get, GROUNDLESS))
    assert held == DARK_KEEP, (
        "REFUSAL's dark ground spells " + str(held) + " "
        "for scheme, face, line height and the sizes, not the light "
        "ground's own " + str(DARK_KEEP))


def test_the_rules_spend_the_former_look_by_token():
    assert ALL_SPENT, (
        "the rules spend no h1 accent, no h1 heading size, no body padding, "
        "no code sunken ground and no code padding by token, so the former "
        "look does not come back through the theme")


def test_the_palette_validator_scores_the_refusal_ink_and_heading():
    unscored = list(filter(lambda value: not HEX.fullmatch(value),
                           GROUND_VALUES))
    assert not unscored, (
        "the refusal theme holds values the palette validator cannot "
        "score, not colours: " + ", ".join(unscored))
    weak = list(filter(None, map(scored, SCORED)))
    assert not weak, (
        "the refusal palette scores under the palette validator's floor: "
        + "; ".join(weak))


def test_the_rejection_artifact_declares_both_grounds_of_the_system():
    artifact = render_rejection("ARCHITECTURE.md",
                                "the contract names a layer no glob claims")
    assert "prefers-color-scheme: dark" in artifact, (
        "the rejection artifact follows no ground: it spells no "
        "prefers-color-scheme block, so a system set to dark still draws "
        "the light ground")
    dark_at = artifact.index("prefers-color-scheme: dark")
    light = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", artifact[:dark_at]))
    dark = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", artifact[dark_at:]))
    assert light.keys() == dark.keys(), (
        "the dark ground does not declare what the light ground does: "
        + ", ".join(sorted(light.keys() ^ dark.keys())))
    assert light != dark, (
        "both grounds spell the same values, so the artifact is always "
        "light whatever the system asks for")


def test_the_rendered_rejection_carries_no_absolute_path():
    planted = "/home/someone/proj/ARCHITECTURE.md"
    artifact = render_rejection(planted,
                                "the contract names a layer no glob claims")
    assert "/home/" not in artifact and "/Users/" not in artifact, (
        "the rendered rejection shows the contract's absolute path, "
        "which uispec.md forbids the artifact to show")


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    names, tests = zip(*sorted(filter(
        lambda item: item[0].startswith("test_"), globals().items())))
    failed = sum(map(outcome_of, names, tests))
    print((f"{failed} failed", "all green")[failed == 0])
    raise SystemExit(bool(failed))
