# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/presentation/page/shell/page.py archituner/presentation/page/views/views.py
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
WITNESS = ("presentation.page", "tests_unit")

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")


def render():
    with tempfile.TemporaryDirectory() as home:
        page = os.path.join(home, "page.html")
        proc = subprocess.run(
            [sys.executable, "-m", "archituner", CONTRACT, "-o", page],
            cwd=REPO, capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, (proc.returncode, proc.stdout,
                                      proc.stderr)
        with open(page, encoding="utf-8") as handle:
            return handle.read()


PAGE = render()


def payload_of(page):
    at = page.index("const DATA = ") + len("const DATA = ")
    value, _ = json.JSONDecoder().raw_decode(page, at)
    return value


def flat_of(page):
    body = re.search(r"function drawMatrix\(\).*?return h;\s*\}", page, re.S)
    assert body, "the page carries no matrix drawer"
    text = BLOCK_COMMENT.sub(" ", body.group(0))
    text = LINE_COMMENT.sub(" ", text)
    return WHITESPACE.sub(" ", text).strip()


def test_this_repositories_page_omits_pairs_the_matrix_walk_names():
    data = payload_of(PAGE)
    carried = {(pair["source"], pair["target"]) for pair in data["pairs"]}
    missing = [(s, t) for s in data["order"] for t in data["order"]
               if s != t and (s, t) not in carried]
    assert missing, "the payload carries a cell for every pair the walk names"
    assert WITNESS in missing, (WITNESS, missing[:4], len(missing))


def test_the_page_draws_the_undecided_cell_instead_of_reading_the_pair():
    gap = re.search(r'pairAt\[s \+ "->" \+ t\]; (.*?)const mark = changing',
                    flat_of(PAGE))
    assert gap, "the shipped matrix never looks the pair up"
    assert gap.group(1).strip() == 'if (!p) { h += "<td></td>"; return; }', (
        "the shipped matrix reads the pair it omits instead of drawing its "
        "cell", gap.group(1))


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
