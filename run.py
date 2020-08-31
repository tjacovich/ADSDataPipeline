
#!/usr/bin/env python

import argparse
import datetime

from adsdata import diffs, tasks
from adsdata.diffs import Diff
from adsdata.process import Processor


app = tasks.app

# python3 run.py PROCESS_BIBCODES bibcode1,bibcode2 [--no-metrics]
# python3 run.py PROCESS_FILE filename.txt [--no-metrics]
#  python3 run.py COMPUTE_DIFF


def main():
    parser = argparse.ArgumentParser(description='Process nonbib input data files and send data to master pipeline')
    subparsers = parser.add_subparsers(help='commands', dest="action", required=True)
    diff_parser = subparsers.add_parser('COMPUTE_DIFF',
                                        help='Compute changed bibcodes by comparing current and previous data sets.  Changed bibcodes are stored in the file ./logs/input/current/changedBibcodes.txt.')
    file_parser = subparsers.add_parser('PROCESS_FILE',
                                        help='Send nonbib and metrics protobufs to master for the list of bibcodes in the provided file')
    file_parser.add_argument('input_filename',
                             action='store',
                             type=str,
                             help='Path to input file, required.')
    file_parser.add_argument('--no-metrics',
                             action='store_false',
                             dest='compute_metrics',
                             help='Only send nonbib protobufs to master, do not init cache or send metrics protobufs')
    bibcodes_parser = subparsers.add_parser('PROCESS_BIBCODES',
                                            help='Send data to master for the bibcodes provided on the command line.')
    bibcodes_parser.add_argument('--bibcodes',
                                 action='store',
                                 default=None,
                                 dest='bibcodes',
                                 nargs='+',
                                 required=True,
                                 type=str,
                                 help='Space delimited list of bibcodess.')
    bibcodes_parser.add_argument('--no-metrics',
                                 dest='compute_metrics',
                                 action='store_false',
                                 help='Only send nonbib protobufs to master, do not init cache or send metrics protobufs.')
    
    args = parser.parse_args()
    
    if args.action == 'COMPUTE_DIFF':
        Diff.compute_diffs()
    else:
        # process.init_cache(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
        # process.open_all(root_dir=app.conf.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/'))
        if args.action == 'PROCESS_BIBCODES':
            # parse and sort
            bibcodes = args.bibcodes.sort()
            with Processor(compute_metrics=args.compute_metrics) as processor:
                processor.process_bibcodes(bibcodes)
            print('processedbibcodes {}'.format(bibcodes))

        elif args.action == 'PROCESS_FILE':
            # first sort input file
            r = diffs.execute('asdfsort -o {} {}'.format(args.input_filename, args.input_filename))
            if r[0] != 0:
                raise Exception('unable to sort input file {}, return code =, {}, out = {}, err = {}'.format(args.input_filename, r[0], r[1], r[2]))
            # send batches of bibcodes to processing
            count = 0
            bibcodes = []
            with open(args.input_filename, 'r') as f, Processor(compute_metrics=args.compute_metrics) as processor:
                for line in f:
                    if count % 10000 == 0:
                        print('{}: processed bibcodes count = {}'.format(datetime.datetime.now(), count))
                    count = count + 1
                    bibcodes.append(line.strip())
                    if len(bibcodes) % 100 == 0:
                        processor.process_bibcodes(bibcodes)
                        bibcodes = []
            if len(bibcodes) > 0:
                processor.process_bibcodes(bibcodes)
            print('{}: completed processing bibcodes from {}, count = {}'.format(datetime.datetime.now(), args.input_filename, count))


if __name__ == '__main__':
    main()
