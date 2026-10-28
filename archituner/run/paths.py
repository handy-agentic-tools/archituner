import os
import subprocess

from archituner.vocabulary import Finding


GIT_SECONDS = 10


def normalise(tree, asked):
    return os.path.relpath(asked, tree) if os.path.isabs(asked) \
        else os.path.normpath(asked)


def prefix(tree, path):
    if path == ".":
        return ""
    if os.path.isdir(os.path.join(tree, path)):
        return path + "/"
    return path


def git_index(tree):
    try:
        listed = subprocess.run(["git", "ls-files"], cwd=tree,
                                capture_output=True, text=True,
                                timeout=GIT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if listed.returncode != 0:
        return set()
    return set(listed.stdout.splitlines())


def head_carries(tree, path):
    try:
        head = subprocess.run(["git", "cat-file", "-e", f"HEAD:./{path}"],
                              cwd=tree, capture_output=True,
                              timeout=GIT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return head.returncode == 0


def git_knows(tree, index, path):
    if path in index:
        return True
    return head_carries(tree, path)


def file_axis(tree, narrowing):
    asked = narrowing.get("file")
    if not asked:
        return narrowing, []
    paths = [prefix(tree, normalise(tree, raw)) for raw in asked]
    index = git_index(tree)
    findings = [Finding(text=f"--file path not found on disk or in git: {p}",
                        produced_by=f"--file {raw}")
                for raw, p in zip(asked, paths)
                if not os.path.exists(os.path.join(tree, p))
                and not git_knows(tree, index, p)]
    return dict(narrowing, file=paths), findings
