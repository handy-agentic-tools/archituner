import dataclasses

from archituner.vocabulary.states import KINDS
from archituner.vocabulary.states import REALISED
from archituner.vocabulary.states import STATES


@dataclasses.dataclass(frozen=True)
class Pair:
    source: str
    target: str
    kind: str
    state: str
    witnesses: tuple = ()

    def __post_init__(self):
        if self.source == self.target:
            raise ValueError(f"source equals target: {self.source}")
        if self.kind not in KINDS:
            raise ValueError(f"not a kind: {self.kind!r}")
        if self.state not in STATES:
            raise ValueError(f"not a state: {self.state!r}")
        if not isinstance(self.witnesses, tuple):
            raise ValueError(f"witnesses are a tuple, not "
                             f"{type(self.witnesses).__name__}")
        if (self.state in REALISED) != bool(self.witnesses):
            raise ValueError(f"state and witnesses disagree: {self.state} with "
                             f"{len(self.witnesses)} witnesses")
