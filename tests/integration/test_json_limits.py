# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/*
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

LIMITS_CONTRACT = """---
layers:
  api:   ["src/api/@@@"]
  core:  ["src/core/@@@"]
  model: ["src/model/@@@"]

limits:
  size: 21
  cyclomatic: 5
  prose_count: 0

  overrides:
    - "size `core`: 12 - gates stay thin"
    - "cyclomatic `src/core/@@@`: 5 - the gate's arithmetic, read whole"

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

API_ENTRY = "import src.core.base\n"
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
CORE_BAD = "import src.api\n"
MODEL_HEAVY = "V = '" + "x" * 20 + "'\n"
CORE_HEAVY = "V = '" + "x" * 10 + "'\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_limits(breach=False, divergent=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", LIMITS_CONTRACT)
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    if breach:
        plant(tree, "src/model/weight.py", MODEL_HEAVY)
        plant(tree, "src/core/weight.py", CORE_HEAVY)
    if divergent:
        plant(tree, "src/core/bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def read_document(proc):
    return json.loads(proc.stdout)


def test_a_clean_reading_carries_the_law_on_its_records():
    proc = drive(build_limits(), "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "ok", document.get("status")
    assert document["breaches"] == [], document["breaches"]
    records = {record["path"]: record for record in document["files"]}
    assert records["src/api/entry.py"]["limits"] == {
        "size": {"limit": 21, "share": 1.0},
        "cyclomatic": {"limit": 5, "share": 0.2},
        "prose_count": {"limit": 0, "share": None}}, \
        records["src/api/entry.py"]["limits"]
    assert records["src/core/base.py"]["limits"]["size"] == \
        {"limit": 12, "share": 0.83}, records["src/core/base.py"]["limits"]
    assert records["src/model/shape.py"]["limits"]["size"] == \
        {"limit": 21, "share": 0.48}, records["src/model/shape.py"]["limits"]
    assert records["src/api/__init__.py"]["limits"]["size"] == \
        {"limit": 21, "share": 0.0}, records["src/api/__init__.py"]["limits"]


def test_a_breach_is_a_divergent_document_with_its_breaches_listed():
    proc = drive(build_limits(breach=True), "--json")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "divergent", document.get("status")
    assert "breach" in (document["reason"] or ""), document["reason"]
    assert sorted(document["breaches"], key=lambda b: b["file"]) == [
        {"file": "src/core/weight.py", "number": "size", "value": 17,
         "limit": 12, "reason": "gates stay thin"},
        {"file": "src/model/weight.py", "number": "size", "value": 27,
         "limit": 21, "reason": None}], document["breaches"]


def test_a_divergence_and_a_breach_together_name_both_classes():
    proc = drive(build_limits(breach=True, divergent=True), "--json")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "divergent", document.get("status")
    reason = document["reason"] or ""
    assert "divergence" in reason, reason
    assert "breach" in reason, reason


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
