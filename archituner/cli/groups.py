AXES = {"--state": "state", "--layer": "layer", "--file": "file"}


def groups_of(rest):
    groups = []
    for token in rest:
        if token.startswith("-"):
            groups.append((token, []))
        elif groups:
            groups[-1][1].append(token)
        else:
            groups.append((None, [token]))
    return groups


def axis_step(flag, values, state):
    if not values:
        return None
    state["narrowing"].setdefault(AXES[flag], []).extend(values)
    return state
