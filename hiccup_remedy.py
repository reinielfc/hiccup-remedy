import argparse
import json
import os
import pathlib
import random
import re
import string
import tempfile

import sh


def main():
    args = get_args()
    config = {'delete_method': 'NONE', 'dryrun': True}

    dupes = get_dupes(args.dirs, config, args.key_length)

    json_string = json.dumps(dupes)
    print(json_string)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='hiccup_remedy', description='')

    parser.add_argument(
        '-k', '--key-length', type=int, default=16,
        help='length of directory names for each group')

    parser.add_argument(
        '-P', '--preserve-path', action='store_true',
        help='file is renamed as its path separated by periods')

    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='do not change files')

    parser.add_argument(
        dest='dirs', metavar='DIR', nargs='+', type=pathlib.Path,
        help='directory paths to find duplicates at', )

    return parser.parse_args()


def get_dupes(dirs: list, config: dict, key_length: int = 16) -> dict[dict]:
    cmd = sh.Command('czkawka-cli')

    with tempfile.NamedTemporaryFile() as tmp:
        config['file_to_save'] = pathlib.Path(tmp.name).absolute()

        cmd('dup', **config,
            d=[dir_path.absolute() for dir_path in dirs],
            _out=os.devnull, _err=os.devnull)

        dupes = {
            generate_key(key_length): parse_group(tmp, line)
            for line in tmp
            if line.startswith(b'---- Size')}

    return dupes


def generate_key(length: int):
    alphanumeric = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric) for i in range(length))


def parse_group(tmp, line) -> dict:
    match = re.search(rb'Size [\d.]+ [KMGT]iB \((\d+)\) - (\d+) files?', line)
    size, count = [int(group) for group in match.groups()]

    return {
        'size': size,
        'matches': [
            tmp.readline().decode('ascii').rstrip('\n')
            for i in range(count)]}


if __name__ == '__main__':
    main()
