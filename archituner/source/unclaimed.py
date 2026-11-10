from archituner.vocabulary import Finding


def directory_of(path):
    return path.rsplit("/", 1)[0] if "/" in path else ""


def claimed_neighbour(path, files):
    directory = directory_of(path)
    return next((other for other, record in files.items()
                 if directory_of(other) == directory and record["layer"]),
                None)


def claimed_import(record):
    return next((entry["path"] for entry in record["imports"]
                 if entry["layer"]), None)


def claimed_importer(record, files):
    return next((path for path in record["importers"]
                 if files[path]["layer"]), None)


def unclaimed_claim(path, record, files):
    for relation, witness in (("beside", claimed_neighbour(path, files)),
                              ("importing", claimed_import(record)),
                              ("imported by", claimed_importer(record, files))):
        if witness:
            return (Finding(
                text=f"{path} is an unclaimed source file {relation} "
                     f"{witness} (layer {files[witness]['layer']})",
                produced_by=f"claimed file {witness}"), path)
    return None


def unclaimed_findings(files):
    claims = []
    for path, record in files.items():
        if record["layer"]:
            continue
        claim = unclaimed_claim(path, record, files)
        if claim:
            claims.append(claim)
    return claims
