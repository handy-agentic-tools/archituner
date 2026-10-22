# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/report/report.py archituner/report/spelling.py archituner/report/summary.py archituner/report/findings.py archituner/report/matrix.py archituner/report/records.py archituner/report/terminal.py archituner/report/breaches.py archituner/report/document.py archituner/source/** archituner/conformance/classification.py archituner/conformance/proposal.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

LIMITS_CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

limits:
  size: 21
  cyclomatic: 5

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

API_ENTRY = "import core_backbone\n"
CORE_BACKBONE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
MODEL_HEAVY = "V = '" + "x" * 20 + "'\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(breach=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", LIMITS_CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BACKBONE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if breach:
        plant(tree, "model_weight.py", MODEL_HEAVY)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_a_report_of_a_breaching_tree_fails_and_names_the_breach():
    proc = drive(build(breach=True), "--report")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "verdict: divergent" in lines, lines
    assert "limit breaches" in lines, lines
    assert lines[lines.index("limit breaches") + 1] == \
        "  model_weight.py: size 27 over 21", lines
    assert "\x1b" not in proc.stdout, "colour reached a piped log"


def test_the_md_report_spells_the_breach_as_a_bullet():
    proc = drive(build(breach=True), "--report", "--format", "md")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "## limit breaches" in lines, lines
    assert lines[lines.index("## limit breaches") + 1] == \
        "- model_weight.py: size 27 over 21", lines


def test_a_clean_tree_reports_no_limit_breaches_and_exits_zero():
    proc = drive(build(), "--report")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "verdict: ok" in lines, lines
    assert "limit breaches" in lines, lines
    assert lines[lines.index("limit breaches") + 1] == "  no limit breaches", \
        lines


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                test()
                print(f"PASS  {name}")
            except Exception as e:
                print(f"FAIL  {name}  {type(e).__name__}: {e}")
                failures += 1
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(1 if failures else 0)
