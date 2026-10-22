import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.summary import stated
from archituner.report.summary import summary_lines
from archituner.report.summary import unclaimed_lines

FLAT_SUMMARY = {
    "contract": "ARCHITECTURE.md", "tree": "repo", "status": "ok",
    "counts": {"convergence": 1, "divergence": 0, "absence": 1, "silence": 0},
    "coverage": {"claimed": 2, "unclaimed": 0},
    "prose_percent": 0.0,
}
HEAD_TEXT = [
    "ARCHITECTURE.md in repo",
    "verdict: ok",
    "counts: ✓ convergence 1  ✗ divergence 0  ○ absence 1  · silence 0",
    "  claimed 2  unclaimed 0",
    "  prose 0.0% of claimed non-blank lines",
]
HEAD_MD = ["# ARCHITECTURE.md in repo"] + HEAD_TEXT[1:]
COLOUR_COUNTS = (
    "counts: "
    "\x1b[38;2;124;192;147m✓\x1b[0m convergence 1  "
    "\x1b[38;2;211;114;105m✗\x1b[0m divergence 0  "
    "\x1b[38;2;247;203;100m○\x1b[0m absence 1  "
    "\x1b[38;2;237;237;237m·\x1b[0m silence 0")
CLAIMED_FILES = [
    {"path": "stray.py", "layer": None},
    {"path": "src_a/x.py", "layer": "a"},
]


def test_the_summary_opens_the_reading_with_the_counts_and_the_tallies():
    assert summary_lines(FLAT_SUMMARY, False, False) == HEAD_TEXT
    assert summary_lines(FLAT_SUMMARY, True, False) == HEAD_MD


def test_colour_wraps_the_counts_glyphs_in_the_page_s_hues():
    assert summary_lines(FLAT_SUMMARY, False, True)[2] == COLOUR_COUNTS


def test_a_narrowed_summary_names_the_question_it_answers():
    document = dict(FLAT_SUMMARY,
                    filters={"layer": ["a", "b"], "min-weight": 2})
    assert summary_lines(document, False, False)[2] \
        == "filters: layer=a,b  min-weight=2"


def test_a_narrowing_axis_is_spelled_by_its_values():
    assert stated("layer", ["a", "b"]) == "layer=a,b"
    assert stated("min-weight", 2) == "min-weight=2"


def test_files_no_layer_claims_are_listed_under_their_own_section():
    document = {"files": CLAIMED_FILES}
    assert unclaimed_lines(document, False) == ["unclaimed files",
                                                "  stray.py"]
    assert unclaimed_lines(document, True) == ["## unclaimed files",
                                               "- stray.py"]


def test_every_file_claimed_draws_no_unclaimed_section():
    assert unclaimed_lines({"files": CLAIMED_FILES[1:]}, False) == []


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
