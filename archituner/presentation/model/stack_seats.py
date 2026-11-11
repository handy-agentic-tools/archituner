from archituner.presentation.model.layout import UNIT

HEM_IN, LANDS = UNIT * 1, UNIT * 9
GUARD, WRAP = UNIT * 3, UNIT * 2


def rung(g, i):
    return g["pad"] + i * g["row"] + g["node_h"] / 2


def claim_of(g, index, p):
    lo = min(rung(g, index[p["source"]]), rung(g, index[p["target"]]))
    hi = max(rung(g, index[p["source"]]), rung(g, index[p["target"]]))
    hem = g["node_h"] / 2 + HEM_IN
    return (lo - hem, hi + hem
            + (LANDS if p["state"] == "absence" else 0))


def meets(claim, lo, hi):
    return lo < claim[1] + GUARD and hi > claim[0] - GUARD


def wraps(claim, lo, hi):
    return claim[0] <= lo + WRAP and claim[1] >= hi - WRAP


def seat_against(claims, seats, lo, hi):
    seat = 0
    taken = set()
    for other, claim in claims.items():
        if not meets(claim, lo, hi):
            continue
        taken.add(seats[other])
        if wraps(claim, lo, hi):
            seat = max(seat, seats[other] + 1)
    while seat in taken:
        seat += 1
    return seat


def lanes(g, index, pool):
    ranked = []
    for i, p in enumerate(pool):
        lo, hi = claim_of(g, index, p)
        ranked.append((-(hi - lo), lo, i, hi))
    ranked.sort()
    seats, claims = {}, {}
    count = 1
    for _, lo, i, hi in ranked:
        key = pool[i]["source"] + "->" + pool[i]["target"]
        seats[key] = seat_against(claims, seats, lo, hi)
        claims[key] = (lo, hi)
        count = max(count, seats[key] + 1)
    return seats, count
