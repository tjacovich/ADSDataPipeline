
#!/usr/bin/env python

import argparse
import datetime
import os

from adsdata.diffs import Diff
from adsdata.process import Processor
from adsdata.memory_cache import Cache
from adsdata.tasks import app
logger = app.logger

# python3 run.py PROCESS_BIBCODES --bibcodes bibcode1 bibcode2 ... bibcodeN [--no-metrics]
# python3 run.py PROCESS_FILE filename.txt [--no-metrics]
#  python3 run.py COMPUTE_DIFF

def main():
    parser = argparse.ArgumentParser(description='Process nonbib input data files and send data to master pipeline')
    subparsers = parser.add_subparsers(help='commands', dest="action", required=True)
    diff_parser = subparsers.add_parser('COMPUTE_DIFF',
                                        help='Compute changed bibcodes by comparing current and previous data sets.  Changed bibcodes are stored in the file ./logs/input/current/changedBibcodes.txt.')
    diff_parser.add_argument('--include-CitationCapture',
                            action='store_true',
                            default=False,
                            dest='include_CC',
                            help='Calculate changes for Classic and CitationCapture records.')
    diff_parser.add_argument('--only-CitationCapture',
                            action='store_true',
                            dest='compute_CC',
                            help='Calculate changes only for CitationCapture records.')
    file_parser = subparsers.add_parser('PROCESS_FILE',
                                        help='Send nonbib and metrics protobufs to master for the list of bibcodes in the provided file')
    file_parser.add_argument('input_filename',
                            action='store',
                            default=None,
                            type=str,
                            help='Path to input file, required.')
    file_parser.add_argument('--only-CitationCapture',
                            action='store_true',
                            default=False,
                            dest='compute_CC',
                            help='Calculate protobufs only for CitationCapture records.')
    file_parser.add_argument('--include-CitationCapture-file',
                            action='store',
                            default=None,
                            type=str,
                            dest='CC_input',
                            help='Path to input file for CitationCapture records. Required for processing software records.')    
    file_parser.add_argument('--no-metrics',
                            action='store_false',
                            dest='compute_metrics',
                            help='Only send nonbib protobufs to master, do not init cache or send metrics protobufs')
    bibcodes_parser = subparsers.add_parser('PROCESS_BIBCODES',
                                            help='Send data to master for the bibcodes provided on the command line.')
    bibcodes_parser.add_argument('--bibcodes',
                                action='store',
                                default=[],
                                dest='bibcodes',
                                nargs='+',
                                required=True,
                                help='Space delimited list of bibcodess.')
    bibcodes_parser.add_argument('--only-CitationCapture',
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
            logger.info("Computing Diffs for both Classic and CitationCapture Records")
            Diff.compute()
            Diff.compute(CC_records=True)
        
        #Computes Diff for Classic records only if compute_CC: False, else calculates only for CitationCapture records
        else:
            Diff.compute(CC_records=args.compute_CC)   
            name = "Classic"
            if args.compute_CC: name = "CitationCapture" 
            logger.info("Computing Diffs for {} Records".format(name))

    else:
        # where with PROCESS_BIBCODES or PROCESS_FILE
        if args.compute_metrics:
            Cache.init()
        
        #Processes Bibcodes from CLI. Bibcodes must be either exlcusively from Classic (default)
        # or exclusively from CitationCapture with --only-CitationCapture. 
        if args.action == 'PROCESS_BIBCODES':
            # parse and sort
            if [bool(args.compute_CC), not bool(args.compute_metrics)].count(True)>1:
                msg="Cannot call --no-metrics with CitationCapture records. Stopping."
                logger.error(msg)
                raise Exception(msg)
                
            bibcodes = sorted(args.bibcodes)
            with Processor(compute_metrics=args.compute_metrics, compute_CC=args.compute_CC) as processor:
                processor.process_bibcodes(bibcodes)
            logger.info('processedbibcodes {}'.format(bibcodes))

        #Process bibcodes from file.
        #If --include-CitationCapture, processes input_file as Classic and included file as CitationCapture records
        #If  --only-CitationCapture, processes input_file as CitationCapture Records
        #Else input_file is Classic records.
        elif args.action == 'PROCESS_FILE':
            if args.CC_input and args.compute_CC:
                msg="Both --only-CitationCapture and --include-CitationCapture-file specified. Please check command line arguments."
                logger.error(msg)
                raise Exception(msg)

            if [bool(args.CC_input), args.compute_CC, not bool(args.compute_metrics)].count(True)>1:
                msg="Cannot call --no-metrics with CitationCapture records included. Stopping."
                logger.error(msg)
                raise Exception(msg)

            Diff.execute('sort -o {} {}'.format(args.input_filename, args.input_filename))

            # send bibcodes from file to processing in batches
            count = 0
            bibcodes = []

            #First processes the classic file
            if not args.compute_CC or args.CC_input:
                with open(args.input_filename, 'r') as f, Processor(compute_metrics=args.compute_metrics) as processor:
                    for line in f:
                        if count % 10000 == 0:
                            logger.info('{}: processed bibcodes count = {}'.format(datetime.datetime.now(), count))
                        count = count + 1
                        line = line.strip()
                        if line:
                            bibcodes.append(line)
                            if len(bibcodes) % 100 == 0:
                                processor.process_bibcodes(bibcodes)
                                bibcodes = []
                    if len(bibcodes) > 0:
                        processor.process_bibcodes(bibcodes)
                logger.info('{}: completed processing bibcodes from {}, count = {}'.format(datetime.datetime.now(), args.input_filename, count))
            
            count = 0
            bibcodes = []

            #Then processes the CitationCapture file
            if args.compute_CC or args.CC_input:
                if args.CC_input:
                    Diff.execute('sort -o {} {}'.format(args.CC_input, args.CC_input))
                else:
                    args.CC_input = args.input_filename
                    Diff.execute('sort -o {} {}'.format(args.CC_input, args.CC_input))
                with open(args.CC_input, 'r') as f, Processor(compute_metrics=args.compute_metrics, compute_CC=True) as processor:
                    for line in f:
                        if count % 10000 == 0:
                            logger.info('{}: processed bibcodes count = {}'.format(datetime.datetime.now(), count))
                        count = count + 1
                        line = line.strip()
                        if line:
                            bibcodes.append(line)
                            if len(bibcodes) % 100 == 0:
                                processor.process_bibcodes(bibcodes)
                                bibcodes = []
                    if len(bibcodes) > 0:
                        processor.process_bibcodes(bibcodes)
                logger.info('{}: completed processing bibcodes from {}, count = {}'.format(datetime.datetime.now(), args.CC_input, count))
                            

if __name__ == '__main__':
    main()
