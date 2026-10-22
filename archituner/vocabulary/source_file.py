import dataclasses


@dataclasses.dataclass(frozen=True)
class SourceFile:
    path: str
    layer: str | None
    imports: tuple = ()
    importers: tuple = ()

    def __post_init__(self):
        if not self.path:
            raise ValueError("a file with no path is not a file a tree holds")
