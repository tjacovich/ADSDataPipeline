
from mock import patch
from io import StringIO

import unittest

from adsdata import reader


class TestReader(unittest.TestCase):
    """ it is important to have comprehensive tests for reader

    tests use StringIO because it supports tell and seek (unlike simplier mocks) """
    
    def test_refereed(self):
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': True}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'refereed': True}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': False}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': True}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': True}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': True}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'refereed': True}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('refereed', 'filename')
            self.assertEqual({'refereed': False}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': True}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'refereed': False}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_standard(self):
        # test that we can read values for bibcodes
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
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
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'reads': ['D']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        # test that we receive no value when we read a bibcode that isn't present
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('reads', 'filename')
            self.assertEqual({'reads': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'reads': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_repeated_bibcode(self):
        # test that repeated bibcodes are properly rolled up
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
AAAAAAAAAAAAAAAAAAA\tAA
AAAAAAAAAAAAAAAAAAA\tAAA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
DDDDDDDDDDDDDDDDDDD\tDD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('citation', 'filename')
            self.assertEqual({'citation': ['A', 'AA', 'AAA']}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'citation': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'citation': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'citation': ['D', 'DD']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'citation': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'citation': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_links(self):
        """read in data links files"""
        # facet_datasources/datasources.links
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\tARI\t1\thttp://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202')):
            f = reader.StandardFileReader('data_link', 'filename')
            v = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            a = {'data_link': {'link_type': 'DATA', 'link_sub_type': 'ARI', 'item_count': 1, 'property': ['DATA'],
                               'url': ['http://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202'], 'title': ['']}}
            self.assertEqual(a, v)

                              
        # electr/all.links
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\thttps://doi.org/10.3931%2Fe-rara-477')):
            f = reader.StandardFileReader('pub_html', 'filename')
            x = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            self.assertEqual({'pub_html': {'link_type': 'ESOURCE', 'link_sub_type': 'PUB_HTML',
                                           'url': ['https://doi.org/10.3931%2Fe-rara-477'],
                                           'property': ['ADS_OPENACCESS', 'ARTICLE', 'OPENACCESS']}}, x)
            # f.read_value_for('AAAAAAAAAAAAAAAAAAA'))

        # eprint_html/all.links
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\thttps://arxiv.org/abs/0908.1823')):
            f = reader.StandardFileReader('eprint_html', 'filename')
            x = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            self.assertEqual({'eprint_html': {'link_type': 'ESOURCE', 'link_sub_type': 'EPRINT_HTML',
                                              'url': 'https://arxiv.org/abs/0908.1823'}}, x)
                             
    def test_list(self):
        # first line of config/links/reads/downloads.links
        download_line = '1057wjlf.book.....C\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1'
        with patch('builtins.open', return_value=StringIO(download_line)):
            f = reader.StandardFileReader('download', 'filename')
            x = f.read_value_for('1057wjlf.book.....C')
            self.assertEqual({'download': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}, x)
        citation_lines = '1890GSAB....1..411D\t2011ESRv..106..215H\n1890GSAB....1..411D\t2014SedG..311...60T\n1890GSAB....1..411D\t2015GSAB..127.1816C'
        with patch('builtins.open', return_value=StringIO(citation_lines)):
            f = reader.StandardFileReader('citation', 'filename')
            x = f.read_value_for('1890GSAB....1..411D')
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

        v = r.read_value_for('2003ASPC..295..361M')
        self.assertTrue('relevance' in v)
        # self.assertEqual(4, len(v['relevance'].keys()))
        self.assertAlmostEqual(.15, v['relevance']['boost']) 
        self.assertEqual(0, v['relevance']['citation_count'])
        self.assertEqual(4, v['relevance']['read_count'])
        self.assertEqual(0, v['relevance']['norm_cites'])

    def test_toc(self):
        r = reader.StandardFileReader('toc', './adsdata/tests/data1/config/links/toc/all.links')
        v = r.read_value_for('2003ASPC..295..361M')
        self.assertTrue('toc' in v)
        self.assertTrue(v['toc'])
        v = r.read_value_for('2004ASPC..295..361M')
        self.assertFalse(v['toc'])

    def test_associated(self):
        with patch('builtins.open', return_value=StringIO('1850AJ......1...72H\t1850AJ......1...57H Main Paper\n1850AJ......1...72H\t1850AJ......1...72H Erratum')):
            f = reader.StandardFileReader('associated', 'filename')
            x = f.read_value_for('1850AJ......1...72H')
            a = {'associated': {'link_type': 'ASSOCIATED', 'link_sub_type': 'NA',
                                'url': ['1850AJ......1...57H', '1850AJ......1...72H'],
                                'title': ['Main Paper', 'Erratum']}}
            self.assertEqual(a, x)

    def test_simbad(self):
        with patch('builtins.open', return_value=StringIO('1857AN.....45...89S\t1500441\tLP*')):
            f = reader.StandardFileReader('simbad_objects', 'filename')
            x = f.read_value_for('1857AN.....45...89S')
            self.assertEqual({'simbad_objects': ['1500441', 'LP*']}, x)

    def test_ned(self):
        with patch('builtins.open', return_value=StringIO('1885AN....112..285E\tMESSIER_031\tG\n1885AN....112..285E\tSN_1885A\tSN')):
            f = reader.StandardFileReader('ned_objects', 'filename')
            x = f.read_value_for('1885AN....112..285E')
            self.assertEqual({'ned_objects': ["MESSIER_031 G", "SN_1885A SN"]}, x)

    def test_isfloat(self):
        self.assertTrue(reader.isFloat('1.2'))
        self.assertTrue(reader.isFloat('1'))
        self.assertFalse(reader.isFloat('abc'))
        self.assertFalse(reader.isFloat('ab.c'))
        
