import os.path
from pathlib import Path
from uuid import uuid4

from util import human_readable


class DupeGroup:
    def __init__(self, size: int, paths: list[Path], sep: str = "."):
        self.key = uuid4()
        self.size = size
        self.sep = sep
        self.is_moved = False
        self.common = os.path.commonpath(paths)
        self.records: list[tuple[Path, Path]] = [self._make_record(p) for p in paths]

    def move(self, dest: Path):
        for origin, destination in self.records:
            dest.joinpath(destination.parent)
            destination.parent.mkdir()
            # origin.rename(destination)

    def _make_record(self, origin: Path) -> tuple[Path, Path]:
        key = Path(str(self.key))
        destination = key.joinpath(
            str(origin.relative_to(self.common)).replace("/", self.sep)
        )

        return origin, destination

    def __str__(self):
        lines = [
            f"---- {self.key} - Size {human_readable(self.size)} ({self.size}) - {len(self.records)} files"
        ]

        for record in self.records:
            origin, destination = record
            lines.append(str(origin))

        return "\n".join(lines) + "\n"
