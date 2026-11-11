# covers: archituner/presentation/** archituner/theme/**
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
BASE = "clamp(0.8px, 0.0625rem, 0.18vw)"
GEOMETRY = (
    ("stack", 840,
     "434dee2342596dcc686839764539be89f7e8691328ae1e36077bb8b1cf15bcd5"),
    ("regions", 1431,
     "135c5cc7e2297442902d1816fb35552978c0c4a07e11a53820a11261eefaddd6"),
    ("overview", 514,
     "5fee3a9d42be83a5af83de9ae54ebab3b6a6bdf8225f3b8a819ee6ebfb8cfd94"))
LADDER = {"hair": "1", "step-1": "2", "step-2": "4", "step-3": "8",
          "step-4": "12", "type-micro": "10", "type-dense": "12",
          "type-small": "11", "type-body": "13", "cell-h": "22",
          "cell": "26", "main-w": "560", "panel-w": "320",
          "search-w": "260", "number-w": "45.5", "line": "19.5",
          "track-wide": "1.04", "stroke-hair": "1", "stroke-mark": "1.5",
          "stroke-node": "2", "stroke-emphasis": "2.5",
          "stroke-selection": "3", "dash-vacant": "3 2",
          "dash-absence": "4 3", "dash-dropped": "1 3", "radius-s": "3",
          "radius-m": "3", "focus-ring": "2", "focus-gap": "1",
          "fade-aside": "0.18", "fade-off": "0.35"}
FILES = {"q0.py": "import q1\n", "q1.py": "import q2\n",
         "q2.py": "import q3\n", "q3.py": "import q4\n", "q4.py": "x = 1\n",
         "sub/a.py": "import q0\n", "sub/b.py": "x = 1\n"}
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


def payload_of(page):
    for line in page.decode("utf-8").splitlines():
        if line.startswith("const DATA = "):
            return json.loads(line[len("const DATA = "):].rstrip(";"))
    raise AssertionError("the page carries no payload line")


def light_of(page):
    text = page.decode("utf-8")
    head = text[text.index("<style>") + 7:text.index("</style>")]
    return dict(PROPS.findall(head.partition("@media")[0]))


def number_of(text, props):
    text = text.strip()
    if text.startswith("var("):
        return number_of(props[text[4:-1].strip().removeprefix("--")], props)
    if text.startswith("max("):
        return max(number_of(part, props) for part in text[4:-1].split(","))
    if text.startswith("calc("):
        value = 1.0
        for factor in text[5:-1].split("*"):
            value *= number_of(factor, props)
        return value
    return float(text.removesuffix("px"))


def resolved(text, props):
    return " ".join(f"{number_of(part, props):g}"
                    for part in re.split(r"(?<=\)) (?=calc\()",
                                         text.strip()))


def test_the_page_keeps_today_s_geometry_and_drops_the_tag_radii():
    with tempfile.TemporaryDirectory() as home:
        page = rendered(home)
    assert page.count(b"rx=") == 0, \
        f"{page.count(b'rx=')} radii still ride the tag instead of the CSS"
    data = payload_of(page)
    wrong = []
    for name, size, digest in GEOMETRY:
        canon = json.dumps(data[name], ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
        if (len(canon), hashlib.sha256(canon).hexdigest()) != (size, digest):
            wrong.append(name)
    assert not wrong, "the drawn geometry moved for: " + ", ".join(wrong)


def test_every_dimension_token_resolves_to_today_at_the_default_unit():
    with tempfile.TemporaryDirectory() as home:
        light = light_of(rendered(home))
    missing = sorted(LADDER.keys() - light.keys())
    assert not missing, "the ladder does not define: " + ", ".join(missing)
    assert light.get("u") == BASE, light.get("u")
    assert not light.keys() & {"type-head", "type-hero"}, \
        "the type scale keeps the deleted aliases"
    unit = dict(light, u="1px")
    got = {}
    for name in sorted(LADDER):
        got[name] = resolved(light[name], unit)
    wrong = [f"{name} wants {LADDER[name]}, got {got[name]}"
             for name in sorted(LADDER) if got[name] != LADDER[name]]
    assert not wrong, ("the ladder does not resolve to today's page at "
                       "--u of 1px: " + "; ".join(wrong))


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
