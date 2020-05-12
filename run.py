
#!/usr/bin/env python

import adsputils
import argparse

from adsdata import memory_cache, process, tasks

app = tasks.app


def main():
    parser = argparse.ArgumentParser(description='Process user input.')
    parser.add_argument('-b', '--bibcodes', dest='bibcodes', action='store',
                        help='A list of bibcodes separated by spaces')
    parser.add_argument('-d', '--diffs', dest='diffs', action='store_true',
                        help='compute changed bibcodes')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='after cache init user can enter bibcodes')
    parser.add_argument('--no-metrics', dest='compute_metrics', action='store_false',
                        help='after cache init user can enter bibcodes')
    parser.add_argument('--test', dest='test', action='store_true',
                        help='use test aggegator')

    args = parser.parse_args()

    if args.bibcodes:
        args.bibcodes = args.bibcodes.split(' ')
        args.bibcodes.sort()

    if args.compute_metrics is True:
        c = process.init_cache(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
        print('cache created: {}'.format(c))

    if args.bibcodes:
        process.process_bibcodes(args.bibcodes, compute_metrics=args.compute_metrics)
    elif args.diffs:
        process.compute_diffs()
    elif args.interactive:
        while True:
            i = input('enter bibcode: ')
            process.process_bibcodes([i.strip()], compute_metrics=args.compute_metrics)
    elif args.test:
        process.test_process(False)
    else:
        process.process(compute_metrics=args.compute_metrics)
    

if __name__ == '__main__':
    main()
