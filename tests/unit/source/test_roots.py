import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)

from archituner.source.roots import import_root

LAYERS = {"pkg": ["pkg/" + "**"], "tests": ["tests/" + "**"]}


def test_package_root_dot_names_from_tree_root():
    root, retry, packages = import_root(LAYERS, ".")
    assert (root, retry, packages) == ("", (), ()), (root, retry, packages)


def test_declared_subtree_root_still_names_as_before():
    root, retry, packages = import_root(LAYERS, "pkg")
    assert (root, retry, packages) == ("pkg/", (), ()), (root, retry, packages)


TESTS = (test_package_root_dot_names_from_tree_root,
         test_declared_subtree_root_still_names_as_before)

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
