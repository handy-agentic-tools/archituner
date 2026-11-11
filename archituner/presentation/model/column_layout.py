from archituner.presentation.model.layout import stack_geometry
from archituner.presentation.model.layout import UNIT
from archituner.presentation.model.stack_layout import stage


def column(order, pairs):
    figure = stage(stack_geometry()["narrow"], order, pairs, False)
    figure.update({"inset": UNIT * 8, "name_base": UNIT * 13,
                   "cell_top": UNIT * 16, "val_base": UNIT * 26,
                   "cell_foot": UNIT * 29})
    return figure
