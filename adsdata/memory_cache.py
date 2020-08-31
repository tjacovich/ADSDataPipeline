
from collections import defaultdict

from adsdata import tasks
from adsdata.file_defs import data_files
from adsputils import load_config

# Code for in-memory caches of citation network, reference network and refereed list
# The cache uses about 50GB of RAM.


class Cache:
    """Provides the class method 'get' to obtain reference, citation or refereed data"""
    
    _initted = False
    _reference_network = None
    _citation_network = None
    _refereed_list = None

    def __init__(self):
        raise RuntimeError('Do not instantiate, call class method get instead')

    @classmethod
    def get(cls, which):
        """returns either a dict (for citation or reference) or a set (for refereed)"""
        if cls._initted is False:
            cls.init()
        if which == 'citation':
            return cls._citation_network.network
        elif which == 'reference':
            return cls._reference_network.network
        elif which == 'refereed':
            return cls._refereed_list.network
        else:
            raise ValueError('Cache.get called with invalid value: {}'.format(which))
        
    @classmethod
    def init(cls):
        if cls._initted is False:
            config = load_config()
            root_dir = config.get('INPUT_DATA_ROOT', './adsdata/tests/data1/config/')
            cls._reference_network = _Network(root_dir + data_files['reference']['path'])
            cls._citation_network = _Network(root_dir + data_files['citation']['path'])
            cls._refereed_list = _Refereed(root_dir + data_files['refereed']['path'])
            cls._initted = True


class _Network:
    """Reads network file into a python dict instance

    A network file (either citation network or reference network) contains two bibcodes
    on every line.  In the reference network file, the first bibcode references the
    second bibcode.  In the citation network file, the first bibcode is cited by the
    second bibcode.  For a variety of reasons, the citation network is not the inverse
    of the reference network.
    """
    
    bibcode_length = 19
    
    def __init__(self, filename):
        self.logger = tasks.app.logger
        self.network = self._load(filename)

    def __getitem__(self, bibcode):
        return self.network[bibcode]
        
    def __setitem__(self, bibcode, value):
        self.network[bibcode] = value

    def _load(self, filename):
        """read a file containing an entire network into dict"""
        d = defaultdict(list)
        count = 0
        expected_length = 2 * self.bibcode_length + 1
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # need more clean up on input
                line = line.strip()
                if len(line) == expected_length:
                    bibcode1 = line[:19]
                    bibcode2 = line[20:39]
                    d[bibcode1].append(bibcode2)
                else:
                    self.logger.error('error in network cache reading {}, line = {}'.format(filename, line))
                count += 1
                if count % 1000000 == 0:
                    self.logger.info('reading {}, lines read = {}'.format(filename, count))
        self.logger.info('completed {}, lines read = {}'.format(filename, count))
        return d

    def __iter__(self):
        return self.network.__iter__()

    def __next__(self):
        return self.network.__next__()
        

class _Refereed:
    """Reads refereed file into a  python set instance

    The input file contains one bibcode on each line.
    """

    bibcode_length = 19
    
    def __init__(self, filename):
        self.logger = tasks.app.logger
        self.network = self._load(filename)

    def _load(self, filename):
        self.logger.info('starting to load refereed')
        d = []
        count = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # need more clean up on input
                line = line.strip()
                if len(line) == self.bibcode_length:
                    d.append(line)
                else:
                    self.logger.error('error in refereed cache reading {}, line = {}'.format(filename, line))
                count += 1
                if count % 1000000 == 0:
                    self.logger.info('reading refereed bibcodes, lines read = {}'.format(count))
        self.logger.info('completed refereed, lines read = {}'.format(count))
        return set(d)
