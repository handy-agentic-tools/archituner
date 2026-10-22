import ast


def definition_of(node, nesting, measures):
    measures["defs"] += 1
    return [(node.decorator_list, nesting), (node.args, nesting),
            (node.returns, nesting),
            (getattr(node, "type_params", None), nesting),
            (node.body, nesting + 1)]


def class_of(node, nesting, measures):
    measures["defs"] += 1
    return [(node.decorator_list, nesting), (node.bases, nesting),
            (node.keywords, nesting),
            (getattr(node, "type_params", None), nesting),
            (node.body, nesting + 1)]


def lambda_of(node, nesting, measures):
    return [(node.args, nesting), (node.body, nesting + 1)]
