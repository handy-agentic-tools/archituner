try:
    from archituner.presentation.page.shell.page import render
    from archituner.presentation.rejection import render_rejection
except ImportError:
    render = None
    render_rejection = None

UNAVAILABLE = ("the html artifact needs the presentation package, "
               "which this install does not carry")


def page_builder(reading, narrowed, quoted, unclaimed, fmt, colour):
    if render is None:
        return {"status": 2, "lines": [UNAVAILABLE], "artifact": None}
    return {"status": 0, "lines": [], "artifact": render(reading)}


def page_refusal(contract_path, reason):
    if render_rejection is None:
        return {"status": 2, "lines": [UNAVAILABLE], "artifact": None}
    return {"status": 2, "lines": [reason],
            "artifact": render_rejection(contract_path, reason)}
