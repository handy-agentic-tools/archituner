from archituner.conformance.proposal import proposal
from archituner.vocabulary import Pair
from archituner.vocabulary import Reading
from archituner.vocabulary import STATES


def pair_readings(order, pairs, edges, reasons, held, stored=None):
    prior = Reading.from_baseline(stored).pairs if stored else {}
    states = {}
    for key, kind in pairs.items():
        realised = key in edges
        states[key] = ("convergence" if kind == "allow" and realised else
                       "divergence" if kind == "forbid" and realised else
                       "absence" if kind == "allow" else "silence")
    table = []
    place = {name: at for at, name in enumerate(order)}
    for s, t in sorted(pairs, key=lambda key: (place[key[0]], place[key[1]])):
        pair = Pair(source=s, target=t, kind=pairs[(s, t)],
                    state=states[(s, t)],
                    witnesses=tuple(edges.get((s, t), ())))
        row = {"source": pair.source, "target": pair.target,
               "kind": pair.kind, "state": pair.state,
               "reason": reasons.get((s, t), ""),
               "imports": list(pair.witnesses),
               "source_files": held.get(s, 0), "target_files": held.get(t, 0),
               "was": prior.get((s, t))}
        row["remedy"] = proposal(row)
        table.append(row)
    counts = {s: sum(1 for v in states.values() if v == s) for s in STATES}
    return table, counts
