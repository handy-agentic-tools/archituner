# covers: archituner/presentation/** archituner/theme/**
import operator
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
FILES = {"q0.py": "import q1\n", "q1.py": "import q2\n",
         "q2.py": "import q3\n", "q3.py": "import q4\n", "q4.py": "x = 1\n",
         "sub/a.py": "import q0\n", "sub/b.py": "x = 1\n"}
ONE_IDIOM = ("button.key", "#reading button", "#ask button")
KEY_BOX = "border: var(--hair) solid var(--rule-strong)"
KEY_STRAY = re.compile(r"#reading button(?![^\n]*button\.key)"
                       r"[^\n]*\n" + re.escape(KEY_BOX))
COMMAND = re.compile(r"(?:^|,)\s*button\s*(?:,|$)")
DISABLED_HOVER = re.compile(r"aria-disabled.*:hover|:hover.*aria-disabled")
CONTRACT = """---
package_root: "."

limits:
  size: 8000
  defs: 8
  depth: 4
  cyclomatic: 30
  cognitive: 50
  prose_count: 0

layers:
  q0: ["q0.py"]
  q1: ["q1.py"]
  q2: ["q2.py"]
  q3: ["q3.py"]
  q4: ["q4.py"]
  sub: ["sub/@@@"]

dependencies:
  allow:
    - q0 -> q1
    - q1 -> q2
    - q2 -> q3
    - q3 -> q4
    - sub -> q0
  forbid:
    - q0 -> q2
    - q0 -> q3
    - q0 -> q4
    - q0 -> sub
    - q1 -> q0
    - q1 -> q3
    - q1 -> q4
    - q1 -> sub
    - q2 -> q0
    - q2 -> q1
    - q2 -> q4
    - q2 -> sub
    - q3 -> q0
    - q3 -> q1
    - q3 -> q2
    - q3 -> sub
    - q4 -> q0
    - q4 -> q1
    - q4 -> q2
    - q4 -> q3
    - q4 -> sub
    - sub -> q1
    - sub -> q2
    - sub -> q3
    - sub -> q4
naming:
  - "every file imports only the standard library"
---

## Layers

| Layer | Home | Responsibility | Rationale |
|---|---|---|---|
| `q0` | `.` | holds its file | one file, one claim |
| `q1` | `.` | holds its file | one file, one claim |
| `q2` | `.` | holds its file | one file, one claim |
| `q3` | `.` | holds its file | one file, one claim |
| `q4` | `.` | holds its file | one file, one claim |
| `sub` | `.` | holds its file | one file, one claim |

## Boundaries

- A test contract: a chain of five layers, a sixth beside it, every other pair forbidden.
""".replace("@@@", "**")
RULES = re.compile(r"([^{}]+)\{([^{}]*)\}")
PROPS = re.compile(r"--([a-z0-9-]+):\s*([^;}]+)")


def rendered(home):
    tree = os.path.join(home, "tree")
    os.mkdir(tree)
    contract = os.path.join(tree, "ARCHITECTURE.md")
    for name, text in dict(FILES, **{"ARCHITECTURE.md": CONTRACT}).items():
        path = os.path.join(tree, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    page = os.path.join(home, "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner", contract,
                           "-o", page], cwd=REPO, capture_output=True,
                          text=True, timeout=120)
    assert done.returncode == 0, (done.stdout, done.stderr)
    with open(page, "rb") as handle:
        return handle.read()


def css_of(page):
    text = page.decode("utf-8")
    return text[text.index("<style>") + 7:text.index("</style>")]


def blocks(css):
    return list(map(lambda rule: (rule[0].strip(), rule[1].strip()),
                    RULES.findall(css)))


def sections(css):
    light, _, dark = css.partition("@media")
    return dict(PROPS.findall(light)), dict(PROPS.findall(dark))


def bodies_of(pairs, keep):
    return list(map(operator.itemgetter(1),
                    filter(lambda pair: keep(pair[0]), pairs)))


def carries(bodies, *wants):
    text = "\n".join(bodies)
    return all(want in text for want in wants)


def key_copy(pair):
    return bool(KEY_STRAY.search("\n".join(pair)))


def one_rule(pair):
    return all(mark in pair[0] for mark in ONE_IDIOM)


def luminance(hex_value):
    parts = (int(hex_value[1:3], 16), int(hex_value[3:5], 16),
             int(hex_value[5:7], 16))
    shaped = [((value / 255 + 0.055) / 1.055) ** 2.4 if value / 255 > 0.04045
              else (value / 255) / 12.92 for value in parts]
    return 0.2126 * shaped[0] + 0.7152 * shaped[1] + 0.0722 * shaped[2]


def test_every_command_answers_hover_and_focus():
    with tempfile.TemporaryDirectory() as home:
        pairs = blocks(css_of(rendered(home)))
    ring = bodies_of(pairs, lambda selector: ":focus-visible" in selector)
    assert ring, "no rule answers the keyboard with a focus ring"
    assert carries(ring, "outline: var(--focus-ring)",
                   "outline-offset: var(--focus-gap)"), ring
    base = bodies_of(pairs, lambda selector: COMMAND.search(selector))
    assert carries(base, "font: inherit", "cursor: pointer"), \
        "no bare button rule brings the raw controls into the one idiom"
    hovers = bodies_of(pairs, lambda selector: ":hover" in selector)
    assert carries(hovers, "var(--surface-raised)"), \
        "no hover raises a control"
    assert carries(bodies_of(pairs,
                             lambda selector: "#matrix td:hover" in selector),
                   "var(--rule-strong)"), "no hover on #matrix td"
    assert carries(bodies_of(pairs,
                             lambda selector: ".layerbox:hover" in selector),
                   "var(--rule-strong)"), "no hover on .layerbox"
    gated = bodies_of(pairs, lambda selector: "aria-disabled" in selector)
    assert carries(gated, "cursor: not-allowed"), gated
    assert not list(filter(DISABLED_HOVER.search,
                           map(operator.itemgetter(0), pairs))), \
        "the disabled control hovers"


def test_the_buttons_read_as_one_idiom_and_the_fields_wear_the_page():
    with tempfile.TemporaryDirectory() as home:
        pairs = blocks(css_of(rendered(home)))
    stray = list(map(operator.itemgetter(0), filter(key_copy, pairs)))
    assert not stray, \
        "the reading and ask buttons hold their own copy of the key box: " \
        + "; ".join(stray)
    assert list(filter(one_rule, pairs)), \
        "no single rule dresses the keys and the reading and ask buttons"
    assert carries(bodies_of(pairs,
                             lambda selector: "nav button" in selector),
                   "cursor: pointer"), \
        "the nav buttons keep the browser's own widget dress"
    fields = bodies_of(pairs, lambda selector: "#search" in selector)
    assert carries(fields, "font: inherit", KEY_BOX), fields


def test_the_hover_ground_reads_against_ink_on_both_grounds():
    with tempfile.TemporaryDirectory() as home:
        light, dark = sections(css_of(rendered(home)))
    for props in (light, dark):
        missing = sorted({"surface-raised", "ink"} - props.keys())
        assert not missing, "the ground lacks: " + ", ".join(missing)
        pair = sorted(map(luminance, (props["surface-raised"],
                                      props["ink"])), reverse=True)
        assert (pair[0] + 0.05) / (pair[1] + 0.05) >= 4.5, pair


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
