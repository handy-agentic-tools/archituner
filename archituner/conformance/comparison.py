from archituner.vocabulary import Reading


def baseline_of(result):
    return {
        "layers": [layer["name"] for layer in result["layers"]],
        "pairs": {f"{p['source']} -> {p['target']}": p["state"] for p in result["pairs"]},
        "files": {f["path"]: f["layer"] for f in result["files"]},
    }


IMPROVED = {("divergence", "silence"), ("absence", "convergence")}
REGRESSED = {("silence", "divergence"), ("convergence", "absence")}


def reading_of(value):
    if isinstance(value, Reading):
        return value
    return (Reading.from_baseline(value) if isinstance(value["pairs"], dict)
            else Reading.from_analysis(value))


ABSENT = object()


def move_of(was, state):
    if (was, state) in IMPROVED:
        return "improved"
    if (was, state) in REGRESSED:
        return "regressed"
    return "unchanged"


def pair_moves(current, stored, shared):
    moves = {}
    for (source, target), state in current.pairs.items():
        was = stored.pairs.get((source, target))
        if was is not None and {source, target} <= shared:
            moves[f"{source} -> {target}"] = move_of(was, state)
    return moves, len(current.pairs) - len(moves)


def dropped_file(was, shared):
    return was is ABSENT or (was is not None and was not in shared)


def file_result(was, layer):
    if was == layer:
        return ("unchanged", None)
    if was is None:
        return ("improved", None)
    if layer is None:
        return ("regressed", None)
    return ("unchanged", {"was": was, "now": layer} if was and layer else None)


def file_moves(current, stored, shared):
    outcomes, relocations = {}, {}
    for path, layer in current.files.items():
        was = stored.files.get(path, ABSENT)
        if not dropped_file(was, shared):
            outcomes[path], move = file_result(was, layer)
            if move is not None:
                relocations[path] = move
    return outcomes, relocations, len(current.files) - len(outcomes)


def compare(current, stored):
    current, stored = reading_of(current), reading_of(stored)
    shared = set(stored.layers) & set(current.layers)
    dropped_layers = sorted(set(stored.layers) ^ set(current.layers))
    moves, dropped = pair_moves(current, stored, shared)
    files, relocations, dropped_files = file_moves(current, stored, shared)
    tally = lambda table: {outcome: list(table.values()).count(outcome)
                           for outcome in ("improved", "unchanged", "regressed")}
    return {"pairs": moves, "dropped": dropped, "dropped_layers": dropped_layers,
            "counts": tally(moves),
            "files": files, "relocations": relocations,
            "dropped_files": dropped_files, "file_counts": tally(files)}
