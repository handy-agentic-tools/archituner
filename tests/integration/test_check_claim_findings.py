# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/presentation/** archituner/source/** archituner/conformance/** archituner/contract/**
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

VALUE = "VALUE = 1\n"
APP_GLOB = "src_app/" + "**"
CORE_GLOB = "src_core/" + "**"
EXTRA_GLOB = "src_extra/" + "**"
ONE_GLOB = "src_app/one/" + "**"
FAR_GLOB = "src_far/" + "**"

CLEAN_CONTRACT = f"""---
layers:
  app:   ["{APP_GLOB}"]
  core:  ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
---
"""
VACANT_CONTRACT = f"""---
layers:
  app:   ["{APP_GLOB}"]
  core:  ["{CORE_GLOB}"]
  extra: ["{EXTRA_GLOB}"]

dependencies:
  allow:
    - app -> core
    - app -> extra
    - core -> app
    - core -> extra
    - extra -> app
    - extra -> core
---
"""
GONE_CONTRACT = f"""---
layers:
  app:   ["{APP_GLOB}"]
  core:  ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app

ignore:
  - "nowhere/{'**'}"
---
"""
TAKE_CONTRACT = CLEAN_CONTRACT[:-4] + "ignore:\n  - \"src_app/main.py\"\n---\n"
HOLE_CONTRACT = f"""---
layers:
  app:     ["{APP_GLOB}"]
  core:    ["{CORE_GLOB}"]
  app.one: ["{ONE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
---
"""
ESCAPE_CONTRACT = f"""---
layers:
  app:     ["{APP_GLOB}"]
  core:    ["{CORE_GLOB}"]
  app.one: ["{ONE_GLOB}"]
  app.far: ["{FAR_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
    - app.one -> app.far
    - app.far -> app.one
---
"""
ALL_CONTRACT = f"""---
layers:
  app:     ["{APP_GLOB}"]
  core:    ["{CORE_GLOB}"]
  extra:   ["{EXTRA_GLOB}"]
  app.one: ["{ONE_GLOB}"]
  app.far: ["{FAR_GLOB}"]

dependencies:
  allow:
    - app -> core
    - app -> extra
    - core -> app
    - core -> extra
    - extra -> app
    - extra -> core
    - app.one -> app.far
    - app.far -> app.one

ignore:
  - "nowhere/{'**'}"
---
"""
DIVERGENT_CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]
  core.one: ["core_one_*"]

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

FLAT_BODIES = {"src_app/main.py": VALUE, "src_core/util.py": VALUE}
HOLE_BODIES = {"src_app/flat.py": VALUE, "src_app/one/deep.py": VALUE,
               "src_core/util.py": VALUE}
TAKE_BODIES = {"src_app/main.py": VALUE, "src_app/other.py": VALUE,
               "src_core/util.py": VALUE}
ESCAPE_BODIES = {"src_app/one/a.py": VALUE, "src_far/escapee.py": VALUE,
                 "src_core/util.py": VALUE}
DIVERGENT_BODIES = {"api_entry.py": "import core_backbone\n",
                    "core_backbone.py": VALUE,
                    "core_bad.py": "import api_entry\n",
                    "core_one_helper.py": VALUE}

VACANT_TEXT = f"glob matches nothing: extra: {EXTRA_GLOB}"
GONE_TEXT = "ignore glob matches nothing: nowhere/" + "**"
TAKES_TEXT = (f"ignore glob src_app/main.py takes src_app/main.py, which "
              f"layer app's {APP_GLOB} would claim; ignore wins")
HOLE_TEXT = (f"src_app/flat.py is claimed by app's {APP_GLOB} and no child "
             f"claims it")
ESCAPE_TEXT = (f"src_far/escapee.py is claimed by app.far's {FAR_GLOB} but "
               f"no glob of its parent app claims it")
BACKBONE_HOLE = ("core_backbone.py is claimed by core's core_* and no child "
                 "claims it")


def plant_all(tree, contract, bodies):
    contract_path = os.path.join(tree, "ARCHITECTURE.md")
    plant(contract_path, contract)
    for rel, body in bodies.items():
        plant(os.path.join(tree, rel), body)
    return contract_path


