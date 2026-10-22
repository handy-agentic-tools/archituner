import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.matrix import matrix_lines

SUB_DOCUMENT = {
    "order": ["a.child", "a.child2", "a", "b"],
    "pairs": [
        {"source": "a.child", "target": "a.child2", "state": "absence"},
        {"source": "a.child2", "target": "a.child", "state": "convergence"},
        {"source": "a", "target": "b", "state": "convergence"},
        {"source": "b", "target": "a", "state": "absence"},
    ],
}
TEXT_ROWS = [
    "matrix: rows import columns; layers in dependency order",
    "            a.child   a.child2  a         b         ",
    "  a.child             ○                             ",
    "  a.child2  ✓                                       ",
    "  a                                       ✓         ",
    "  b                             ○                   ",
]
MD_ROWS = [
    "## matrix: rows import columns; layers in dependency order",
    "",
    "|  | a.child | a.child2 | a | b |",
    "| --- | --- | --- | --- | --- |",
    "| a.child |   | ○ |   |   |",
    "| a.child2 | ✓ |   |   |   |",
    "| a |   |   |   | ✓ |",
    "| b |   |   | ○ |   |",
]


def test_a_sublayer_contract_renders_as_text_without_a_missing_pair():
    assert matrix_lines(SUB_DOCUMENT, False, False) == TEXT_ROWS


def test_a_sublayer_contract_renders_as_md_without_a_missing_pair():
    rows = matrix_lines(SUB_DOCUMENT, True, False)
    assert rows[:4] == MD_ROWS[:4]
    assert [row.split("|")[1].strip() for row in rows[4:]] \
        == SUB_DOCUMENT["order"]


def test_an_undecided_parent_and_child_cell_renders_the_diagonal_s_blank():
    rows = matrix_lines(SUB_DOCUMENT, True, False)
    assert rows[4] == "| a.child |   | ○ |   |   |"
    assert rows[6] == "| a |   |   |   | ✓ |"


def test_a_decided_pair_still_shows_its_glyph():
    rows = matrix_lines(SUB_DOCUMENT, True, False)
    assert rows[5] == "| a.child2 | ✓ |   |   |   |"
    assert rows[7] == "| b |   |   | ○ |   |"


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
