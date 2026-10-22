import ast

from archituner.source.definitions import class_of
from archituner.source.definitions import definition_of
from archituner.source.definitions import lambda_of
from archituner.source.flow import branch_of
from archituner.source.flow import except_of
from archituner.source.flow import loop_of
from archituner.source.flow import match_of
from archituner.source.flow import reroute_of
from archituner.source.flow import try_of
from archituner.source.scoring import assertion_of
from archituner.source.scoring import boolop_of
from archituner.source.scoring import comprehension_of
from archituner.source.scoring import ternary_of

HANDLERS = {
    ast.FunctionDef: definition_of,
    ast.AsyncFunctionDef: definition_of,
    ast.ClassDef: class_of,
    ast.Lambda: lambda_of,
    ast.If: branch_of,
    ast.While: branch_of,
    ast.For: loop_of,
    ast.AsyncFor: loop_of,
    ast.ExceptHandler: except_of,
    ast.Match: match_of,
    ast.match_case: match_of,
    ast.Try: try_of,
    ast.TryStar: try_of,
    ast.Break: reroute_of,
    ast.Continue: reroute_of,
    ast.IfExp: ternary_of,
    ast.Assert: assertion_of,
    ast.BoolOp: boolop_of,
    ast.ListComp: comprehension_of,
    ast.SetComp: comprehension_of,
    ast.GeneratorExp: comprehension_of,
    ast.DictComp: comprehension_of,
}


def measures_of(parsed):
    measures = {"defs": 0, "depth": 0, "cyclomatic": 1, "cognitive": 0}
    visit(parsed, 0, measures)
    return measures


def plain_of(node, nesting, measures):
    return [(child, nesting) for child in ast.iter_child_nodes(node)]


def visit(node, nesting, measures):
    if isinstance(node, list):
        for item in node:
            visit(item, nesting, measures)
        return
    if node is None:
        return
    measures["depth"] = max(measures["depth"], nesting)
    children = HANDLERS.get(type(node), plain_of)(node, nesting, measures)
    for child, held in children:
        visit(child, held, measures)
