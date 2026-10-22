from archituner.contract.boundaries import boundaries_coverage
from archituner.contract.boundaries import boundaries_reasons
from archituner.contract.frontmatter import parse_front_matter
from archituner.contract.names import refuse_undeclared_ancestors
from archituner.contract.overlap import overlap_findings
from archituner.contract.pairs import decide_pairs
from archituner.contract.bullets import bullet_list
from archituner.contract.prose import layers_table
from archituner.contract.prose import prose_sections
from archituner.contract.refusals import reject
from archituner.vocabulary import Contract


def read_contract(path):
    layers, allow, forbid, naming, package_root, ignore, limits, overrides, \
        body = parse_front_matter(path)
    if not layers:
        reject("layers is missing or empty")
    empty = [name for name, globs in layers.items() if not globs]
    if empty:
        reject(f"a layer has no globs: {empty[0]}")
    refuse_undeclared_ancestors(layers)
    for number, _selector, _value, _reason in overrides:
        if number not in limits:
            reject(f"an override names a number whose default is absent: "
                   f"{number}")

    findings = []
    pairs = decide_pairs(layers, allow, forbid, findings)
    findings += overlap_findings(layers)
    return Contract(path=path, layers=layers, pairs=pairs, naming=naming,
                    package_root=package_root, body=body, findings=findings,
                    ignore=ignore, limits=limits, overrides=overrides)
