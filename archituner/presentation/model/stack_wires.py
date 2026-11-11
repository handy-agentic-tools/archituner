from archituner.presentation.model.layout import UNIT
from archituner.presentation.model.stack_docks import docks
from archituner.presentation.model.stack_seats import lanes
from archituner.presentation.model.stack_seats import WRAP

DROP, PAST = UNIT * 4, UNIT * 1


def spell(number):
    return int(number) if number == int(number) else number


def passes(vx, lx, near, far, clear):
    return near < vx < far and abs(vx - lx) > clear


def lands_between(held, other, y):
    lo, hi = held[other]
    return lo + PAST < y < hi - PAST


def meet(held, other, vx, edge, lx, y1, y2, near, far, clear, out, inn):
    if not passes(vx, lx, near, far, clear):
        return
    if lands_between(held, other, y1):
        out.append((abs(edge - vx), vx))
    if lands_between(held, other, y2):
        inn.append((abs(lx - vx), vx))


def crossings(pool, x, held, p, edge, y1, y2, hop):
    lx = x[p["source"] + "->" + p["target"]]
    near, far = min(lx, edge), max(lx, edge)
    clear = hop + WRAP
    out, inn = [], []
    for q in pool:
        if q is not p:
            other = q["source"] + "->" + q["target"]
            meet(held, other, x[other], edge, lx, y1, y2,
                 near, far, clear, out, inn)
    return out, inn


def hopped(marks):
    return [spell(v) for _, v in sorted(marks)]


def wire_of(edge, key, x, y1, y2, out, inn):
    return {"x": spell(edge), "a": spell(y1), "b": spell(y2),
            "l": spell(x[key]), "my": spell((y1 + y2) / 2 + DROP),
            "hops_out": hopped(out), "hops_in": hopped(inn)}


def routed(g, order, pool, edge, anchor, span, sign):
    index = {name: i for i, name in enumerate(order)}
    seats, count = lanes(g, index, pool)
    exit_dock, entry_dock = docks(g, order, index, pool, seats)
    pitch = span / count
    x, held = {}, {}
    for key, seat in seats.items():
        x[key] = anchor + sign * (seat + 0.5) * pitch
    for p in pool:
        key = p["source"] + "->" + p["target"]
        held[key] = (min(exit_dock[key], entry_dock[key]),
                     max(exit_dock[key], entry_dock[key]))
    wires = {}
    for p in pool:
        key = p["source"] + "->" + p["target"]
        y1, y2 = exit_dock[key], entry_dock[key]
        out, inn = crossings(pool, x, held, p, edge, y1, y2, g["hop"])
        wires[key] = wire_of(edge, key, x, y1, y2, out, inn)
    return wires
