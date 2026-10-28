# covers: archituner/__main__.py archituner/cli/** archituner/conformance/** archituner/run/**
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

CONTRACT_NESTED = """---
layers:
  api:   ["**/api_*"]
  core:  ["**/core_*"]
  model: ["**/model_*"]

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

DOUBLED_SLASH = "archituner/" + "/core_bad.py"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(nested=False):
    tree = tempfile.mkdtemp()
    plant(tree, "ARCHITECTURE.md", CONTRACT_NESTED if nested else CONTRACT)
    plant(tree, "api_entry.py", API_ENTRY)
    plant(tree, "core_backbone.py", CORE_BACKBONE)
    plant(tree, "model_shape.py", MODEL_SHAPE)
    plant(tree, "core_bad.py", CORE_BAD)
    plant(tree, "model_bad.py", MODEL_BAD)
    if nested:
        plant(tree, "archituner/core_bad.py", CORE_BAD)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(*args, cwd=None):
    where = cwd or tempfile.mkdtemp()
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=where, capture_output=True, text=True,
                          timeout=120,
                          env=dict(os.environ, PYTHONPATH=REPO))


def git(tree, *args):
    subprocess.run(["git", "-C", tree, *args], capture_output=True,
                   check=True)


def planted_repo():
    tree = os.path.dirname(build())
    git(tree, "init", "-q")
    git(tree, "add", "-A")
    git(tree, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
        "-m", "t")
    return tree


def finding(proc, path):
    assert proc.returncode != 0 and path in proc.stdout, \
        (proc.returncode, proc.stdout, proc.stderr)


def test_a_file_axis_path_answers_alike_in_every_spelling():
    contract = build(nested=True)
    absolute = os.path.join(os.path.dirname(contract), "archituner",
                            "core_bad.py")
    asked = ("archituner/core_bad.py", "./archituner/core_bad.py", absolute,
             DOUBLED_SLASH)
    runs = [drive(contract, "--check", "--file", one) for one in asked]
    assert [run.returncode for run in runs] == [1, 1, 1, 1], runs
    assert runs[0].stdout == runs[1].stdout == runs[2].stdout == \
        runs[3].stdout, runs
    lines = runs[0].stdout.splitlines()
    assert "divergence: core -> api" in lines, lines
    assert "    archituner/core_bad.py imports api_entry" in lines, lines


def test_a_directory_and_its_slashed_form_select_the_files_below():
    contract = build(nested=True)
    bare = drive(contract, "--check", "--file", "archituner")
    slashed = drive(contract, "--check", "--file", "archituner/")
    named = drive(contract, "--check", "--file", "archituner/core_bad.py")
    codes = (bare.returncode, slashed.returncode, named.returncode)
    assert codes == (1, 1, 1), (codes, bare.stdout, slashed.stdout,
                                named.stdout)
    assert bare.stdout == slashed.stdout == named.stdout, \
        (bare.stdout, slashed.stdout, named.stdout)
    lines = bare.stdout.splitlines()
    assert "divergence: core -> api" in lines, lines
    assert "    archituner/core_bad.py imports api_entry" in lines, lines


def test_the_tree_root_spellings_answer_as_the_unnarrowed_check():
    contract = build()
    plain = drive(contract, "--check")
    dot = drive(contract, "--check", "--file", ".")
    dotted = drive(contract, "--check", "--file", "./")
    tree = os.path.dirname(contract)
    absolute = drive(contract, "--check", "--file", tree)
    assert (dot.returncode, dotted.returncode, absolute.returncode) == \
        (1, 1, 1), (plain, dot, dotted, absolute)
    assert dot.stdout == dotted.stdout == absolute.stdout == plain.stdout, \
        (plain, dot, dotted, absolute)
    finding(plain, "divergence: core -> api")


def test_a_path_nowhere_on_disk_is_a_finding_wherever_it_is_asked():
    alone = drive(build(), "--check", "--file", "ghost.py")
    finding(alone, "ghost.py")
    beside = drive(build(), "--check", "--file", "core_bad.py", "ghost.py")
    lines = beside.stdout.splitlines()
    finding(beside, "ghost.py")
    assert "divergence: core -> api" in lines, lines


def test_a_path_unknown_to_head_and_index_is_a_finding_inside_a_repo():
    tree = planted_repo()
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--check", "--file",
                 "no/such.py", cwd=tree)
    finding(proc, "no/such.py")


def test_a_path_the_head_still_carries_does_not_fail_the_gate():
    tree = planted_repo()
    os.remove(os.path.join(tree, "model_shape.py"))
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--check", "--file",
                 "model_shape.py", cwd=tree)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "no divergence" in proc.stdout.splitlines(), proc.stdout


def test_a_path_only_the_index_carries_does_not_fail_the_gate():
    tree = planted_repo()
    plant(tree, "indexed.py", MODEL_SHAPE)
    git(tree, "add", "indexed.py")
    os.remove(os.path.join(tree, "indexed.py"))
    proc = drive(os.path.join(tree, "ARCHITECTURE.md"), "--check", "--file",
                 "indexed.py", cwd=tree)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "no divergence" in proc.stdout.splitlines(), proc.stdout


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
