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


def test_given_no_paths_every_test_runs():
    tree = scratch_tree()
    plant(tree, "tests/unit/scratch/test_x.py", RUNS)
    plant(tree, "tests/integration/test_flow.py", COVERS_SCRATCH)
    plant(tree, "tests/lints/test_one.py", COVERS_SCRATCH)
    plant(tree, "tests/lints/test_bare.py", RUNS)
    proc = drive(tree)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert carried(proc.stdout) == {
        "tests/unit/scratch/test_x.py",
        "tests/integration/test_flow.py",
        "tests/lints/test_one.py",
        "tests/lints/test_bare.py"}, proc.stdout
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
