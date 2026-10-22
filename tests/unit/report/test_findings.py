import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.findings import divergences_lines
from archituner.report.findings import findings_lines
from archituner.vocabulary import Finding

DIV_DOCUMENT = {
    "pairs": [
        {"source": "core", "target": "api", "kind": "forbid",
         "state": "divergence",
         "reason": "a stage never reaches back to the thing that constructed it",
         "was": None, "imports": [],
         "remedy": Finding(text="drop the import of api_entry from core_bad.py",
                           produced_by="core_bad.py:1")},
    ],
    "crossings": [
        {"file": "core_b.py", "line": 1, "module": "api_entry",
         "source": "core", "target": "api", "kind": "forbid",
         "state": "divergence", "code": "import api_entry"},
        {"file": "core_a.py", "line": 2, "module": "api_exit",
         "source": "core", "target": "api", "kind": "forbid",
         "state": "divergence", "code": "import api_exit"},
    ],
}
DIV_TEXT = [
    "divergences",
    "  divergence: core -> api",
    "    core_a.py:2 imports api_exit",
    "    core_b.py:1 imports api_entry",
    "    contract: a stage never reaches back to the thing that constructed it",
    "    remedy: drop the import of api_entry from core_bad.py",
]


def test_an_empty_findings_section_says_so():
    assert findings_lines({"findings": []}, False) == ["findings",
                                                       "  no findings"]
    assert findings_lines({"findings": []}, True) == ["## findings",
                                                      "- no findings"]


def test_a_finding_is_listed_by_its_text():
    finding = Finding(text="no Boundaries line reaches model -> core",
                      produced_by="the pair table")
    assert findings_lines({"findings": [finding]}, False) == [
        "findings", "  no Boundaries line reaches model -> core"]
    assert findings_lines({"findings": [finding]}, True) == [
        "## findings", "- no Boundaries line reaches model -> core"]


def test_a_divergence_lists_its_witnesses_sorted_beside_reason_and_remedy():
    assert divergences_lines(DIV_DOCUMENT, False) == DIV_TEXT
    assert divergences_lines(DIV_DOCUMENT, True) \
        == ["## " + DIV_TEXT[0]] + DIV_TEXT[1:]


def test_no_divergence_draws_no_section():
    assert divergences_lines({"pairs": [], "crossings": []}, False) == []


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
