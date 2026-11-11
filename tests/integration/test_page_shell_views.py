# covers: archituner/presentation/**
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CLAIMS = {
    "archituner/presentation/model/column_layout.py": "presentation.model",
    "archituner/presentation/model/stack_layout.py": "presentation.model",
    "archituner/presentation/page/shell/events.py":
        "presentation.page.shell",
    "archituner/presentation/page/shell/page.py":
        "presentation.page.shell",
    "archituner/presentation/page/shell/shell.py":
        "presentation.page.shell",
    "archituner/presentation/page/views/axes.py":
        "presentation.page.views",
    "archituner/presentation/page/views/coverage.py":
        "presentation.page.views",
    "archituner/presentation/page/views/detail.py":
        "presentation.page.views",
    "archituner/presentation/page/views/grounds.py":
        "presentation.page.views",
    "archituner/presentation/page/views/layers.py":
        "presentation.page.views",
    "archituner/presentation/page/views/narrow.py":
        "presentation.page.views",
    "archituner/presentation/page/views/panel.py":
        "presentation.page.views",
    "archituner/presentation/page/views/readings.py":
        "presentation.page.views",
    "archituner/presentation/page/views/rules.py":
        "presentation.page.views",
    "archituner/presentation/page/views/views.py":
        "presentation.page.views",
}
SEEDS = ("0", "1", "2")


def claims_of():
    proc = subprocess.run([sys.executable, "-m", "archituner",
                           "ARCHITECTURE.md", "--json"], cwd=REPO,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), (proc.returncode, proc.stdout,
                                       proc.stderr)
    document = json.loads(proc.stdout)
    return {record["path"]: record["layer"] for record in document["files"]}


def contract_in(home):
    tree = os.path.join(home, "tree")
    shutil.copytree(REPO, tree,
                    ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                  ".venv"))
    return os.path.join(tree, "ARCHITECTURE.md")


def page_of(contract, home, seed):
    page = os.path.join(home, "page" + seed + ".html")
    env = dict(os.environ, PYTHONHASHSEED=seed)
    proc = subprocess.run([sys.executable, "-m", "archituner", contract,
                           "-o", page], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    with open(page, "rb") as handle:
        return handle.read()


def test_each_page_module_is_claimed_by_the_sublayer_the_contract_names():
    claims = claims_of()
    assert {path: claims.get(path) for path in CLAIMS} == CLAIMS, (
        {path: claims.get(path) for path in CLAIMS})


def test_the_page_builds_to_identical_bytes_under_three_hash_seeds():
    with tempfile.TemporaryDirectory() as home:
        contract = contract_in(home)
        pages = [page_of(contract, home, seed) for seed in SEEDS]
    assert pages[0].startswith(b"<!doctype html>"), pages[0][:40]
    assert pages[0] == pages[1] == pages[2], (len(pages[0]), len(pages[1]),
                                              len(pages[2]))
    for page in pages:
        missing = [mark for mark in (b'role="tablist"', b"aria-selected=",
                                     b"all files") if mark not in page]
        assert not missing, missing


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
