import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.document import crossings_data
from archituner.report.document import crossings_document
from archituner.report.document import machine_document
from archituner.report.document import outcome_document
from archituner.vocabulary import Finding

SUB_DATA = {
    "contract": "ARCHITECTURE.md", "tree": "repo", "status": "ok",
    "order": ["a.child", "a.child2", "a", "b"],
    "pairs": [
        {"source": "a.child", "target": "a.child2", "kind": "allow",
         "state": "absence", "reason": "", "was": None, "imports": [],
         "remedy": Finding(
             text="nothing exercises a.child -> a.child2, and this run "
                  "cannot tell an unwritten crossing from a stale "
                  "permission: both layers hold files and no stored "
                  "baseline reads this pair, so what would separate the "
                  "two is an earlier reading in which the pair was realised",
             produced_by="a.child holds 1 file(s), a.child2 holds 1 "
                         "file(s); no stored baseline reads the pair")},
        {"source": "a.child2", "target": "a.child", "kind": "allow",
         "state": "convergence", "reason": "", "was": None,
         "imports": [{"file": "src/pkg_a/child2/d.py",
                      "module": "src.pkg_a.child.c", "line": 1}],
         "remedy": None},
        {"source": "a", "target": "b", "kind": "allow",
         "state": "convergence", "reason": "", "was": None,
         "imports": [{"file": "src/pkg_a/child/c.py",
                      "module": "pkg_b.b", "line": 1}],
         "remedy": None},
        {"source": "b", "target": "a", "kind": "allow",
         "state": "absence", "reason": "", "was": None, "imports": [],
         "remedy": Finding(
             text="nothing exercises b -> a, and this run cannot tell an "
                  "unwritten crossing from a stale permission: both layers "
                  "hold files and no stored baseline reads this pair, so "
                  "what would separate the two is an earlier reading in "
                  "which the pair was realised",
             produced_by="b holds 1 file(s), a holds 1 file(s); no stored "
                         "baseline reads the pair")},
    ],
    "counts": {"convergence": 2, "divergence": 0, "absence": 2, "silence": 0},
    "coverage": {"claimed": 4, "unclaimed": 0},
    "prose_percent": 0.0,
    "findings": [],
    "files": [
        {"path": "src/pkg_a/a.py", "layer": "a", "defs": 1, "depth": 0,
         "cyclomatic": 1, "cognitive": 0},
        {"path": "src/pkg_a/child/c.py", "layer": "a.child", "defs": 1,
         "depth": 0, "cyclomatic": 1, "cognitive": 0},
        {"path": "src/pkg_a/child2/d.py", "layer": "a.child2", "defs": 1,
         "depth": 0, "cyclomatic": 1, "cognitive": 0},
        {"path": "src/pkg_b/b.py", "layer": "b", "defs": 1, "depth": 0,
         "cyclomatic": 1, "cognitive": 0},
    ],
    "change": None,
}
SUB_QUOTED = {("src/pkg_a/child/c.py", 1): "from pkg_b.b import b",
              ("src/pkg_a/child2/d.py", 1): "from src.pkg_a.child.c import c"}
EXPECTED_CROSSINGS = [
    {"file": "src/pkg_a/child/c.py", "line": 1, "module": "pkg_b.b",
     "source": "a", "target": "b", "kind": "allow", "state": "convergence",
     "code": "from pkg_b.b import b"},
    {"file": "src/pkg_a/child2/d.py", "line": 1,
     "module": "src.pkg_a.child.c", "source": "a.child2",
     "target": "a.child", "kind": "allow", "state": "convergence",
     "code": "from src.pkg_a.child.c import c"},
]
SUB_NARROWED = {"pairs": [SUB_DATA["pairs"][1], SUB_DATA["pairs"][2]],
                "files": SUB_DATA["files"], "narrowing": {}}
FED_PATH = {"file": ["src/pkg_a/child/c.py"]}
FED_PATH_NARROWED = {"pairs": [SUB_DATA["pairs"][2]],
                     "files": [SUB_DATA["files"][1]], "narrowing": FED_PATH}


def test_the_document_stamps_its_schema_and_keeps_the_reading():
    document = crossings_data(SUB_DATA, SUB_NARROWED, SUB_QUOTED)
    assert (document["schema"], document["pairs"],
            document["files"]) == (1, SUB_DATA["pairs"], SUB_DATA["files"])


def test_the_crossings_are_one_flat_sorted_list_of_every_realised_witness():
    assert crossings_data(SUB_DATA, SUB_NARROWED, SUB_QUOTED)["crossings"] \
        == EXPECTED_CROSSINGS


def test_an_unscoped_question_adds_no_filters_key():
    assert "filters" not in crossings_data(SUB_DATA, SUB_NARROWED, SUB_QUOTED)


def test_a_fed_path_names_its_narrowing_and_narrows_the_answers():
    document = crossings_data(SUB_DATA, FED_PATH_NARROWED, SUB_QUOTED)
    assert (document["filters"], document["files"],
            document["crossings"]) == (FED_PATH,
                                       [SUB_DATA["files"][1]],
                                       [EXPECTED_CROSSINGS[0]])


def test_an_outcome_is_one_sorted_stable_json_object():
    assert outcome_document("refused", "no front matter") == (
        '{\n  "reason": "no front matter",\n  "schema": 1,\n'
        '  "status": "refused"\n}')


def test_the_document_s_bytes_parse_back_to_its_plain_values():
    document = crossings_data(SUB_DATA, SUB_NARROWED, SUB_QUOTED)
    parsed = json.loads(crossings_document(SUB_DATA, SUB_NARROWED, SUB_QUOTED))
    assert (parsed["crossings"], parsed["schema"],
            document["schema"]) == (document["crossings"], 1, 1)


READING = {"order": ["api", "core"],
           "pairs": [{"source": "api", "target": "core", "kind": "allow",
                      "state": "convergence", "reason": "", "was": None,
                      "imports": [], "source_files": 1, "target_files": 1}],
           "breaches": [], "files": [],
           "coverage": {"claimed": 1, "unclaimed": 0}}
BREACH = {"file": "api_entry.py", "number": "defs", "value": 9, "limit": 8,
          "reason": None}


def narrowed(diverged, breaches):
    return {"pairs": READING["pairs"], "breaches": breaches,
            "files": READING["files"], "witnesses": [], "diverged": diverged,
            "narrowing": {}}


def answered(document, status, reason, breaches):
    assert (document["status"], document["reason"], document["breaches"],
            document["order"], document["coverage"], "regions" in document,
            "stack" in document) == (status, reason, breaches,
                                     READING["order"], READING["coverage"],
                                     False, False)


def test_the_machine_document_answers_each_failing_class_of_its_narrowing():
    answered(machine_document(READING, narrowed(False, [])), "ok", None, [])
    answered(machine_document(READING, narrowed(True, [])), "divergent",
             "divergence", [])
    answered(machine_document(READING, narrowed(False, [BREACH])),
             "divergent", "limit breach", [BREACH])
    answered(machine_document(READING, narrowed(True, [BREACH])),
             "divergent", "divergence and limit breach", [BREACH])


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
