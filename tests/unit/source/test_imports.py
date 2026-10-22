import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)

import archituner.source.imports


def snippet_tree(files):
    directory = tempfile.mkdtemp()
    for path, body in files.items():
        full = os.path.join(directory, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(body)
    return directory


def test_package_root_dot_names_from_tree_root():
    naming = archituner.source.imports
    named = (naming.module_of("pkg/x.py", ""),
             naming.module_of("tests/test_x.py", ""))
    assert named == ("pkg.x", "tests.test_x"), named
    by_module = {"pkg.x": "pkg/x.py", "tests.test_x": "tests/test_x.py"}
    assert naming.resolve("pkg.x", by_module, ()) == "pkg/x.py", by_module


def test_declared_subtree_root_still_names_as_before():
    named = archituner.source.imports.module_of("pkg/x.py", "pkg/")
    assert named == "x", named


def test_an_import_from_a_sublayer_is_judged_by_its_ancestors_pair():
    tree = snippet_tree({"src/pkg_a/child/c.py": "import pkg_b.b\n",
                         "src/pkg_a/child2/d.py": "import src.pkg_a.child.c\n",
                         "src/pkg_a/child/e.py": "import gone.mod\n",
                         "src/pkg_b/b.py": "B = 1\n"})
    records = {
        "src/pkg_a/child/c.py": {"path": "src/pkg_a/child/c.py",
                                 "layer": "a.child",
                                 "module": "src.pkg_a.child.c",
                                 "imports": [], "importers": []},
        "src/pkg_a/child2/d.py": {"path": "src/pkg_a/child2/d.py",
                                  "layer": "a.child2",
                                  "module": "src.pkg_a.child2.d",
                                  "imports": [], "importers": []},
        "src/pkg_a/child/e.py": {"path": "src/pkg_a/child/e.py",
                                 "layer": "a.child",
                                 "module": "src.pkg_a.child.e",
                                 "imports": [], "importers": []},
        "src/pkg_b/b.py": {"path": "src/pkg_b/b.py",
                           "layer": "b",
                           "module": "src.pkg_b.b",
                           "imports": [], "importers": []}}
    by_module = {"src.pkg_a.child.c": "src/pkg_a/child/c.py",
                 "src.pkg_a.child2.d": "src/pkg_a/child2/d.py",
                 "src.pkg_a.child.e": "src/pkg_a/child/e.py",
                 "src.pkg_b.b": "src/pkg_b/b.py"}
    edges = archituner.source.imports.resolve_imports(
        tree, records, by_module, ("src",))
    assert set(edges) == {("a", "b"), ("a.child2", "a.child")}, sorted(edges)


TESTS = (test_package_root_dot_names_from_tree_root,
         test_declared_subtree_root_still_names_as_before,
         test_an_import_from_a_sublayer_is_judged_by_its_ancestors_pair)

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
