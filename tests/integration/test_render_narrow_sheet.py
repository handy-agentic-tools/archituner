# covers: archituner/presentation/**
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

REST = "Click a box to see that layer."
AGAIN = "Click the box again to see the whole project."
RIGHT = " on the right"


def render():
    page = os.path.join(tempfile.mkdtemp(), "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner",
                           os.path.join(REPO, "ARCHITECTURE.md"), "-o", page],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    with open(page, "rb") as handle:
        return handle.read()


PAGE = render()
TEXT = PAGE.decode("utf-8")
STYLE = TEXT[TEXT.index("<style>") + 7:TEXT.index("</style>")]
SCRIPT = TEXT[TEXT.index("<script>") + 8:TEXT.index("</script>")]


def block_of(work, needle):
    start = work.index(needle)
    open_at = work.index("{", start)
    depth = 0
    for at, char in enumerate(work[open_at:], open_at):
        depth += (char == "{") - (char == "}")
        if not depth:
            return start, at + 1
    raise AssertionError(f"the {needle} block never closes")


def narrow_of():
    work = re.sub(r"/\*.*?\*/", lambda mark: " " * len(mark.group()),
                  STYLE, flags=re.S)
    assert "@media (max-width" in work, ("the page draws one layout for "
        "every width: no width threshold carries the narrow layout, so "
        "the narrow dress has nothing to live in")
    start, end = block_of(work, "@media (max-width")
    return work[start:end], work[:start] + work[end:]


def rules_of(sheet):
    return re.findall(r"[^{}]+\{[^{}]*\}", sheet)


def picked(rules, mark):
    return list(filter(lambda rule: mark in rule, rules))


def hidden(rules):
    return list(filter(lambda rule: "display:none" in re.sub(r"\s+", "", rule),
                       rules))


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


def test_the_panel_raises_as_a_sheet_over_the_drawing_when_a_box_is_held():
    narrow, _ = narrow_of()
    sheet = picked(rules_of(narrow), "data-sheet")
    assert sheet, ("the narrow block dresses no sheet: with a box held the "
        "panel keeps its wide dress and nothing raises over the drawing")
    body = "".join(sheet)
    assert re.search(r"position:\s*(?:fixed|absolute)", body), ("the "
        "sheet stays in the page's flow, so it pushes the drawing down "
        "instead of covering it")
    assert re.search(r"(?<![\w-])bottom:\s*(?:0\b|calc\(var\(--u\) \* 0\))",
                     body), ("the sheet is pinned to no bottom edge, so it "
        "does not rise from the screen's bottom")
    assert re.search(r"(?:(?<![\w-])(?:left|right):\s*"
                     r"(?:0\b|calc\(var\(--u\) \* 0\))|"
                     r"(?<![\w-])width:\s*100%)", body), ("the sheet does "
        "not span the screen's width")
    marked = list(filter(lambda line: "selection" in line
                         and ("data-sheet" in line
                              or "dataset.sheet" in line),
                         SCRIPT.splitlines()))
    assert marked, ("the script does not mark the sheet beside the "
        "selection that raises it, so the narrow block has no state to "
        "key the raised panel on: "
        + str(picked(SCRIPT.splitlines(), "data-sheet")))


def test_the_sheet_carries_a_cross_and_the_wide_page_keeps_none():
    assert re.search(r"<button[^>]*data-close[^>]*>\s*✕", TEXT), ("no "
        "cross stands beside the panel's name: a phone has no Escape, so "
        "the sheet offers no way to close it")
    narrow, wide = narrow_of()
    wide_rules = picked(rules_of(wide), "data-close")
    assert wide_rules, ("no wide rule holds the cross, so the wide page "
        "shows a control it never carried")
    assert hidden(wide_rules) == wide_rules, ("the wide rules do not hide "
        "the cross, so the wide page gains a control it never carried")
    narrow_rules = picked(rules_of(narrow), "data-close")
    assert narrow_rules, ("the narrow block never dresses the cross, so "
        "the sheet stays unclosable")
    assert not hidden(narrow_rules), ("the narrow block hides the cross "
        "itself, so the sheet stays unclosable")
    assert re.search(r"dataset\.close[\s\S]{0,200}?selection = null",
                     SCRIPT), ("the cross clears no selection: it is a "
        "mark without the one job Escape does")


def test_the_words_say_click_without_naming_a_side():
    wrong = list(filter(lambda sentence: SCRIPT.count(sentence) != 1,
                        (REST, AGAIN)))
    assert not wrong, ("the page does not carry each sketch sentence "
        f"exactly once, and the narrow page is the only one they are "
        f"written for: {wrong}")
    narrow, wide = narrow_of()
    concealed = picked(hidden(rules_of(wide)), ".hint")
    assert concealed, ("no wide rule hides the hint, so the wide page "
        "gains wording it never carried")
    narrow_hints = picked(rules_of(narrow), ".hint")
    assert narrow_hints, ("the narrow block never dresses the hint, so "
        "the narrow reader is left without the words")
    assert not hidden(narrow_hints), ("the narrow block hides the hint "
        "itself, so the narrow reader is left without the words")
    assert RIGHT not in TEXT, ("the page names the side the wide layout "
        "opens with, one a narrow screen does not have: the sheet rises "
        f"over the drawing instead, so the words send nobody{RIGHT}")


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
