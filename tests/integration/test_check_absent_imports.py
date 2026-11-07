# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py archituner/conformance/classification.py archituner/conformance/proposal.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CONTRACT = """---
package_root: "."

layers:
  api: ["pkg/__init__.py"]
  cli: ["pkg/cli/@@@"]

dependencies:
  allow:
    - api -> cli
  forbid:
    - cli -> api
---

## Boundaries

- `cli -> api`: a command never reaches the package root.
""".replace("@@@", "**")

ROOT_INIT = "from pkg.cli import main\n"
CLI_INIT = ""
GUARDED_PAGE = ("try:\n    from pkg.presentation.page import render\n"
                "except ImportError:\n    render = None\n")


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "pkg/__init__.py", ROOT_INIT)
    plant(tree, "pkg/cli/__init__.py", CLI_INIT)
    plant(tree, "pkg/cli/page.py", GUARDED_PAGE)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_an_import_of_a_module_absent_from_the_tree_is_no_divergence():
    proc = drive(build(), "--check")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


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
