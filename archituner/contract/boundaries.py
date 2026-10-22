import re

from archituner.contract.edges import read_spans
from archituner.vocabulary import Finding


def boundaries_reasons(text, layers, allow_pairs):
    reasons, findings = {}, []
    for raw in (text or "").split("\n- "):
        bullet = raw.strip().lstrip("- ").strip()
        if not bullet:
            continue
        head, sep, reason = bullet.partition(":")
        if not sep:
            continue
        spans = re.findall(r"`([^`]+)`", head)
        edges, noted = read_spans(head, spans, layers, allow_pairs)
        if not edges and spans and not noted:
            findings.append(Finding(
                text=f"Boundaries line names no real edge: {head.strip()[:80]}",
                produced_by=f"Boundaries line: {head.strip()[:80]}"))
        findings += noted
        for edge in edges:
            reasons[edge] = reason.strip()
    return reasons, findings


def boundaries_coverage(forbidden, allowed, reasons):
    findings = [Finding(text=f"forbidden pair reached by no Boundaries line: {s} -> {t}",
                        produced_by=f"pair {s} -> {t}")
                for s, t in sorted(forbidden - set(reasons))]
    findings += [Finding(text=f"Boundaries line claims an allowed pair is forbidden: {s} -> {t}",
                         produced_by=f"pair {s} -> {t}")
                 for s, t in sorted(set(reasons) & allowed)]
    return findings
