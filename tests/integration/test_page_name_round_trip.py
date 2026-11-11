# covers: archituner/presentation/page/views/** archituner/presentation/page/shell/**
import html.parser
import json
import os
import re
import subprocess
import sys
import tempfile
from html import unescape

ONE = "it's \"layer\" & <one>"
TWO = "two's layer & <two>"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
FILES = {"it's.py": "import elsewhere\n", "elsewhere.py": "x = 1\n"}
PAIRS = (ONE + "->" + TWO, TWO + "->" + ONE)
HITS = ("layer:" + ONE, "layer:" + TWO, "file:it's.py", "file:elsewhere.py",
        "pair:" + PAIRS[0], "pair:" + PAIRS[1])
STEPS = ({"label": "coverage", "type": "click", "dataset": {"view": "coverage"}},
         {"label": "layers", "type": "click", "dataset": {"view": "layers"}},
         {"label": "matrix", "type": "click", "dataset": {"view": "matrix"}},
         {"label": "files", "type": "click", "dataset": {"panelTab": "files"}},
         {"label": "search", "type": "input", "value": "s"})
TEXTS = (("layers", "#view", (ONE, TWO)),
         ("matrix", "#view", (ONE, TWO)),
         ("coverage", "#view", (ONE, TWO)),
         ("files", "#panel-body", tuple(FILES)),
         ("search", "#results", ("it's.py", ONE, TWO)))
KINDS = {"data-file": tuple(FILES), "data-layer": (ONE, TWO),
         "data-pair": PAIRS, "data-hit": HITS}
ROWS = re.compile(r"data-file='([^']*)'[^>]*>\s*<span class='p'>([^<]*)<")

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
  it's "layer" & <one>: ["it's.py"]
  two's layer & <two>: ["elsewhere.py"]

dependencies:
  allow:
    - it's "layer" & <one> -> two's layer & <two>
    - two's layer & <two> -> it's "layer" & <one>
  forbid: []

naming:
  - "every file imports only the standard library"
---

## Layers

| Layer | Home | Responsibility | Rationale |
|---|---|---|---|
| `it's "layer" & <one>` | `.` | holds the quoted file | one file, one claim |
| `two's layer & <two>` | `.` | holds the other file | one file, one claim |

## Boundaries

