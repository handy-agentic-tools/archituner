# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/report/report.py archituner/conformance/classification.py archituner/conformance/proposal.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

LIMITS_CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

limits:
  size: 21
  cyclomatic: 5
  prose_count: 0

  overrides:
    - "size `core`: 12 - gates stay thin"
    - "cyclomatic `core_*`: 5 - the gate's arithmetic, read whole"

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

AFTER_CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

limits:
  cyclomatic: 5
  prose_count: 0

  overrides:
    - "size `core`: 12 - gates stay thin"
    - "cyclomatic `core_*`: 5 - the gate's arithmetic, read whole"

  size: 12

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

PROSE_CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

limits:
  prose_count: 0

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
CORE_BASE = "VALUE = 1\n"
MODEL_SHAPE = "VALUE = 2\n"
MODEL_HEAVY = "V = '" + "x" * 20 + "'\n"
CORE_HEAVY = "V = '" + "x" * 10 + "'\n"
PROSE_NOTE = MODEL_SHAPE + "# a note for the reader\n"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_limits(breach=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", LIMITS_CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if breach:
        plant(tree, "model_weight.py", MODEL_HEAVY)
        plant(tree, "core_weight.py", CORE_HEAVY)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_prose():
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", PROSE_CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BASE)
    plant(tree, "model_shape.py", PROSE_NOTE)
    return os.path.join(tree, "ARCHITECTURE.md")


def build_after(default="size: 12", breach=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md",
          AFTER_CONTRACT.replace("  size: 12\n\ndependencies",
                                 "  " + default + "\n\ndependencies"))
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BASE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    if breach:
        plant(tree, "model_weight.py", MODEL_HEAVY)
        plant(tree, "core_weight.py", CORE_HEAVY)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def breach_line(lines, path):
    found = [line for line in lines if path in line]
    assert len(found) == 1, lines
    return found[0]


def carries(line, words):
    assert all(word in line for word in words), line


def test_a_file_past_its_limit_fails_the_gate_one_line_per_breach():
    proc = drive(build_limits(breach=True), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "no divergence" not in proc.stdout, proc.stdout
    lines = proc.stdout.splitlines()
    carries(breach_line(lines, "model_weight.py"), ("size", "27", "21"))
    carries(breach_line(lines, "core_weight.py"),
            ("size", "17", "12", "gates stay thin"))


def test_a_check_fed_files_scopes_the_limit_verdict_to_them():
    contract = build_limits(breach=True)
    proc = drive(contract, "--check", "--file", "api_entry.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout
    proc = drive(contract, "--check", "--file", "model_weight.py")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert any("model_weight.py" in line
               for line in proc.stdout.splitlines()), proc.stdout


def test_prose_past_its_limit_is_a_breach_the_same_way():
    proc = drive(build_prose(), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "no divergence" not in proc.stdout, proc.stdout
    carries(breach_line(proc.stdout.splitlines(), "model_shape.py"),
            ("prose_count",))


def test_a_default_written_after_the_override_items_gates_the_tree():
    proc = drive(build_after(breach=True), "--check")
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "no divergence" not in proc.stdout, proc.stdout
    lines = proc.stdout.splitlines()
    carries(breach_line(lines, "model_weight.py"), ("size", "27", "12"))
    carries(breach_line(lines, "core_weight.py"),
            ("size", "17", "12", "gates stay thin"))


def test_an_unknown_number_written_after_the_override_items_is_refused():
    proc = drive(build_after("size: 12\n  fanout: 5"), "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    carries(breach_line(proc.stdout.splitlines(), "fanout"),
            ("a number no file record carries",))


def test_a_non_plain_count_written_after_the_override_items_is_refused():
    proc = drive(build_after("size: none"), "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    carries(breach_line(proc.stdout.splitlines(), "not a plain count"),
            ("size",))


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
