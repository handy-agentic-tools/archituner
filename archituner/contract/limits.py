from archituner.contract.refusals import reject
from archituner.contract.syntax import glob_list
from archituner.contract.syntax import parse_override
from archituner.contract.syntax import plain_count


MEASURED = ("size", "defs", "depth", "cyclomatic", "cognitive", "prose_count")


def read_default(stripped, limits):
    number, raw = stripped.split(":", 1)
    number, raw = number.strip(), raw.strip()
    if number not in MEASURED:
        reject(f"a limits key names a number no file record "
               f"carries: {number}")
    count = plain_count(raw)
    if count is None:
        reject(f"a limits default is not a plain count: {number}: {raw}")
    limits[number] = count


def read_limits_line(section, stripped, limits, overrides):
    if section == "limits" and stripped.startswith("overrides:"):
        raw = stripped.split(":", 1)[1].strip()
        if raw:
            overrides = [parse_override(entry) for entry in glob_list(raw)]
        else:
            section = "overrides"
    elif section == "overrides" and stripped.startswith("- "):
        overrides.append(parse_override(stripped[2:].strip().strip('"')))
    elif section in ("limits", "overrides") and ":" in stripped:
        read_default(stripped, limits)
    return section, overrides
