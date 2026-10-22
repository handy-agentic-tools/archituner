# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/report/report.py archituner/report/spelling.py archituner/report/summary.py archituner/report/findings.py archituner/report/matrix.py archituner/report/records.py archituner/report/terminal.py archituner/report/breaches.py archituner/report/document.py archituner/conformance/classification.py archituner/conformance/proposal.py
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

BROKEN_CONTRACT = "layers:\n  api: [\"api_*\"]\n"

API_ENTRY = "import core_base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
CORE_BAD = "import api_entry\n"
STRAY = "Z = 3\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(divergent, stray=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_base.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if divergent:
        plant(tree, "core_bad.py", CORE_BAD)
    if stray:
        plant(tree, "stray.py", STRAY)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_broken():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", BROKEN_CONTRACT)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_a_divergent_reading_fails_the_verdict_it_prints():
    proc = drive(build(True), "--report")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "verdict: divergent" in lines, lines
    assert "counts: ✓ convergence 1  ✗ divergence 1  ○ absence 2" \
        "  · silence 2" in lines, lines
    assert "matrix: rows import columns; layers in dependency order" in lines, \
        lines
    assert "  divergence: core -> api" in lines, lines
    assert "    core_bad.py:1 imports api_entry" in lines, lines
    assert [line for line in lines if line.startswith("    remedy: ")], lines
    assert "\x1b" not in proc.stdout, "colour reached a piped log"


def test_a_clean_reading_is_green_and_lists_the_unclaimed():
    proc = drive(build(False, stray=True), "--report")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "verdict: ok" in lines, lines
    assert "unclaimed files" in lines, lines
    assert lines[lines.index("unclaimed files") + 1] == "  stray.py", lines


def test_a_refusal_prints_its_reason_at_the_refusal_exit():
    proc = drive(build_broken(), "--report")
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines(), proc.stdout
    assert "ARCHITECTURE.md" in proc.stdout, proc.stdout


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
