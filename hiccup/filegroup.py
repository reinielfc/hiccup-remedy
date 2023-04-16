import inspect
import io
import os
import re
from pathlib import Path
from uuid import uuid4, UUID

from util import human_readable


class FileGroup:
    _HEADER_PATTERN: re.Pattern

    def __init__(self, **attr):
        self._id = uuid4()
        self._attr = attr
        self._files: list[dict] = []


    def move(self, dest: Path):
        pass

    @classmethod
    def from_header(cls, header: str) -> 'FileGroup':
        return cls()

    @classmethod
    def is_header(cls, string: str) -> bool:
        return cls._HEADER_PATTERN.search(string) is not None


class DuplicateFileGroup(FileGroup):
    pass
