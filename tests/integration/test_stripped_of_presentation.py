# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/report/* archituner/vocabulary/** archituner/conformance/visibility.py
import json
import os
import shutil
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


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_base.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    plant(tree, "core_bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def stripped(home):
    tree = os.path.join(home, "archituner")
    shutil.copytree(os.path.join(REPO, "archituner"), tree,
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.rmtree(os.path.join(tree, "presentation"))
    return home


def drive(root, contract, *args):
    env = dict(os.environ, PYTHONPATH=root)
    return subprocess.run([sys.executable, "-m", "archituner", contract,
                           *args], cwd=os.path.dirname(contract), env=env,
                          capture_output=True, text=True, timeout=120)


def without_page_numbers(document):
    return {key: value for key, value in document.items()
            if key not in ("regions", "stack")}


def test_the_text_flows_answer_the_same_without_the_page_package():
    contract = build()
    with tempfile.TemporaryDirectory() as home:
        bare = stripped(home)
        for args in (["--check"], ["--report"], ["--json"]):
            whole = drive(REPO, contract, *args)
            cut = drive(bare, contract, *args)
            assert cut.returncode == whole.returncode, \
                (args, whole.returncode, cut.returncode, whole.stderr,
                 cut.stderr)
            if args == ["--json"]:
                assert json.loads(cut.stdout) == \
                    without_page_numbers(json.loads(whole.stdout)), \
                    (cut.stdout, whole.stdout)
            else:
                assert cut.stdout == whole.stdout, \
                    (args, cut.stdout, whole.stdout, cut.stderr)


def test_the_page_mode_refuses_without_the_page_package():
    contract = build()
    with tempfile.TemporaryDirectory() as home:
        cut = drive(stripped(home), contract, "-o", "page.html")
    assert cut.returncode != 0, (cut.returncode, cut.stdout, cut.stderr)
    assert cut.stdout.splitlines(), cut.stdout
    assert "Traceback" not in cut.stderr, cut.stderr


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
