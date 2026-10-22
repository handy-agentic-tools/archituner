# covers: archituner/__main__.py archituner/cli/**
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

API_ENTRY = "import core_backbone\n"
CORE_BACKBONE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
CORE_BAD = "import api_entry\n"
MODEL_BAD = "import api_entry\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BACKBONE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    plant(tree, "core_bad.py", CORE_BAD)
    plant(tree, "model_bad.py", MODEL_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    where = tempfile.mkdtemp()
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=where, capture_output=True, text=True,
                          timeout=120,
                          env=dict(os.environ, PYTHONPATH=REPO))


def test_a_check_fed_two_files_names_both_divergences():
    proc = drive(build(), "--check", "--file", "core_bad.py", "model_bad.py")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    lines = proc.stdout.splitlines()
    assert "divergence: core -> api" in lines, lines
    assert "divergence: model -> api" in lines, lines
    assert "    core_bad.py imports api_entry" in lines, lines
    assert "    model_bad.py imports api_entry" in lines, lines


def test_a_check_fed_a_clean_file_beside_a_bad_one_still_fails():
    proc = drive(build(), "--check", "--file", "core_backbone.py",
                 "core_bad.py")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "divergence: core -> api" in proc.stdout.splitlines(), proc.stdout


def test_a_json_feed_of_two_layers_filters_to_both_pairs():
    proc = drive(build(), "--json", "--layer", "api", "core")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    document = json.loads(proc.stdout)
    assert document["status"] == "divergent", document["status"]
    assert sorted((c["source"], c["target"], c["state"])
                  for c in document["crossings"]) == [
        ("api", "core", "convergence"),
        ("core", "api", "divergence")], document["crossings"]


def test_a_state_feed_naming_both_states_keeps_the_convergence_witness():
    proc = drive(build(), "--json", "--state", "divergence", "convergence")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    document = json.loads(proc.stdout)
    assert sorted((c["source"], c["target"], c["state"], c["file"])
                  for c in document["crossings"]) == [
        ("api", "core", "convergence", "api_entry.py"),
        ("core", "api", "divergence", "core_bad.py"),
        ("model", "api", "divergence", "model_bad.py")], \
        document["crossings"]


def test_a_stray_word_after_a_mode_flag_refuses():
    proc = drive(build(), "--check", "strayword")
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout == "", proc.stdout
    assert proc.stderr.startswith("usage:"), proc.stderr


def test_an_unknown_flag_refuses():
    proc = drive(build(), "--bogus")
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout == "", proc.stdout
    assert proc.stderr.startswith("usage:"), proc.stderr


def test_a_trailing_file_flag_naming_no_value_refuses():
    proc = drive(build(), "--check", "--file")
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout == "", proc.stdout
    assert proc.stderr.startswith("usage:"), proc.stderr


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
