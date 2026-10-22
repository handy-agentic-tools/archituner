import re

from archituner.contract.refusals import reject


def glob_list(raw):
    return [part.strip().strip('"') for part in
            raw.strip().lstrip("[").rstrip("]").split(",") if part.strip()]


def plain_count(raw):
    return int(raw) if raw.isascii() and raw.isdigit() else None


OVERRIDE_ENTRY = re.compile(r"^(\w+) `([^`]+)`: (\S+) - (.+)$")


def parse_override(entry):
    matched = OVERRIDE_ENTRY.match(entry)
    if not matched:
        reject(f"a limits override is not its one shape - number, selector, "
               f"value, reason: {entry}")
    number, selector, raw, reason = matched.groups()
    value = None if raw == "none" else plain_count(raw)
    if value is None and raw != "none":
        reject(f"a limits override is not its one shape - number, selector, "
               f"value, reason: {entry}")
    return number, selector, value, reason
