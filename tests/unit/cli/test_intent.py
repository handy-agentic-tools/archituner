import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.cli.intent import read


def test_a_bare_contract_checks():
    assert read(["archituner", "c.md"]) == ("check", {}, None)


def test_each_mode_flag_names_its_mode():
    assert [read(["archituner", "c.md", "--check"]),
            read(["archituner", "c.md", "--baseline"]),
            read(["archituner", "c.md", "--json"]),
            read(["archituner", "c.md", "--report"])] == [
        ("check", {}, None), ("baseline", {}, None),
        ("json", {}, None), ("report", {}, None)]


def test_the_narrowing_flags_join_every_value_in_order():
    assert [read(["archituner", "c.md", "--file", "a", "b"]),
            read(["archituner", "c.md", "--layer", "api", "core"]),
            read(["archituner", "c.md", "--state",
                  "divergence", "convergence"])] == [
        ("check", {"file": ["a", "b"]}, None),
        ("check", {"layer": ["api", "core"]}, None),
        ("check", {"state": ["divergence", "convergence"]}, None)]


def test_repeated_flags_accumulate():
    assert read(["archituner", "c.md", "--file", "a", "--file", "b"]) == \
        ("check", {"file": ["a", "b"]}, None)


def test_the_axes_compose_beside_a_mode_and_a_weight():
    assert read(["archituner", "c.md", "--check", "--file", "a", "b",
                 "--layer", "x", "--min-weight", "2"]) == \
        ("check", {"file": ["a", "b"], "layer": ["x"],
                   "min-weight": 2}, None)


def test_the_last_weight_fed_wins():
    assert read(["archituner", "c.md", "--min-weight", "3",
                 "--min-weight", "4"]) == \
        ("check", {"min-weight": 4}, None)


def test_the_format_homes_in_the_report_wherever_it_is_fed():
    assert [read(["archituner", "c.md", "--report", "--format", "md"]),
            read(["archituner", "c.md", "--format", "md", "--report"]),
            read(["archituner", "c.md", "--format", "md"]),
            read(["archituner", "c.md", "--report", "--format", "tex"])] == [
        ("report", {}, "md"), ("report", {}, "md"), None, None]


def test_out_homes_in_render_beside_no_other_mode():
    assert [read(["archituner", "c.md", "-o", "out.html"]),
            read(["archituner", "c.md", "--check", "-o", "out.html"]),
            read(["archituner", "c.md", "-o", "out.html", "--check"])] == [
        ("render", {}, None), None, None]


def test_two_mode_flags_refuse():
    assert [read(["archituner", "c.md", "--check", "--json"]),
            read(["archituner", "c.md", "--report", "--baseline"])] == \
        [None, None]


def test_a_stray_token_refuses():
    assert [read(["archituner", "c.md", "--check", "stray"]),
            read(["archituner", "c.md", "extra.md"]),
            read(["archituner", "c.md", "--bogus"]),
            read(["archituner", "c.md", "--min-weight", "3", "4"]),
            read(["archituner", "c.md", "-o", "a", "b"]),
            read(["archituner", "c.md", "-o", "--bogus"])] == [None] * 6


def test_a_valued_flag_naming_no_value_refuses():
    assert [read(["archituner", "c.md", "--file"]),
            read(["archituner", "c.md", "--file", "--check"]),
            read(["archituner", "c.md", "--min-weight"]),
            read(["archituner", "c.md", "--min-weight", "x"]),
            read(["archituner", "c.md", "-o"]),
            read(["archituner", "c.md", "--format"])] == [None] * 6


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
