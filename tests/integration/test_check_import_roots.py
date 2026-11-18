# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py archituner/conformance/classification.py archituner/conformance/proposal.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

FORBID_CONTRACT = """---
package_root: "pkg"

layers:
  model: ["pkg/model/@@@"]
  tests_unit: ["tests/unit/@@@"]

dependencies:
  allow:
    - model -> tests_unit
  forbid:
    - tests_unit -> model
---

## Boundaries

- `tests_unit -> model`: a test never reaches the model.
""".replace("@@@", "**")

ALLOWED_CONTRACT = """---
package_root: "pkg"

layers:
  model: ["pkg/model/@@@"]
  tests_unit: ["tests/unit/@@@"]

dependencies:
  allow:
    - model -> tests_unit
    - tests_unit -> model
---
""".replace("@@@", "**")

NESTED_CONTRACT = """---
package_root: "pkg"

layers:
  cli: ["src/pkg/cli/@@@"]
  model: ["src/pkg/model/@@@"]

dependencies:
  allow:
    - model -> cli
  forbid:
    - cli -> model
---

## Boundaries

- `cli -> model`: a command never reaches the model layer.
""".replace("@@@", "**")

BOTH_FORMS = "from pkg.model import X\nimport pkg.model.shapes\n"

GUARDED_ABSENT = ("try:\n    from pkg.gone import x\n"
                  "except ImportError:\n    x = None\n")


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_model_tree(contract, test_body):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", contract)
    plant(tree, "pkg/__init__.py", "")
    plant(tree, "pkg/model/__init__.py", "X = 1\n")
    plant(tree, "pkg/model/shapes.py", "SIDES = 4\n")
    plant(tree, "tests/unit/test_x.py", test_body)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_an_absolute_root_prefixed_import_from_outside_the_root_makes_a_forbid_fail():
    proc = drive(build_model_tree(FORBID_CONTRACT, BOTH_FORMS), "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence" in proc.stdout, proc.stdout
    assert "tests_unit -> model" in proc.stdout, proc.stdout
    assert "tests/unit/test_x.py" in proc.stdout, proc.stdout


def test_the_same_tree_with_the_edge_allowed_stays_green():
    proc = drive(build_model_tree(ALLOWED_CONTRACT, BOTH_FORMS), "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_a_guarded_import_of_an_absent_module_is_no_edge():
    proc = drive(build_model_tree(FORBID_CONTRACT, GUARDED_ABSENT), "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_an_absolute_import_from_under_a_deeper_root_prefix_makes_a_forbid_fail():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", NESTED_CONTRACT)
    plant(tree, "src/pkg/__init__.py", "")
    plant(tree, "src/pkg/cli/__init__.py", "")
    plant(tree, "src/pkg/cli/main.py", "from pkg.model import X\n")
    plant(tree, "src/pkg/model/__init__.py", "X = 1\n")
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: cli -> model" in proc.stdout, proc.stdout
    assert "src/pkg/cli/main.py" in proc.stdout, proc.stdout


def test_an_import_whose_first_segment_is_not_the_root_is_no_edge():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", FORBID_CONTRACT)
    plant(tree, "pkg/__init__.py", "")
    plant(tree, "pkg/model/__init__.py", "X = 1\n")
    plant(tree, "pkg/model/shapes.py", "SIDES = 4\n")
    plant(tree, "tests/unit/test_x.py", "from tools.model import x\n")
    plant(tree, "tools/model/__init__.py", "")
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_an_import_of_a_layer_through_the_root_package_itself_makes_a_forbid_fail():
    proc = drive(build_model_tree(FORBID_CONTRACT, "from pkg import model\n"),
                 "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence" in proc.stdout, proc.stdout
    assert "tests_unit -> model" in proc.stdout, proc.stdout
    assert "tests/unit/test_x.py" in proc.stdout, proc.stdout


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
