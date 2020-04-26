
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
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': True}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'refereed': True}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': False}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': True}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': True}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': True}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'refereed': True}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': False}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': True}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'refereed': False}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_standard(self):
        # test that we can read values for bibcodes
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': ['A']}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'reads': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'reads': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'reads': ['D']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'reads': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test we can skip bibcodes that are in the file
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'reads': ['D']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        # test that we receive no value when we read a bibcode that isn't present
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'reads': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test that repeated bibcodes are properly rolled up
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
AAAAAAAAAAAAAAAAAAA\tAA
AAAAAAAAAAAAAAAAAAA\tAAA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
DDDDDDDDDDDDDDDDDDD\tDD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': ['A', 'AA', 'AAA']}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'reads': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'reads': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'reads': ['D', 'DD']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'reads': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_links(self):
        """read in data links files"""
        # facet_datasources/datasources.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\tARI\t1\thttp://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202')):
            f = reader.StandardFileReader('data_link', 'filename')
            self.assertEqual({'data_link': {'link_type': 'DATA', 'link_sub_type': 'ARI', 'item_count': 1,
                                            'url': 'http://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202', 'title': ''}},
                             f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
                              
        # electr/all.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\thttps://doi.org/10.3931%2Fe-rara-477')):
            f = reader.StandardFileReader('pub_html', 'filename')
            x = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            self.assertEqual({'pub_html': {'link_type': 'ESOURCE', 'link_sub_type': 'PUB_HTML',
                                           'url': 'https://doi.org/10.3931%2Fe-rara-477'}}, x)
            # f.read_value_for('AAAAAAAAAAAAAAAAAAA'))

        # eprint_html/all.links
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\thttps://arxiv.org/abs/0908.1823')):
            f = reader.StandardFileReader('eprint_html', 'filename')
            x = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            self.assertEqual({'eprint_html': {'link_type': 'ESOURCE', 'link_sub_type': 'EPRINT_HTML',
                                              'url': 'https://arxiv.org/abs/0908.1823'}}, x)
                             
    def test_list(self):
        # first line of config/links/reads/downloads.links
        download_line = '1057wjlf.book.....C\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1'
        with patch('__builtin__.open', return_value=StringIO.StringIO(download_line)):
            f = reader.StandardFileReader('download', 'filename')
            x = f.read_value_for('1057wjlf.book.....C')
            print '!!', x
            self.assertEqual({'download': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}, x)
        citation_lines = '1890GSAB....1..411D\t2011ESRv..106..215H\n1890GSAB....1..411D\t2014SedG..311...60T\n1890GSAB....1..411D\t2015GSAB..127.1816C'
        with patch('__builtin__.open', return_value=StringIO.StringIO(citation_lines)):
            f = reader.StandardFileReader('citation', 'filename')
            x = f.read_value_for('1890GSAB....1..411D')
            print '!!', x
            self.assertEqual({'citation': ['2011ESRv..106..215H', '2014SedG..311...60T', '2015GSAB..127.1816C']}, x)

    def test_downloads(self):
        bibcodes = ['1057wjlf.book.....C', '1886Natur..34Q.131.', '1905PhRvI..21..247N', '1908PhRvI..27..367N']
        downloads = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     [],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        r = reader.StandardFileReader('download', './adsdata/tests/data1/config/links/reads/downloads.links')
        for i in range(0, len(bibcodes) - 1):
            x = r.read_value_for(bibcodes[i])
            self.assertEqual({'download': downloads[i]}, x)

    def test_relevance(self):
        r = reader.StandardFileReader('relevance', './adsdata/tests/data1/config/links/relevance/docmetrics.tab')
        v = r.read_value_for('1905PhRvI..21..247N')
        self.assertTrue('relevance' in v)
        # self.assertEqual(4, len(v['relevance'].keys()))
        self.assertAlmostEqual(.11, v['relevance']['boost']) 
        self.assertEqual(2, v['relevance']['citation_count'])
        self.assertEqual(0, v['relevance']['read_count'])
        self.assertEqual(2386, v['relevance']['norm_cites'])

    def test_associated(self):
        with patch('__builtin__.open', return_value=StringIO.StringIO('1850AJ......1...72H\t1850AJ......1...57H\tMain Paper\n1850AJ......1...72H\t1850AJ......1...72H\tErratum')):
            f = reader.StandardFileReader('associated', 'filename')
            x = f.read_value_for('1850AJ......1...72H')
            self.assertEqual({'associated': {'link_type': 'ASSOCIATED', 'link_sub_type': 'NA',
                                             'url': ['1850AJ......1...57H', '1850AJ......1...72H'],
                                             'title': ['Main Paper', 'Erratum']}},
                             x)
                   
    def test_isfloat(self):
        self.assertTrue(reader.isFloat('1.2'))
        self.assertTrue(reader.isFloat('1'))
        self.assertFalse(reader.isFloat('abc'))
        self.assertFalse(reader.isFloat('ab.c'))
        
