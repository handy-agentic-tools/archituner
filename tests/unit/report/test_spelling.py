import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.spelling import coloured_glyph
from archituner.report.spelling import item_line
from archituner.report.spelling import section_line
from archituner.vocabulary import STATES


def test_a_glyph_off_colour_is_the_page_s_own_mark():
    assert [coloured_glyph(state, False) for state in STATES] \
        == ["✓", "✗", "○", "·"]


def test_a_glyph_on_colour_wraps_the_same_mark_in_the_page_s_hue():
    assert [coloured_glyph(state, True) for state in STATES] == [
        "\x1b[38;2;124;192;147m✓\x1b[0m",
        "\x1b[38;2;211;114;105m✗\x1b[0m",
        "\x1b[38;2;247;203;100m○\x1b[0m",
        "\x1b[38;2;237;237;237m·\x1b[0m",
    ]


def test_a_section_line_heads_itself_for_the_terminal_and_hashes_for_md():
    assert [section_line("prose", md) for md in (False, True)] \
        == ["prose", "## prose"]
    title = "matrix: rows import columns; layers in dependency order"
    assert section_line(title, True) == "## " + title


def test_an_item_line_bullets_for_md_and_indents_for_the_terminal():
    assert [item_line("no prose", md) for md in (False, True)] \
        == ["  no prose", "- no prose"]
    assert [item_line("stray.py", md) for md in (False, True)] \
        == ["  stray.py", "- stray.py"]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
