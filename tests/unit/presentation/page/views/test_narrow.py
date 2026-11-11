import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../../../../.."))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.narrow import script

BLOCK_COMMENT = re.compile(r"/[*].*?[*]/", re.S)
LINE_COMMENT = re.compile(r"[/]{2}.*")
WHITESPACE = re.compile(r"\s+")


def without_prose(text):
    flat = BLOCK_COMMENT.sub(" ", text)
    flat = LINE_COMMENT.sub(" ", flat)
    return WHITESPACE.sub(" ", flat).strip()


def drawer_of():
    flat = without_prose(script())
    return flat[flat.index("function drawColumn() {"):]


def test_the_column_drawer_builds_each_wire_from_the_payload_s_numbers():
    body = drawer_of()
    pieces = ("d='M \"", '" H "', '" V "', "hops_out", "hops_in",
              "DATA.stack_narrow.wires")
    missing = list(filter(lambda piece: piece not in body, pieces))
    bent = re.search(r" Q | Q\"|\"Q ", body)
    assert not missing and not bent and not re.search(r"\.arcs\b", body), \
        ("issue 283: the column does not draw every drawn pair as one "
         "right-angled wire built from the payload's own numbers - missing: "
         + json.dumps(missing) + ("; the pair still bends through a curve"
                                  if bent else
                                  "; the drawer still reads the arcs"))
    assert re.search(r"marker-end", body), ("issue 283: the wire lands on "
        "no arrowhead, so the drawing no longer answers which layer is "
        "used - the arrow is the one connection a box edge carries")
    assert re.search(r"<title>", body) and re.search(r"data-pair=", body), \
        ("issue 283: the wire carries no tooltip and no pair mark of its "
         "own, so hover behaves for nothing like the arcs it replaces")


def test_every_wire_carries_its_state_mark_at_its_lane():
    body = drawer_of()
    mark = re.search(r"<text x='\" \+ \w+\.l \+ \"' y='\" \+ \w+\.my \+ \"' "
                     r"text-anchor='middle'>\" \+ GLYPH\[", body)
    assert mark, ("issue 283: the column draws no state mark on the wire - "
                  "the glyph, the circle or the cross must stand at the "
                  "middle of the wire's own vertical lane, at the dense "
                  "size, on the phone as on the wide screen: "
                  + re.findall(r"<text[^>]*>", body).__str__())
    paired = re.search(r"data-pair=[^>]*>\" \+ GLYPH\[", body)
    assert paired, ("issue 283: the wire's state mark answers no pair, so "
                    "clicking it selects nothing")


def test_the_column_draws_at_its_own_natural_size():
    body = drawer_of()
    tag = re.search(r"<svg id='stack'[^>]*>", body)
    assert tag, "the column draws into no svg of its own"
    width = re.search(r"<svg id='stack'[^>]*width='\" \+ g\.width", body)
    height = re.search(r"<svg id='stack'[^>]*height='\" \+ g\.height", body)
    assert width and height, ("issue 283: the column's svg carries no "
        "width and height of its own stage, so the drawing is left to the "
        "stylesheet's column and comes out scaled instead of 1:1 - the "
        "phone's stack is 366 units wide and draws at 366: " + tag.group(0))


if __name__ == "__main__":
    for name, test in filter(lambda pair: pair[0].startswith("test_"),
                             sorted(globals().items())):
        test()
        print(f"PASS  {name}")
    print("all green")
