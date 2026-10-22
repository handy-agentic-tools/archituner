from archituner.matching import glob_matcher
from archituner.matching import match_path
from archituner.source.reading import parent_name
from archituner.vocabulary import Finding


def claims_any(glob, files):
    return any(match_path(glob_matcher(glob), path) for path in files)


def first_matching_glob(globs, path):
    return next(g for g in globs if match_path(glob_matcher(g), path))


def taking_findings(glob, taken, layers, lmap):
    claims = []
    for path in taken:
        layer = lmap.layer_of(path)
        if layer:
            claim = first_matching_glob(layers[layer], path)
            claims.append((Finding(
                text=f"ignore glob {glob} takes {path}, which layer "
                     f"{layer}'s {claim} would claim; ignore wins",
                produced_by=f"ignore glob {glob}, layer {layer} glob {claim}"),
                path))
    return claims


def ignore_findings(walked, layers, lmap, ignore_matchers):
    claims = []
    for glob, matcher in ignore_matchers:
        taken = [path for path in walked if match_path(matcher, path)]
        claims += (taking_findings(glob, taken, layers, lmap) if taken
                   else [(Finding(
                       text=f"ignore glob matches nothing: {glob}",
                       produced_by=f"ignore glob {glob}"), None)])
    return claims


def sublayer_claims(path, layer, layers):
    if not layer:
        return []
    glob = first_matching_glob(layers[layer], path)
    parent = parent_name(layer)
    claims = []
    no_parent_claim = parent is not None and not any(
        match_path(glob_matcher(g), path) for g in layers[parent])
    no_child_claims = any(name.startswith(layer + ".") for name in layers)
    if no_parent_claim:
        claims.append((Finding(
            text=f"{path} is claimed by {layer}'s {glob} but no glob of "
                 f"its parent {parent} claims it",
            produced_by=f"layer {layer}, glob {glob}"), path))
    if no_child_claims:
        claims.append((Finding(
            text=f"{path} is claimed by {layer}'s {glob} and no child "
                 f"claims it",
            produced_by=f"layer {layer}, glob {glob}"), path))
    return claims


def sublayer_findings(files, layers):
    claims = []
    for path, record in files.items():
        claims += sublayer_claims(path, record["layer"], layers)
    return claims


def vacant_findings(files, layers):
    claims = []
    for name, globs in layers.items():
        vacant = [g for g in globs if not claims_any(g, files)]
        for g in vacant:
            claims.append((Finding(text=f"glob matches nothing: {name}: {g}",
                                   produced_by=f"layer {name}, glob {g}"),
                           None))
    return claims
