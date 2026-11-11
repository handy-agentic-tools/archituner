import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.stack_seats import claim_of
from archituner.presentation.model.stack_seats import lanes
from archituner.presentation.model.stack_seats import meets
from archituner.presentation.model.stack_seats import seat_against
from archituner.presentation.model.stack_seats import wraps

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


def test_nested_wrapped_and_fanned_pairs_each_take_a_lane_of_their_own():
    laid = lanes(WIDE, INDEX, DRAWN)
    assert laid == (SEATS, 5), ("issue 283: the band does not hold one "
        "lane per wire that needs it at the same time, the longest claim "
        "placed outermost first so every wire sits after the wires that "
        "wrap it and the band never merges anything into a bus: "
        + json.dumps(laid, sort_keys=True))
    assert laid[0]["api->core"] < laid[0]["model->core"], ("issue 283: a "
        "wire does not take a deeper lane than the wire it wraps, so "
        "nesting - and the fan of two wires landing on core with it - "
        "crosses itself: " + json.dumps(laid[0], sort_keys=True))


def test_a_lane_is_shared_only_when_two_verticals_never_meet():
    share = lanes(WIDE, INDEX, [pair("api->model", "convergence"),
                                pair("web->util", "convergence")])
    assert share == ({"api->model": 0, "web->util": 0}, 1), ("issue 283: "
        "two wires whose vertical ranges never meet do not share the "
        "band's one lane, so the band wastes a lane on nothing: "
        + json.dumps(share, sort_keys=True))
    apart = lanes(WIDE, INDEX, [pair("api->model", "convergence"),
                                pair("model->web", "convergence")])
    assert apart == ({"api->model": 0, "model->web": 1}, 2), ("issue 283: "
        "two wires through one box take a lane each even where only the "
        "margins of their claims meet, so no two standing wires ever "
        "merge: " + json.dumps(apart, sort_keys=True))


def test_an_absence_landing_stretches_the_claim_past_the_solid_one():
    solid = claim_of(WIDE, INDEX, pair("api->model", "convergence"))
    assert solid == (27.0, 85.0), ("issue 283: a solid pair's claim is "
        "not its rows held by a hem of half a box: "
        + json.dumps(solid))
    absent = claim_of(WIDE, INDEX, pair("api->model", "absence"))
    assert absent == (27.0, 94.0), ("issue 283: an absence's claim does "
        "not run below its target's hem to hold the strip it lands in: "
        + json.dumps(absent))
    laid = lanes(WIDE, INDEX, [pair("api->model", "absence"),
                               pair("web->util", "convergence")])
    assert laid == ({"api->model": 1, "web->util": 0}, 2), ("issue 283: "
        "the absence's landing strip does not keep its lane to itself "
        "where the solid pair's claim would have shared it with "
        "web->util: " + json.dumps(laid, sort_keys=True))


def test_a_seat_is_taken_only_from_wires_that_meet_and_wrap():
    claims = {"outer": (0, 100), "inner": (10, 90), "far": (200, 300)}
    seats = {"outer": 0, "inner": 1, "far": 0}
    assert (seat_against(claims, seats, 20, 80),
            seat_against({"busy": (0, 100)}, {"busy": 0}, 20, 150),
            seat_against({"far": (200, 300)}, {"far": 0}, 20, 150)) \
        == (2, 1, 0), ("issue 283: a seat is not taken only from the "
        "wires that meet and wrap one - a wire nested inside two others "
        "runs outside both, a crossing wire takes the shallowest free "
        "lane, a wire whose verticals never meet another's takes none: "
        + json.dumps((claims, seats)))
    assert (meets((27.0, 153.0), 155, 200), meets((27.0, 153.0), 156, 200),
            wraps((27.0, 153.0), 29, 151), wraps((30.0, 153.0), 27, 151)) \
        == (True, False, True, False), ("issue 283: a claim does not "
        "hold another clear by the guard of three units, and wraps "
        "another only when it holds both its ends within the wrap of "
        "two units, so only the wire running around one pushes it "
        "deeper: " + json.dumps((27.0, 153.0)))


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
