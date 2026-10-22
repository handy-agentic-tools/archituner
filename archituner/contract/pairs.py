from archituner.contract.names import parent_of
from archituner.contract.names import sibling_sets
from archituner.contract.refusals import reject
from archituner.vocabulary import Finding


def judged_edge(kind, edge, layers, pairs, findings):
    source, arrow, target = edge.partition(" -> ")
    if not arrow:
        findings.append(Finding(
            text=f"dependency line is not an edge: {edge}",
            produced_by=f"dependencies.{kind} line: {edge}"))
        return None
    if source not in layers or target not in layers:
        reject(f"edge names an unknown layer: {edge}")
    if parent_of(source) != parent_of(target):
        reject(f"edge is not between siblings: {edge}")
    if source == target:
        findings.append(Finding(
            text=f"a layer names itself, which is not a pair: {edge}",
            produced_by=f"dependencies.{kind} line: {edge}"))
        return None
    if (source, target) in pairs:
        reject(f"pair in both lists: {edge}")
    return source, target


def owed_pairs(members, pairs):
    return [(a, b) for a in members for b in members
            if a != b and (a, b) not in pairs]


def decide_pairs(layers, allow, forbid, findings):
    if not allow and not forbid:
        reject("both dependencies.allow and dependencies.forbid are absent")
    pairs = {}
    for kind, edges in (("allow", allow), ("forbid", forbid)):
        for edge in edges:
            judged = judged_edge(kind, edge, layers, pairs, findings)
            if judged is not None:
                pairs[judged] = kind
    sets = sibling_sets(layers)
    missing = []
    for members in sets.values():
        missing += owed_pairs(members, pairs)
    if missing:
        total = sum(len(members) * (len(members) - 1) for members in sets.values())
        reject(f"pair set is not total, {len(missing)} of {total} "
               f"missing, first: {missing[0][0]} -> {missing[0][1]}")
    return pairs
