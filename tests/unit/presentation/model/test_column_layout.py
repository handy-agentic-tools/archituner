import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.column_layout import column

ORDER = ["api", "model", "web", "core", "util"]


def pair(name, state):
    return {"source": name.split("->")[0], "target": name.split("->")[1],
            "state": state}


DRAWN = [pair("api->core", "convergence"), pair("model->util", "convergence"),
         pair("web->core", "absence"), pair("web->util", "convergence"),
         pair("core->util", "convergence")]

EXPECTED = {
    "width": 366, "height": 242, "cell": 50, "head_y": 16,
    "centres": [183, 233, 283, 333],
    "inset": 8, "name_base": 13, "cell_top": 16, "val_base": 26,
    "cell_foot": 29, "hop": 3.5,
    "nodes": [
        {"name": "api", "x": 158, "y": 26, "width": 200, "height": 30},
        {"name": "model", "x": 158, "y": 64, "width": 200, "height": 30},
        {"name": "web", "x": 158, "y": 102, "width": 200, "height": 30},
        {"name": "core", "x": 158, "y": 140, "width": 200, "height": 30},
        {"name": "util", "x": 158, "y": 178, "width": 200, "height": 30},
    ],
    "wires": {
        "api->core": {"x": 158, "a": 41, "b": 147, "l": 22.4, "my": 98,
                      "hops_out": [], "hops_in": [51.2, 80, 108.8]},
        "model->util": {"x": 158, "a": 79, "b": 201.5, "l": 51.2,
                        "my": 144.25, "hops_out": [], "hops_in": []},
        "web->core": {"x": 158, "a": 123.5, "b": 164, "l": 108.8,
                      "my": 147.75, "hops_out": [], "hops_in": [137.6]},
        "web->util": {"x": 158, "a": 110.5, "b": 193, "l": 80, "my": 155.75,
                      "hops_out": [], "hops_in": []},
        "core->util": {"x": 158, "a": 156.5, "b": 184.5, "l": 137.6,
                       "my": 174.5, "hops_out": [], "hops_in": []},
    },
}


def test_the_column_lays_each_drawn_pair_as_one_right_angled_wire():
    figure = column(ORDER, DRAWN)
    assert figure == EXPECTED, (
        "issue 283: the column does not lay every drawn pair as one "
        "right-angled wire - an exit dock on the source's left edge, its "
        "own vertical lane in the left band, an entry dock with the arrow "
        "on the target's left edge, the state mark at the middle of the "
        "lane and a hop where a horizontal run passes another wire's lane "
        "- and the phone stage does not stand at its own natural size, 366 "
        "units with 8 unit margins and 200 unit two-row boxes: "
        + json.dumps(figure, sort_keys=True))


def test_the_wires_dock_in_parts_and_absence_lands_below_them():
    wires = column(ORDER, DRAWN).get("wires")
    assert wires, ("issue 283: the column carries no wire per drawn pair, "
                   "so there is nothing docked, landed or laned to judge: "
                   + json.dumps(column(ORDER, DRAWN), sort_keys=True))
    core_in = wires["api->core"]["b"]
    core_out = wires["core->util"]["a"]
    assert core_in < core_out, ("issue 283: the wire landing on core does "
                                "not land above the wire leaving it - a "
                                "box's edge is a docking strip, wires land "
                                "on its upper part and leave from its lower "
                                f"part ({core_in} then {core_out})")
    assert max(core_in, core_out) < wires["web->core"]["b"], ("issue 283: "
        "the absence does not land in its own strip below every other wire "
        "at its target, dashed and marked circle: "
        + json.dumps(wires["web->core"], sort_keys=True))
    outs = sorted(wires[key]["a"] for key in ("web->core", "web->util"))
    assert outs[0] < outs[1], ("issue 283: two wires of one box share the "
        "height they leave at, so neither owns its hover along the run: "
        + json.dumps(outs))


def test_nested_and_fanned_lanes_never_cross_and_a_crossing_is_a_hop():
    wires = column(ORDER, DRAWN).get("wires")
    assert wires, ("issue 283: the column carries no wire per drawn pair, "
                   "so there is nothing laned or hopped to judge: "
                   + json.dumps(column(ORDER, DRAWN), sort_keys=True))
    fan = [(wires[key]["l"], wires[key]["b"])
           for key in ("model->util", "web->util", "core->util")]
    assert fan[0][0] < fan[1][0] < fan[2][0], ("issue 283: the three wires "
        "into one target are not laned outer first, the longest wrapping "
        "deepest, so the fan crosses itself: " + json.dumps(fan))
    wrapped = [wires[key]["l"]
               for key in ("model->util", "web->core", "web->util",
                           "core->util")]
    assert wires["api->core"]["l"] < min(wrapped), ("issue 283: a wire "
        "wrapping others does not run deeper than every wire it wraps, so "
        "nesting crosses: " + json.dumps(wires["api->core"], sort_keys=True))
    assert wires["api->core"]["hops_in"] == [51.2, 80, 108.8], ("issue "
        "283: a crossing is not a horizontal run hopping over the standing "
        "wire's lane: " + json.dumps(wires["api->core"], sort_keys=True))
    assert wires["web->core"]["hops_in"] == [137.6], ("issue 283: the "
        "absence's landing run does not hop the lane it passes: "
        + json.dumps(wires["web->core"], sort_keys=True))


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
