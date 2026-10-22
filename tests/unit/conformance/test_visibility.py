import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
from archituner.conformance.visibility import file_visible
from archituner.conformance.visibility import narrow
from archituner.conformance.visibility import pair_visible
from archituner.conformance.visibility import scoped_pairs

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "conformance", "visibility.py")


def pair(state="convergence", source="cli", target="run", files=("a.py",)):
    return {"state": state, "source": source, "target": target,
            "imports": [{"file": name} for name in files]}


def test_no_axis_fed_leaves_every_realised_pair_visible_and_whole():
    one = pair()
    two = pair(state="divergence", source="run", target="vocabulary",
               files=("a.py", "b.py"))
    assert pair_visible(two, {})
    assert scoped_pairs([one, two], {}) == [one, two]


def test_a_pair_with_both_ends_named_layers_stays_and_one_end_outside_goes():
    asked = {"layer": ["cli", "vocabulary"]}
    both = pair(source="cli", target="vocabulary")
    source_outside = pair(source="run", target="vocabulary")
    target_outside = pair(source="cli", target="run")
    answer = (pair_visible(both, asked), pair_visible(source_outside, asked),
              pair_visible(target_outside, asked))
    assert answer == (True, False, False)


def test_a_pair_at_the_weight_stays_and_one_below_goes():
    asked = {"min-weight": 2}
    at = pair(files=("a.py", "b.py"))
    below = pair(files=("a.py",))
    assert (pair_visible(at, asked), pair_visible(below, asked)) == \
        (True, False)


def test_the_weight_measures_the_whole_run_never_the_witnesses_an_axis_kept():
    asked = {"min-weight": 3, "file": ["a.py"]}
    three = pair(files=("a.py", "b.py", "c.py"))
    assert scoped_pairs([three], asked) == \
        [dict(three, imports=[{"file": "a.py"}])]


def test_the_file_axis_holds_its_named_path_and_answers_everything_unasked():
    assert (file_visible("a.py", {"file": ["a.py"]}),
            file_visible("b.py", {"file": ["a.py"]}),
            file_visible("b.py", {})) == (True, False, True)


def test_a_pair_whose_witnesses_the_file_axis_filtered_away_drops():
    assert scoped_pairs([pair(files=("b.py", "c.py"))],
                        {"file": ["a.py"]}) == []


def test_a_fed_path_and_the_axes_answer_one_question_together():
    asked = {"state": ["convergence"], "file": ["a.py"]}
    inside = pair(files=("a.py",))
    unasked = pair(state="divergence", files=("a.py",))
    unwitnessed = pair(files=("b.py",))
    assert scoped_pairs([inside, unasked, unwitnessed], asked) == [inside]


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_visibility_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout.splitlines(),
            two.returncode, two.stdout.splitlines()) == \
        (0, ["no divergence"], 0, ["no divergence"]), \
        (one.returncode, two.returncode, one.stdout, one.stderr)


WITNESS = {"file": "a.py", "module": "m", "line": 1}
OTHER = {"file": "b.py", "module": "n", "line": 2}
PAIRS = [
    {"source": "cli", "target": "run", "kind": "allow",
     "state": "convergence", "reason": "", "imports": [WITNESS]},
    {"source": "run", "target": "cli", "kind": "forbid",
     "state": "divergence", "reason": "", "imports": [OTHER]},
]
RESULT = {"pairs": PAIRS,
          "breaches": [{"file": "a.py", "number": "defs", "value": 9,
                        "limit": 8, "reason": None},
                       {"file": "b.py", "number": "size", "value": 99,
                        "limit": 21, "reason": None}],
          "files": [{"path": "a.py", "layer": "cli"},
                    {"path": "b.py", "layer": "run"}]}


def answers(narrowing, expected):
    assert narrow(RESULT, narrowing) == expected


def test_narrow_answers_the_whole_result_when_nothing_is_asked():
    answers({}, {"pairs": PAIRS, "breaches": RESULT["breaches"],
                 "files": RESULT["files"], "witnesses": [WITNESS, OTHER],
                 "diverged": True, "narrowing": {}})


def test_narrow_drops_unasked_states_witnesses_and_paths_together():
    asked = {"state": ["convergence"], "file": ["a.py"]}
    answers(asked, {"pairs": [PAIRS[0]], "breaches": [RESULT["breaches"][0]],
                    "files": [RESULT["files"][0]], "witnesses": [WITNESS],
                    "diverged": False, "narrowing": asked})


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
