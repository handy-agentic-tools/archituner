import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.breaches import breaches_lines

BREACHES = [
    {"file": "model_weight.py", "number": "size", "value": 27,
     "limit": 21, "reason": None},
    {"file": "core_bad.py", "number": "cyclomatic", "value": 34,
     "limit": 30, "reason": None},
    {"file": "core_weight.py", "number": "size", "value": 17,
     "limit": 12, "reason": "gates stay thin"},
]
SORTED_TEXT = [
    "limit breaches",
    "  core_bad.py: cyclomatic 34 over 30",
    "  core_weight.py: size 17 over 12 - gates stay thin",
    "  model_weight.py: size 27 over 21",
]
SORTED_MD = [
    "## limit breaches",
    "- core_bad.py: cyclomatic 34 over 30",
    "- core_weight.py: size 17 over 12 - gates stay thin",
    "- model_weight.py: size 27 over 21",
]


def test_breaches_are_listed_sorted_by_file_then_number():
    assert breaches_lines({"breaches": BREACHES}, False) == SORTED_TEXT
    assert breaches_lines({"breaches": BREACHES}, True) == SORTED_MD


def test_the_reason_is_spelled_where_an_override_set_the_limit():
    breaches = [
        {"file": "b_two.py", "number": "size", "value": 17, "limit": 12,
         "reason": "gates stay thin"},
        {"file": "a_one.py", "number": "size", "value": 27, "limit": 21,
         "reason": None},
    ]
    assert breaches_lines({"breaches": breaches}, False) == [
        "limit breaches",
        "  a_one.py: size 27 over 21",
        "  b_two.py: size 17 over 12 - gates stay thin",
    ]
    assert breaches_lines({"breaches": breaches}, True) == [
        "## limit breaches",
        "- a_one.py: size 27 over 21",
        "- b_two.py: size 17 over 12 - gates stay thin",
    ]


def test_a_clean_reading_names_no_limit_breaches():
    assert breaches_lines({"breaches": []}, False) == ["limit breaches",
                                                       "  no limit breaches"]
    assert breaches_lines({"breaches": []}, True) == ["## limit breaches",
                                                      "- no limit breaches"]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
