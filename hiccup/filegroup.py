import re
import shutil
from pathlib import Path
from uuid import uuid4

from prettytable import PrettyTable


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


class SimilarImageGroup(FileGroup):
    _FILE_PATTERN = re.compile(r'^(/.*) - (\d+x\d+) - ([\d.]+ [KMGT]iB) - (.*)$')
    _HEADER_PATTERN = re.compile(r'^Found \d+ images which have similar friends$')

    def add(self, file_str: str):
        match = self._FILE_PATTERN.search(file_str)
        file_path, dimensions, size_h, similarity = match.groups()
        path = Path(file_path)
        attr = dict(dimensions=dimensions, size_h=size_h, similarity=similarity)

        self._files.append(dict(path=path, attr=attr))

    @staticmethod
    def _attr_str(a: dict) -> str:
        return '.'.join([a['similarity'], a['dimensions']]) + '_'

    @staticmethod
    def _make_table():
        table = PrettyTable(header=False, border=False, preserve_internal_border=True, align='l', padding_width=1)
        table.add_column('similarity', [], 'l')
        table.add_column('dimensions', [], 'r')
        table.add_column('size_h', [], 'r')
        table.add_column('path', [], 'l')

        return table

    def __str__(self):
        files = self._files
        header = f'---- FileGroup ({len(files)}) {self._id} -> SimilarImage\n'

        def make_row(file_dict: dict):
            path = file_dict['path']
            dimensions, size_h, similarity = file_dict['attr'].values()
            return similarity, dimensions, size_h, path

        table = self._make_table()
        table.add_rows(map(make_row, files))

        return header + str(table)
