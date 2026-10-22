# covers: tests/run.py
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
RUNNER = os.path.join("tests", "run.py")

RUNS = "import sys\nsys.exit(0)\n"
COVERS_SCRATCH = "# covers: scratch/" + "**\n" + RUNS
SHEBANG = "#!/usr/bin/env python3\n"
COVERS_TOO_LATE = SHEBANG + "import sys\n" + COVERS_SCRATCH
COVERS_UNANCHORED = "import sys\n" + COVERS_SCRATCH


def scratch_tree():
    tree = tempfile.mkdtemp()
    os.makedirs(os.path.join(tree, "tests"))
    shutil.copy(os.path.join(REPO, RUNNER), os.path.join(tree, RUNNER))
    return tree


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def drive(tree, *paths):
    return subprocess.run([sys.executable, RUNNER, *paths], cwd=tree,
                          capture_output=True, text=True, timeout=120)


def carried(out):
    return {line.split("  ")[1] for line in out.splitlines()
            if line.startswith("PASS  ") or line.startswith("FAIL  ")}


def test_a_covers_line_anywhere_else_leaves_the_file_bare():
    tree = scratch_tree()
    plant(tree, "tests/integration/test_flow.py", COVERS_TOO_LATE)
    plant(tree, "tests/integration/test_other.py", COVERS_UNANCHORED)
    proc = drive(tree, "other/y.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert carried(proc.stdout) == {
        "tests/integration/test_flow.py",
        "tests/integration/test_other.py"}, proc.stdout
    assert proc.stdout.splitlines()[-1] == "all green", proc.stdout


def test_a_flow_with_no_covers_line_runs_on_a_scoped_run():
    tree = scratch_tree()
    plant(tree, "tests/integration/test_bare.py", RUNS)
    proc = drive(tree, "other/y.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert carried(proc.stdout) == {"tests/integration/test_bare.py"}, \
        proc.stdout
    assert proc.stdout.splitlines()[-1] == "all green", proc.stdout


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
