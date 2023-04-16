import inspect
import io
import os
import re
from pathlib import Path
from uuid import uuid4, UUID

from util import human_readable


class FileGroup:
    def __init__(self, record_list: list[str], **attr: dict):
        self._key: UUID = uuid4()
        self._attr: dict = attr
        self._records: list = [self._make_record(r) for r in record_list]
        self._common = Path(os.path.commonpath(
            [r['orig']['path'] for r in self._records]))
        self._set_record_names()

    def _make_record(self, record_str: str) -> dict:
        pass

    def _set_record_names(self):
        for r in self._records:
            r['name'] = str(r['orig']['path'].relative_to(self._common)).replace('/', '.')

    def move(self, dest: Path):
        key_path = Path(str(self._key))
        dest_dir = dest.joinpath(key_path)
        dest_dir.mkdir(exist_ok=True)

        for r in self._records:
            orig: Path = r['orig']['path']
            dest: Path = dest_dir.joinpath(r['name'])

            orig.rename(dest)

    @staticmethod
    def from_header(header: bytes, open_file: io.BufferedIOBase) -> 'FileGroup':
        pass

    @staticmethod
    def str_is_header(line: str | bytes) -> bool:
        pass


class DuplicateFileGroup(FileGroup):
    def __str__(self):
        size = self._attr['size']
        lines = [f'---- {self._key} - Size {human_readable(size)} ({size}) - {len(self._records)} files']
        lines += [str(r['orig']['path']) for r in self._records]

        return '\n'.join(lines) + '\n'

    def _make_record(self, record_str: str) -> dict:
        return {'orig': dict(path=Path(record_str)), 'dest': dict(path=None)}

    @staticmethod
    def from_header(header: bytes, open_file: io.BufferedIOBase) -> FileGroup:
        match = re.search(br'Size [\d.]+ [KMGT]iB \((\d+)\) - (\d+) files?', header)
        size, num_files = map(int, match.groups())
        record_list = [
            open_file.readline().decode('ascii').rstrip('\n')
            for i in range(num_files)]

        return DuplicateFileGroup(record_list, size=size)

    @staticmethod
    def str_is_header(line: str | bytes) -> bool:
        return line.startswith(b'---- Size')
