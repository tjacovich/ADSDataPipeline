
#!/usr/bin/env python

import argparse
import datetime

from adsdata import tasks
from adsdata.diffs import Diff
from adsdata.process import Processor
from adsdata.memory_cache import Cache

# python3 run.py PROCESS_BIBCODES bibcode1,bibcode2 [--no-metrics]
# python3 run.py PROCESS_FILE filename.txt [--no-metrics]
#  python3 run.py COMPUTE_DIFF


def main():
    parser = argparse.ArgumentParser(description='Process nonbib input data files and send data to master pipeline')
    subparsers = parser.add_subparsers(help='commands', dest="action", required=True)
    diff_parser = subparsers.add_parser('COMPUTE_DIFF',
                                        help='Compute changed bibcodes by comparing current and previous data sets.  Changed bibcodes are stored in the file ./logs/input/current/changedBibcodes.txt.')
    diff_parser.add_argument('--include-CitationCapture',
                            action='store_false',
                            dest='include_CC',
                            help='Calculate changes for Classic and CitationCapture records.')
    diff_parser.add_argument('--only-CitationCapture',
                            action='store_false',
                            dest='only_CC',
                            help='Calculate changes only for CitationCapture records.')
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
    bibcodes_parser.add_argument('--CitationCapture',
                            action='store_false',
                            dest='compute_CC',
                            help='Calculate protobufs only for CitationCapture records.')
    bibcodes_parser.add_argument('--no-metrics',
                                 dest='compute_metrics',
                                 action='store_false',
                                 help='Only send nonbib protobufs to master, do not init cache or send metrics protobufs.')
    
    args = parser.parse_args()
    
    if args.action == 'COMPUTE_DIFF':
        #calculates Diff for all records sources
        if args.include_CC:
            Diff.compute()
            Diff.compute(CC_records=True)
        #Computes Diff for Classic records only if only_CC: False, else calculates only for CitationCapture records
        else:
            Diff.compute(CC_records=args.only_CC)
            
    else:
        # where with PROCESS_BIBCODES or PROCESS_FILE
        if args.compute_metrics:
            Cache.init()
        if args.action == 'PROCESS_BIBCODES':
            # parse and sort
            bibcodes = args.bibcodes.sort()
            with Processor(compute_metrics=args.compute_metrics, compute_CC=args.compute_CC) as processor:
                processor.process_bibcodes(bibcodes)
            print('processedbibcodes {}'.format(bibcodes))

        elif args.action == 'PROCESS_FILE':
            Diff.execute('sort -o {} {}'.format(args.input_filename, args.input_filename))
            # send bibcodes from file to processing in batches
            count = 0
            bibcodes = []
            with open(args.input_filename, 'r') as f, Processor(compute_metrics=args.compute_metrics, compute_CC=args.compute_CC) as processor:
                for line in f:
                    if count % 10000 == 0:
                        print('{}: processed bibcodes count = {}'.format(datetime.datetime.now(), count))
                    count = count + 1
                    line = line.strip()
                    if line:
                        bibcodes.append(line)
                        if len(bibcodes) % 100 == 0:
                            processor.process_bibcodes(bibcodes)
                            bibcodes = []
                if len(bibcodes) > 0:
                    processor.process_bibcodes(bibcodes)
            print('{}: completed processing bibcodes from {}, count = {}'.format(datetime.datetime.now(), args.input_filename, count))


if __name__ == '__main__':
    main()
