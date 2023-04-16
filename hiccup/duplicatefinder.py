import itertools
import os
from pathlib import Path
from tempfile import TemporaryFile, NamedTemporaryFile

import sh

from hiccup.filegroup import FileGroup, DuplicateFileGroup


class DuplicateFinder:
    TYPE = {
        'dup': {'group_type': DuplicateFileGroup, 'cmd_defaults': dict(dryrun=True, m=1)}}

    def __init__(self, finder_type: str):
        self._cmd = sh.Command('czkawka-cli').bake(finder_type)
        self._type = DuplicateFinder.TYPE[finder_type]
        self._dirs: list[Path] = []

    def _find_groups(self, tmp: TemporaryFile):
        group_type: FileGroup = self._type['group_type']

        self._cmd(
            d=[d.resolve() for d in self._dirs],
            **self._type['cmd_defaults'],
            file_to_save=Path(tmp.name).resolve(),
            _out=os.devnull, _err=os.devnull)

        groups = (
            group_type.from_header(header, tmp)
            for header in tmp
            if group_type.str_is_header(header))

        return groups

    @property
    def dirs(self):
        return self._dirs

    @dirs.setter
    def dirs(self, dirs: list[Path]):
        self._dirs = dirs

    def find(self, move: bool = None, dest: Path = Path("..")):
        with NamedTemporaryFile() as tmp:
            groups = self._find_groups(tmp)

            groups = ((g, print(g))[0] for g in groups)

            if move:
                groups = ((g, g.move(dest))[0] for g in groups)
                footer = "Done!"
            else:
                footer = "--- DRY RUN ---"

            list(groups)
            print(footer)
