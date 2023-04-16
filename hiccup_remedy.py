import os
from argparse import Namespace, ArgumentParser
from pathlib import Path

from hiccup.duplicatefinder import DuplicateFinder


def main():
    args = get_args()
    finder = DuplicateFinder(args.mode)
    finder.dirs = args.dirs

    print(args)

    finder.find(move=(not args.dry_run), dest=args.dest)


def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        '-m', '--mode', type=str, choices=DuplicateFinder.TYPE.keys(), default='dup',
        help='mode of operation')

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


if __name__ == '__main__':
    main()
