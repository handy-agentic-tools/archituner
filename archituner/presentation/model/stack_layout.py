from archituner.presentation.model.layout import stack_geometry
from archituner.presentation.model.layout import UNIT
from archituner.presentation.model.stack_wires import routed
from archituner.presentation.model.stack_wires import spell

INSET = UNIT * 8
NUDGE = UNIT * 0.5
HEADER_Y = UNIT * 10
IN, OUT = UNIT * 1, -UNIT * 1


def bands_of(pairs, wide):
    left, right = [], []
    for p in pairs:
        side = left
        if wide and p["state"] == "divergence":
            side = right
        if p["state"] != "silence":
            side.append(p)
    return left, right


def stage(g, order, pairs, wide):
    left, right = bands_of(pairs, wide)
    box = g["margin"] + g["band_l"] + g["gap_l"]
    edge = box + g["node_w"]
    width = edge + (g["margin"] + g["band_r"] if right else 0) + g["margin"]
    wires = routed(g, order, left, box, g["margin"], g["band_l"], IN)
    if right:
        wires.update(routed(g, order, right, edge, width - g["margin"],
                            g["band_r"], OUT))
    cell = g["cell"]
    return {"width": spell(width), "height": len(order) * g["row"] + g["pad"] * 2,
            "cell": spell(cell), "head_y": spell(g["pad"] - HEADER_Y),
            "hop": spell(g["hop"]),
            "centres": [spell(edge - cell * (4 - k) + cell / 2)
                        for k in range(4)],
            "nodes": [{"name": name, "x": spell(box),
                       "y": g["pad"] + i * g["row"], "width": g["node_w"],
                       "height": g["node_h"]}
                      for i, name in enumerate(order)],
            "wires": wires}


def stack(order, pairs):
    return stage(stack_geometry(), order, pairs, True)
