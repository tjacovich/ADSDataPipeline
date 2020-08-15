
from unittest.mock import patch, mock_open
import unittest
from adsdata import memory_cache


class TestMemoryCache(unittest.TestCase):

    def test_refereed(self):
        with patch('builtins.open', mock_open(read_data='1234567890123456789\n2234567890123456789')):
            ref = memory_cache.Refereed('foo.txt')
            self.assertTrue('1234567890123456789' in ref.network)
            self.assertFalse('asdfasdf' in ref.network)
            self.assertTrue(type(ref.network) is set)

    def test_refereed_invalid_bibcode(self):
        with patch('builtins.open', mock_open(read_data='1234567890123456789\n211\n2234567890123456789')):
            with patch('adsdata.memory_cache.logger') as m:
                ref = memory_cache.Refereed('foo.txt')
                self.assertTrue('1234567890123456789' in ref.network)
                self.assertTrue('2234567890123456789' in ref.network)
                self.assertFalse('asdfasdf' in ref.network)
                self.assertTrue(type(ref.network) is set)
                self.assertTrue(m.error.called)

    def test_reference(self):
        with patch('builtins.open',
                   mock_open(read_data='2014arXiv1401.7089B\t2003ASPC..295..361M\n2016PhRvL.116f1102A\t2003ASPC..295..361M\n')):
            ref = memory_cache.Network('foo.txt')
            self.assertTrue('2003ASPC..295..361M' in ref.network['2014arXiv1401.7089B'])
            self.assertEqual(len(ref.network['2014arXiv1401.7089B']), 1)
            self.assertEqual(len(ref.network), 2)
            self.assertTrue('2003ASPC..295..361M' in ref.network['2016PhRvL.116f1102A'])

    def test_citation(self):
        with patch('builtins.open', mock_open(read_data='2003ASPC..295..361M\t2014arXiv1401.7089A\n2003ASPC..295..361M\t2014arXiv1401.7089B\n2016PhRvL.116f1102A\t2003ASPC..295..361M\n')):
            cite = memory_cache.Network('foo.txt')
            self.assertTrue('2014arXiv1401.7089B' in cite.network['2003ASPC..295..361M'])
            self.assertEqual(len(cite.network['2003ASPC..295..361M']), 2)
            self.assertEqual(len(cite.network), 2)
            self.assertEqual([], cite.network['asdf'])

    def test_citation_invalid_bibcode(self):
        with patch('builtins.open', mock_open(read_data='2003ASPC..295..361M\t2014arXiv1401.7089A\nasdf\n2003ASPC..295..361M\t2014arXiv1401.7089B\n2016PhRvL.116f1102A\t2003ASPC..295..361M\n')):
            with patch('adsdata.memory_cache.logger') as m:
                cite = memory_cache.Network('foo.txt')
                self.assertTrue('2014arXiv1401.7089B' in cite.network['2003ASPC..295..361M'])
                self.assertEqual(len(cite.network['2003ASPC..295..361M']), 2)
                self.assertEqual(len(cite.network), 2)
                self.assertEqual([], cite.network['asdf'])
                self.assertTrue(m.error.called)
