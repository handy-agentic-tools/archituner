import contextlib
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.perform import perform

CONTRACT = """---
layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

dependencies:
  allow:
    - api -> core
    - api -> model
    - core -> model
  forbid:
    - core -> api
    - model -> api
    - model -> core
---

## Boundaries

- `model -> *`: a representation computes nothing and depends on nothing.
- `core -> api`: a stage never reaches back to the thing that constructed it.
"""
STORED_NAME = ".archituner-baseline.json"
ANSWER = {"status": 0, "lines": [], "artifact": "<page-bytes>"}
QUOTED = {("api_entry.py", 1): "import core_backbone"}


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(contract_text=CONTRACT, **files):
    tree = os.path.join(tempfile.mkdtemp(), "scratch")
    plant(tree, "ARCHITECTURE.md", contract_text)
    for name, text in files.items():
        plant(tree, f"{name}.py", text)
    return tree, os.path.join(tree, "ARCHITECTURE.md")


def drive(contract, out, builder, refusal, **kwargs):
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        return perform(contract, out, builder, refusal, **kwargs)


def settled():
    return build(api_entry="import core_backbone\n",
                 core_backbone="VALUE = 1\n", model_shape="VALUE = 2\n")


def recorder(answer, calls):
    def record(*args):
        calls.append(args)
        return answer
    return record


def boom_refusal(contract_path, reason):
    raise AssertionError(f"refusal reached: {reason}")


class bright(io.StringIO):
    def isatty(self):
        return True


def read_of(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_a_refusal_is_handed_its_reason_and_its_artifact_is_written():
    tree, contract = build("not a contract\n")
    page = os.path.join(tree, "r.html")
    calls = []
    answer = drive(contract, page, None, recorder(
        {"status": 2, "lines": ["refused"], "artifact": "REJECTION"}, calls))
    reason = f"rejected: {contract} does not open with front matter"
    assert (answer["status"], answer["report"], calls,
            read_of(page)) == (2, ["refused", f"  -> {page}"],
                               [(contract, reason)], "REJECTION")


def test_a_refusal_without_an_artifact_writes_nothing():
    tree, contract = build("not a contract\n")
    page = os.path.join(tree, "r.html")
    answer = drive(contract, page, None, recorder(
        {"status": 2, "lines": ["refused"], "artifact": None}, []))
    assert (answer["report"], os.path.exists(page)) == (["refused"], False)


def test_a_baseline_intent_writes_the_stored_reading_over_whatever_is_kept():
    tree, contract = settled()
    kept = os.path.join(tree, STORED_NAME)
    with open(kept, "w", encoding="utf-8") as handle:
        handle.write("not json\n")
    answer = drive(contract, os.path.join(tree, "p.html"), None, boom_refusal)
    stored = json.loads(read_of(kept))
    assert (answer["status"], answer["report"], stored["files"],
            stored["pairs"]["api -> core"], stored["layers"]) == (
        (0, [f"baseline written: {kept}"],
         {"api_entry.py": "api", "core_backbone.py": "core",
          "model_shape.py": "model"}, "convergence", ["api", "core", "model"]))


def test_the_builder_is_handed_the_reading_the_narrowing_and_the_quotes():
    tree, contract = settled()
    calls = []
    drive(contract, os.path.join(tree, "p.html"), recorder(ANSWER, calls),
          boom_refusal, narrowing={"file": ["api_entry.py"]}, fmt="md")
    reading, narrowed, quoted, unclaimed, fmt, colour = calls[0]
    assert (reading["baseline"], reading["change"], unclaimed, fmt,
            colour, narrowed["narrowing"], quoted) == \
        (STORED_NAME, None, None, "md", False,
         {"file": ["api_entry.py"]}, QUOTED)


def test_a_narrowing_that_keeps_nothing_hands_empty_answers():
    tree, contract = settled()
    calls = []
    drive(contract, os.path.join(tree, "p.html"), recorder(ANSWER, calls),
          boom_refusal, narrowing={"file": ["gone.py"]})
    reading, narrowed, quoted, unclaimed, fmt, colour = calls[0]
    assert (narrowed["pairs"], narrowed["witnesses"], narrowed["diverged"],
            quoted) == ([], [], False, {})


def test_the_colour_asks_the_terminal_and_yields_to_no_color():
    tree, contract = settled()
    page = os.path.join(tree, "p.html")
    lit, dim = [], []
    with contextlib.redirect_stdout(bright()):
        perform(contract, page, recorder(ANSWER, lit), boom_refusal)
    os.environ["NO_COLOR"] = "1"
    try:
        with contextlib.redirect_stdout(bright()):
            perform(contract, page, recorder(ANSWER, dim), boom_refusal)
    finally:
        os.environ.pop("NO_COLOR", None)
    assert (lit[0][5], dim[0][5]) == (True, False)


def test_the_builder_s_answer_is_relayed_its_artifact_written_and_tallied():
    tree, contract = settled()
    page = os.path.join(tree, "archituner.html")
    answer = drive(contract, page, recorder({"status": 0, "lines": [],
                                             "artifact": "<page-bytes>"},
                                            []), boom_refusal)
    assert (answer["status"], answer["report"], read_of(page)) == (
        0, [contract,
            "  layers 3  files 3  unclaimed 0",
            "  convergence 1  divergence 0  absence 2  silence 3",
            "  findings 0",
            f"  -> {page}"], "<page-bytes>")


def test_a_builder_line_answers_alone_and_writes_nothing():
    tree, contract = settled()
    page = os.path.join(tree, "p.html")
    answer = drive(contract, page, recorder({"status": 1,
                                             "lines": ["limit breach: x"],
                                             "artifact": None}, []),
                   boom_refusal)
    assert (answer["status"], answer["report"],
            os.path.exists(page)) == (1, ["limit breach: x"], False)


def test_an_unclaimed_tree_is_handed_to_the_builder_as_its_sentence():
    tree, contract = build(stray="VALUE = 1\n")
    calls = []
    drive(contract, os.path.join(tree, "p.html"), recorder(ANSWER, calls),
          boom_refusal)
    assert (calls[0][3], os.path.exists(os.path.join(tree, STORED_NAME))) == \
        ("failed run: 1 file(s) walked, none claimed by any layer", False)


def test_a_stored_baseline_rides_the_reading_as_the_change():
    tree, contract = settled()
    drive(contract, os.path.join(tree, "p.html"), None, boom_refusal)
    plant(tree, "core_backbone.py", "import api_entry\nVALUE = 1\n")
    calls = []
    drive(contract, os.path.join(tree, "p.html"), recorder(ANSWER, calls),
          boom_refusal)
    assert calls[0][0]["change"]["counts"] == \
        {"improved": 0, "regressed": 1, "unchanged": 5}


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
