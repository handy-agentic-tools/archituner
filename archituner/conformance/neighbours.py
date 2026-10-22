def neighbours(names, edges):
    rank = {name: position for position, name in enumerate(names)}
    uses = {name: set() for name in names}
    for (source, target) in edges:
        if source in uses and target in uses and source != target:
            uses[source].add(target)
    return {name: {"uses": sorted(uses[name], key=rank.__getitem__),
                   "used_by": [other for other in names
                               if name in uses[other]]}
            for name in names}
