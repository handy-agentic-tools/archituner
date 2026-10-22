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
  api:   ["src/api/@@@"]
  core:  ["src/core/@@@"]
  model: ["src/model/@@@"]

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
""".replace("@@@", "**")

FAILED_CONTRACT = """---
layers:
  gone: ["gone/@@@"]
  far:  ["far/@@@"]

dependencies:
  forbid:
    - gone -> far
    - far -> gone
---
""".replace("@@@", "**")

BROKEN_CONTRACT = "layers:\n  api: [\"src/" + "**\"]\n"

API_ENTRY = "import src.core.base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
CORE_BAD = "import src.api\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(divergent):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    if divergent:
        plant(tree, "src/core/bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_unclaimed():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", FAILED_CONTRACT)
    plant(tree, "loose/a.py", "X = 1\n")
    plant(tree, "loose/b.py", "Y = 2\n")
    return os.path.join(tree, "ARCHITECTURE.md")


def build_broken():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", BROKEN_CONTRACT)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def read_document(proc):
    return json.loads(proc.stdout)


def test_a_clean_reading_is_one_ok_document():
    proc = drive(build(False), "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["schema"] == 1, document.get("schema")
    assert document["status"] == "ok", document.get("status")
    assert document["contract"] == "ARCHITECTURE.md", document["contract"]
    assert len(document["crossings"]) == 1, document["crossings"]
    assert document["crossings"][0] == {
        "file": "src/api/entry.py", "line": 1,
        "module": "src.core.base", "source": "api", "target": "core",
        "kind": "allow", "state": "convergence",
        "code": "import src.core.base"}, document["crossings"]


def test_a_realised_forbidden_pair_is_a_divergent_document():
    proc = drive(build(True), "--json")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    crossings = [c for c in read_document(proc)["crossings"]
                 if c["state"] == "divergence"]
    assert len(crossings) == 1, crossings
    assert crossings[0] == {
        "file": "src/core/bad.py", "line": 1, "module": "src.api",
        "source": "core", "target": "api", "kind": "forbid",
        "state": "divergence", "code": "import src.api"}, crossings


def test_a_run_that_claims_nothing_is_a_failed_run_document():
    proc = drive(build_unclaimed(), "--json")
    assert proc.returncode == 3, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "failed_run", document.get("status")
    assert "2 file(s) walked" in document["reason"], document["reason"]


def test_a_refused_contract_is_a_rejected_document():
    proc = drive(build_broken(), "--json")
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["schema"] == 1, document.get("schema")
    assert document["status"] == "rejected", document.get("status")
    assert document["reason"], document


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
