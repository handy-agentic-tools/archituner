FORMATS = ("md",)


def weight_step(flag, values, state):
    if len(values) != 1:
        return None
    try:
        state["narrowing"]["min-weight"] = int(values[0])
    except ValueError:
        return None
    return state


def format_step(flag, values, state):
    if len(values) != 1 or values[0] not in FORMATS:
        return None
    state["fmt"] = values[0]
    return state


def out_step(flag, values, state):
    if len(values) != 1 or state["mode"] is not None:
        return None
    state["mode"] = "render"
    return state
