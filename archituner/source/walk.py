import os
import re

from archituner.matching import glob_matcher


SKIPPED_DIRECTORIES = {"__pycache__", ".git"}


def gitignore_rule_of(line):
    pattern = line.rstrip("\n").strip()
    if not pattern or pattern.startswith("#"):
        return None
    negated = pattern.startswith("!")
    pattern = pattern.removeprefix("!")
    directory_only = pattern.endswith("/")
    pattern = pattern.rstrip("/")
    anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
    pattern = pattern.lstrip("/")
    body = glob_matcher(pattern).pattern[1:-1]
    prefix = "" if anchored else "(?:.*/)?"
    return re.compile(f"^{prefix}{body}(?:/.*)?$"), negated, directory_only


def gitignore_rules(tree):
    path = os.path.join(tree, ".gitignore")
    if not os.path.exists(path):
        return []
    rules = []
    for line in open(path, encoding="utf-8"):
        rule = gitignore_rule_of(line)
        if rule is not None:
            rules.append(rule)
    return rules


def directory_applies(directory_only, is_directory):
    return not directory_only or is_directory


def ignored(relative_path, rules, is_directory):
    decision = False
    for matcher, negated, directory_only in rules:
        if directory_applies(directory_only, is_directory) \
                and matcher.match(relative_path):
            decision = not negated
    return decision


def kept(name, directory, rules, here):
    return (name not in SKIPPED_DIRECTORIES
            and not os.path.exists(os.path.join(directory, name, ".git"))
            and not ignored(here + name, rules, is_directory=True))


def kept_directories(directory, subdirectories, rules, here):
    return [name for name in subdirectories
            if kept(name, directory, rules, here)]


def python_files(filenames, here, rules):
    return [here + filename for filename in filenames
            if filename.endswith(".py")
            if not ignored(here + filename, rules, is_directory=False)]


def source_files(tree):
    rules = gitignore_rules(tree)
    for directory, subdirectories, filenames in os.walk(tree):
        here = os.path.relpath(directory, tree).replace(os.sep, "/")
        here = "" if here == "." else here + "/"
        subdirectories[:] = kept_directories(directory, subdirectories,
                                             rules, here)
        yield from python_files(filenames, here, rules)
