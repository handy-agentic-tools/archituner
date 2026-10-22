from archituner.vocabulary.states import STATES


def check_reading(layers, pairs):
    declared = set(layers)
    named = set()
    for (source, target), state in pairs.items():
        check_pair(source, target, state)
        named.update((source, target))
    check_declared(named, declared, pairs)


def check_pair(source, target, state):
    if source == target:
        raise ValueError(f"source equals target: {source}")
    if state not in STATES:
        raise ValueError(f"not a state: {state!r}")


def check_declared(named, declared, pairs):
    for name in sorted(named - declared):
        check_total(name, named, pairs)


def check_total(name, named, pairs):
    for other in named:
        if other != name:
            check_arrows(name, other, pairs)


def check_arrows(name, other, pairs):
    if (name, other) not in pairs or (other, name) not in pairs:
        raise ValueError(f"pair names a layer the reading does not have: {name}")
