from archituner.contract.limits import read_limits_line
from archituner.contract.refusals import reject
from archituner.contract.syntax import glob_list


def opens_section(front, line, stripped):
    if line.startswith(" ") or not stripped.endswith(":"):
        return False
    front["section"] = stripped[:-1]
    return True


def read_section_line(front, stripped):
    section = front["section"]
    if section == "layers" and ":" in stripped:
        name, raw = stripped.split(":", 1)
        if not raw.strip():
            reject(f"{name.strip()} opens a nested block: a layer's value is "
                   f"its same-line list of globs")
        front["layers"][name.strip()] = glob_list(raw)
    elif stripped in ("allow:", "forbid:"):
        front["section"] = stripped[:-1]
    elif section in ("allow", "forbid") and stripped.startswith("- "):
        (front["allow"] if section == "allow" else front["forbid"]).append(stripped[2:])
    elif section == "naming" and stripped.startswith("- "):
        front["naming"].append(stripped[2:].strip('"'))
    elif section == "ignore" and stripped.startswith("- "):
        front["ignore"].append(stripped[2:].strip().strip('"'))
    else:
        front["section"], front["overrides"] = read_limits_line(
            section, stripped, front["limits"], front["overrides"])
