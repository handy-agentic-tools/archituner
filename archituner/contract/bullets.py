def bullet_list(text):
    items, buf = [], None
    for line in (text or "").splitlines():
        if line.startswith("- "):
            if buf:
                items.append(buf)
            buf = line[2:].strip()
        elif buf is not None and line.startswith("  "):
            buf += " " + line.strip()
    if buf:
        items.append(buf)
    return items
