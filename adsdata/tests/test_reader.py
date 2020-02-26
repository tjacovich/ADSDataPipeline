
from mock import patch
from mock import mock_open
import StringIO
import mock
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):
    """ it is important to have comprehensive tests for reader

    tests use StringIO because it supports tell and seek (unlike simplier mocks) """
    
    def test_refereed(self):
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename', bool)
            self.assertTrue(f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertTrue(True, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename', bool)
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertTrue(f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename', bool)
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_standard(self):
        # test that we can read values for bibcodes
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['A'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test we can skip bibcodes that are in the file
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        # test that we receive no value when we read a bibcode that isn't present
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test that repeated bibcodes are properly rolled up
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
AAAAAAAAAAAAAAAAAAA\tAA
AAAAAAAAAAAAAAAAAAA\tAAA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
DDDDDDDDDDDDDDDDDDD\tDD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['A', 'AA', 'AAA'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual(['D', 'DD'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_links(self):
        """read in data links files"""
        # facet_datasources/datasources.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\tARI\t1\thttp://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202')):
                   f = reader.StandardFileReader('filename')
                   self.assertEqual(['ARI', '1', 'http://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))

        # electr/all.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\thttps://doi.org/10.3931%2Fe-rara-477')):
                   f = reader.StandardFileReader('filename')
                   self.assertEqual(['https://doi.org/10.3931%2Fe-rara-477'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))

        # eprint_html/all.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\thttps://arxiv.org/abs/0908.1823')):
                   f = reader.StandardFileReader('filename')
                   self.assertEqual(['https://arxiv.org/abs/0908.1823'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))

    def test_list(self):
        # first line of config/links/reads/downloads.links
        download_line = '1057wjlf.book.....C\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1'
        with patch('__builtin__.open', return_value=StringIO.StringIO(download_line)):
            f = reader.StandardFileReader('filename')
            l = f.read_value_for('1057wjlf.book.....C')
            print '!!', l
            self.assertEqual(1, l[0])
            self.assertEqual(0, l[1])
            self.assertEqual(0, l[-2])
            self.assertEqual(1, l[-1])
        citation_lines = '1890GSAB....1..411D\t2011ESRv..106..215H\n1890GSAB....1..411D\t2014SedG..311...60T\n1890GSAB....1..411D\t2015GSAB..127.1816C'
        with patch('__builtin__.open', return_value=StringIO.StringIO(citation_lines)):
            f = reader.StandardFileReader('filename')
            l = f.read_value_for('1890GSAB....1..411D')
            print '!!', l
            self.assertEqual('2011ESRv..106..215H', l[0])
            self.assertEqual('2014SedG..311...60T', l[1])
            self.assertEqual('2015GSAB..127.1816C', l[2])
            self.assertEqual(3, len(l))

