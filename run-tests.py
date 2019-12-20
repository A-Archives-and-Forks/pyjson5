#!/usr/bin/env python

from argparse import ArgumentParser
from logging import basicConfig, INFO, getLogger
from pathlib import Path
from subprocess import Popen

from colorama import init, Fore
from pyjson5 import decode_io


argparser = ArgumentParser(description='Run JSON5 parser tests')
argparser.add_argument('tests', nargs='?', type=Path, default=Path('third-party/json5-tests'))

suffix_implies_success = {
    '.json': True,
    '.json5': True,
    '.txt': False,
}

if __name__ == '__main__':
    basicConfig(level=INFO)
    logger = getLogger(__name__)

    init()

    good = 0
    bad = 0
    severe = 0

    args = argparser.parse_args()
    index = 0
    for path in sorted(args.tests.glob('*/*.*')):
        kind = path.suffix.split('.')[-1]
        expect_success = suffix_implies_success.get(path.suffix)
        if expect_success is None:
            continue

        index += 1
        category = path.parent.name
        name = path.stem
        try:
            p = Popen(('/usr/bin/env', 'python', 'transcode-to-json.py', str(path)))
            outcome = p.wait(5)
        except Exception:
            logger.error('Error while testing: %s', path, exc_info=True)
            errors += 1
            continue

        is_success = outcome == 0
        is_failure = outcome == 1
        is_severe = outcome not in (0, 1)
        is_good = is_success if expect_success else is_failure

        code = (
            Fore.RED + '😱' if is_severe else
            Fore.CYAN + '😄' if is_good else
            Fore.YELLOW + '😠'
        )
        print(
            '#', index, ' ', code, ' '
            'Category <', category, '> | '
            'Test <', name, '> | '
            'Data <', kind, '> | '
            'Expected <', 'pass' if expect_success else 'FAIL', '> | '
            'Actual <', 'pass' if is_success else 'FAIL', '>',
            Fore.RESET,
            sep='',
        )
        if is_severe:
            severe += 1
        elif is_good:
            good += 1
        else:
            bad += 1

    is_severe = severe > 0
    is_good = bad == 0
    code = (
        Fore.RED + '😱' if is_severe else
        Fore.CYAN + '😄' if is_good else
        Fore.YELLOW + '😠'
    )
    print()
    print(
        code, ' ',
        good, ' × correct outcome | ',
        bad, ' × wrong outcome | ',
        severe, ' × severe errors',
        Fore.RESET,
        sep=''
    )
    raise SystemExit(2 if is_severe else 0 if is_good else 1)
