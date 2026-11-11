import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.stack_wires import routed

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

EXPECTED = {
    "api->core": {"x": 380, "a": 39, "b": 141, "l": 55.2, "my": 94,
                  "hops_out": [], "hops_in": [125.60000000000001, 196]},
    "core->util": {"x": 380, "a": 147, "b": 169, "l": 336.8, "my": 162,
                   "hops_out": [], "hops_in": []},
    "model->core": {"x": 380, "a": 77.5, "b": 135, "l": 266.40000000000003,
                    "my": 110.25, "hops_out": [], "hops_in": []},
    "model->util": {"x": 380, "a": 68.5, "b": 174.5,
                    "l": 125.60000000000001, "my": 125.5,
                    "hops_out": [], "hops_in": [196]},
    "web->util": {"x": 380, "a": 107, "b": 180, "l": 196, "my": 147.5,
                  "hops_out": [266.40000000000003], "hops_in": []},
}


def test_routed_lays_each_drawn_pair_as_one_right_angled_wire():
    wires = routed(WIDE, ORDER, DRAWN, 380, 20, 352, 1)
    assert wires == EXPECTED, ("issue 283: the band does not lay every "
        "drawn pair as one right-angled wire - an exit dock on the "
        "source's edge, the wire's own vertical lane in the band, an "
        "entry dock on the target's edge and the state mark at the "
        "middle of the lane: " + json.dumps(wires, sort_keys=True))


def test_a_hop_is_laid_only_where_a_run_passes_a_foreign_wire():
    wires = routed(WIDE, ORDER, DRAWN, 380, 20, 352, 1)
    assert wires["api->core"]["hops_in"] == [
        wires["model->util"]["l"], wires["web->util"]["l"]], ("issue 283: "
        "the landing run of api->core does not hop exactly the lanes it "
        "passes, once each, nearest lane first: "
        + json.dumps(wires["api->core"], sort_keys=True))
    assert wires["model->core"]["l"] not in wires["api->core"]["hops_in"], \
        ("issue 283: the landing run of api->core hops a wire whose lane "
         "it never crosses - the wire landing beside it on core lands "
         "clear of the run: " + json.dumps(wires["api->core"],
                                           sort_keys=True))
    assert wires["web->util"]["hops_out"] == [wires["model->core"]["l"]], \
        ("issue 283: the leaving run of web->util does not hop the one "
         "lane it passes: " + json.dumps(wires["web->util"],
                                         sort_keys=True))
    assert (wires["core->util"]["hops_out"], wires["core->util"]["hops_in"],
            wires["model->core"]["hops_out"],
            wires["model->core"]["hops_in"]) == ([], [], [], []), \
        ("issue 283: a wire lays a hop where no foreign lane stands "
         "between its lane and the boxes' edge, or where no run passes a "
         "lane at all: " + json.dumps((wires["core->util"],
                                       wires["model->core"]),
                                      sort_keys=True))


def test_the_lane_and_the_mark_are_spelled_for_a_browser():
    wires = routed(WIDE, ORDER, DRAWN, 380, 20, 352, 1)
    assert json.dumps(wires, sort_keys=True) == json.dumps(
        EXPECTED, sort_keys=True), ("issue 283: a whole coordinate is "
        "spelled as a float a browser concatenates with a decimal point, "
        "not as a number: " + json.dumps(wires, sort_keys=True))
    for key, wire in wires.items():
        assert wire["my"] == (wire["a"] + wire["b"]) / 2 + 4, ("issue "
            f"283: the state mark of {key} does not stand at the middle "
            "of the lane, dropped four units below it: "
            + json.dumps(wire, sort_keys=True))


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
