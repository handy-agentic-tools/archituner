# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/presentation/** archituner/source/** archituner/conformance/** archituner/contract/**
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

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


def drive(tree, *args):
    env = dict(os.environ, PYTHONPATH=REPO)
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=tree, env=env, capture_output=True,
                          timeout=120)


def test_an_explicit_out_still_renders_the_page():
    tree = build(False)
    contract = os.path.join(tree, "ARCHITECTURE.md")
    page = os.path.join(tree, "page.html")
    proc = drive(tree, contract, "-o", page)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert os.path.isfile(page), proc.stdout
    with open(page, "rb") as handle:
        assert handle.read().startswith(b"<!doctype html>"), \
            "the page is not the html artifact"


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
