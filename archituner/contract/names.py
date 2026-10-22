from archituner.contract.refusals import reject


def parent_of(name):
    head, dot, _ = name.rpartition(".")
    return head if dot else None


def non_sibling_pair(src, tgt, layers):
    return src in layers and tgt in layers \
        and parent_of(src) != parent_of(tgt)


def refuse_undeclared_ancestors(layers):
    for name in layers:
        parent = parent_of(name)
        if parent and parent not in layers:
            reject(f"a dotted name's parent is not declared: {name} names {parent}")


def sibling_sets(layers):
    sets = {}
    for name in layers:
        sets.setdefault(parent_of(name), []).append(name)
    return sets
