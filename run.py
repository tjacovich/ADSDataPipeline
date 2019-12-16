
#!/usr/bin/env python

import adsputils
import argparse

from adsdata import process
from adsdata import memory_cache

def main():
    parser = argparse.ArgumentParser(description='Process user input.')

    args = parser.parse_args()
    c = memory_cache.init()
    print 'cache ready'
    process.process()
    

if __name__ == '__main__':
    main()
