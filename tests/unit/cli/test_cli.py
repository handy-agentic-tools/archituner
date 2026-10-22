import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.cli as cli


def fake_perform(calls):
    def perform(contract, out, builder, refusal, narrowing=None, fmt=None):
        calls.append((contract, out, builder, refusal, narrowing, fmt))
        return {"status": 0, "report": ["fake line"]}
    return perform


def drive(argv):
    calls = []
    keep = (cli.perform, cli.declared_version)
    cli.perform = fake_perform(calls)
    cli.declared_version = lambda: "9.9"
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
    finally:
        cli.perform, cli.declared_version = keep
    return code, out.getvalue(), err.getvalue(), calls


def refuser(argv):
    code, out, err, calls = drive(argv)
    assert (code, calls, out, err.startswith("usage:")) == \
        (2, [], "", True), (code, out, err, calls)


def test_help_and_version_exit_0_without_reaching_perform():
    code, out, err, calls = drive(["archituner", "--help"])
    assert (code, out.startswith("usage:"), err, calls) == (0, True, "", [])
    code, out, err, calls = drive(["archituner", "-h"])
    assert (code, out.startswith("usage:"), err, calls) == (0, True, "", [])
    assert drive(["archituner", "--version"]) == (0, "9.9\n", "", [])


def test_help_is_answered_before_any_stray_token():
    code, out, err, calls = drive(["archituner", "--help", "stray"])
    assert (code, out.startswith("usage:"), err, calls) == (0, True, "", [])


def hands(argv, builder, refusal, narrowing=None):
    assert drive(argv)[3] == [("c.md", "archituner.html", builder, refusal,
                               narrowing, None)]


def test_a_clean_check_argv_reaches_perform_once():
    assert drive(["archituner", "c.md", "--check"]) == \
        (0, "fake line\n", "", [("c.md", "archituner.html", cli.check_outcome,
                                 cli.refused, {}, None)])


def test_each_mode_hands_perform_its_own_builder_pair():
    hands(["archituner", "c.md", "--json"], cli.json_outcome, cli.rejected)
    hands(["archituner", "c.md", "--report"], cli.reading_outcome,
          cli.refused)
    hands(["archituner", "c.md", "--baseline"], None, cli.refused)
    hands(["archituner", "c.md"], cli.check_outcome, cli.refused, {})
    assert drive(["archituner", "c.md", "-o", "out.html"])[3] == \
        [("c.md", "out.html", cli.page_builder, cli.page_refusal,
          None, None)]


def test_narrowing_flags_join_every_value_in_order():
    code, out, err, calls = drive(
        ["archituner", "c.md", "--check", "--file", "a", "b",
         "--layer", "x", "y", "--state", "s1", "s2", "--min-weight", "2"])
    assert calls == [("c.md", "archituner.html", cli.check_outcome,
                      cli.refused,
                      {"file": ["a", "b"], "layer": ["x", "y"],
                       "state": ["s1", "s2"], "min-weight": 2}, None)], calls


def test_repeated_narrowing_flags_accumulate():
    code, out, err, calls = drive(
        ["archituner", "c.md", "--file", "a", "--file", "b"])
    assert calls == [("c.md", "archituner.html", cli.check_outcome,
                      cli.refused, {"file": ["a", "b"]}, None)], calls


def test_a_stray_word_after_a_mode_flag_refuses():
    refuser(["archituner", "c.md", "--check", "stray"])


def test_a_second_contract_refuses():
    refuser(["archituner", "c.md", "extra.md"])


def test_an_unknown_flag_refuses():
    refuser(["archituner", "c.md", "--bogus"])


def test_a_second_value_for_a_one_value_flag_refuses():
    refuser(["archituner", "c.md", "--min-weight", "3", "4"])
    refuser(["archituner", "c.md", "-o", "a", "b"])


def test_a_flag_after_out_refuses():
    refuser(["archituner", "c.md", "-o", "--bogus"])


def test_out_naming_no_value_refuses():
    refuser(["archituner", "c.md", "-o"])


def test_a_valued_flag_naming_no_value_refuses():
    refuser(["archituner", "c.md", "--file"])
    refuser(["archituner", "c.md", "--file", "--check"])
    refuser(["archituner", "c.md", "--min-weight"])


def test_an_argv_naming_no_contract_refuses():
    refuser(["archituner", "--check"])


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
