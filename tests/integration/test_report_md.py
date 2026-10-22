# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/report/report.py archituner/report/spelling.py archituner/report/summary.py archituner/report/findings.py archituner/report/matrix.py archituner/report/records.py archituner/report/terminal.py archituner/report/breaches.py archituner/report/document.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

dependencies:
  allow:
    - api -> core
    - api -> model
    - core -> model
  forbid:
    - core -> api
    - model -> api
    - model -> core
---

## Boundaries

- `model -> *`: a representation computes nothing and depends on nothing.
- `core -> api`: a stage never reaches back to the thing that constructed it.
"""

API_ENTRY = "import core_base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
CORE_BAD = "import api_entry\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(divergent):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_base.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if divergent:
        plant(tree, "core_bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_format_md_spells_the_same_sections_as_a_table():
    proc = drive(build(True), "--report", "--format", "md")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "verdict: divergent" in lines, lines
    assert "## matrix: rows import columns; layers in dependency order" \
        in lines, lines
    assert "| --- | --- | --- | --- |" in lines, lines
    assert [line for line in lines if line.startswith("| core | ✗")], lines
    assert "\x1b" not in proc.stdout, "colour reached the markdown"


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
