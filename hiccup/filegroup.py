import inspect
import io
import os
import re
from pathlib import Path
from uuid import uuid4, UUID

from util import human_readable


class FileGroup:
    def __init__(self, **attr):
        self._id = uuid4()
        self._attr = attr
        self._files: list[dict] = []


    def move(self, dest: Path):
        pass

    @staticmethod
    def from_header(header: bytes, open_file: io.BufferedIOBase) -> 'FileGroup':
        pass

    @staticmethod
    def is_header(line: str | bytes) -> bool:
        pass


class DuplicateFileGroup(FileGroup):
    pass
