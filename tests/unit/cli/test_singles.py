import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.cli.singles import FORMATS
from archituner.cli.singles import format_step
from archituner.cli.singles import out_step
from archituner.cli.singles import weight_step


def state():
    return {"narrowing": {}, "fmt": None, "mode": None}


def test_the_formats_carry_the_markdown_spelling():
    assert FORMATS == ("md",)


def test_the_weight_step_carries_the_one_number_fed():
    assert [weight_step("--min-weight", ["3"], state()),
            weight_step("--min-weight", ["4"], {
                "narrowing": {"min-weight": 3}, "fmt": None,
                "mode": None})] == [
        {"narrowing": {"min-weight": 3}, "fmt": None, "mode": None},
        {"narrowing": {"min-weight": 4}, "fmt": None, "mode": None}]


def test_the_weight_step_refuses_anything_but_one_number():
    assert [weight_step("--min-weight", ["x"], state()),
            weight_step("--min-weight", [], state()),
            weight_step("--min-weight", ["3", "4"], state())] == \
        [None, None, None]


def test_the_format_step_carries_the_report_spelling():
    assert format_step("--format", ["md"], state()) == {
        "narrowing": {}, "fmt": "md", "mode": None}


def test_the_format_step_refuses_anything_but_one_known_format():
    assert [format_step("--format", ["tex"], state()),
            format_step("--format", [], state()),
            format_step("--format", ["md", "md"], state())] == \
        [None, None, None]


def test_out_step_sets_its_home_the_default_mode():
    assert out_step("-o", ["out.html"], state()) == {
        "narrowing": {}, "fmt": None, "mode": "render"}


def test_out_step_refuses_when_a_mode_is_already_set():
    assert out_step("-o", ["out.html"], {
        "narrowing": {}, "fmt": None, "mode": "json"}) is None


def test_out_step_refuses_anything_but_one_value():
    assert [out_step("-o", ["a", "b"], state()),
            out_step("-o", [], state())] == [None, None]


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
