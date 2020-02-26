
import mock
from mock import patch
from mock import mock_open
import StringIO
import unittest

from adsdata import metrics


class TestMetrics(unittest.TestCase):
    
    def test_simple(self):
        d = {'canonical': "1998PPGeo..22..553A", 'refereed': False, 'authors': ["Arnfield, A. L."],
             'downloads': [], 'reads': [1, 2, 3, 4], 'downloads': [0, 1, 2, 3],
             'citations':  [], 'id': 11, 'reference': ["1997BoLMe..85..475M"]}
        with patch('adsdata.memory_cache.get', return_value={'refereed': [], 'reference': {}, 'citation': {}}):
            m = metrics.compute_metrics(d)
            self.assertEqual(m['bibcode'], d['canonical'])
