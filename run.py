
#!/usr/bin/env python

import argparse
import datetime

from adsdata import process, tasks

app = tasks.app


def main():
    parser = argparse.ArgumentParser(description='Process user input.')
    parser.add_argument('-b', '--bibcodes', dest='bibcodes', action='store',
                        help='A list of bibcodes separated by spaces')
    parser.add_argument('-d', '--diffs', dest='diffs', action='store_true',
                        help='compute changed bibcodes')
    parser.add_argument('-f', '--filename', dest='filename', action='store',
                        help='file of sorted bibcodes to process')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='after cache init user can enter bibcodes')
    parser.add_argument('--no-metrics', dest='compute_metrics', action='store_false',
                        help='after cache init user can enter bibcodes')
    parser.add_argument('--queue', dest='queue', action='store_true',
                        help='queue bibcodes to workers, always computes metrics')

    args = parser.parse_args()

    if args.bibcodes:
        args.bibcodes = args.bibcodes.split(' ')
        args.bibcodes.sort()

    if args.compute_metrics is True and args.queue is False:
        c = process.init_cache(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
        print('cache created: {}'.format(c))

    if args.queue is False:
        process.open_all(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))

    if args.bibcodes:
        if args.queue:
            tasks.task_process_bibcodes.delay(args.bibcodes)
        else:
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
                    if args.queue:
                        tasks.task_process_bibcodes.delay(bibcodes)
                    else:
                        process.process_bibcodes(bibcodes, compute_metrics=args.compute_metrics)
                    bibcodes = []
        if len(bibcodes) > 0:
            if args.queue:
                tasks.task_process_bibcodes.delay(bibcodes)
            else:
                process.process_bibcodes(bibcodes, compute_metrics=args.compute_metrics)
        print('{}: completed, count = {}'.format(datetime.datetime.now(), count))
    elif args.interactive:
        while True:
            i = input('enter bibcode: ')
            if args.queue:
                tasks.task_process_bibcodes.delay([i.strip()])
            else:
                process.process_bibcodes([i.strip()], compute_metrics=args.compute_metrics)
    else:
        print('you must provide a list of bibcodes to process')
    

if __name__ == '__main__':
    main()
