import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.report.outcomes import JSON_EXITS
from archituner.report.outcomes import check_outcome
from archituner.report.outcomes import json_outcome
from archituner.report.outcomes import reading_outcome
from archituner.report.outcomes import refused
from archituner.report.outcomes import rejected
from archituner.vocabulary import Finding

WITNESS = {"file": "api_entry.py", "module": "core_backbone", "line": 1}
PAIR = {"source": "api", "target": "core", "kind": "allow",
        "state": "convergence", "reason": "", "was": None,
        "imports": [WITNESS], "source_files": 1, "target_files": 1}
DIV_PAIR = dict(PAIR, state="divergence",
                reason="a stage never reaches back to the thing that "
                       "constructed it",
                remedy=Finding(text="drop the import of core_backbone",
                               produced_by="api_entry.py:1"))
READING = {"contract": "ARCHITECTURE.md", "tree": "scratch",
           "order": ["api", "core"], "pairs": [PAIR], "breaches": [],
           "files": [{"path": "api_entry.py", "layer": "api", "defs": 1,
                      "depth": 0, "cyclomatic": 1, "cognitive": 0}],
           "coverage": {"claimed": 1, "unclaimed": 0},
           "prose_percent": 0.0, "findings": [],
           "counts": {"convergence": 1, "divergence": 0, "absence": 0,
                      "silence": 0},
           "baseline": ".archituner-baseline.json", "change": None}
BREACH = {"file": "api_entry.py", "number": "defs", "value": 9, "limit": 8,
          "reason": None}
QUOTED = {("api_entry.py", 1): "import core_backbone"}
UNCLAIMED = "failed run: 1 file(s) walked, none claimed by any layer"
CROSSING = {"file": "api_entry.py", "line": 1, "module": "core_backbone",
            "source": "api", "target": "core", "kind": "allow",
            "state": "convergence", "code": "import core_backbone"}
DIV_LINES = [
    "divergence: api -> core",
    "    api_entry.py imports core_backbone",
    "    contract: a stage never reaches back to the thing that constructed "
    "it",
    "    remedy: drop the import of core_backbone"]


def narrowed(diverged, breaches, pairs):
    return {"pairs": pairs, "breaches": breaches, "files": READING["files"],
            "witnesses": [WITNESS], "diverged": diverged, "narrowing": {}}


def answered(answer, status, lines, artifact=None):
    assert answer == {"status": status, "lines": lines, "artifact": artifact}


def jsoned(answer, status, doc_status, reason):
    document = json.loads(answer["lines"][0])
    assert (answer["status"], document["schema"], document["status"],
            document["reason"]) == (status, 1, doc_status, reason)
    return document


def headed(answer, status, head, verdict):
    lines = answer["lines"][0].splitlines()
    assert (answer["status"], lines[0], lines[1]) == (status, head, verdict)


def test_the_four_statuses_ride_four_distinct_exits():
    assert (JSON_EXITS, len(set(JSON_EXITS.values()))) == (
        {"ok": 0, "divergent": 1, "rejected": 2, "failed_run": 3}, 4)


def test_a_text_refusal_answers_its_reason_at_the_refusal_exit():
    answered(refused("c.md", "no front matter"), 2, ["no front matter"])


def test_a_json_refusal_answers_the_rejected_document():
    jsoned(rejected("c.md", "no front matter"), 2, "rejected",
           "no front matter")


def test_a_clean_check_answers_no_divergence_and_an_unclaimed_its_sentence():
    answered(check_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                           None, None, False), 0, ["no divergence"])
    answered(check_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                           UNCLAIMED, None, False), 1, [UNCLAIMED])


def test_a_divergent_check_lists_its_witnesses_reason_and_remedy():
    answered(check_outcome(READING, narrowed(True, [], [DIV_PAIR]), QUOTED,
                           None, None, False), 1, DIV_LINES)


def test_a_breaching_check_answers_its_breach_lines():
    answered(check_outcome(READING, narrowed(False, [BREACH], [PAIR]),
                           QUOTED, None, None, False), 1,
             ["limit breach: api_entry.py: defs 9 over 8"])


def test_the_json_door_answers_the_document_and_the_realised_exit():
    answer = json_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                          None, None, False)
    document = jsoned(answer, 0, "ok", None)
    assert (document["crossings"], document["change"]) == ([CROSSING], None)


def test_a_divergent_json_door_answers_divergent_at_status_one():
    jsoned(json_outcome(READING, narrowed(True, [], [DIV_PAIR]), QUOTED,
                        None, None, False), 1, "divergent", "divergence")


def test_an_unclaimed_json_door_answers_the_failed_run_document():
    jsoned(json_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                        UNCLAIMED, None, False), 3, "failed_run", UNCLAIMED)


def test_the_report_door_answers_the_verdict_head_of_its_text():
    headed(reading_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                           None, None, False), 0,
           "ARCHITECTURE.md in scratch", "verdict: ok")


def test_the_report_door_spells_md_when_asked():
    headed(reading_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                           None, "md", False), 0,
           "# ARCHITECTURE.md in scratch", "verdict: ok")


def test_the_report_door_colours_its_counts_only_when_asked():
    plain = reading_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                            None, None, False)
    coloured = reading_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                               None, None, True)
    assert ("\x1b" in coloured["lines"][0],
            "\x1b" not in plain["lines"][0]) == (True, True)


def test_an_unclaimed_report_door_answers_the_failed_run_at_status_one():
    answered(reading_outcome(READING, narrowed(False, [], [PAIR]), QUOTED,
                             UNCLAIMED, None, False), 1, [UNCLAIMED])


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
