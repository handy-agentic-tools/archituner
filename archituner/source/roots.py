import os


def glob_package(glob):
    static = glob.split("*", 1)[0].rstrip("/")
    return static.rsplit("/", 1)[-1] if static else None


def import_root(layers, declared):
    all_globs = [g for globs in layers.values() for g in globs]
    prefix = os.path.commonprefix(all_globs)
    prefix = prefix[:prefix.rfind("/") + 1] if "/" in prefix else ""
    if not declared:
        shared = prefix.rstrip("/").replace("/", ".")
        if shared:
            return "", (shared,), ()
        return "", (), tuple((name, _glob_dir(g), glob_package(g))
                             for name, globs in layers.items() for g in globs
                             if glob_package(g))
    wanted = declared.strip("/")
    if wanted == ".":
        return "", (), ()
    segments = prefix.strip("/").split("/") if prefix else []
    if wanted in segments:
        return "/".join(segments[:segments.index(wanted) + 1]) + "/", (), ()
    return wanted + "/", (), ()


def _glob_dir(glob):
    static = glob.split("*", 1)[0]
    return static if static.endswith("/") else static + "/"
