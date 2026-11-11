import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
from archituner.presentation.model.stack_layout import stack

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "model",
                        "stack_layout.py")

ORDER = ["api", "model", "web", "core", "util"]

DRAWN = {
    "width": 1244,
    "height": 226,
    "cell": 56,
    "head_y": 18,
    "hop": 5,
    "centres": [788, 844, 900, 956],
    "nodes": [
        {"name": "api", "x": 380, "y": 28, "width": 604, "height": 22},
        {"name": "model", "x": 380, "y": 62, "width": 604, "height": 22},
        {"name": "web", "x": 380, "y": 96, "width": 604, "height": 22},
        {"name": "core", "x": 380, "y": 130, "width": 604, "height": 22},
        {"name": "util", "x": 380, "y": 164, "width": 604, "height": 22},
    ],
    "wires": {
        "api->core": {"x": 380, "a": 39, "b": 136.5, "l": 108, "my": 91.75,
                      "hops_out": [], "hops_in": []},
        "core->util": {"x": 380, "a": 145.5, "b": 175, "l": 284,
                       "my": 164.25, "hops_out": [], "hops_in": []},
        "model->api": {"x": 984, "a": 77.5, "b": 39, "l": 1059, "my": 62.25,
                       "hops_out": [], "hops_in": []},
        "core->model": {"x": 984, "a": 141, "b": 68.5, "l": 1169,
                        "my": 108.75, "hops_out": [], "hops_in": [1059]},
    },
}

def pair(name, state):
    return {"source": name.split("->")[0], "target": name.split("->")[1],
            "state": state}


def reading():
    states = {"api->core": "convergence", "core->util": "convergence",
              "core->model": "divergence", "model->api": "divergence"}
    return [pair(name, states[name])
            for name in ("api->core", "core->util", "model->api",
                         "core->model")]


def test_the_stage_the_rows_and_the_wires_are_laid_out_over_the_order():
    assert stack(ORDER, reading()) == DRAWN, ("issue 283: the stage's "
        "wires are not the left band's router with divergences mirrored "
        "on the boxes' right edge - the right band is that router's exact "
        "mirror, its lanes reflected from the boxes' right edge and its "
        "entry docks in the left band's uncrossing order, per the issue's "
        "decision: " + json.dumps(stack(ORDER, reading()), sort_keys=True))


def test_the_header_row_hangs_above_the_boxes_over_the_four_cells():
    laid = stack(ORDER, reading())
    top = laid["nodes"][0]
    assert laid["head_y"] < top["y"], (laid["head_y"], top["y"])
    assert laid["centres"] == [top["x"] + top["width"]
                               - laid["cell"] * (4 - k) + laid["cell"] // 2
                               for k in range(4)], laid["centres"]


def test_every_coordinate_is_spelled_as_a_number_a_browser_concatenates():
    text = json.dumps(stack(ORDER, reading()), sort_keys=True)
    assert text == json.dumps(DRAWN, sort_keys=True), text


def test_an_absence_wire_lands_in_its_own_strip_below_the_solid_heads():
    laid = stack(ORDER, [pair("api->core", "convergence"),
                         pair("model->core", "absence")])
    wires = laid.get("wires", {})
    assert wires.get("model->core") == {"x": 380, "a": 73, "b": 146,
                                        "l": 284, "my": 113.5,
                                        "hops_out": [], "hops_in": []}, \
        ("issue 283: the absence does not land in its own strip below its "
         "target's fan: " + json.dumps(wires, sort_keys=True))
    assert wires["model->core"]["b"] > wires["api->core"]["b"], \
        ("the absence does not land clear below the solid entry at its "
         "target: " + json.dumps(wires, sort_keys=True))


def test_the_wire_depths_are_taken_once_over_every_non_silence_pair():
    quiet = [pair("api->mid", "convergence"), pair("api->util", "silence")]
    laid = stack(["api", "mid", "util"], quiet)
    wires = laid.get("wires", {})
    assert "api->util" not in wires, wires
    assert wires.get("api->mid", {}).get("l") == 196, \
        ("issue 283: the drawn pair takes no lane of its own in the band: "
         + json.dumps(wires, sort_keys=True))


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_stack_layout_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


if __name__ == "__main__":
    for name, test in filter(lambda pair: pair[0].startswith("test_"),
                             sorted(globals().items())):
        test()
        print(f"PASS  {name}")
    print("all green")
