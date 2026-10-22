import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.cli.groups import AXES
from archituner.cli.groups import axis_step
from archituner.cli.groups import groups_of


def state():
    return {"narrowing": {}, "fmt": None, "mode": None}


def test_the_axes_name_the_three_narrowing_flags():
    assert AXES == {"--state": "state", "--layer": "layer",
                    "--file": "file"}


def test_an_axis_step_joins_every_value_in_order():
    assert [axis_step("--file", ["a", "b"], state()),
            axis_step("--layer", ["api", "core"], state()),
            axis_step("--state", ["divergence", "convergence"],
                      state())] == [
        {"narrowing": {"file": ["a", "b"]}, "fmt": None, "mode": None},
        {"narrowing": {"layer": ["api", "core"]}, "fmt": None, "mode": None},
        {"narrowing": {"state": ["divergence", "convergence"]},
         "fmt": None, "mode": None}]


def test_an_axis_step_accumulates_what_earlier_visits_joined():
    began = {"narrowing": {"file": ["a"]}, "fmt": None, "mode": None}
    assert axis_step("--file", ["b"], began) == {
        "narrowing": {"file": ["a", "b"]}, "fmt": None, "mode": None}


def test_an_axis_naming_no_value_refuses():
    assert axis_step("--file", [], state()) is None


def test_groups_of_opens_a_group_at_every_dash_token():
    assert [groups_of(["--file", "a", "b", "--check"]),
            groups_of(["--min-weight", "3", "-o", "out.html"])] == [
        [("--file", ["a", "b"]), ("--check", [])],
        [("--min-weight", ["3"]), ("-o", ["out.html"])]]


def test_a_stray_word_opens_a_group_with_no_flag():
    assert [groups_of(["stray", "--check"]),
            groups_of(["extra.md", "--file", "a"])] == [
        [(None, ["stray"]), ("--check", [])],
        [(None, ["extra.md"]), ("--file", ["a"])]]


def test_an_empty_tail_holds_no_group_and_a_lone_flag_no_value():
    assert [groups_of([]), groups_of(["--file"])] == [[], [("--file", [])]]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
