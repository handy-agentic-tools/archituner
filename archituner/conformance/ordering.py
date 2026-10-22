def topological(names, allow_pairs):
    remaining = list(names)
    order = []
    while remaining:
        free = [n for n in remaining
                if not any((m, n) in allow_pairs for m in remaining if m != n)]
        if not free:
            free = [remaining[0]]
        order += free
        remaining = [n for n in remaining if n not in free]
    return order


def longest_path(order, allow_pairs):
    rank = dict(zip(order, range(len(order))))
    ranked = [(rank[s], s, t) for (s, t) in allow_pairs if rank[t] > rank[s]]
    ranked.sort(reverse=True)
    longest = dict.fromkeys(order, 0)
    for (_, s, t) in ranked:
        longest[s] = max(longest[s], longest[t] + 1)
    return max(longest.values(), default=0)


def measure_shape(names, allow_pairs, edges):
    fan = {n: {"out": 0, "in": 0, "out_realised": 0, "in_realised": 0} for n in names}
    for (s, t) in allow_pairs:
        fan[s]["out"] += 1
        fan[t]["in"] += 1
        if (s, t) in edges:
            fan[s]["out_realised"] += 1
            fan[t]["in_realised"] += 1
    realised = sum(1 for p in allow_pairs if p in edges)
    return {"per_layer": [{"name": n, **fan[n]} for n in names],
            "longest_path": longest_path(topological(names, allow_pairs),
                                         allow_pairs),
            "permitted": len(allow_pairs), "realised": realised}
