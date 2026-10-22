from archituner.contract.names import non_sibling_pair
from archituner.contract.names import parent_of
from archituner.vocabulary import Finding


def wildcard_edges(src, spans, span, layers, allow_pairs):
    exceptions = set(spans[spans.index(span) + 1:])
    edges = []
    for other in layers:
        if other == src or other in exceptions:
            continue
        if parent_of(other) != parent_of(src):
            continue
        if (src, other) in allow_pairs:
            continue
        edges.append((src, other))
    return edges


def read_spans(head, spans, layers, allow_pairs):
    edges, findings = [], []
    for span in spans:
        src, arrow, tgt = span.partition(" -> ")
        if not arrow:
            continue
        if tgt == "*":
            edges += wildcard_edges(src, spans, span, layers, allow_pairs)
            return edges, findings
        if non_sibling_pair(src, tgt, layers):
            findings.append(Finding(
                text=f"Boundaries line names a non-sibling pair: "
                     f"{src} -> {tgt}",
                produced_by=f"Boundaries line: {head.strip()[:80]}"))
        else:
            edges.append((src, tgt))
    return edges, findings
