import ast
import os

from archituner.source.measures import measures_of


def complexity_of(tree, path):
    try:
        parsed = ast.parse(open(os.path.join(tree, path), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return {"defs": 0, "depth": 0, "cyclomatic": 1, "cognitive": 0}
    return measures_of(parsed)
