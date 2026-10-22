# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/*
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

NONE_CONTRACT = """---
layers:
  api:   ["src/api/@@@"]
  core:  ["src/core/@@@"]
  model: ["src/model/@@@"]

limits:
  size: 21

  overrides:
    - "size `model`: none - the model carries generated tables"

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

VACANT_CONTRACT = """---
layers:
  api:   ["src/api/@@@"]
  core:  ["src/core/@@@"]
  model: ["src/model/@@@"]

limits:
  size: 21

  overrides:
    - "size `gone/@@@`: 5 - nobody lives here"

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

ORDER_TEMPLATE = """---
layers:
  api:   ["src/api/@@@"]
  core:  ["src/core/@@@"]
  model: ["src/model/@@@"]

limits:
  size: 21

  overrides:
%s

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
MODEL_HEAVY = "V = '" + "x" * 20 + "'\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_flat(contract):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", contract)
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_order(*entries):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", ORDER_TEMPLATE % "".join(
        f'    - "{entry}"\n' for entry in entries))
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def read_document(proc):
    return json.loads(proc.stdout)


def test_a_none_override_lifts_the_law_on_the_document():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", NONE_CONTRACT)
    plant(tree, "src/api/__init__.py", "")
    plant(tree, "src/api/entry.py", API_ENTRY)
    plant(tree, "src/core/__init__.py", "")
    plant(tree, "src/core/base.py", CORE_BASE)
    plant(tree, "src/model/__init__.py", "")
    plant(tree, "src/model/shape.py", MODEL_SHAPE)
    plant(tree, "src/model/weight.py", MODEL_HEAVY)
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "ok", document.get("status")
    assert document["breaches"] == [], document["breaches"]
    records = {record["path"]: record for record in document["files"]}
    lifted = {"size": {"limit": None, "share": None}}
    assert records["src/model/shape.py"]["limits"] == lifted, \
        records["src/model/shape.py"]["limits"]
    assert records["src/model/weight.py"]["limits"] == lifted, \
        records["src/model/weight.py"]["limits"]
    assert set(records["src/core/base.py"]["limits"]) == {"size"}, \
        records["src/core/base.py"]["limits"]


def test_the_first_override_in_declaration_order_sets_the_limit():
    proc = drive(build_order("size `core`: 12 - gates stay thin",
                             "size `src/core/base.py`: 4 - the later entry "
                             "never re-judges"), "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "ok", document.get("status")
    assert document["breaches"] == [], document["breaches"]
    proc = drive(build_order("size `src/core/base.py`: 4 - the later entry "
                             "never re-judges",
                             "size `core`: 12 - gates stay thin"), "--json")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "divergent", document.get("status")
    assert document["breaches"] == [
        {"file": "src/core/base.py", "number": "size", "value": 10,
         "limit": 4, "reason": "the later entry never re-judges"}], \
        document["breaches"]


def test_an_override_whose_selector_reaches_no_file_is_a_finding_not_a_refusal():
    proc = drive(build_flat(VACANT_CONTRACT), "--json")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    document = read_document(proc)
    assert document["status"] == "ok", document.get("status")
    assert any(("gone/" + "**") in finding["text"]
               for finding in document["findings"]), \
        sorted(finding["text"] for finding in document["findings"])


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
