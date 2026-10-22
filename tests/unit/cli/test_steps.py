import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.cli.steps import LONELY
from archituner.cli.steps import MODES
from archituner.cli.steps import VALUED
from archituner.cli.steps import mode_step
from archituner.cli.steps import step


def state():
    return {"narrowing": {}, "fmt": None, "mode": None}


def test_the_tables_name_the_flags_and_what_each_takes():
    assert MODES == {"--check": "check", "--baseline": "baseline",
                     "--json": "json", "--report": "report"}
    assert (sorted(LONELY), sorted(VALUED)) == \
        (["--baseline", "--check", "--json", "--report"],
         ["--format", "--min-weight", "-o"])


def test_a_mode_step_sets_its_mode():
    assert [mode_step("--check", [], state()),
            mode_step("--baseline", [], state()),
            mode_step("--json", [], state()),
            mode_step("--report", [], state())] == [
        {"narrowing": {}, "fmt": None, "mode": "check"},
        {"narrowing": {}, "fmt": None, "mode": "baseline"},
        {"narrowing": {}, "fmt": None, "mode": "json"},
        {"narrowing": {}, "fmt": None, "mode": "report"}]


def test_a_second_mode_refuses():
    assert mode_step("--json", [], {"narrowing": {}, "fmt": None,
                                    "mode": "check"}) is None


def test_a_mode_flag_takes_no_value():
    assert mode_step("--check", ["stray"], state()) is None


def test_step_routes_each_flag_to_its_family():
    assert [step("--check", [], state()),
            step("--file", ["a", "b"], state()),
            step("--min-weight", ["3"], state())] == [
        {"narrowing": {}, "fmt": None, "mode": "check"},
        {"narrowing": {"file": ["a", "b"]}, "fmt": None, "mode": None},
        {"narrowing": {"min-weight": 3}, "fmt": None, "mode": None}]


def test_step_routes_the_report_spelling_and_the_render_output():
    assert [step("--format", ["md"], state()),
            step("-o", ["out.html"], state())] == [
        {"narrowing": {}, "fmt": "md", "mode": None},
        {"narrowing": {}, "fmt": None, "mode": "render"}]


def test_step_refuses_an_unknown_flag():
    assert step("--bogus", [], state()) is None


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