def plant(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def drive(contract_path, *flags):
    return subprocess.run([sys.executable, "-m", "archituner", contract_path,
                           *flags], cwd=REPO, capture_output=True,
                          text=True, timeout=120)


def runs(contract_path):
    check = drive(contract_path, "--check")
    blob = drive(contract_path, "--json")
    report = drive(contract_path, "--report")
    assert max(check.returncode, blob.returncode,
               report.returncode) in (0, 1), \
        (check.returncode, check.stdout, blob.stdout, report.stdout)
    findings = json.loads(blob.stdout)["findings"]
    return check, report.stdout, [f["text"] for f in findings]


def fails_naming(contract_path, texts, *flags):
    proc = drive(contract_path, "--check", *flags)
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert all(text in proc.stdout for text in texts), \
        (texts, proc.stdout)
    return proc


def test_a_vacant_glob_fails_the_check():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, VACANT_CONTRACT, FLAT_BODIES),
                     [VACANT_TEXT])


def test_an_ignore_finding_fails_the_check():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, GONE_CONTRACT, FLAT_BODIES),
                     [GONE_TEXT])
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, TAKE_CONTRACT, TAKE_BODIES),
                     [TAKES_TEXT])


def test_a_sublayer_hole_fails_the_check():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, HOLE_CONTRACT, HOLE_BODIES),
                     [HOLE_TEXT])


def test_a_sublayer_escape_fails_the_check():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, ESCAPE_CONTRACT, ESCAPE_BODIES),
                     [ESCAPE_TEXT])


def test_a_tree_earning_one_of_each_class_names_all_three_in_its_check():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(plant_all(tree, ALL_CONTRACT, ESCAPE_BODIES),
                     [VACANT_TEXT, GONE_TEXT, ESCAPE_TEXT])


def test_report_and_json_still_list_the_claim_findings():
    shapes = [
        (VACANT_CONTRACT, FLAT_BODIES, [VACANT_TEXT]),
        (GONE_CONTRACT, FLAT_BODIES, [GONE_TEXT]),
        (TAKE_CONTRACT, TAKE_BODIES, [TAKES_TEXT]),
        (HOLE_CONTRACT, HOLE_BODIES, [HOLE_TEXT]),
        (ESCAPE_CONTRACT, ESCAPE_BODIES, [ESCAPE_TEXT]),
        (ALL_CONTRACT, ESCAPE_BODIES,
         [VACANT_TEXT, GONE_TEXT, ESCAPE_TEXT]),
    ]
    for contract, bodies, texts in shapes:
        with tempfile.TemporaryDirectory() as tree:
            _check, report, json_texts = runs(
                plant_all(tree, contract, bodies))
        for text in texts:
            assert text in json_texts, (text, json_texts)
            assert text in report, (text, report)


def test_a_clean_tree_still_prints_no_divergence_and_exits_zero():
    with tempfile.TemporaryDirectory() as tree:
        check, _report, _texts = runs(
            plant_all(tree, CLEAN_CONTRACT, FLAT_BODIES))
    assert check.returncode == 0, (check.returncode, check.stdout)
    assert check.stdout == "no divergence\n", check.stdout


def test_narrowing_to_a_finding_path_names_the_finding():
    with tempfile.TemporaryDirectory() as tree:
        contract = plant_all(tree, HOLE_CONTRACT, HOLE_BODIES)
        fails_naming(contract, [HOLE_TEXT], "--file", "src_app/flat.py")


def test_narrowing_hides_a_path_finding_but_keeps_a_pathless_one():
    with tempfile.TemporaryDirectory() as tree:
        contract = plant_all(tree, HOLE_CONTRACT, HOLE_BODIES)
        hidden = drive(contract, "--check", "--file", "src_app/one/deep.py")
    assert hidden.returncode == 0, (hidden.returncode, hidden.stdout)
    assert HOLE_TEXT not in hidden.stdout, hidden.stdout
    with tempfile.TemporaryDirectory() as tree:
        contract = plant_all(tree, VACANT_CONTRACT, FLAT_BODIES)
        fails_naming(contract, [VACANT_TEXT], "--file", "src_app/main.py")


def test_a_divergence_keeps_its_narrowing_beside_a_hidden_finding():
    with tempfile.TemporaryDirectory() as tree:
        contract = plant_all(tree, DIVERGENT_CONTRACT, DIVERGENT_BODIES)
        check = fails_naming(contract, ["divergence: core -> api"],
                             "--file", "core_bad.py")
    assert BACKBONE_HOLE not in check.stdout, check.stdout


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
