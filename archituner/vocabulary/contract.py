import dataclasses
import os


@dataclasses.dataclass
class Contract:
    path: str
    layers: dict
    pairs: dict
    naming: list
    package_root: str | None
    body: str
    findings: list
    ignore: list = dataclasses.field(default_factory=list)
    limits: dict = dataclasses.field(default_factory=dict)
    overrides: list = dataclasses.field(default_factory=list)

    @property
    def tree(self):
        return os.path.dirname(os.path.abspath(self.path)) or "."

    @property
    def allowed(self):
        return {pair for pair, kind in self.pairs.items() if kind == "allow"}
