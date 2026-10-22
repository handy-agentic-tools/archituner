from archituner.contract.refusals import reject
from archituner.contract.sections import opens_section
from archituner.contract.sections import read_section_line
from archituner.contract.syntax import glob_list


def read_top_key(front, line, stripped):
    if line.startswith(" ") or not (stripped.startswith("package_root:")
                                    or stripped.startswith("ignore:")):
        return False
    key, raw = stripped.split(":", 1)
    raw = raw.strip()
    if key == "package_root":
        if not raw:
            reject("package_root takes its one value on its own line: "
                   "package_root: src")
        front["package_root"] = raw.strip('"')
    elif raw:
        front["ignore"] = glob_list(raw)
    else:
        front["section"] = "ignore"
    return True


def parse_front_matter(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    if not lines or lines[0].strip() != "---":
        reject(f"{path} does not open with front matter")
    if "---" not in lines[1:]:
        reject(f"{path} front matter never closes")
    end = lines.index("---", 1)

    front = {"layers": {}, "allow": [], "forbid": [], "naming": [],
             "package_root": None, "ignore": [], "limits": {},
             "overrides": [], "section": None}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped:
            continue
        if read_top_key(front, line, stripped):
            continue
        if opens_section(front, line, stripped):
            continue
        read_section_line(front, stripped)

    return (front["layers"], front["allow"], front["forbid"], front["naming"],
            front["package_root"], front["ignore"], front["limits"],
            front["overrides"], "\n".join(lines[end + 1:]))
