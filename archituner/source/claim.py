import os
from operator import itemgetter

from archituner.matching import glob_matcher
from archituner.matching import match_path
from archituner.source.complexity import complexity_of
from archituner.source.findings import ignore_findings
from archituner.source.findings import sublayer_findings
from archituner.source.findings import vacant_findings
from archituner.source.imports import module_of
from archituner.source.walk import source_files
from archituner.vocabulary import SourceFile


class LayerMap:
    def __init__(self, layers):
        self.matchers = [(name, [glob_matcher(g) for g in globs])
                         for name, globs in layers.items()]
        self.matchers.sort(key=lambda entry: entry[0].count("."),
                           reverse=True)

    def layer_of(self, path):
        for name, matchers in self.matchers:
            if path_matched(matchers, path):
                return name
        return None


def path_matched(matchers, path):
    return any(match_path(matcher, path) for matcher in matchers)


def decoded_size(tree, path):
    try:
        with open(os.path.join(tree, path), encoding="utf-8") as handle:
            return len(handle.read())
    except UnicodeDecodeError:
        return None


def record_of(tree, path, layer, module):
    walked_file = SourceFile(path=path, layer=layer)
    return {"path": walked_file.path, "layer": walked_file.layer,
            "module": module,
            "imports": list(walked_file.imports),
            "importers": list(walked_file.importers),
            "size": decoded_size(tree, path),
            **complexity_of(tree, path)}


def named_module(path, layer, module, packages):
    for claimed_layer, static_dir, package in packages:
        if layer == claimed_layer:
            under = module_of(path, static_dir)
            if under is not None:
                return f"{package}.{under}" if under else package
    return module


def claim_files(tree, layers, root, packages=(), ignore=()):
    lmap = LayerMap(layers)
    ignore_matchers = [(glob, glob_matcher(glob)) for glob in ignore]
    walked = sorted(source_files(tree))
    files = {}
    path_by_module = {}
    for path in walked:
        if any(match_path(matcher, path) for _glob, matcher in ignore_matchers):
            continue
        layer = lmap.layer_of(path)
        module = named_module(path, layer, module_of(path, root), packages)
        files[path] = record_of(tree, path, layer, module)
        if module:
            path_by_module[module] = path
    claims = ignore_findings(walked, layers, lmap, ignore_matchers)
    claims += vacant_findings(files, layers)
    claims += sublayer_findings(files, layers)
    findings = list(map(itemgetter(0), claims))
    return files, path_by_module, findings, claims
