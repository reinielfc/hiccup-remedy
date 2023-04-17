import itertools
import os.path
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Iterable, Generator

import sh

from hiccup.filegroup import FileGroup, DuplicateFileGroup, SimilarImageGroup


class Finder:
    MODES = {
        'dup': {'group_type': DuplicateFileGroup, 'conf_override': dict(dryrun=True)},
        'image': {'group_type': SimilarImageGroup, 'conf_override': dict()}}

    def __init__(self, mode: str, **conf):
        self._cmd: sh.Command = sh.Command('czkawka-cli').bake(mode)
        self._mode: dict = self.MODES[mode]
        self._conf: dict = conf

        conf.update(self._mode['conf_override'])

    def find(self, *dirs: Path):
        with NamedTemporaryFile() as tmp:
            groups = self._find_groups(*dirs, of=tmp)
            [print(g) for g in groups]

    def move(self, *dirs: Path, dest=Path('.'), quiet=False):
        with NamedTemporaryFile() as tmp:
            groups = self._find_groups(*dirs, of=tmp)

            if not quiet:
                groups = map(lambda g: (g, print(g))[0], groups)

            common_path = Path(os.path.commonpath(dirs)).resolve()
            [g.move(dest, common_path) for g in groups]

    def _find_groups(self, *dirs: Path, of: IO) -> Generator[FileGroup, any, None]:
        self._conf.update(
            directories=[d.resolve() for d in dirs],
            file_to_save=Path(of.name).resolve(),
            _out=os.devnull)

        self._cmd(**self._conf)
        lines = map(lambda l: l.decode('ascii').rstrip('\n'), of)

        return self._parse_groups(lines)

    def _parse_groups(self, lines: Iterable[str]):
        group_type: type[FileGroup] = self._mode['group_type']

        for line in lines:
            if group_type.is_header(line):
                group = group_type.from_header(line)
                group_files = itertools.takewhile(group_type.is_file, lines)

                for f in group_files:
                    group.add(f)

                yield group
