import dataclasses

from archituner.vocabulary.reading_law import check_reading


@dataclasses.dataclass(frozen=True)
class Reading:
    layers: tuple
    pairs: dict
    files: dict

    def __post_init__(self):
        check_reading(self.layers, self.pairs)

    @classmethod
    def from_analysis(cls, result):
        return cls(layers=tuple(layer["name"] for layer in result["layers"]),
                   pairs={(p["source"], p["target"]): p["state"]
                          for p in result["pairs"]},
                   files={f["path"]: f["layer"] for f in result["files"]})

    @classmethod
    def from_baseline(cls, document):
        pairs = {}
        for key, state in document["pairs"].items():
            pairs[_pair_of(key)] = state
        return cls(layers=tuple(document["layers"]), pairs=pairs,
                   files=dict(document["files"]))


def _pair_of(key):
    source, arrow, target = key.partition(" -> ")
    if not arrow:
        raise ValueError(f"baseline key is not a pair: {key!r}")
    return source, target
