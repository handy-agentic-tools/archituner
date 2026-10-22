import dataclasses


@dataclasses.dataclass(frozen=True)
class Finding:
    text: str
    produced_by: str

    def __post_init__(self):
        if not self.produced_by:
            raise ValueError(f"a finding names what produced it: {self.text!r}")
