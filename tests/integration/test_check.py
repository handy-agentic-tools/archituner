# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py archituner/conformance/classification.py archituner/conformance/proposal.py
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

FAILED_CONTRACT = """---
layers:
  gone: ["gone_*"]
  far:  ["far_*"]

dependencies:
  forbid:
    - gone -> far
    - far -> gone
---
"""

TREE_CONTRACT = """---
package_root: "src"

layers:
  app:      ["src/app/@@@"]
  app.ui:   ["src/app/ui/@@@"]
  app.core: ["src/app/core/@@@"]

dependencies:
  allow:
    - app.ui -> app.core
  forbid:
    - app.core -> app.ui
---
""".replace("@@@", "**")

FLAT_CONTRACT = """---
package_root: "src"

layers:
  ui:   ["src/app/ui/@@@"]
  core: ["src/app/core/@@@"]

dependencies:
  allow:
    - ui -> core
  forbid:
    - core -> ui
---
""".replace("@@@", "**")

API_ENTRY = "import core_backbone\n"
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
    plant(tree, "core_backbone.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if divergent:
        plant(tree, "core_bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_unclaimed():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", FAILED_CONTRACT)
    plant(tree, "loose/a.py", "X = 1\n")
    plant(tree, "loose/b.py", "Y = 2\n")
    return os.path.join(tree, "ARCHITECTURE.md")


def build_tree(contract):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", contract)
    plant(tree, "src/app/__init__.py", "")
    plant(tree, "src/app/ui/__init__.py", "")
    plant(tree, "src/app/ui/x.py", "X = 1\n")
    plant(tree, "src/app/core/__init__.py", "")
    plant(tree, "src/app/core/m.py", "from app.ui.x import X\n")
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_a_clean_tree_leaves_the_gate_silent_and_green():
    proc = drive(build(False), "--check")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_a_realised_forbidden_pair_names_itself_and_fails():
    proc = drive(build(True), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: core -> api" in proc.stdout.splitlines(), proc.stdout
    assert "    core_bad.py imports api_entry" in proc.stdout.splitlines(), \
        proc.stdout
    assert [line for line in proc.stdout.splitlines()
            if line.startswith("    remedy: ")], proc.stdout


def test_a_check_fed_files_answers_those_files_alone():
    contract = build(True)
    proc = drive(contract, "--check", "--file", "core_bad.py")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: core -> api" in proc.stdout, proc.stdout
    proc = drive(contract, "--check", "--file", "api_entry.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_a_run_that_claims_nothing_is_a_failed_run_not_a_clean_one():
    proc = drive(build_unclaimed(), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == [
        "failed run: 2 file(s) walked, none claimed by any layer"], proc.stdout


def test_a_tree_contract_gates_on_a_forbidden_sublayer_import():
    proc = drive(build_tree(TREE_CONTRACT), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: app.core -> app.ui" in proc.stdout.splitlines(), \
        proc.stdout
    assert "    src/app/core/m.py imports app.ui.x" in proc.stdout.splitlines(), \
        proc.stdout


def test_the_same_edge_between_flat_layers_reports():
    proc = drive(build_tree(FLAT_CONTRACT), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: core -> ui" in proc.stdout.splitlines(), proc.stdout
    assert "    src/app/core/m.py imports app.ui.x" in proc.stdout.splitlines(), \
        proc.stdout


def run_one(pair):
    name, test = pair
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    entries = sorted(filter(lambda item: item[0].startswith("test_"),
                            globals().items()))
    failures = sum(map(run_one, entries))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
