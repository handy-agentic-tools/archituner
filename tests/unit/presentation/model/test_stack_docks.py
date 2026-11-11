import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.stack_docks import docks
from archituner.presentation.model.stack_docks import rounded

WIDE = {"row": 34, "pad": 28, "margin": 20, "node_w": 604, "node_h": 22,
        "band_l": 352, "gap_l": 8, "band_r": 220, "cell": 56, "hop": 5}

ORDER = ["api", "model", "web", "core", "util"]
INDEX = {name: i for i, name in enumerate(ORDER)}


def pair(name, state):
    return {"source": name.split("->")[0], "target": name.split("->")[1],
            "state": state}


DRAWN = [pair("api->core", "convergence"), pair("model->util", "convergence"),
         pair("model->core", "convergence"), pair("web->util", "absence"),
         pair("core->util", "convergence")]

SEATS = {"api->core": 0, "core->util": 4, "model->core": 3,
         "model->util": 1, "web->util": 2}

EXIT = {"api->core": 39.0, "core->util": 147.0, "model->core": 77.5,
        "model->util": 68.5, "web->util": 107.0}
ENTRY = {"api->core": 141.0, "core->util": 169.0, "model->core": 135.0,
         "model->util": 174.5, "web->util": 180.0}


def test_a_box_docks_its_wires_in_two_parts_inputs_above_outputs():
    laid = docks(WIDE, ORDER, INDEX, DRAWN, SEATS)
    assert laid == (EXIT, ENTRY), ("issue 283: the boxes' edges are not "
        "docking strips that spread every wire of the box along its edge, "
        "a height apart, in the lane order that keeps a fan from "
        "crossing: " + json.dumps(laid, sort_keys=True))
    assert max(ENTRY["api->core"], ENTRY["model->core"]) \
        < EXIT["core->util"], ("issue 283: a wire leaving core does not "
        "leave below every wire landing on it - wires land on a box's "
        "upper part and leave from its lower part, so a wire leaving a "
        "box never passes under a wire landing on it: "
        + json.dumps((ENTRY["api->core"], ENTRY["model->core"],
                      EXIT["core->util"])))


def test_no_two_paths_of_one_box_share_a_height():
    laid = docks(WIDE, ORDER, INDEX, DRAWN, SEATS)
    edge = {}
    for p in DRAWN:
        edge.setdefault(p["source"], []).append(
            laid[0][p["source"] + "->" + p["target"]])
        edge.setdefault(p["target"], []).append(
            laid[1][p["source"] + "->" + p["target"]])
    assert edge == {"api": [39.0], "model": [68.5, 77.5], "web": [107.0],
                    "core": [141.0, 135.0, 147.0],
                    "util": [174.5, 180.0, 169.0]}, ("issue 283: the "
        "paths of one box do not meet its edge at distinct heights, one "
        "apiece - no two wires of one box share a height, so each owns "
        "its hover along the run: " + json.dumps(edge, sort_keys=True))


def test_an_absence_lands_in_its_own_strip_below_the_solid_docks():
    laid = docks(WIDE, ORDER, INDEX, DRAWN, SEATS)
    assert max(ENTRY["model->util"], ENTRY["core->util"]) \
        < laid[1]["web->util"] == 180.0, ("issue 283: the absence does "
        "not land in a strip of its own below every solid wire at its "
        "target, dashed and marked circle: "
        + json.dumps(laid[1], sort_keys=True))
    strip = [pair("api->util", "absence"), pair("model->util", "absence")]
    entry = docks(WIDE, ["api", "model", "util"],
                  {"api": 0, "model": 1, "util": 2}, strip,
                  {"api->util": 0, "model->util": 0})[1]
    assert entry == {"api->util": 112.0, "model->util": 109.0}, ("issue "
        "283: two absences into one target do not stack a step of three "
        "units apart in their own strip at the target's hem: "
        + json.dumps(entry, sort_keys=True))


def test_deep_lanes_dock_high_leaving_and_low_landing_on_half_units():
    laid = docks(WIDE, ORDER, INDEX, DRAWN, SEATS)
    assert laid[0]["model->util"] < laid[0]["model->core"], ("issue 283: "
        "the deeper lane does not dock high leaving model, so the two "
        "wires out of one box start crossed: "
        + json.dumps(laid[0], sort_keys=True))
    assert laid[1]["api->core"] > laid[1]["model->core"], ("issue 283: "
        "the deeper lane does not dock low landing on core, so the fan "
        "into one target crosses itself: "
        + json.dumps(laid[1], sort_keys=True))
    assert (rounded(143.25), rounded(143.75), rounded(143.2)) \
        == (143.5, 144.0, 143.0), ("issue 283: docks do not round to "
        "half units, so a browser draws heights no grid holds")


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
