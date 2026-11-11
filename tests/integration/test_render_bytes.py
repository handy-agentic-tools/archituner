# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/presentation/**
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PAYLOAD = "const DATA = "
DIGEST = "6f070f69512aea5313df9f42ffa0a0a19b3dc6ac7991301df577340c196373c3"
BYTES = 90250
PAGE_MODULE = "archituner/presentation/page/shell/page.py"


def drive(contract, path):
    return subprocess.run([sys.executable, "-m", "archituner", contract,
                           "-o", path],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def check_of_page():
    return subprocess.run(
        [sys.executable, "-m", "archituner", "ARCHITECTURE.md", "--check",
         "--file", PAGE_MODULE],
        cwd=REPO, capture_output=True, text=True, timeout=120)


def read_of(path):
    with open(path, "rb") as handle:
        return handle.read()


def past_payload(page):
    text = page.decode("utf-8")
    return "\n".join(line for line in text.splitlines()
                     if not line.startswith(PAYLOAD)).encode("utf-8")


def copy_of_this_tree(home):
    tree = os.path.join(home, "tree")
    shutil.copytree(REPO, tree,
                    ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                  ".venv"))
    return os.path.join(tree, "ARCHITECTURE.md")


def test_a_check_rerun_over_the_page_module_prints_the_same_bytes():
    one = check_of_page()
    two = check_of_page()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, two.stdout)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


def test_a_rerun_of_this_tree_regenerates_the_same_bytes_payload_included():
    with tempfile.TemporaryDirectory() as home:
        contract = copy_of_this_tree(home)
        one = os.path.join(home, "first.html")
        two = os.path.join(home, "second.html")
        proc = drive(contract, one)
        assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
        proc = drive(contract, two)
        assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
        first, second = read_of(one), read_of(two)
    assert first.startswith(b"<!doctype html>") and PAYLOAD.encode() in first, \
        (first[:40], len(first))
    assert first == second, (len(first), len(second), next(
        (i for i, (a, b) in enumerate(zip(first, second)) if a != b),
        min(len(first), len(second))))


def test_the_page_past_its_payload_line_hashes_the_digest_frozen_on_main():
    contract = os.path.join(REPO, "ARCHITECTURE.md")
    with tempfile.TemporaryDirectory() as home:
        page = os.path.join(home, "page.html")
        proc = drive(contract, page)
        assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
        body = past_payload(read_of(page))
    assert len(body) == BYTES, (len(body), BYTES)
    assert hashlib.sha256(body).hexdigest() == DIGEST, (
        hashlib.sha256(body).hexdigest(), DIGEST)


MARKS = (b'role="tablist"', b'data-panel-tab=', b'aria-selected=',
         b'all files', b'DATA.files.length')


def test_the_page_at_rest_carries_the_panel_s_tab_strip():
    contract = os.path.join(REPO, "ARCHITECTURE.md")
    with tempfile.TemporaryDirectory() as home:
        page = os.path.join(home, "page.html")
        proc = drive(contract, page)
        assert proc.returncode == 0, (proc.returncode, proc.stdout,
                                      proc.stderr)
        body = read_of(page)
    assert all(map(lambda mark: mark in body, MARKS)), MARKS


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
