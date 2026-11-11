import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
import archituner.presentation.model.layout as layout
from archituner.presentation.model.layout import UNIT
from archituner.presentation.model.layout import canvas
from archituner.presentation.model.layout import regions
from archituner.presentation.model.layout import squarify
from archituner.presentation.model.layout import stack_geometry

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "model", "layout.py")

TREE = {'tree': {'path': '.',
          'name': '.',
          'layer': None,
          'kind': 'dir',
          'files': 9,
          'members': [],
          'children': [{'path': 'src/api',
                        'name': 'api',
                        'layer': 'api',
                        'kind': 'dir',
                        'files': 6,
                        'members': [],
                        'children': [{'path': 'src/api/entry.py',
                                      'name': 'entry.py',
                                      'layer': 'api',
                                      'kind': 'file',
                                      'files': 4,
                                      'members': ['src/api/entry.py'],
                                      'children': []},
                                     {'path': 'src/api/util.py',
                                      'name': 'util.py',
                                      'layer': 'api',
                                      'kind': 'file',
                                      'files': 2,
                                      'members': ['src/api/util.py'],
                                      'children': []}]},
                       {'path': 'src/core',
                        'name': 'core',
                        'layer': 'core',
                        'kind': 'dir',
                        'files': 2,
                        'members': [],
                        'children': [{'path': 'src/core/base.py',
                                      'name': 'base.py',
                                      'layer': 'core',
                                      'kind': 'file',
                                      'files': 2,
                                      'members': ['src/core/base.py'],
                                      'children': []}]},
                       {'path': 'stray.py',
                        'name': 'stray.py',
                        'layer': None,
                        'kind': 'file',
                        'files': 1,
                        'members': ['stray.py'],
                        'children': []}]}}

BOXES = [   {   'id': 'src/api|api|0',
        'path': 'src/api',
        'name': 'api',
        'layer': 'api',
        'files': 6,
        'members': [],
        'x': 0,
        'y': 0,
        'width': 666.6666666666667,
        'height': 620.0,
        'parent': None,
        'depth': 0,
        'opened': True},
    {   'id': 'src/api/entry.py|api|1',
        'path': 'src/api/entry.py',
        'name': 'entry.py',
        'layer': 'api',
        'files': 4,
        'members': ['src/api/entry.py'],
        'x': 3,
        'y': 15,
        'width': 440.44444444444446,
        'height': 602.0,
        'parent': 'src/api|api|0',
        'depth': 1,
        'opened': False},
    {   'id': 'src/api/util.py|api|1',
        'path': 'src/api/util.py',
        'name': 'util.py',
        'layer': 'api',
        'files': 2,
        'members': ['src/api/util.py'],
        'x': 443.44444444444446,
        'y': 15,
        'width': 220.22222222222226,
        'height': 601.9999999999999,
        'parent': 'src/api|api|0',
        'depth': 1,
        'opened': False},
    {   'id': 'src/core|core|0',
        'path': 'src/core',
        'name': 'core',
        'layer': 'core',
        'files': 2,
        'members': [],
        'x': 666.6666666666667,
        'y': 0,
        'width': 333.33333333333326,
        'height': 413.3333333333334,
        'parent': None,
        'depth': 0,
        'opened': True},
    {   'id': 'src/core/base.py|core|1',
        'path': 'src/core/base.py',
        'name': 'base.py',
        'layer': 'core',
        'files': 2,
        'members': ['src/core/base.py'],
        'x': 669.6666666666667,
        'y': 15,
        'width': 327.33333333333326,
        'height': 395.3333333333334,
        'parent': 'src/core|core|0',
        'depth': 1,
        'opened': False},
    {   'id': 'stray.py||0',
        'path': 'stray.py',
        'name': 'stray.py',
        'layer': None,
        'files': 1,
        'members': ['stray.py'],
        'x': 666.6666666666667,
        'y': 413.3333333333334,
        'width': 333.3333333333335,
        'height': 206.66666666666657,
        'parent': None,
        'depth': 0,
        'opened': False}]


