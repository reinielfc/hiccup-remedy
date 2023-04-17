import os
from argparse import ArgumentParser
from pathlib import Path

from hiccup.finder import Finder


def main():
    args = get_args()
    finder = Finder(args.mode)

    if args.dry_run:
        finder.find(*args.dirs)
        print("--- DRY RUN ---")
    else:
        finder.move(*args.dirs, dest=args.dest)


def get_args():
    parser = ArgumentParser(prog='hiccup_remedy.py')

    parser.add_argument(
        '-m', '--mode', type=str, choices=Finder.MODES.keys(), default='dup',
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
