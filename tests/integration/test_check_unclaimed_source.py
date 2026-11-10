# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/presentation/** archituner/source/** archituner/conformance/** archituner/contract/** archituner/report/**
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

VALUE = "VALUE = 1\n"
APP_GLOB = "app_" + "*"
CORE_GLOB = "core_" + "*"
ORPHAN = "stray/orphan.py"

OPEN_CONTRACT = f"""---
layers:
  app:  ["{APP_GLOB}"]
  core: ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
---
"""
CLAIMED_CONTRACT = f"""---
layers:
  app:  ["{APP_GLOB}", "loose.py"]
  core: ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
---
"""
IGNORED_CONTRACT = f"""---
layers:
  app:  ["{APP_GLOB}"]
  core: ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app

ignore:
  - "loose.py"
---
"""
PKG_CONTRACT = f"""---
layers:
  app:  ["{APP_GLOB}", "pkg/{APP_GLOB}"]
  core: ["{CORE_GLOB}"]

dependencies:
  allow:
    - app -> core
    - core -> app
---
"""

BESIDE_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                 "loose.py": VALUE}
IMPORTING_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                    ORPHAN: "import core_util\n"}
IMPORTED_BODIES = {"app_main.py": "import stray.orphan\n",
                   "core_util.py": VALUE, ORPHAN: VALUE}
ALONE_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE, ORPHAN: VALUE}
IGNORED_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                  "loose.py": "import core_util\n"}
PKG_BESIDE_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                     "pkg/app_main.py": VALUE, "pkg/loose.py": VALUE}
UNCLAIMED_IMPORTING_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                              "stray/a.py": "import stray.b\n",
                              "stray/b.py": VALUE}
GITIGNORED_BODIES = {"app_main.py": VALUE, "core_util.py": VALUE,
                     "loose.py": "import core_util\n",
                     ".gitignore": "loose.py\n"}
CLAIMED_IMPORTING_BODIES = {"app_main.py": "import loose\n",
                            "core_util.py": VALUE, "loose.py": VALUE}


def build(tree, bodies, contract=OPEN_CONTRACT):
    for rel, text in [("ARCHITECTURE.md", contract), *bodies.items()]:
        path = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(contract_path, *flags):
    return subprocess.run([sys.executable, "-m", "archituner", contract_path,
                           *flags], cwd=REPO, capture_output=True,
                          text=True, timeout=120)


def fails_naming(contract_path, path):
    proc = drive(contract_path, "--check")
    assert proc.returncode != 0, (proc.returncode, proc.stdout, proc.stderr)
    assert path in proc.stdout, (path, proc.stdout)
    return proc


def runs_green(contract_path):
    proc = drive(contract_path, "--check")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout
    return proc


def test_an_unclaimed_file_beside_a_claimed_file_is_named_and_exits_non_zero():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(build(tree, BESIDE_BODIES), "loose.py")


def test_an_unclaimed_file_importing_a_claimed_file_is_named_and_exits_non_zero():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(build(tree, IMPORTING_BODIES), ORPHAN)


def test_an_unclaimed_file_imported_by_a_claimed_file_is_named_and_exits_non_zero():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(build(tree, IMPORTED_BODIES), ORPHAN)


def test_an_unclaimed_file_beside_a_claimed_file_in_a_subdirectory_is_named_and_exits_non_zero():
    with tempfile.TemporaryDirectory() as tree:
        fails_naming(build(tree, PKG_BESIDE_BODIES, contract=PKG_CONTRACT),
                     "pkg/loose.py")


def test_claiming_the_file_into_a_layer_turns_the_run_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, BESIDE_BODIES, contract=CLAIMED_CONTRACT))


def test_an_unclaimed_file_with_no_claimed_neighbour_or_import_either_way_stays_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, ALONE_BODIES))


def test_an_unclaimed_file_beside_a_claimed_file_but_ignored_stays_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, IGNORED_BODIES, contract=IGNORED_CONTRACT))


def test_an_unclaimed_file_importing_an_unclaimed_file_stays_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, UNCLAIMED_IMPORTING_BODIES))


def test_a_file_excluded_by_the_gitignore_stays_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, GITIGNORED_BODIES))


def test_a_claimed_file_importing_an_ignored_file_stays_green():
    with tempfile.TemporaryDirectory() as tree:
        runs_green(build(tree, CLAIMED_IMPORTING_BODIES,
                         contract=IGNORED_CONTRACT))


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
