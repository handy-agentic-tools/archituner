import ast

from archituner.source.flow import flow_break


def ternary_of(node, nesting, measures):
    flow_break(nesting, measures)
    return [(node.test, nesting), (node.body, nesting),
            (node.orelse, nesting)]


def assertion_of(node, nesting, measures):
    flow_break(nesting, measures)
    return [(node.test, nesting), (node.msg, nesting)]


def boolop_of(node, nesting, measures):
    extra = len(node.values) - 1
    measures["cyclomatic"] += extra
    measures["cognitive"] += extra * (1 + nesting)
    return [(node.values, nesting)]


def comprehension_of(node, nesting, measures):
    children = []
    innermost = nesting
    for clause in node.generators:
        flow_break(innermost, measures)
        children.append((clause.target, innermost + 1))
        children.append((clause.iter, innermost + 1))
        for condition in clause.ifs:
            measures["cyclomatic"] += 1
            measures["cognitive"] += 2 + innermost
            children.append((condition, innermost + 1))
        innermost += 1
    if isinstance(node, ast.DictComp):
        children.append((node.key, innermost))
        children.append((node.value, innermost))
    else:
        children.append((node.elt, innermost))
    return children
