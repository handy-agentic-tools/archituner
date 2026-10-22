def chains(names, edges, entry):
    rank = {name: i for i, name in enumerate(names)}
    successors = {name: [] for name in names}
    for (source, target) in edges:
        if source in successors and target in successors:
            successors[source].append(target)
    chain = {name: None for name in names}
    if entry is None:
        return {"chain": chain, "longest_chain": []}
    best = [entry]
    stack = [[entry]]
    while stack:
        path = stack.pop()
        last = path[-1]
        chain[last] = longer(chain[last], len(path) - 1)
        if better(path, best, rank):
            best = path
        for target in successors[last]:
            if target not in path:
                stack.append(path + [target])
    return {"chain": chain, "longest_chain": best}


def longer(held, links):
    return max(held, links) if held is not None else links


def better(path, held, rank):
    if len(path) != len(held):
        return len(path) > len(held)
    return [rank[n] for n in path] < [rank[n] for n in held]

