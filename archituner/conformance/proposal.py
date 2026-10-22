from archituner.vocabulary import Finding


def statements(witnesses):
    return sorted({(w["file"], w["line"]) for w in witnesses})


def vacant(pair):
    return [name for name, held in ((pair["source"], pair["source_files"]),
                                    (pair["target"], pair["target_files"]))
            if not held]


def divergence_proposal(pair):
    lines = statements(pair["imports"])
    where, line = lines[0]
    files = len({path for path, _ in lines})
    return Finding(
        text=f"remove the {len(lines)} import statement(s) in {files} file(s) "
             f"crossing {pair['source']} -> {pair['target']}, starting with "
             f"{where}:{line}",
        produced_by=f"{len(pair['imports'])} witness(es) resolved from "
                    f"{len(lines)} import statement(s) in {files} file(s)")


def absence_proposal(pair):
    source, target = pair["source"], pair["target"]
    was = pair["was"]
    drawn_from = (f"{source} holds {pair['source_files']} file(s), "
                  f"{target} holds {pair['target_files']} file(s); "
                  + (f"the stored baseline reads the pair as {was}" if was
                     else "no stored baseline reads the pair"))
    empty = vacant(pair)
    if empty:
        text = (f"nothing exercises {source} -> {target} because the tree gives "
                f"{' and '.join(empty)} no file at all, so the edge is "
                f"unfireable until that code is written")
    elif was in ("convergence", "divergence"):
        text = (f"nothing exercises {source} -> {target} now, though the stored "
                f"baseline reads it as a {was}: the crossing was written once "
                f"and has since gone, which is a deletion to account for rather "
                f"than a permission never taken up")
    elif was == "silence":
        text = (f"nothing exercises {source} -> {target}, and the stored "
                f"baseline reads it as a silence: the permission is newer than "
                f"the baseline, so no code has yet been written under it")
    else:
        text = (f"nothing exercises {source} -> {target}, and this run cannot "
                f"tell an unwritten crossing from a stale permission: both "
                f"layers hold files and "
                + (f"the stored baseline reads it as {was} too" if was
                   else "no stored baseline reads this pair")
                + ", so what would separate the two is an earlier reading in "
                  "which the pair was realised")
    return Finding(text=text, produced_by=drawn_from)


def proposal(pair):
    if pair["state"] == "divergence":
        return divergence_proposal(pair)
    if pair["state"] == "absence":
        return absence_proposal(pair)
    return None


def remedy(pair):
    proposed = proposal(pair)
    return proposed.text if proposed else ""
