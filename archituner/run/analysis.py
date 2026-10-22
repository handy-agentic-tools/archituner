import os

from archituner.conformance import coverage_tree
from archituner.conformance import measure_shape
from archituner.conformance import pair_readings
from archituner.conformance import topological
from archituner.conformance.chains import chains
from archituner.conformance.neighbours import neighbours
from archituner.contract import boundaries_coverage
from archituner.contract import boundaries_reasons
from archituner.contract import bullet_list
from archituner.contract import layers_table
from archituner.contract import prose_sections
from archituner.contract import read_contract
from archituner.run.prose import measure_prose
from archituner.run.siblings import cross_contract_names
from archituner.source import claim_files
from archituner.source import import_root
from archituner.source import measure_limits
from archituner.source import read_surface
from archituner.source import resolve_imports
from archituner.source.entry import entry_layer


class Analysis(dict):
    def __init__(self, mapping, claims):
        super().__init__(mapping)
        self.claims = claims


def analyse(contract_path, stored=None):
    contract = read_contract(contract_path)
    tree, layers, pairs = contract.tree, contract.layers, contract.pairs
    naming, package_root, body = contract.naming, contract.package_root, contract.body
    findings = list(contract.findings)

    root, retry_prefix, packages = import_root(layers, package_root)

    files, path_by_module, claim_findings, claims = claim_files(
        tree, layers, root, packages, ignore=contract.ignore)
    findings += claim_findings

    edges = resolve_imports(tree, files, path_by_module, retry_prefix)

    sections = prose_sections(body)
    cells = layers_table(sections.get("Layers"))
    allow_pairs = contract.allowed
    reasons, boundary_findings = boundaries_reasons(
        sections.get("Boundaries"), list(layers), allow_pairs)
    findings += boundary_findings
    findings += boundaries_coverage(
        forbidden={p for p, k in pairs.items() if k == "forbid"},
        allowed=allow_pairs, reasons=set(reasons))

    order = topological(list(layers), allow_pairs)
    held = held_counts(files, layers)
    pair_table, counts = pair_readings(order, pairs, edges, reasons, held, stored)
    entry = entry_layer(files)
    layer_chains = chains(list(layers), edges, entry)
    layer_neighbours = neighbours(order, edges)
    shape = measure_shape(list(layers), allow_pairs, edges)
    shape["longest_chain"] = layer_chains["longest_chain"]
    surface = read_surface(tree, files, order, pairs)
    surface["cross_contract"] = cross_contract_names(tree, layers)
    prose_percent = measure_prose(tree, files)
    breaches, limits_findings = measure_limits(
        files, layers, contract.limits, contract.overrides)
    findings += limits_findings

    return Analysis({
        "contract": os.path.basename(contract_path),
        "tree": os.path.basename(tree),
        "order": order,
        "layers": layer_rows(order, files, layers, cells,
                             layer_chains["chain"], layer_neighbours),
        "pairs": pair_table,
        "files": sorted(files.values(), key=lambda r: r["path"]),
        "coverage": coverage_of(files),
        "surface": surface,
        "shape": shape,
        "prose_percent": prose_percent,
        "breaches": breaches,
        "naming": naming,
        "invariants": bullet_list(sections.get("Invariants")),
        "enforcement": sections.get("Enforcement", ""),
        "findings": findings,
        "counts": counts,
    }, claims)


def held_counts(files, layers):
    return {name: sum(1 for r in files.values() if r["layer"] == name)
            for name in layers}


def coverage_of(files):
    return {"tree": coverage_tree(files.values()),
            "claimed": tally(files, True),
            "unclaimed": tally(files, False)}


def tally(files, claimed):
    return sum(1 for f in files.values() if bool(f["layer"]) == claimed)


def layer_rows(order, files, layers, cells, chain, near):
    return [{"name": n, "globs": layers[n], "chain": chain[n],
             "uses": near[n]["uses"], "used_by": near[n]["used_by"],
             "files": sorted(p for p, r in files.items() if r["layer"] == n),
             **cells.get(n, {"responsibility": "", "rationale": ""})}
            for n in order]
