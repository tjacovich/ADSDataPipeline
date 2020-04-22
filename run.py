
#!/usr/bin/env python

import adsputils
import argparse

from adsdata import process
from adsdata import memory_cache


def main():
    parser = argparse.ArgumentParser(description='Process user input.')
    parser.add_argument('-b', '--bibcodes', dest='bibcodes', action='store',
                        help='A list of bibcodes separated by spaces')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='after cache init user can enter bibcodes')

    args = parser.parse_args()
    if args.bibcodes:
        args.bibcodes = args.bibcodes.split(' ')
        args.bibcodes.sort()

    c = memory_cache.init()    
    print 'cache ready'

    if args.bibcodes:
        process.process_bibcode(args.bibcodes)
    elif args.interactive:
        while True:
            i = raw_input('enter bibcode: ')
            process.process_bibcode([i.strip()])
    else:
        process.process()
    

if __name__ == '__main__':
    main()
