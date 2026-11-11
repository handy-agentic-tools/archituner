# covers: archituner/presentation/page/views/views.py archituner/presentation/page/views/readings.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
GONE = ("function drawShape", "fan-out", "fan-in",
        "longest permitted path", "permitted edges realised")


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


def test_the_nav_and_the_drawer_map_name_no_shape_view():
    drawn = page()
    assert b'"coverage"]' in drawn, "the views array"
    assert b"coverage: drawCov}" in drawn, "the drawer map"
    for gone in (b'"coverage", "surface", "shape"]',
                 b"surface: drawSurface, shape: drawShape}"):
        assert gone not in drawn, gone


def test_no_term_of_art_the_vocabulary_bans_is_on_the_page():
    drawn = page()
    for word in GONE:
        assert word.encode() not in drawn, word


def test_the_coverage_figure_buttons_still_open_their_members():
    drawn = page()
    for kept in (b'"fmove"', b'"fdropped"', b'kind === "fmove"',
                 b'kind === "fdropped"', b"figureMembers(kind, id)",
                 b"[data-figure]"):
        assert kept in drawn, kept


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
