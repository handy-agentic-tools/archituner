"""The package root: the names one import away, and no module of its own."""

from archituner.conformance import baseline_of
from archituner.conformance import compare
from archituner.conformance import measure_shape
from archituner.conformance import remedy
from archituner.contract import boundaries_reasons
from archituner.contract import read_contract
from archituner.matching import glob_matcher
from archituner.matching import match_path
try:
    from archituner.presentation.model import treemap
    from archituner.presentation.page.shell.page import render
    from archituner.presentation.rejection import render_rejection
except ImportError:
    render = None
    render_rejection = None
    treemap = None
from archituner.run import analyse
from archituner.source import relative_base
from archituner.source import resolve
