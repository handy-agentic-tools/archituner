# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py archituner/conformance/classification.py archituner/conformance/proposal.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

STDLIB_CONTRACT = """---
package_root: "pkg"

layers:
  cli: ["pkg/cli/@@@"]
  {name}: ["pkg/{name}/@@@"]

dependencies:
  allow:
    - {name} -> cli
  forbid:
    - cli -> {name}
---

## Boundaries

- `cli -> {name}`: a command never reaches the {name} layer.
""".replace("@@@", "**")


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_stdlib_tree(name, filename, body):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", STDLIB_CONTRACT.format(name=name))
    plant(tree, "pkg/__init__.py", "")
    plant(tree, "pkg/{}/__init__.py".format(name), "helper = 1\n")
    plant(tree, "pkg/cli/__init__.py", "")
    plant(tree, "pkg/cli/{}".format(filename), body)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_a_relative_import_into_a_layer_named_math_makes_a_forbid_fail():
    contract = build_stdlib_tree("math", "main.py",
                                 "from ..math import helper\n")
    proc = drive(contract, "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: cli -> math" in proc.stdout, proc.stdout
    assert "pkg/cli/main.py" in proc.stdout, proc.stdout


def test_an_absolute_root_prefixed_import_into_a_layer_named_math_makes_a_forbid_fail():
    contract = build_stdlib_tree("math", "other.py",
                                 "from pkg.math import helper\n")
    proc = drive(contract, "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: cli -> math" in proc.stdout, proc.stdout
    assert "pkg/cli/other.py" in proc.stdout, proc.stdout


def test_the_relative_form_into_a_layer_named_types_makes_a_forbid_fail():
    contract = build_stdlib_tree("types", "main.py",
                                 "from ..types import helper\n")
    proc = drive(contract, "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: cli -> types" in proc.stdout, proc.stdout
    assert "pkg/cli/main.py" in proc.stdout, proc.stdout


def test_the_absolute_form_into_a_layer_named_types_makes_a_forbid_fail():
    contract = build_stdlib_tree("types", "other.py",
                                 "from pkg.types import helper\n")
    proc = drive(contract, "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: cli -> types" in proc.stdout, proc.stdout
    assert "pkg/cli/other.py" in proc.stdout, proc.stdout


def test_a_genuine_stdlib_import_matching_no_walked_module_is_no_edge():
    contract = build_stdlib_tree("other", "main.py",
                                 "import math\nimport os\n")
    proc = drive(contract, "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_a_bare_stdlib_import_of_a_stdlib_named_layer_is_no_edge():
    contract = build_stdlib_tree("math", "main.py",
                                 "import math\nfrom math import sqrt\n")
    proc = drive(contract, "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_a_bare_stdlib_import_of_a_stdlib_named_types_layer_is_no_edge():
    contract = build_stdlib_tree("types", "main.py", "import types\n")
    proc = drive(contract, "--check")
    observed = (proc.returncode, proc.stdout.splitlines())
    assert observed == (0, ["no divergence"]), observed


def test_a_mixed_file_reports_only_the_relative_imports_divergence():
    contract = build_stdlib_tree(
        "math", "main.py", "import math\nfrom ..math import helper\n")
    proc = drive(contract, "--check")
    witness = "starting with pkg/cli/main.py:2" in proc.stdout
    bare = "pkg/cli/main.py:1" not in proc.stdout
    observed = (bool(proc.returncode), witness, bare)
    assert observed == (True, True, True), (proc.returncode, proc.stdout)


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