- A test contract: two layers, one edge each way, nothing forbidden.
"""

HARNESS = """const fs = require("fs");
const page = fs.readFileSync(process.argv[2], "utf8");
const steps = JSON.parse(process.argv[3]);
const body = page.split("<script>")[1].split("</script>")[0];
const regions = {}, snap = {}, errors = [], listeners = {}, made = {};
console.error = (...a) => errors.push(a.join(" "));
process.on("uncaughtException", e => errors.push(String(e)));
function element(sel) {
  if (made[sel]) return made[sel];
  const el = { id: sel, className: "", dataset: {},
    toggleAttribute() {}, focus() {}, selectedOptions: [] };
  Object.defineProperty(el, "innerHTML", { get() { return el._h || ""; },
    set(v) { el._h = String(v); regions[el.id] = el._h; } });
  Object.defineProperty(el, "textContent", { get() { return el._t || ""; },
    set(v) { el._t = String(v); regions[el.id] = el._t; } });
  made[sel] = el;
  return el;
}
globalThis.document = {
  querySelector: element,
  addEventListener(type, fn) {
    (listeners[type] = listeners[type] || []).push(fn); },
};
globalThis.take = label => { snap[label] = {...regions}; };
globalThis.dispatch = () => {
  for (const step of steps) {
    try {
      if (step.type === "input") {
        for (const fn of listeners.input)
          fn({ target: { id: "search", value: step.value } });
      } else {
        const target = { dataset: step.dataset };
        target.closest = sel => {
          const names = String(sel).match(/data-[a-z-]+/g) || [];
          const hit = names.some(name => target.dataset[name.slice(5)
            .replace(/-([a-z])/g, (m, c) => c.toUpperCase())] !== undefined);
          return hit ? target : null;
        };
        for (const fn of listeners.click) fn({ target });
      }
    } catch (e) { errors.push(String(e)); }
    globalThis.take(step.label);
  }
};
require("vm").runInThisContext(body + "\\n;take('rest');dispatch();");
process.stdout.write(JSON.stringify({ snap, errors }));
"""


def build(home):
    tree = os.path.join(home, "tree")
    os.mkdir(tree)
    with open(os.path.join(tree, "it's.py"), "w", encoding="utf-8") as handle:
        handle.write(FILES["it's.py"])
    with open(os.path.join(tree, "elsewhere.py"), "w",
              encoding="utf-8") as handle:
        handle.write(FILES["elsewhere.py"])
    contract = os.path.join(tree, "ARCHITECTURE.md")
    with open(contract, "w", encoding="utf-8") as handle:
        handle.write(CONTRACT)
    return contract


def page_of(home):
    page = os.path.join(home, "page.html")
    subprocess.run([sys.executable, "-m", "archituner",
                    os.path.join(home, "tree", "ARCHITECTURE.md"), "-o", page],
                   cwd=REPO, capture_output=True, text=True,
                   timeout=120).check_returncode()
    return page


def drive(home, page, steps):
    harness = os.path.join(home, "harness.js")
    with open(harness, "w", encoding="utf-8") as handle:
        handle.write(HARNESS)
    proc = subprocess.run(["node", harness, page, json.dumps(steps)],
                          cwd=home, capture_output=True, text=True,
                          timeout=120)
    proc.check_returncode()
    return json.loads(proc.stdout)


def rendered(home, steps):
    build(home)
    page = page_of(home)
    result = drive(home, page, steps)
    assert result["errors"] == [], result["errors"]
    return page, result


class Markup(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs, self.texts, self.by_name = [], [], {}

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            value = unescape(value or "")
            self.attrs.append((name, value))
            self.by_name.setdefault(name, []).append(value)

    def handle_data(self, data):
        self.texts.append(data)


def parse(markup):
    parser = Markup()
    parser.feed(markup)
    return parser


def scanned(snap):
    parser = Markup()
    for markups in snap.values():
        for markup in markups.values():
            parser.feed(markup)
    return parser


def test_every_data_attribute_round_trips_the_full_name():
    with tempfile.TemporaryDirectory() as home:
        _, result = rendered(home, STEPS)
    seen = scanned(result["snap"]).by_name
    assert all(set(seen.get(n, ())) == set(w) for n, w in KINDS.items()), seen
    assert all(ONE in v or TWO in v for v in seen.get("data-region", ())), seen


def test_every_text_node_shows_the_measured_name_literally():
    with tempfile.TemporaryDirectory() as home:
        _, result = rendered(home, STEPS)
    for label, sel, tokens in TEXTS:
        parser = parse(result["snap"][label].get(sel, ""))
        blob = " ".join(parser.texts + parser.by_name.get("title", []))
        for token in tokens:
            assert token in blob, (label, sel, token, blob[:200])


def test_clicking_the_row_selects_the_whole_file_with_a_clean_console():
    with tempfile.TemporaryDirectory() as home:
        page, result = rendered(home, STEPS)
        rows = ROWS.findall(result["snap"]["files"].get("#panel-body", ""))
        row = {unescape(t): unescape(v) for v, t in rows}
        assert row.get("it's.py") == "it's.py", row
        picked = drive(home, page, [{"label": "picked", "type": "click",
                                     "dataset": {"file": row["it's.py"]}}])
    assert picked["errors"] == [], picked["errors"]
    panel = parse(picked["snap"]["picked"].get("#panel-name", ""))
    assert "".join(panel.texts) == "it's.py", panel.texts
    body = parse(picked["snap"]["picked"].get("#panel-body", ""))
    assert "imports" in " ".join(body.texts), body.texts


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    TESTS = (test_every_data_attribute_round_trips_the_full_name,
             test_every_text_node_shows_the_measured_name_literally,
             test_clicking_the_row_selects_the_whole_file_with_a_clean_console)
    failures = 0
    for test in TESTS:
        failures += outcome_of(test.__name__, test)
    print(("all green", f"{failures} failed")[failures > 0])
    raise SystemExit(min(failures, 1))
