import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.terminal import terminal_report
from archituner.vocabulary import Finding

FLAT_DOCUMENT = {
    "contract": "ARCHITECTURE.md", "tree": "repo", "status": "ok",
    "order": ["a", "b"],
    "pairs": [
        {"source": "a", "target": "b", "kind": "allow",
         "state": "convergence", "reason": "", "was": None,
         "imports": [{"file": "src_a/x.py", "module": "src_b.b", "line": 1}],
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
    "counts": {"convergence": 1, "divergence": 0, "absence": 1, "silence": 0},
    "coverage": {"claimed": 2, "unclaimed": 0},
    "prose_percent": 0.0,
    "findings": [],
    "breaches": [],
    "files": [
        {"path": "src_a/x.py", "layer": "a", "defs": 1, "depth": 0,
         "cyclomatic": 1, "cognitive": 0},
        {"path": "src_b/b.py", "layer": "b", "defs": 1, "depth": 0,
         "cyclomatic": 1, "cognitive": 0},
    ],
    "change": None,
    "schema": 1,
    "crossings": [
        {"file": "src_a/x.py", "line": 1, "module": "src_b.b",
         "source": "a", "target": "b", "kind": "allow",
         "state": "convergence", "code": "from src_b.b import b"},
    ],
}
FLAT_TEXT = "\n".join([
    "ARCHITECTURE.md in repo",
    "verdict: ok",
    "counts: ✓ convergence 1  ✗ divergence 0  ○ absence 1  · silence 0",
    "  claimed 2  unclaimed 0",
    "  prose 0.0% of claimed non-blank lines",
    "findings",
    "  no findings",
    "limit breaches",
    "  no limit breaches",
    "matrix: rows import columns; layers in dependency order",
    "     a  b  ",
    "  a     ✓  ",
    "  b  ○     ",
    "files: worst first - cognitive, then cyclomatic, then path",
    "  src_a/x.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
    "  src_b/b.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
    "prose",
    "  no prose",
])
FLAT_MD_TEXT = "\n".join([
    "# ARCHITECTURE.md in repo",
    "verdict: ok",
    "counts: ✓ convergence 1  ✗ divergence 0  ○ absence 1  · silence 0",
    "  claimed 2  unclaimed 0",
    "  prose 0.0% of claimed non-blank lines",
    "## findings",
    "- no findings",
    "## limit breaches",
    "- no limit breaches",
    "## matrix: rows import columns; layers in dependency order",
    "",
    "|  | a | b |",
    "| --- | --- | --- |",
    "| a |   | ✓ |",
    "| b | ○ |   |",
    "## files: worst first - cognitive, then cyclomatic, then path",
    "- src_a/x.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
    "- src_b/b.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
    "## prose",
    "- no prose",
])


def test_a_flat_contract_renders_today_s_bytes():
    assert terminal_report(FLAT_DOCUMENT, None, False) == FLAT_TEXT
    assert terminal_report(FLAT_DOCUMENT, "md", False) == FLAT_MD_TEXT


def test_a_stored_baseline_adds_its_comparison_line():
    document = dict(FLAT_DOCUMENT,
                    change={"counts": {"improved": 1, "regressed": 0,
                                       "unchanged": 2}})
    assert terminal_report(document, None, False) == (
        FLAT_TEXT + "\n  vs baseline: improved 1  regressed 0  unchanged 2")
    assert terminal_report(document, "md", False) == (
        FLAT_MD_TEXT + "\n  vs baseline: improved 1  regressed 0  unchanged 2")


BREACH = [{"file": "src_b/b.py", "number": "cognitive", "value": 68,
           "limit": 50, "reason": None}]


def test_the_breaches_section_sits_directly_after_the_findings():
    lines = terminal_report(dict(FLAT_DOCUMENT, breaches=BREACH),
                            None, False).splitlines()
    assert "limit breaches" in lines, lines
    assert lines[lines.index("limit breaches") - 1] == "  no findings", lines
    assert lines[lines.index("limit breaches") + 1] == \
        "  src_b/b.py: cognitive 68 over 50", lines
    md_lines = terminal_report(dict(FLAT_DOCUMENT, breaches=BREACH),
                               "md", False).splitlines()
    assert "## limit breaches" in md_lines, md_lines
    assert md_lines[md_lines.index("## limit breaches") - 1] == "- no findings"
    assert md_lines[md_lines.index("## limit breaches") + 1] == \
        "- src_b/b.py: cognitive 68 over 50"


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
