import os

from archituner.conformance.visibility import file_visible


def _claim_visible(path, narrowing):
    return path is None or file_visible(path, narrowing)


def visible_claims(claims, narrowing):
    return [finding for finding, path in claims
            if _claim_visible(path, narrowing)]


def quoted_lines(tree, witnesses):
    wanted = {}
    for witness in witnesses:
        wanted.setdefault(witness["file"], set()).add(witness["line"])
    quoted = {}
    for path, numbers in sorted(wanted.items()):
        with open(os.path.join(tree, path), encoding="utf-8") as handle:
            body = handle.readlines()
        for number in numbers:
            quoted[(path, number)] = body[number - 1].strip()
    return quoted


def page_lines(reading, contract_path, out):
    counts = reading["counts"]
    lines = [f"{contract_path}",
             f"  layers {len(reading['layers'])}  files {len(reading['files'])}  "
             f"unclaimed {sum(1 for f in reading['files'] if not f['layer'])}",
             f"  convergence {counts['convergence']}  divergence "
             f"{counts['divergence']}  absence {counts['absence']}  "
             f"silence {counts['silence']}",
             f"  findings {len(reading['findings'])}"]
    if reading["change"]:
        moved = reading["change"]["counts"]
        lines.append(f"  vs baseline: improved {moved['improved']}  "
                     f"regressed {moved['regressed']}")
    lines.append(f"  -> {out}")
    return lines
