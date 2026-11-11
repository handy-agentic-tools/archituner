# covers: archituner/presentation/page/views/** archituner/presentation/page/shell/**
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = {"q0.py": "import q1\n", "q1.py": "import q2\n",
         "q2.py": "import q3\n", "q3.py": "import q4\n", "q4.py": "x = 1\n"}
STEPS = ({"label": "beyond", "type": "input", "value": "q"},
         {"label": "within", "type": "input", "value": "claim"})
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

dependencies:
  allow:
    - q0 -> q1
    - q1 -> q2
    - q2 -> q3
    - q3 -> q4
  forbid:
    - q0 -> q2
    - q0 -> q3
    - q0 -> q4
    - q1 -> q0
    - q1 -> q3
    - q1 -> q4
    - q2 -> q0
    - q2 -> q1
    - q2 -> q4
    - q3 -> q0
    - q3 -> q1
    - q3 -> q2
    - q4 -> q0
    - q4 -> q1
    - q4 -> q2
    - q4 -> q3

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

## Boundaries

- A test contract: five layers in a chain, every other pair forbidden.
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
      for (const fn of listeners.input)
        fn({ target: { id: "search", value: step.value } });
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
    for name, text in FILES.items():
        with open(os.path.join(tree, name), "w", encoding="utf-8") as handle:
            handle.write(text)
    contract = os.path.join(tree, "ARCHITECTURE.md")
    with open(contract, "w", encoding="utf-8") as handle:
        handle.write(CONTRACT)
    return contract


def driven(home):
    contract = build(home)
    page = os.path.join(home, "page.html")
    subprocess.run([sys.executable, "-m", "archituner", contract, "-o", page],
                   cwd=REPO, capture_output=True, text=True,
                   timeout=120).check_returncode()
    harness = os.path.join(home, "harness.js")
    with open(harness, "w", encoding="utf-8") as handle:
        handle.write(HARNESS)
    proc = subprocess.run(["node", harness, page, json.dumps(STEPS)],
                          cwd=home, capture_output=True, text=True,
                          timeout=120)
    proc.check_returncode()
    result = json.loads(proc.stdout)
    assert result["errors"] == [], result["errors"]
    return result["snap"]


def plain(markup):
    return re.sub(r"<[^>]*>", " ", markup)


def test_a_one_letter_query_beyond_the_cap_counts_what_it_shows():
    with tempfile.TemporaryDirectory() as home:
        row = driven(home)["beyond"]["#results"]
    assert row.count("data-hit=") == 8, row
    assert "8 of 30" in plain(row), row


def test_a_query_within_the_cap_names_no_count():
    with tempfile.TemporaryDirectory() as home:
        row = driven(home)["within"]["#results"]
    assert row.count("data-hit=") == 5, row
    assert not re.search(r"\d of \d", plain(row)), row


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
