# covers: archituner/presentation/page/views/views.py archituner/presentation/page/views/readings.py
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
GONE = ("function drawSurface", ">surface<", "entry layer: ",
        "named from ", "single-contract repository")


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


def test_the_nav_and_the_drawer_map_name_no_surface_view():
    drawn = page()
    assert b'"coverage"]' in drawn, "the views array"
    assert b"coverage: drawCov}" in drawn, "the drawer map"
    for gone in (b'"coverage", "surface"]',
                 b"coverage: drawCov, surface: drawSurface}"):
        assert gone not in drawn, gone


def test_no_term_of_art_the_vocabulary_bans_is_on_the_page():
    drawn = page()
    for word in GONE:
        assert word.encode() not in drawn, word


def test_the_reading_still_carries_the_surface_facts():
    drawn = page()
    for kept in (b'"surface":', b'"entry"', b'"cross_contract"'):
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
