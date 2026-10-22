import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)

import archituner.source


def test_a_child_claim_beats_its_parent_s_glob():
    lmap = archituner.source.LayerMap(
        {"app": ["src/app/" + "**"],
         "app.ui": ["src/app/ui/" + "**"],
         "app.core": ["src/app/core/" + "**"]})
    assert lmap.layer_of("src/app/ui/x.py") == "app.ui", \
        lmap.layer_of("src/app/ui/x.py")
    assert lmap.layer_of("src/app/core/m.py") == "app.core", \
        lmap.layer_of("src/app/core/m.py")
    assert lmap.layer_of("src/app/__init__.py") == "app", \
        lmap.layer_of("src/app/__init__.py")


def test_a_deeper_child_still_claims_its_own():
    lmap = archituner.source.LayerMap(
        {"a": ["src/a/" + "**"],
         "a.b": ["src/a/b/" + "**"],
         "a.b.c": ["src/a/b/c/" + "**"]})
    assert lmap.layer_of("src/a/b/c/x.py") == "a.b.c", \
        lmap.layer_of("src/a/b/c/x.py")


def test_equal_depths_keep_declaration_order():
    lmap = archituner.source.LayerMap(
        {"one": ["src/tie/" + "**"], "two": ["src/tie/" + "**"]})
    assert lmap.layer_of("src/tie/x.py") == "one", \
        lmap.layer_of("src/tie/x.py")


TESTS = (test_a_child_claim_beats_its_parent_s_glob,
         test_a_deeper_child_still_claims_its_own,
         test_equal_depths_keep_declaration_order)

failed = []
for test in TESTS:
    try:
        test()
        print(f"PASS  {test.__name__}")
    except Exception as e:
        print(f"FAIL  {test.__name__}  {type(e).__name__}: {e}")
        failed.append(test.__name__)
print(f"{len(failed)} failed" if failed else "all green")
raise SystemExit(bool(failed))
