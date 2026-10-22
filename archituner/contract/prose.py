import re


def prose_sections(body):
    sections = {}
    current, buf = None, []
    for line in body.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def layers_table(text):
    cells = {}
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(parts) >= 4 and parts[0] not in ("Layer", "") and not set(parts[0]) <= {"-"}:
            cells[parts[0].strip("`")] = {"responsibility": parts[2], "rationale": parts[3]}
    return cells
