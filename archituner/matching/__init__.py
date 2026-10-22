import re


def glob_matcher(pattern):
    parts = []
    for token in re.split(r"(\*\*/|\*\*|\*)", pattern):
        if token == "**/":
            parts.append("(?:[^/]+/)*")
        elif token == "**":
            parts.append(".*")
        elif token == "*":
            parts.append("[^/]*")
        else:
            parts.append(re.escape(token))
    return re.compile("^" + "".join(parts) + "$")


def match_path(matcher, path):
    return matcher.match(path.replace("\\", "/"))
