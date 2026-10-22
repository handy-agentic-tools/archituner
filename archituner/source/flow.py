import ast


def flow_break(nesting, measures):
    measures["cyclomatic"] += 1
    measures["cognitive"] += 1 + nesting


def else_children(orelse, nesting, measures):
    if not orelse:
        return []
    if len(orelse) == 1 and isinstance(orelse[0], ast.If):
        return [(orelse, nesting)]
    measures["cognitive"] += 1 + nesting
    return [(orelse, nesting + 1)]


def branch_of(node, nesting, measures):
    flow_break(nesting, measures)
    children = [(node.test, nesting + 1), (node.body, nesting + 1)]
    children += else_children(node.orelse, nesting, measures)
    return children


def loop_of(node, nesting, measures):
    flow_break(nesting, measures)
    children = [(node.target, nesting + 1), (node.iter, nesting + 1),
                (node.body, nesting + 1)]
    children += else_children(node.orelse, nesting, measures)
    return children


def except_of(node, nesting, measures):
    flow_break(nesting, measures)
    return [(node.type, nesting + 1), (node.body, nesting + 1)]


def match_of(node, nesting, measures):
    if isinstance(node, ast.Match):
        return [(node.subject, nesting), (node.cases, nesting)]
    flow_break(nesting, measures)
    return [(node.guard, nesting + 1), (node.pattern, nesting + 1),
            (node.body, nesting + 1)]


def try_of(node, nesting, measures):
    children = [(node.body, nesting), (node.handlers, nesting)]
    children += else_children(node.orelse, nesting, measures)
    children.append((node.finalbody, nesting))
    return children


def reroute_of(node, nesting, measures):
    measures["cognitive"] += 1 + nesting
    return []
