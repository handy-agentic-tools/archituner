import ast
import os


def assigns_all(node):
    return any(isinstance(t, ast.Name) and t.id == "__all__"
               for t in node.targets)


def assigned_all(node):
    if not isinstance(node, ast.Assign):
        return None
    if not assigns_all(node):
        return None
    try:
        value = ast.literal_eval(node.value)
    except (ValueError, SyntaxError):
        return None
    if not isinstance(value, (list, tuple)):
        return None
    return [name for name in value if isinstance(name, str)]


def declared_all(parsed):
    declared = None
    for node in parsed.body:
        own = assigned_all(node)
        if own is not None:
            declared = own
    return declared


def parsed_or_none(tree, path, record, entry):
    if record["layer"] != entry:
        return None
    try:
        return ast.parse(
            open(os.path.join(tree, path), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError):
        return None


def parsed_of(tree, files, entry):
    parsed = {}
    for path, record in files.items():
        body = parsed_or_none(tree, path, record, entry)
        if body is not None:
            parsed[path] = body
    return parsed


def public_names(node):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) \
            and not node.name.startswith("_"):
        return [node.name]
    if not isinstance(node, ast.Assign):
        return []
    return [target.id for target in node.targets
            if isinstance(target, ast.Name)
            and not target.id.startswith("_")]


def names_of(tree_):
    names = []
    for node in tree_.body:
        names += public_names(node)
    return names
