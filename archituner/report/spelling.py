from archituner.vocabulary import GLYPH
from archituner.vocabulary import STATE_COLOURS


def coloured_glyph(state, colour):
    glyph = GLYPH[state]
    if not colour:
        return glyph
    token = STATE_COLOURS[state]
    r, g, b = (int(token[i:i + 2], 16) for i in (1, 3, 5))
    return f"\x1b[38;2;{r};{g};{b}m{glyph}\x1b[0m"


def section_line(title, md):
    return f"## {title}" if md else title


def item_line(text, md, indent="  "):
    return f"- {text}" if md else f"{indent}{text}"
