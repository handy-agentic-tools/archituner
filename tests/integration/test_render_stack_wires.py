# covers: archituner/presentation/model/stack_layout.py archituner/presentation/model/layout.py archituner/presentation/page/shell/page.py
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PAYLOAD = "const DATA = "


def render():
    page = os.path.join(tempfile.mkdtemp(), "page.html")
    done = subprocess.run([sys.executable, "-m", "archituner",
                           os.path.join(REPO, "ARCHITECTURE.md"), "-o", page],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    with open(page, encoding="utf-8") as handle:
        return handle.read()


PAGE = render()
DATA = json.loads(next(line for line in PAGE.splitlines()
                       if line.startswith(PAYLOAD))[len(PAYLOAD):].rstrip(";"))
ORDER = DATA["order"]
STACK = DATA.get("stack") or {}
WIRES = STACK.get("wires") or {}
EDGE = (STACK.get("nodes") or [{"x": 0}])[0]["x"]
SEATS = {"x", "a", "b", "l", "my", "hops_out", "hops_in"}
RUNS = [(k, x, w["a"]) for k, w in WIRES.items() for x in w["hops_out"]]
RUNS += [(k, x, w["b"]) for k, w in WIRES.items() for x in w["hops_in"]]
LANES = {}
for key, wire in WIRES.items():
    LANES.setdefault(round(wire["l"], 6), []).append(
        (min(wire["a"], wire["b"]), max(wire["a"], wire["b"])))
for runs in LANES.values():
    runs.sort()
MEETS = [(lane, runs[near], runs[near + 1]) for lane, runs in LANES.items()
         for near in range(len(runs) - 1)]
LANEX = {round(wire["l"], 6) for wire in WIRES.values()}
GUARD = ("issue 283: the payload carries no wire per drawn pair, so the "
         "stack still lays curved arcs out and no wire can be judged: "
         + json.dumps(STACK, sort_keys=True)[:600])


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


def test_every_drawn_pair_is_one_wire_on_the_box_edge():
    drawn = {p["source"] + "->" + p["target"] for p in DATA["pairs"]
             if p["state"] != "silence"}
    assert WIRES, GUARD
    assert set(WIRES) == drawn, ("issue 283: the wires and the drawn pairs "
        "disagree - every drawn pair is one wire and silence draws none: "
        + json.dumps(sorted(set(WIRES) ^ drawn)))
    stray = list(filter(lambda key: WIRES[key].keys() != SEATS, WIRES))
    assert not stray, ("issue 283: a wire carries faces no right-angled "
        "path owns - the curve's control is among them: "
        + json.dumps({k: sorted(WIRES[k].keys() ^ SEATS) for k in stray}))
    bent = list(filter(lambda item: sum(map(int, (
        item[1]["x"] == EDGE, 0 < item[1]["l"] < item[1]["x"],
        item[1]["my"] == (item[1]["a"] + item[1]["b"]) / 2 + 4))) != 3,
        WIRES.items()))
    assert not bent, ("issue 283: a wire does not dock on the boxes' left "
        "edge with its own lane in the band beside it, or its state mark "
        "stands off the middle of its vertical run: "
        + json.dumps(dict(bent), sort_keys=True))


def test_hops_name_lanes_and_lanes_never_share_a_crossing():
    assert WIRES, GUARD
    stray = list(filter(lambda run: round(run[1], 6) not in LANEX, RUNS))
    assert not stray, ("issue 283: a hop bridges no wire's vertical lane - "
        "a crossing is a horizontal run passing a lane, nothing else: "
        + json.dumps(stray[:8]))
    met = list(filter(lambda pair: pair[2][0] - pair[1][1] < 3, MEETS))
    assert not met, ("issue 283: two wires share a lane whose vertical runs "
        "could meet, so the lanes are not shared only between wires that "
        f"never meet: {met[:4]}")


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
