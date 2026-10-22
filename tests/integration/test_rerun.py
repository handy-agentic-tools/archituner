# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py
import json
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

REPO_CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
RUN_ROOT = "archituner/run/__init__.py"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = os.path.join(tempfile.mkdtemp(), "scratch")
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", "import core_backbone\n")
    plant(tree, "core_backbone.py", "VALUE = 1\n")
    plant(tree, "model_shape.py", "VALUE = 2\n")
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def rerun(*args):
    one = drive(*args)
    two = drive(*args)
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, two.stdout)
    return one


def test_a_check_rerun_over_the_run_root_prints_the_same_bytes():
    one = drive(REPO_CONTRACT, "--check", "--file", RUN_ROOT)
    two = drive(REPO_CONTRACT, "--check", "--file", RUN_ROOT)
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, two.stdout)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


def test_a_json_rerun_over_one_unchanged_tree_prints_the_same_bytes():
    proc = rerun(build(), "--json")
    assert proc.returncode == 0, proc.stdout
    document = json.loads(proc.stdout)
    assert document["status"] == "ok", document.get("status")


def test_a_check_rerun_over_one_unchanged_tree_prints_the_same_bytes():
    proc = rerun(build(), "--check")
    assert proc.returncode == 0, proc.stdout
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_a_report_rerun_over_one_unchanged_tree_prints_the_same_bytes():
    proc = rerun(build(), "--report")
    assert proc.returncode == 0, proc.stdout
    assert "verdict: ok" in proc.stdout.splitlines(), proc.stdout


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
