import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.records import files_lines
from archituner.report.records import prose_lines

RECORDS = [
    {"path": "b_two.py", "layer": "core", "defs": 1, "depth": 0,
     "cyclomatic": 1, "cognitive": 12},
    {"path": "a_one.py", "layer": "api", "defs": 2, "depth": 1,
     "cyclomatic": 3, "cognitive": 9, "prose_count": 2, "prose_percent": 4.0,
     "prose": [{"line": 3, "text": "the comment this rule keeps out"},
               {"line": 7, "text": "another"}]},
    {"path": "c_three.py", "layer": None, "defs": 1, "depth": 0,
     "cyclomatic": 1, "cognitive": 0},
]
FILES_TEXT = [
    "files: worst first - cognitive, then cyclomatic, then path",
    "  b_two.py  defs 1  depth 0  cyclomatic 1  cognitive 12",
    "  a_one.py  defs 2  depth 1  cyclomatic 3  cognitive 9  prose 2 (4.0%)",
    "  c_three.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
]
FILES_MD = [
    "## files: worst first - cognitive, then cyclomatic, then path",
    "- b_two.py  defs 1  depth 0  cyclomatic 1  cognitive 12",
    "- a_one.py  defs 2  depth 1  cyclomatic 3  cognitive 9  prose 2 (4.0%)",
    "- c_three.py  defs 1  depth 0  cyclomatic 1  cognitive 0",
]


def test_files_render_worst_first_with_their_own_numbers():
    assert files_lines({"files": RECORDS}, False) == FILES_TEXT
    assert files_lines({"files": RECORDS}, True) == FILES_MD


def test_prose_entries_are_listed_at_file_line_in_the_records_own_order():
    assert prose_lines({"files": RECORDS}, False) == [
        "prose",
        "  a_one.py:3  the comment this rule keeps out",
        "  a_one.py:7  another",
    ]
    assert prose_lines({"files": RECORDS}, True) == [
        "## prose",
        "- a_one.py:3  the comment this rule keeps out",
        "- a_one.py:7  another",
    ]


def test_no_prose_says_so():
    assert prose_lines({"files": [RECORDS[0]]}, False) == ["prose",
                                                           "  no prose"]
    assert prose_lines({"files": [RECORDS[0]]}, True) == ["## prose",
                                                          "- no prose"]


LAW_RECORDS = [
    {"path": "big.py", "layer": "core", "size": 2400, "defs": 1, "depth": 1,
     "cyclomatic": 1, "cognitive": 12,
     "limits": {"size": {"limit": 8000, "share": 0.3},
                "defs": {"limit": None, "share": None},
                "depth": {"limit": 0, "share": None},
                "cognitive": {"limit": 50, "share": 0.24}}},
    {"path": "plain.py", "layer": None, "size": 512, "defs": 1, "depth": 0,
     "cyclomatic": 1, "cognitive": 0},
]
LAW_TEXT = [
    "files: worst first - cognitive, then cyclomatic, then path",
    "  big.py  size 2400/8000 (0.3)  defs 1/none  depth 1/0"
    "  cyclomatic 1  cognitive 12/50 (0.24)",
    "  plain.py  size 512  defs 1  depth 0  cyclomatic 1  cognitive 0",
]
LAW_MD = [
    "## files: worst first - cognitive, then cyclomatic, then path",
    "- big.py  size 2400/8000 (0.3)  defs 1/none  depth 1/0"
    "  cyclomatic 1  cognitive 12/50 (0.24)",
    "- plain.py  size 512  defs 1  depth 0  cyclomatic 1  cognitive 0",
]


def test_a_governed_number_prints_its_law_beside_its_value():
    assert files_lines({"files": LAW_RECORDS}, False) == LAW_TEXT
    assert files_lines({"files": LAW_RECORDS}, True) == LAW_MD


def test_size_prints_first_where_the_record_carries_it():
    records = [{"path": "sized.py", "layer": "core", "size": 512, "defs": 1,
                "depth": 0, "cyclomatic": 1, "cognitive": 0}]
    assert files_lines({"files": records}, False) == [
        "files: worst first - cognitive, then cyclomatic, then path",
        "  sized.py  size 512  defs 1  depth 0  cyclomatic 1  cognitive 0",
    ]
    assert files_lines({"files": records}, True) == [
        "## files: worst first - cognitive, then cyclomatic, then path",
        "- sized.py  size 512  defs 1  depth 0  cyclomatic 1  cognitive 0",
    ]


GOVERNED_PROSE = [
    {"path": "shared.py", "layer": "api", "defs": 1, "depth": 0,
     "cyclomatic": 3, "cognitive": 9, "prose_count": 3, "prose_percent": 6.0,
     "prose": [{"line": 3, "text": "the comment this rule keeps out"}],
     "limits": {"prose_count": {"limit": 50, "share": 0.06}}},
    {"path": "zero.py", "layer": "api", "defs": 1, "depth": 0,
     "cyclomatic": 3, "cognitive": 9, "prose_count": 3, "prose_percent": 12.5,
     "prose": [{"line": 3, "text": "the comment this rule keeps out"}],
     "limits": {"prose_count": {"limit": 0, "share": None}}},
]


def test_governed_prose_prints_its_law_beside_its_percent():
    assert files_lines({"files": GOVERNED_PROSE}, False) == [
        "files: worst first - cognitive, then cyclomatic, then path",
        "  shared.py  defs 1  depth 0  cyclomatic 3  cognitive 9"
        "  prose 3/50 (0.06) (6.0%)",
        "  zero.py  defs 1  depth 0  cyclomatic 3  cognitive 9"
        "  prose 3/0 (12.5%)",
    ]
    assert files_lines({"files": GOVERNED_PROSE}, True) == [
        "## files: worst first - cognitive, then cyclomatic, then path",
        "- shared.py  defs 1  depth 0  cyclomatic 3  cognitive 9"
        "  prose 3/50 (0.06) (6.0%)",
        "- zero.py  defs 1  depth 0  cyclomatic 3  cognitive 9"
        "  prose 3/0 (12.5%)",
    ]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
