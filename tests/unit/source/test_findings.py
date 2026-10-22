import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)

from archituner.source.findings import sublayer_findings


TREE_GLOB = "src_a/" + "**"
ESCAPE_GLOB = "src_x/" + "**"
OUTSIDE_GLOB = "src_q/" + "**"

LAYERS = {"a": [TREE_GLOB],
          "b": ["src_b/" + "**"],
          "a.child": [ESCAPE_GLOB, "src_a/child/" + "**"]}
FILES = {"src_a/flat.py": {"layer": "a"},
         "src_b/flat.py": {"layer": "b"},
         "src_x/outside.py": {"layer": "a.child"}}

CHAIN = {"p": [TREE_GLOB],
         "p.mid": [OUTSIDE_GLOB],
         "p.mid.leaf": ["src_a/deep/" + "**"]}
CHAIN_FILES = {"src_q/ahead.py": {"layer": "p.mid"},
               "src_q/zfile.py": {"layer": "p.mid"}}


def rows(findings):
    return [(f.text, f.produced_by) for f, _path in findings]


def test_a_flat_file_under_a_parent_with_children_is_a_hole():
    findings = sublayer_findings(FILES, LAYERS)
    hole = (f"src_a/flat.py is claimed by a's {TREE_GLOB} and no child "
            f"claims it", f"layer a, glob {TREE_GLOB}")
    assert rows(findings)[0] == hole, rows(findings)


def test_a_child_file_outside_its_parent_is_an_escape():
    findings = sublayer_findings(FILES, LAYERS)
    escape = (f"src_x/outside.py is claimed by a.child's {ESCAPE_GLOB} "
              f"but no glob of its parent a claims it",
              f"layer a.child, glob {ESCAPE_GLOB}")
    assert rows(findings)[1] == escape, rows(findings)


def test_findings_come_in_walked_path_order_escape_before_hole():
    findings = sublayer_findings(CHAIN_FILES, CHAIN)
    expected = [
        (f"src_q/ahead.py is claimed by p.mid's {OUTSIDE_GLOB} but no glob "
         f"of its parent p claims it", f"layer p.mid, glob {OUTSIDE_GLOB}"),
        (f"src_q/ahead.py is claimed by p.mid's {OUTSIDE_GLOB} and no child "
         f"claims it", f"layer p.mid, glob {OUTSIDE_GLOB}"),
        (f"src_q/zfile.py is claimed by p.mid's {OUTSIDE_GLOB} but no glob "
         f"of its parent p claims it", f"layer p.mid, glob {OUTSIDE_GLOB}"),
        (f"src_q/zfile.py is claimed by p.mid's {OUTSIDE_GLOB} and no child "
         f"claims it", f"layer p.mid, glob {OUTSIDE_GLOB}")]
    assert rows(findings) == expected, rows(findings)


def test_a_layer_with_no_children_and_no_parent_earns_nothing():
    findings = sublayer_findings({"src_b/flat.py": {"layer": "b"}}, LAYERS)
    assert findings == [], rows(findings)


def test_no_finding_holds_a_probe_path():
    findings = sublayer_findings(FILES, LAYERS) \
        + sublayer_findings(CHAIN_FILES, CHAIN)
    assert all("probe" not in f.text and "probe" not in f.produced_by
               for f, _path in findings), rows(findings)


TESTS = (test_a_flat_file_under_a_parent_with_children_is_a_hole,
         test_a_child_file_outside_its_parent_is_an_escape,
         test_findings_come_in_walked_path_order_escape_before_hole,
         test_a_layer_with_no_children_and_no_parent_earns_nothing,
         test_no_finding_holds_a_probe_path)

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
