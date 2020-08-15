
from collections import defaultdict

from adsdata import tasks

# code for in-memory caches

logger = tasks.app.logger
bibcode_length = 19


class Network:

    def __init__(self, filename):
        self.network = self._load(filename)

    def __getitem__(self, bibcode):
        return self.network[bibcode]
        
    def __setitem__(self, bibcode, value):
        self.network[bibcode] = value

    def _load(self, filename):
        """load file containing entire citation network into dict"""
        global logger, bibcode_length
        d = defaultdict(list)
        count = 0
        expected_length = 2 * bibcode_length + 1
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # need more clean up on input
                line = line.strip()
                if len(line) == expected_length:
                    bibcode1 = line[:19]
                    bibcode2 = line[20:39]
                    d[bibcode1].append(bibcode2)
                else:
                    logger.error('error in network cache reading {}, line = {}'.format(filename, line))
                count += 1
                if count % 1000000 == 0:
                    logger.info('reading {}, count = {}'.format(filename, count))
        return d
        # logger.info('completed {}, count = {}'.format(filename, count))

    def __iter__(self):
        return self.network.__iter__()

    def __next__(self):
        return self.network.__next__()
        
    def get(self, bibcode):
        return self.network[bibcode]


class Refereed:
    """a simple file with one bibcode on each line

    I've read that memberhip of a set is O(1) suggesting there some hashing in the background
    but, membership test seems to use the iterator.  
    It is important that membership test be O(1) rather than O(n).  
    """
    def __init__(self, filename):
        self.network = self._load(filename)

    # def __iter__(self):
    #    return self.network.__iter__()

    def _load(self, filename):
        logger.info('starting to load refereed')
        d = []
        count = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # need more clean up on input
                line = line.strip()
                if len(line) == bibcode_length:
                    d.append(line)
                else:
                    logger.error('error in refereed cache reading {}, line = {}'.format(filename, line))
                count += 1
                if count % 1000000 == 0:
                    logger.info('reading refereed, count = {}'.format(count))
        logger.info('completed refereed')    
        return set(d)
