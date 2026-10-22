import ast
import io
import re
import sys
import tokenize

MARKUP_OPENER = "<" + "!--"
BLOCK_OPENER = "/" + "*"
LINE_COMMENT = "/" + "/"
SHEBANG = "#!"
COVERS = "# covers:"

FSTRING_MIDDLE = getattr(tokenize, "FSTRING_MIDDLE", -1)
STRING_TOKENS = (tokenize.STRING, FSTRING_MIDDLE)

SCOPES = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)

COMMENT_FORMS = re.compile("|".join((re.escape(MARKUP_OPENER),
                                     re.escape(BLOCK_OPENER))))
LINE_FORMS = re.compile("(?<!:)" + re.escape(LINE_COMMENT))


def refused_spots(value):
    return [match.start()
            for match in (*COMMENT_FORMS.finditer(value),
                          *LINE_FORMS.finditer(value))]


def form_rows(row, value):
    return [(row + value.count("\n", 0, at), "comment form")
            for at in refused_spots(value)]


def allowed_comment(token, covers_row):
    return any(token.start == (row, 0) and token.string.startswith(marker)
               for row, marker in ((1, SHEBANG), (covers_row, COVERS)))


def token_findings(data):
    found = []
    covers_row = 2 if data.startswith(SHEBANG.encode()) else 1
    for token in tokenize.tokenize(io.BytesIO(data).readline):
        if token.type == tokenize.COMMENT:
            if not allowed_comment(token, covers_row):
                found.append((token.start[0], "comment"))
        elif token.type in STRING_TOKENS:
            found += form_rows(token.start[0], token.string)
    return found


def docstring_rows(node):
    if not isinstance(node, SCOPES) or not node.body:
        return []
    first = node.body[0]
    if not isinstance(first, ast.Expr):
        return []
    value = first.value
    if isinstance(value, ast.JoinedStr) or (
            isinstance(value, ast.Constant) and isinstance(value.value, str)):
        return [(value.lineno, "docstring")]
    return []


def docstring_findings(data):
    found = []
    for node in ast.walk(ast.parse(data)):
        found += docstring_rows(node)
    return found


def findings(data):
    return sorted(set(token_findings(data) + docstring_findings(data)))


def main(paths):
    refused = False
    for path in paths:
        with open(path, "rb") as handle:
            data = handle.read()
        for row, reason in findings(data):
            print(f"{path}:{row} {reason}")
            refused = True
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
