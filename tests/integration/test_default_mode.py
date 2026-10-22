# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/presentation/** archituner/source/** archituner/conformance/** archituner/contract/**
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

STAR = "**"

CLEAN_CONTRACT = (
    "---\n"
    "layers:\n"
    '  api:   ["api_*"]\n'
    '  core:  ["core_*"]\n'
    "\n"
    "dependencies:\n"
    "  allow:\n"
    "    - api -> core\n"
    "    - core -> api\n"
    "---\n"
)

DIVERGENT_CONTRACT = (
    "---\n"
    "layers:\n"
    '  api:   ["api_*"]\n'
    '  core:  ["core_*"]\n'
    '  model: ["model_*"]\n'
    "\n"
    "dependencies:\n"
    "  allow:\n"
    "    - api -> core\n"
    "    - api -> model\n"
    "    - core -> model\n"
    "  forbid:\n"
    "    - core -> api\n"
    "    - model -> api\n"
    "    - model -> core\n"
    "---\n"
    "\n"
    "## Boundaries\n"
    "\n"
    "- `model -> *`: a representation computes nothing and depends on "
    "nothing.\n"
    "- `core -> api`: a stage never reaches back to the thing that "
    "constructed it.\n"
)

BROKEN_CONTRACT = 'layers:\n  api: ["src/' + STAR + '"]\n'


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(divergent):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md",
          DIVERGENT_CONTRACT if divergent else CLEAN_CONTRACT)
    plant(tree, "api_entry.py", "import core_base\n")
    plant(tree, "core_base.py", "VALUE = 1\n")
    if divergent:
        plant(tree, "core_backbone.py", "VALUE = 1\n")
        plant(tree, "model_shape.py", "VALUE = 2\n")
        plant(tree, "core_bad.py", "import api_entry\n")
    return tree


def build_broken():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", BROKEN_CONTRACT)
    return tree


def drive(tree, *args):
    env = dict(os.environ, PYTHONPATH=REPO)
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=tree, env=env, capture_output=True,
                          timeout=120)


def test_a_bare_run_answers_what_check_answers():
    trees = [(build(False), 0, b"no divergence\n"),
             (build(True), 1, b"divergence: core -> api"),
             (build_broken(), 2, b"front matter")]
    for tree, code, evidence in trees:
        contract = os.path.join(tree, "ARCHITECTURE.md")
        bare = drive(tree, contract)
        check = drive(tree, contract, "--check")
        assert bare.returncode == check.returncode == code, \
            (bare.returncode, check.returncode, bare.stdout, check.stdout,
             bare.stderr, check.stderr)
        assert bare.stdout == check.stdout, (bare.stdout, check.stdout)
        assert bare.stderr == check.stderr, (bare.stderr, check.stderr)
        assert evidence in bare.stdout, bare.stdout


def test_a_bare_run_writes_no_page_into_its_directory():
    for tree in (build(False), build(True), build_broken()):
        contract = os.path.join(tree, "ARCHITECTURE.md")
        bare = drive(tree, contract)
        assert bare.returncode in (0, 1, 2), (bare.returncode, bare.stdout,
                                              bare.stderr)
        assert not os.path.exists(os.path.join(tree, "archituner.html")), \
            "the bare run wrote archituner.html"


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
