from operator import itemgetter

from archituner.report.spelling import item_line
from archituner.report.spelling import section_line

CROSSING_KEY = itemgetter("file", "line", "module")


def findings_lines(document, md):
    lines = [section_line("findings", md)]
    findings = document["findings"]
    if not findings:
        lines.append(item_line("no findings", md))
    for finding in findings:
        lines.append(item_line(finding.text, md))
    return lines


def divergences_lines(document, md):
    divergences = {}
    for crossing in document["crossings"]:
        if crossing["state"] == "divergence":
            key = (crossing["source"], crossing["target"])
            divergences.setdefault(key, []).append(crossing)
    if not divergences:
        return []
    pair_at = {(p["source"], p["target"]): p for p in document["pairs"]}
    lines = [section_line("divergences", md)]
    for source, target in sorted(divergences):
        pair = pair_at[(source, target)]
        lines.append(f"  divergence: {source} -> {target}")
        for crossing in sorted(divergences[(source, target)],
                               key=CROSSING_KEY):
            lines.append(f"    {crossing['file']}:{crossing['line']}"
                         f" imports {crossing['module']}")
        if pair["reason"]:
            lines.append(f"    contract: {pair['reason']}")
        lines.append(f"    remedy: {pair['remedy'].text}")
    return lines