def test_the_layout_answers_the_canvas_as_two_numbers():
    assert canvas() == (1000, 620)


def test_rows_land_in_fixed_rectangles_on_a_wide_canvas():
    assert squarify([{'path': 'a', 'files': 4}, {'path': 'b', 'files': 1}], 0, 0, 100, 40) == [   {   'path': 'a',
        'files': 4,
        'x': 0,
        'y': 0,
        'width': 80.0,
        'height': 40.0},
    {   'path': 'b',
        'files': 1,
        'x': 80.0,
        'y': 0,
        'width': 20.0,
        'height': 40.0}]


def test_rows_land_in_fixed_rectangles_on_a_tall_canvas():
    assert squarify([{'path': 'a', 'files': 4}, {'path': 'b', 'files': 1}], 0, 0, 40, 100) == [   {   'path': 'a',
        'files': 4,
        'x': 0,
        'y': 0,
        'width': 40.0,
        'height': 80.0},
    {   'path': 'b',
        'files': 1,
        'x': 0,
        'y': 80.0,
        'width': 40.0,
        'height': 20.0}]


def test_no_item_or_no_extent_places_nothing():
    assert (squarify([], 0, 0, 100, 40),
            squarify([{'path': 'a', 'files': 1}], 0, 0, 0, 40)) == ([], [])


def test_regions_are_fixed_nested_boxes_over_a_tree_built_in_memory():
    assert regions(TREE) == BOXES


def test_the_layout_hands_over_the_numbers_the_drawer_names_a_box_by():
    numbers = getattr(layout, "labels", lambda: None)
    assert numbers() == (40, 46, 11, 13, 25), (
        "the layout hands over no numbers for the drawer's names: no "
        "labels() answers beside canvas(), or the five numbers are not "
        "the ones the drawer names a box by, 40, 46, 11, 13, 25 - so the "
        f"drawer keeps spelling them itself: {numbers()}")


FACES = ("row", "pad", "margin", "node_w", "node_h", "band_l", "band_r")


def narrow_of():
    narrow = stack_geometry().get("narrow")
    assert narrow is not None, ("the layout answers no narrow figure of "
        "the stack beside the wide one: at a phone's width the page draws "
        "the one wide stage scaled down, and no numbers beside it say how "
        "the column is drawn")
    return narrow


def test_the_layout_answers_a_narrow_figure_of_the_stack_beside_the_wide_one():
    narrow = narrow_of()
    missing = list(filter(lambda face: face not in narrow, FACES))
    assert not missing, ("the narrow figure answers fewer faces than the "
        f"wide one: {missing}")


def test_the_narrow_column_fits_a_phone_that_spans_390_units():
    narrow = narrow_of()
    column = (narrow["margin"] + narrow["band_l"] + narrow["node_w"]
              + narrow["band_r"] + narrow["margin"])
    assert column <= 390 * UNIT, (f"the narrow stage is {column} units "
        "wide, past the 390 a phone spans, so the column itself would "
        "scroll sideways")


def test_a_narrow_box_holds_two_rows_where_the_wide_box_holds_one():
    geometry = stack_geometry()
    narrow = narrow_of()
    assert narrow["node_h"] > geometry["node_h"], (f"a narrow box stands "
        f"{narrow['node_h']} units tall against the wide box's "
        f"{geometry['node_h']}, so it holds one row, not the name above "
        "and the four cells below")


def test_the_narrow_boxes_leave_a_gutter_and_keep_to_rows():
    narrow = narrow_of()
    assert min(narrow["band_l"], narrow["row"] - narrow["node_h"]) > 0, (
        "the narrow figure leaves no gutter for the bus the uses arrows "
        "run in, or a narrow box's row is shorter than the box itself, "
        f"so two boxes overlap: {narrow}")


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_layout_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert (one.returncode, one.stdout.splitlines()) == \
        (0, ["no divergence"]), (one.returncode, one.stdout, one.stderr)


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
