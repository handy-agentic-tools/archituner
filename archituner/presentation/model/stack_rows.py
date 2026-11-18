def parent_of(name):
    return name.rpartition(".")[0]


def under_of(declared):
    known = set(declared)
    under = {}
    for name in declared:
        if parent_of(name) in known:
            under.setdefault(parent_of(name), []).append(name)
    return under


def family(name, under, rows):
    rows.append(name)
    for child in under.get(name, ()):
        family(child, under, rows)


def display_order(order, declared):
    known = set(declared)
    under = under_of(declared)
    rows = []
    for name in order:
        if parent_of(name) in known:
            continue
        family(name, under, rows)
    return rows


def depth_of(name):
    return name.count(".")
