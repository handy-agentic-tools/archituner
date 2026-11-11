import math

from archituner.presentation.model.layout import UNIT
from archituner.presentation.model.stack_seats import rung

STRIP, RESERVE, BELOW, STEP = UNIT * 2, UNIT * 7, UNIT * 4, UNIT * 3


def rounded(dock):
    return math.floor(dock * 2 + 0.5) / 2


def spread(items, y, zone, seats, docks, flip):
    step = (zone[1] - zone[0]) / max(len(items), 1)
    for k, p in enumerate(sorted(items, key=lambda q: seats[
            q["source"] + "->" + q["target"]])):
        key = p["source"] + "->" + p["target"]
        along = zone[0] + (k + 0.5) * step
        docks[key] = rounded(
            y + (zone[0] + zone[1] - along if flip else along))


def docks(g, order, index, pool, seats):
    leaving, landing, absent = {}, {}, {}
    for name in order:
        leaving[name], landing[name], absent[name] = [], [], []
    exit_dock, entry_dock = {}, {}
    for p in pool:
        leaving[p["source"]].append(p)
        if p["state"] == "absence":
            target = absent[p["target"]]
            y = rung(g, index[p["target"]]) - g["node_h"] / 2
            key = p["source"] + "->" + p["target"]
            entry_dock[key] = rounded(
                y + g["node_h"] - STRIP - BELOW - len(target) * STEP)
            target.append(p)
        else:
            landing[p["target"]].append(p)
    for name in order:
        y = rung(g, index[name]) - g["node_h"] / 2
        hem = g["node_h"] - STRIP
        reserve = RESERVE if absent[name] else 0
        docked = len(leaving[name]) + len(landing[name])
        cut = STRIP + (hem - STRIP - reserve) * len(landing[name]) \
            / max(docked, 1)
        spread(leaving[name], y, (cut, hem - reserve), seats, exit_dock, False)
        spread(landing[name], y, (STRIP, cut), seats, entry_dock, True)
    return exit_dock, entry_dock
