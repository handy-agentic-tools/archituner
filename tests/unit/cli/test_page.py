import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.cli import page

READING = {"contract": "ARCHITECTURE.md"}
NARROWED = {"pairs": [], "breaches": [], "files": [], "witnesses": [],
            "diverged": False, "narrowing": {}}


def fake_draw(calls, answer):
    def draw(reading):
        calls.append(reading)
        return answer
    return draw


def fake_reject(calls, answer):
    def reject(contract_path, reason):
        calls.append((contract_path, reason))
        return answer
    return reject


def test_the_page_builder_renders_the_reading_into_its_artifact():
    calls = []
    keep = (page.render, page.render_rejection)
    page.render = fake_draw(calls, "<page>")
    page.render_rejection = fake_reject([], "<rejection>")
    try:
        answer = page.page_builder(READING, NARROWED, {}, None, None, False)
    finally:
        page.render, page.render_rejection = keep
    assert (answer["status"], answer["lines"], answer["artifact"]) == \
        (0, [], "<page>")
    assert calls == [READING]


def test_the_page_refusal_renders_the_rejection_into_its_artifact():
    calls = []
    keep = (page.render, page.render_rejection)
    page.render = fake_draw([], "<page>")
    page.render_rejection = fake_reject(calls, "<rejection>")
    try:
        answer = page.page_refusal("c.md", "no front matter")
    finally:
        page.render, page.render_rejection = keep
    assert (answer["status"], answer["lines"], answer["artifact"]) == \
        (2, ["no front matter"], "<rejection>")
    assert calls == [("c.md", "no front matter")]


def test_without_presentation_the_page_answers_a_refusal_and_writes_nothing():
    keep = (page.render, page.render_rejection)
    page.render = None
    page.render_rejection = None
    try:
        built = page.page_builder(READING, NARROWED, {}, None, None, False)
        refused = page.page_refusal("c.md", "no front matter")
    finally:
        page.render, page.render_rejection = keep
    assert (built["status"] != 0, built["artifact"] is None,
            bool(built["lines"])) == (True, True, True)
    assert (refused["status"] != 0, refused["artifact"] is None,
            bool(refused["lines"])) == (True, True, True)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
