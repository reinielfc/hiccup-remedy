import re
import shutil
from pathlib import Path
from uuid import uuid4


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
    _HEADER_PATTERN = re.compile(r'^---- Size ([\d.]+ [KMGT]iB) \((\d+)\) - \d+ files?$')
    _FILE_PATTERN = re.compile(r'^/.*$')

    def add(self, file_str: str):
        match = self._FILE_PATTERN.match(file_str)
        path = Path(match.group())
        self._files.append(dict(path=path, attr={}))

    @classmethod
    def from_header(cls, header: str) -> FileGroup:
        match = cls._HEADER_PATTERN.search(header)
        size_h, size_b = match.groups()

        return cls(size_h=size_h, size_b=size_b)

    def __str__(self):
        size_h, size_b = self._attr.values()
        files = self._files

        lines = [f'---- FileGroup ({len(files)}) {self._id} -> Duplicate @ {size_h} ({size_b})']
        lines += map(lambda f: str(f['path']), files)

        return '\n'.join(lines) + '\n'

