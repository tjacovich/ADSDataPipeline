
from collections import defaultdict
from adsputils import setup_logging

# code for in-memory caches

logger = setup_logging('adsdata', 'INFO')

class BaseNetwork:

    def _load(self, filename):
        """load file containing entire citation network into dict"""
        global logger
        d = defaultdict(set)
        count = 0
        with open(filename) as f:
            for line in f:
                # need more clean up on input
                print('line: {}'.format(line))
                line = line.strip()
                bibcode1 = line[:19]
                bibcode2 = line[20:39]
                d[bibcode1].add(bibcode2)
                count += 1
                if count % 1000000 == 0:
                    logger.info('reading {}, count = {}'.format(filename, count))
        return d
        # logger.info('completed {}, count = {}'.format(filename, count))


class ReferenceNetwork(BaseNetwork):

    def __init__(self):
        """load file containing entire citation network into dict"""
        self.network = self._load('reference filename')


class CitationNetwork(BaseNetwork):

    def __init__(self):
        """load file containing entire citation network into dict"""
        self.network = self._load('citation filename')


class Refereed:
    """a simple file with one bibcode on each line"""
    def __init__(self):
        self.refereed = self._load('refereed filename')
        
    def _load(self, filename):
        logger.info('starting to load refereed')
        d = set()
        count = 0
        with open(filename) as f:
            for line in f:
                # need more clean up on input
                line = line.strip()
                d.add(line)
                count += 1
                if count % 1000000 == 0:
                    logger.info('reading refereed, count = {}'.format(count))
        logger.info('completed refereed')    
        return d


