def entry_layer(files):
    mains = sorted(path for path, record in files.items()
                   if record["layer"] and path.endswith("__main__.py"))
    return files[mains[0]]["layer"] if mains else None
