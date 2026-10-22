from archituner.cli.groups import groups_of
from archituner.cli.steps import step


def read(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        return None
    state = {"narrowing": {}, "fmt": None, "mode": None}
    for flag, values in groups_of(argv[2:]):
        state = step(flag, values, state)
        if state is None:
            return None
    mode = state["mode"] or "check"
    fmt = state["fmt"]
    if fmt is not None and mode != "report":
        return None
    return mode, state["narrowing"], fmt
