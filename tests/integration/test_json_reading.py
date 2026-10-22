# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/*
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


def drive(contract):
    return subprocess.run(
        [sys.executable, "-m", "archituner", contract, "--json"],
        cwd=REPO, capture_output=True, text=True, timeout=120)


def test_the_json_document_answers_the_reading_without_the_page_numbers():
    proc = drive(build())
    document = json.loads(proc.stdout)
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert ("regions" in document, "stack" in document) == (False, False)
    assert (document["schema"], document["status"], document["reason"]) == \
        (1, "divergent", "divergence")
    assert sorted(pair["state"] for pair in document["pairs"]) == \
        ["absence", "absence", "convergence", "divergence", "silence",
         "silence"]
    assert document["counts"] == {"convergence": 1, "divergence": 1,
                                  "absence": 2, "silence": 2}
    assert [crossing["code"] for crossing
            in document["crossings"]] == \
        ["import core_base", "import api_entry"]
    assert (document["baseline"], document["change"]) == \
        (".archituner-baseline.json", None)
    assert [key for key in ("contract", "tree", "order", "layers", "pairs",
                            "files", "coverage", "breaches", "findings",
                            "counts", "crossings")
            if key not in document] == []


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
