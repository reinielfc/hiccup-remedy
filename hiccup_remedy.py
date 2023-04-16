import os
import re
from argparse import Namespace, ArgumentParser
from pathlib import Path
from tempfile import NamedTemporaryFile

from sh import Command

from dupe_group import DupeGroup


def main():
    args = get_args()

    print(args)
    dupes = find_dupes(args.dirs, args.dest, dict())

    [print(d) for d in dupes]


def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        '-d', '--dest', type=Path, default=Path(os.getcwd()),
        help='destination of dupes')

    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='do not change files')

    parser.add_argument(
        dest='dirs', metavar='DIR', nargs='+', type=Path,
        help='directory paths to find duplicates at')

    return parser.parse_args()


def find_dupes(dirs: list[Path], dest: Path, config: dict):
    czkawka = Command('czkawka-cli')

    with NamedTemporaryFile() as tmp:
        config.update(  # set default config
            dryrun=True,
            file_to_save=Path(tmp.name).resolve())

        czkawka(  # run command
            'dup', **config,
            d=[d.resolve() for d in dirs],
            _out=os.devnull, _err=os.devnull)

        headers = filter(lambda line: line.startswith(b'---- Size'), tmp)
        groups = map(lambda header: parse_group(tmp, header), headers)

        return list(groups)


def parse_group(tmp_file, line: bytes) -> DupeGroup:
    match = re.search(br'Size [\d.]+ [KMGT]iB \((\d+)\) - (\d+) files?', line)
    size, num_files = map(int, match.groups())
    records = [
        Path(tmp_file.readline().decode('ascii').rstrip('\n'))
        for i in range(num_files)]

    return DupeGroup(size, records)


if __name__ == '__main__':
    main()
