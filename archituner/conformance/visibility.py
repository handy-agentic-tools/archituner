from archituner.vocabulary import REALISED


def pair_visible(pair, narrowing):
    states = narrowing.get("state")
    layers = narrowing.get("layer")
    return ((not states or pair["state"] in states)
            and (not layers
                 or (pair["source"] in layers and pair["target"] in layers))
            and len(pair["imports"]) >= narrowing.get("min-weight", 0))


def under(path, asked):
    asked = asked.rstrip("/")
    return not asked or (path + "/").startswith(asked + "/")


def file_visible(path, narrowing):
    paths = narrowing.get("file")
    return not paths or any(under(path, asked) for asked in paths)


def scoped_pair(pair, narrowing):
    if not pair_visible(pair, narrowing):
        return None
    witnesses = [w for w in pair["imports"]
                 if file_visible(w["file"], narrowing)]
    if not witnesses:
        return None
    return dict(pair, imports=witnesses)


def scoped_pairs(pairs, narrowing):
    scoped = []
    for pair in pairs:
        narrowed = scoped_pair(pair, narrowing)
        if narrowed is not None:
            scoped.append(narrowed)
    return scoped


def narrow(result, narrowing):
    pairs = scoped_pairs(result["pairs"], narrowing)
    return {"pairs": pairs,
            "breaches": [b for b in result["breaches"]
                         if file_visible(b["file"], narrowing)],
            "files": [f for f in result["files"]
                      if file_visible(f["path"], narrowing)],
            "witnesses": [w for p in pairs if p["state"] in REALISED
                          for w in p["imports"]],
            "diverged": any(p["state"] == "divergence" for p in pairs),
            "narrowing": narrowing}
