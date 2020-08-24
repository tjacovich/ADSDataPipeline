
#!/usr/bin/env python

import argparse
import datetime

from adsdata import process, tasks

app = tasks.app


def main():
    parser = argparse.ArgumentParser(description='Process user input.')
    parser.add_argument('-b', '--bibcodes', dest='bibcodes', action='store',
                        help='send data to master for list of bibcodes separated by spaces')
    parser.add_argument('-d', '--diffs', dest='diffs', action='store_true',
                        help='compute changed bibcodes')
    parser.add_argument('-f', '--filename', dest='filename', action='store',
                        help='send data to master for file of sorted bibcodes')
    parser.add_argument('--no-metrics', dest='compute_metrics', action='store_false',
                        help='compute and send nonbib protobufs, cache init not needed')

    args = parser.parse_args()

    if args.bibcodes:
        args.bibcodes = args.bibcodes.split(' ')
        args.bibcodes.sort()

    if args.compute_metrics is True and args.diffs is False:
        c = process.init_cache(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
        print('cache created: {}'.format(c))

    process.open_all(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))

    if args.bibcodes:
        process.process_bibcodes(args.bibcodes, compute_metrics=args.compute_metrics)
    elif args.diffs:
        process.compute_diffs()
    elif args.filename:
        count = 0
        bibcodes = []
        with open(args.filename, 'r') as f:
            for line in f:
                if count % 10000 == 0:
                    print('{}: count = {}'.format(datetime.datetime.now(), count))
                count = count + 1
                bibcodes.append(line.strip())
                if len(bibcodes) % 100 == 0:
                    process.process_bibcodes(bibcodes, compute_metrics=args.compute_metrics)
                    bibcodes = []
        if len(bibcodes) > 0:
            process.process_bibcodes(bibcodes, compute_metrics=args.compute_metrics)
        print('{}: completed, count = {}'.format(datetime.datetime.now(), count))
    else:
        print('you must provide a list of bibcodes to process')
    

if __name__ == '__main__':
    main()
