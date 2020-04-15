
import mock
from mock import patch
from mock import mock_open
import StringIO
import io
import unittest

from adsdata import metrics
from adsdata import memory_cache


class TestMetrics(unittest.TestCase):
    
    def test_simple(self):
        d = {'canonical': "1998PPGeo..22..553A", 'refereed': False, 'authors': ["Arnfield, A. L."],
             'reads': [1, 2, 3, 4], 'download': [0, 1, 2, 3],
             'citations':  [], 'id': 11, 'reference': ["1997BoLMe..85..475M"]}
        m = mock_open(read_data='')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('__builtin__.open', m):
            x = memory_cache.BaseNetwork('foo')
            y = memory_cache.BaseNetwork('foo')
            z = memory_cache.BaseNetwork('foo')
            memory_cache.cache['reference'] = x
            memory_cache.cache['citation'] = y
            memory_cache.cache['refereed'] = z

            m = metrics.compute_metrics(d)
            self.assertEqual(m['bibcode'], d['canonical'])
