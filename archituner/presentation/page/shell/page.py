import dataclasses
import json

from archituner.presentation.model.column_layout import column
from archituner.presentation.model.layout import regions
from archituner.presentation.model.stack_layout import stack
from archituner.presentation.page.shell.events import SCRIPT as EVENTS
from archituner.presentation.page.shell.shell import BODY
from archituner.presentation.page.shell.shell import CLOSE
from archituner.presentation.page.shell.shell import HEAD
from archituner.presentation.page.views.axes import SCRIPT as AXES
from archituner.presentation.page.views.coverage import script as coverage_script
from archituner.presentation.page.views.coverage import style as coverage_style
from archituner.presentation.page.views.detail import SCRIPT as DETAIL
from archituner.presentation.page.views.grounds import GROUND
from archituner.presentation.page.views.layers import heads as layers_heads
from archituner.presentation.page.views.layers import script as layers_script
from archituner.presentation.page.views.layers import style as layers_style
from archituner.presentation.page.views.narrow import script as narrow_script
from archituner.presentation.page.views.narrow import style as narrow_style
from archituner.presentation.page.views.panel import overview as panel_overview
from archituner.presentation.page.views.panel import script as panel_script
from archituner.presentation.page.views.panel import style as panel_style
from archituner.presentation.page.views.readings import SCRIPT as READINGS
from archituner.presentation.page.views.rules import RULES
from archituner.presentation.page.views.views import SCRIPT as VIEWS
from archituner.theme import DARK
from archituner.theme import LIGHT
from archituner.theme import MOVED
from archituner.vocabulary import GLYPH


LINE = 78


def table(mapping):
    body = ", ".join(f'{key}: "{mark}"' for key, mark in mapping.items())
    return "{" + body + "}"


def wrapped(value, column):
    if column + len(value) + 1 <= LINE:
        return value
    items = value.split(", ")
    head, width = [], column
    for item in items:
        if head:
            width += 2
        if width + len(item) + 1 > LINE:
            break
        head.append(item)
        width += len(item)
    return ", ".join(head) + ",\n" + " " * column + ", ".join(items[len(head):])


def spent(shell, ground, label):
    for name, value in ground.items():
        if name == "mono":
            value = wrapped(value, len("    --mono: "))
        shell = shell.replace(f"__{label}-{name}__", value)
    return shell


def payload_of(result):
    return dict(result, regions=regions(result["coverage"]),
                stack=stack(result["order"], result["pairs"]),
                stack_narrow=column(result["order"], result["pairs"]),
                overview=panel_overview(result))


def render(result):
    payload = json.dumps(payload_of(result), ensure_ascii=False,
                         default=dataclasses.asdict)
    return TEMPLATE.replace("__DATA__", payload.replace("</", "<\\/"))


SHELL = (HEAD
         + GROUND
         + RULES
         + narrow_style()
         + BODY
         + READINGS
         + AXES
         + VIEWS
         + panel_script()
         + DETAIL
         + EVENTS
         + CLOSE)


TEMPLATE = spent(spent((SHELL
                        .replace("__GLYPH_MAP__", table(GLYPH))
                        .replace("__MOVED_MAP__", table(MOVED))
                        .replace("__PANEL_STYLE__", panel_style())
                        .replace("__COVERAGE_STYLE__", coverage_style())
                        .replace("__LAYERS_STYLE__", layers_style() + layers_heads())
                        .replace("__LAYERS_SCRIPT__", layers_script())
                        .replace("__NARROW_SCRIPT__", narrow_script())
                        .replace("__COVERAGE_SCRIPT__", coverage_script())),
                       LIGHT, "light"), DARK, "dark")
