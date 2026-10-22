from archituner.cli.groups import AXES
from archituner.cli.groups import axis_step
from archituner.cli.singles import format_step
from archituner.cli.singles import out_step
from archituner.cli.singles import weight_step

MODES = {"--baseline": "baseline", "--check": "check",
         "--json": "json", "--report": "report"}
LONELY = ("--baseline", "--check", "--json", "--report")
VALUED = {"--min-weight": weight_step, "--format": format_step, "-o": out_step}


def mode_step(flag, values, state):
    if values or state["mode"] is not None:
        return None
    state["mode"] = MODES[flag]
    return state


def step(flag, values, state):
    if flag in AXES:
        return axis_step(flag, values, state)
    if flag in VALUED:
        return VALUED[flag](flag, values, state)
    if flag in LONELY:
        return mode_step(flag, values, state)
    return None
