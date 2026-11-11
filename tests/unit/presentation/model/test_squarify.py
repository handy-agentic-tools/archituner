import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.squarify import grown_row
from archituner.presentation.model.squarify import row_laid
from archituner.presentation.model.squarify import squarify
from archituner.presentation.model.squarify import worst_ratio

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "model", "squarify.py")

A = {"path": "a", "files": 4}
B = {"path": "b", "files": 1}
INF = float("inf")


def test_the_worst_box_in_a_row_scores_its_sides():
    one = worst_ratio([dict(A)], 40, 800)
    both = worst_ratio([dict(A), dict(B)], 40, 800)
    assert (one, both) == (2.0, 12.5), (one, both)


def test_a_degenerate_row_reads_as_bad_as_it_gets():
    empty = worst_ratio([], 40, 800)
    no_side = worst_ratio([dict(A)], 0, 800)
    no_files = worst_ratio([{"path": "a", "files": 0}], 40, 800)
    assert (empty, no_side, no_files) == (INF, INF, INF), \
        (empty, no_side, no_files)


def test_a_row_grows_only_while_its_worst_box_improves():
    items = [{"path": "a", "files": 1}, {"path": "b", "files": 1},
             {"path": "c", "files": 1}]
    row = grown_row(items, [], 40, 533)
    assert (row, items) == ([{"path": "a", "files": 1},
                             {"path": "b", "files": 1}],
                            [{"path": "c", "files": 1}]), (row, items)


def test_a_row_lands_along_the_shorter_side_and_leaves_its_band():
    wide = row_laid([dict(A)], 800, 3, 5, 100, 40)
    tall = row_laid([dict(A)], 800, 3, 5, 40, 100)
    assert wide == ([{"path": "a", "files": 4, "x": 3, "y": 5,
                      "width": 80.0, "height": 40.0}],
                    83.0, 5, 20.0, 40), wide
    assert tall == ([{"path": "a", "files": 4, "x": 3, "y": 5,
                      "width": 40.0, "height": 80.0}],
                    3, 85.0, 40, 20.0), tall


def test_the_frame_re_decides_its_shorter_side_every_row():
    boxes = squarify([dict(A), dict(B)], 0, 0, 40, 40)
    assert boxes == [{"path": "a", "files": 4, "x": 0, "y": 0,
                      "width": 40.0, "height": 32.0},
                     {"path": "b", "files": 1, "x": 0, "y": 32.0,
                      "width": 40.0, "height": 8.0}], boxes


def test_rows_land_in_fixed_rectangles_on_a_wide_canvas():
    boxes = squarify([dict(A), dict(B)], 0, 0, 100, 40)
    assert boxes == [{"path": "a", "files": 4, "x": 0, "y": 0,
                      "width": 80.0, "height": 40.0},
                     {"path": "b", "files": 1, "x": 80.0, "y": 0,
                      "width": 20.0, "height": 40.0}], boxes


def test_rows_land_in_fixed_rectangles_on_a_tall_canvas():
    boxes = squarify([dict(A), dict(B)], 0, 0, 40, 100)
    assert boxes == [{"path": "a", "files": 4, "x": 0, "y": 0,
                      "width": 40.0, "height": 80.0},
                     {"path": "b", "files": 1, "x": 0, "y": 80.0,
                      "width": 40.0, "height": 20.0}], boxes


def test_no_item_or_no_extent_places_nothing():
    placed = (squarify([], 0, 0, 100, 40),
              squarify([dict(A)], 0, 0, 0, 40),
              squarify([{"path": "a", "files": 0}], 0, 0, 100, 40))
    assert placed == ([], [], []), placed


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_squarify_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
