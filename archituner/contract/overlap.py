from archituner.matching import glob_matcher
from archituner.matching import match_path
from archituner.vocabulary import Finding


def probe_path(pattern):
    return (pattern.replace("**/", "probe/")
                   .replace("**", "probe/probe.py")
                   .replace("*", "probe"))


def claimed_elsewhere(pattern, globs):
    return any(match_path(glob_matcher(g), probe_path(pattern)) for g in globs)


def strangers(i, j, name, other, seen):
    if i == j or (min(i, j), max(i, j)) in seen:
        return False
    return not (name.startswith(other + ".") or other.startswith(name + "."))


def overlap_findings(layers):
    findings = []
    names = list(layers)
    seen = set()
    for i, name in enumerate(names):
        for j, other in enumerate(names):
            if not strangers(i, j, name, other, seen):
                continue
            pattern = next((p for p in layers[name]
                            if claimed_elsewhere(p, layers[other])), None)
            if pattern is not None:
                winner, loser = (name, other) if i < j else (other, name)
                findings.append(Finding(
                    text=f"globs overlap: {name}'s {pattern} and {other}'s globs can claim "
                         f"one path; first match wins, so {winner} takes it and {loser} "
                         f"never sees it",
                    produced_by=f"layers {name} and {other}, glob {pattern}"))
                seen.add((min(i, j), max(i, j)))
    return findings
