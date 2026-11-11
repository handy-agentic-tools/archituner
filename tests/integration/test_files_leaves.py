# covers: archituner/presentation/page/views/views.py archituner/presentation/page/views/readings.py archituner/presentation/page/shell/events.py archituner/presentation/page/views/rules.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
GONE = ("function drawFiles", "files: drawFiles", "let sortBy",
        "data-sort", "id='files'", "a file carries what it did",
        "#files td, #files th", "button.sort")


def page():
    with tempfile.TemporaryDirectory() as home:
        out = os.path.join(home, "page.html")
        proc = subprocess.run(
            [sys.executable, "-m", "archituner", CONTRACT, "-o", out],
            cwd=REPO, capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, (proc.returncode, proc.stdout,
                                      proc.stderr)
        with open(out, "rb") as handle:
            return handle.read()


def test_the_nav_and_the_drawer_map_name_no_files_view():
    drawn = page()
    assert b'const views = ["layers", "matrix", "coverage"' in drawn, \
        "the views array"
    assert b"layers: PHONE.matches ? drawColumn : drawLayers" in drawn \
        and b"coverage: drawCov" in drawn, "the drawer map"
    for gone in (b'"matrix", "files"', b'"files", "coverage"'):
        assert gone not in drawn, gone
    for gone in GONE:
        assert gone.encode() not in drawn, gone


def test_a_file_search_hit_selects_the_file_without_switching_view():
    drawn = page()
    start = drawn.index(b"t.dataset.hit")
    branch = drawn[start:drawn.index(b"draw();", start)]
    assert b'selection = {kind, id: rest.join(":")}' in branch, (
        "the hit stopped selecting the file it names")
    assert b'pair: "matrix"' in branch and b'layer: "layers"' in branch, (
        "the pair and layer routing moved with the files view")
    assert b'file: "files"' not in branch, (
        "a file search hit still switches the view")


def test_every_file_stays_reachable_by_the_panel_and_by_search():
    drawn = page()
    assert b'"files", "all files"' in drawn, "the panel's list of files"
    assert b'INDEX.push({kind: "file"' in drawn, "the search index"


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
