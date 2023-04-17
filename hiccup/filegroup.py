import inspect
import io
import os
import re
from pathlib import Path
from uuid import uuid4, UUID

from util import human_readable


class FileGroup:
    _HEADER_PATTERN: re.Pattern
    _FILE_PATTERN: re.Pattern

    def __init__(self, **attr):
        self._id = uuid4()
        self._attr = attr
        self._files: list[dict] = []

    def add(self, file_str: str):
        pass

    def move(self, dest_dir: Path, common_path: Path = None):
        id_dir = dest_dir.joinpath(Path(str(self._id)))
        id_dir.mkdir(exist_ok=True)

        for f in self._files:
            orig: Path = f['path']
            attr: str = self._attr_str(f.get('attr'))

            name: str = attr + str(orig.relative_to(common_path)).replace('/', '.') \
                if common_path else orig.name

            dest: Path = id_dir.joinpath(name).resolve()
            shutil.move(orig, dest)
            print(f"renamed '{orig}' -> '{dest}'", '\n')

    @staticmethod
    def _attr_str(attr: dict) -> str:
        return ""

    @classmethod
    def from_header(cls, header: str) -> 'FileGroup':
        return cls()

    @classmethod
    def is_header(cls, string: str) -> bool:
        return cls._HEADER_PATTERN.search(string) is not None

    @classmethod
    def is_file(cls, string: str) -> bool:
        return cls._FILE_PATTERN.search(string) is not None

    def __str__(self):
        files = self._files

        lines = [f'==== FileGroup ({len(files)}) {self._id} :: Attributes={self._attr} ====']
        lines += map(lambda f: f"{f['path']} --- Attributes={f.get('attr')}", files)

        return '\n'.join(lines)


class DuplicateFileGroup(FileGroup):
    pass
