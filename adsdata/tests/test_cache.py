
from mock import patch
from mock import mock_open
import StringIO
import mock
import unittest

from adsdata import memory_cache


class TestMemoryCache(unittest.TestCase):

    def test_refereed(self):
        m = mock_open(read_data='asdf\njkl')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('__builtin__.open', m):
            ref = memory_cache.Refereed()
            self.assertTrue('asdf' in ref)
            self.assertTrue('asdf' in ref.refereed)
            self.assertFalse('asdfasdf' in ref.refereed)

    def test_reference(self):
        m = mock_open(read_data='2014arXiv1401.7089B\t2003ASPC..295..361M\n2016PhRvL.116f1102A\t2003ASPC..295..361M\n')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('__builtin__.open', m):
            ref = memory_cache.ReferenceNetwork()
            self.assertTrue('2003ASPC..295..361M' in ref.network['2014arXiv1401.7089B'])
            self.assertEqual(len(ref.network['2014arXiv1401.7089B']), 1)
            self.assertEqual(len(ref.network), 2)
            self.assertTrue('2003ASPC..295..361M' in ref.network['2016PhRvL.116f1102A'])

    def test_citation(self):
        m = mock_open(read_data='2003ASPC..295..361M\t2014arXiv1401.7089A\n2003ASPC..295..361M\t2014arXiv1401.7089B\n2016PhRvL.116f1102A\t2003ASPC..295..361M\n')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('__builtin__.open', m):
            cite = memory_cache.CitationNetwork()
            self.assertTrue('2014arXiv1401.7089B' in cite.network['2003ASPC..295..361M'])
            self.assertEqual(len(cite.network['2003ASPC..295..361M']), 2)
            self.assertEqual(len(cite.network), 2)
