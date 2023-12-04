
from mock import patch
from io import StringIO

import unittest

from adsdata import reader
from adsdata.file_defs import data_files

class TestReader(unittest.TestCase):
    """ it is important to have comprehensive tests for reader

    tests use StringIO because it supports tell and seek (unlike simplier mocks) """
    
    def test_refereed(self):
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.NonbibFileReader('refereed', data_files['refereed'])
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': {'refereed': False}}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.NonbibFileReader('refereed', data_files['refereed'])
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.NonbibFileReader('refereed', data_files['refereed'])
            self.assertEqual({'refereed': {'refereed': False}}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'refereed': {'refereed': False}}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_standard(self):
        # test that we can read values for bibcodes
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.NonbibFileReader('reads', data_files['reads'])
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
            f = reader.NonbibFileReader('reads', data_files['reads'])
            self.assertEqual({'reads': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'reads': ['D']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'reads': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        # test that we receive no value when we read a bibcode that isn't present
        with patch('builtins.open', return_value=StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.NonbibFileReader('reads', data_files['reads'])
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
            f = reader.NonbibFileReader('citation', data_files['citation'])
            self.assertEqual({'citation': ['A', 'AA', 'AAA']}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual({'citation': ['B']}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual({'citation': []}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual({'citation': ['D', 'DD']}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual({'citation': ['E']}, f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertEqual({'citation': []}, f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_links(self):
        """read in data links files"""
        # facet_datasources/datasources.links
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\tARI\t1\thttp://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202')):
            f = reader.NonbibFileReader('data_link', data_files['data_link'])
            v = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            a = {'data_link': {'link_type': 'DATA', 'link_sub_type': 'ARI', 'item_count': 1, 'property': ['DATA'],
                               'url': ['http://dc.g-vo.org/arigfh/katkat/byhdw/qp/1202'], 'title': ['']}}
            self.assertEqual(a, v)

        with patch('builtins.open', return_value=StringIO('2004MNRAS.354L..31M\tCDS\t2\thttp://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31\n2004MNRAS.354L..31M\tVizier\t1\thttp://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31')):
            f = reader.NonbibFileReader('data_link', data_files['data_link'])
            v = f.read_value_for('2004MNRAS.354L..31M')
            a = {'data_link':
                 [{"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "title": [""], "item_count": 2, "link_type": "DATA", "link_sub_type": "CDS", 'property': ['DATA']},
                  {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "title": [""], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier", 'property': ['DATA']}]}
            self.assertEqual(a, v)

        # electr/all.links
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\thttps://doi.org/10.3931%2Fe-rara-477')):
            f = reader.NonbibFileReader('pub_html', data_files['pub_html'])
            x = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            self.assertEqual({'pub_html': {'link_type': 'ESOURCE', 'link_sub_type': 'PUB_HTML',
                                           'url': ['https://doi.org/10.3931%2Fe-rara-477']}}, x)

        # eprint_html/all.links
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\thttps://arxiv.org/abs/0908.1823')):
            f = reader.NonbibFileReader('eprint_html', data_files['eprint_html'])
            v = f.read_value_for('AAAAAAAAAAAAAAAAAAA')
            a = {'eprint_html': {'link_type': 'ESOURCE', 'link_sub_type': 'EPRINT_HTML',
                                 'url': 'https://arxiv.org/abs/0908.1823',
                                 'property': ['EPRINT_OPENACCESS', 'OPENACCESS']}}
            self.assertEqual(a, v)
                             
    def test_list(self):
        # first line of config/links/reads/downloads.links
        self.maxDiff = None
        download_line = '1057wjlf.book.....C\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1'
        with patch('builtins.open', return_value=StringIO(download_line)):
            f = reader.NonbibFileReader('download', data_files['download'])
            x = f.read_value_for('1057wjlf.book.....C')
            self.assertEqual({'download': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}, x)
        citation_lines = '1890GSAB....1..411D\t2011ESRv..106..215H\n1890GSAB....1..411D\t2014SedG..311...60T\n1890GSAB....1..411D\t2015GSAB..127.1816C'
        with patch('builtins.open', return_value=StringIO(citation_lines)):
            f = reader.NonbibFileReader('citation', data_files['citation'])
            x = f.read_value_for('1890GSAB....1..411D')
            self.assertEqual({'citation': ['2011ESRv..106..215H', '2014SedG..311...60T', '2015GSAB..127.1816C']}, x)

    def test_downloads(self):
        self.maxDiff = None
        bibcodes = ['1057wjlf.book.....C', '1886Natur..34Q.131.', '1905PhRvI..21..247N', '1908PhRvI..27..367N', '2003ASPC..295..361M']
        downloads = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     [],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0]]
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('download', data_files['download'])
            for i in range(0, len(bibcodes)):
                x = r.read_value_for(bibcodes[i])
                a = {'download': downloads[i]}
                self.assertEqual(a, x, 'for bibcode ' + bibcodes[i])

    def test_grants(self):
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('grants', data_files['grants'])
            v = r.read_value_for('1980AJ.....85..780L')
            self.assertTrue('grants' in v)
            self.assertEqual(v['grants'], ['NSF-AST 0725267', 'NSF-AST 1211349'])
            v = r.read_value_for('2010AJ....140..933R')
            self.assertTrue('grants' in v)
            self.assertEqual(v['grants'], ['NSF-AST 0706980'])
        
    def test_relevance(self):
        self.maxDiff = None
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('relevance', data_files['relevance'])
            v = r.read_value_for('1905PhRvI..21..247N')
            self.assertTrue('relevance' in v)
            # self.assertEqual(4, len(v['relevance'].keys()))
            self.assertAlmostEqual(.11, v['relevance']['boost']) 
            self.assertEqual(2, v['relevance']['deprecated_citation_count'])
            self.assertEqual(0, v['relevance']['read_count'])
            self.assertEqual(2386, v['relevance']['norm_cites'])

            v = r.read_value_for('2003ASPC..295..361M')
            self.assertTrue('relevance' in v)
            # self.assertEqual(4, len(v['relevance'].keys()))
            self.assertAlmostEqual(.15, v['relevance']['boost'])
            self.assertEqual(0, v['relevance']['deprecated_citation_count'])
            self.assertEqual(4, v['relevance']['read_count'])
            self.assertEqual(0, v['relevance']['norm_cites'])
            
    def test_refereed_from_file(self):
        self.maxDiff = None
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('refereed', data_files['refereed'])
            v = r.read_value_for('2004MNRAS.354L..31M')
            a = {'refereed': {'refereed': True, 'property': ['REFEREED']}}
            self.assertEqual(a, v)
    
    def test_toc(self):
        self.maxDiff = None
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('toc', data_files['toc'])
            v = r.read_value_for('2003ASPC..295..361M')
            a = {'toc': {'toc': True, 'link_type': 'TOC', 'link_sub_type': 'NA'}}
            self.assertEqual(a, v)
            v = r.read_value_for('2004ASPC..295..361M')
            a = {'toc': {'toc': False}}
            self.assertEqual(a, v)

    def test_private(self):
        self.maxDiff = None
        with patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            r = reader.NonbibFileReader('private', data_files['private'])
            v = r.read_value_for('1920NW......8..958S')
            a = {'private': {'private': True, 'property': ['PRIVATE']}}
            self.assertEqual(a, v)
            v = r.read_value_for('2003ASPC..295..361M')
            a = {'private': {'private': False}}
            self.assertEqual(a, v)

    def test_associated(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1850AJ......1...72H\t1850AJ......1...57H Main Paper\n1850AJ......1...72H\t1850AJ......1...72H Erratum')):
            f = reader.NonbibFileReader('associated', data_files['associated'])
            v = f.read_value_for('1850AJ......1...72H')
            a = {'associated': {'link_type': 'ASSOCIATED', 'link_sub_type': 'NA',
                                'url': ['1850AJ......1...57H', '1850AJ......1...72H'],
                                'title': ['Main Paper', 'Erratum']}}
            self.assertEqual(a, v)

        # a few bibcodes only have one entry in associated
        with patch('builtins.open', return_value=StringIO('1993yCat.3135....0C\t1993yCat.3135....0C Catalog Description')):
            f = reader.NonbibFileReader('associated', data_files['associated'])
            v = f.read_value_for('1993yCat.3135....0C')
            a = {'associated': {'link_type': 'ASSOCIATED', 'link_sub_type': 'NA',
                                'url': ['1993yCat.3135....0C'],
                                'title': ['Catalog Description']}}
            self.assertEqual(a, v)

    def test_simbad(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1857AN.....45...89S\t1500441\tLP*')):
            f = reader.NonbibFileReader('simbad_objects', data_files['simbad_objects'])
            v = f.read_value_for('1857AN.....45...89S')
            self.assertEqual({'simbad_objects': ['1500441 LP*']}, v)
        with patch('builtins.open', return_value=StringIO('2010A&A...521A..55C\t2419335\treg\n2010A&A...521A..55C\t3754378\tGrG')):
            f = reader.NonbibFileReader('simbad_objects', data_files['simbad_objects'])
            v = f.read_value_for('2010A&A...521A..55C')
            self.assertEqual({'simbad_objects': ['2419335 reg', '3754378 GrG']}, v)
        with patch('builtins.open', return_value=StringIO('1991PASP..103..494P\t947046\t')):
            f = reader.NonbibFileReader('simbad_objects', data_files['simbad_objects'])
            v = f.read_value_for('1991PASP..103..494P')
            self.assertEqual({'simbad_objects': ['947046 ']}, v)

    def test_ned(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1885AN....112..285E\tMESSIER_031\tG\n1885AN....112..285E\tSN_1885A\tSN')):
            f = reader.NonbibFileReader('ned_objects', data_files['ned_objects'])
            v = f.read_value_for('1885AN....112..285E')
            self.assertEqual({'ned_objects': ["MESSIER_031 G", "SN_1885A SN"]}, v)
        with patch('builtins.open', return_value=StringIO('1885AN....112..285E\tMESSIER_031\tG\n1885AN....112..285E\tSN_1885A')):
            f = reader.NonbibFileReader('ned_objects', data_files['ned_objects'])
            v = f.read_value_for('1885AN....112..285E')
            self.assertEqual({'ned_objects': ["MESSIER_031 G", "SN_1885A "]}, v)

    def test_presentation(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1997kbls.confE..10C\thttp://online.kitp.ucsb.edu/online/bblunch/carroll/')):
            f = reader.NonbibFileReader('presentation', data_files['presentation'])
            v = f.read_value_for('1997kbls.confE..10C')
            a = {'presentation': {'link_type': 'PRESENTATION', 'link_sub_type': 'NA',
                                  'url': ['http://online.kitp.ucsb.edu/online/bblunch/carroll/']}}
            self.assertEqual(a, v)

    def test_librarycatalog(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1810hdla.book.....V\thttp://www.worldcat.org/oclc/02869597')):
            f = reader.NonbibFileReader('librarycatalog', data_files['librarycatalog'])
            v = f.read_value_for('1810hdla.book.....V')
            a = {'librarycatalog': {'link_type': 'LIBRARYCATALOG', 'link_sub_type': 'NA',
                                    'url': ['http://www.worldcat.org/oclc/02869597']}}
            self.assertEqual(a, v)

    def test_ocrabstract(self):
        self.maxDiff = None
        with patch('builtins.open', return_value=StringIO('1886Natur..34Q.131.\n1954PhRv...96..730K\n')):
            f = reader.NonbibFileReader('ocrabstract', data_files['ocrabstract'])
            v = f.read_value_for('1954PhRv...96..730K')
            a = {'ocrabstract': {'property': ['OCRABSTRACT'], 'ocrabstract': True}}
            self.assertEqual(a, v)
        
    def test_convert_scalar(self):
        with patch('builtins.open', return_value=StringIO('')):
            f = reader.NonbibFileReader('refereed', data_files['refereed'])
            self.assertEqual(f._convert_scalar('1'), 1)
            self.assertAlmostEqual(f._convert_scalar('1.2'), 1.2)
            self.assertEqual(f._convert_scalar('abc'), 'abc')
            self.assertEqual(f._convert_scalar('ab.c'), 'ab.c')

    def test_invalid_bibcode(self):
        """verify short input lines are skipped and logged as errors"""
        with patch('builtins.open', return_value=StringIO('AAAAAAAAAAAAAAAAAAA\nBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            with patch('adsdata.tasks.app.logger') as m:
                f = reader.NonbibFileReader('refereed', data_files['refereed'])
                self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
                self.assertEqual({'refereed': {'refereed': False}}, f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
                self.assertEqual({'refereed': {'refereed': False}}, f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
                self.assertEqual({'refereed': {'refereed': True, 'property': ['REFEREED']}}, f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
                self.assertTrue(m.error.called)

    def test_get_bibcode(self):
        with patch('builtins.open', return_value=StringIO('')):
            with patch('adsdata.tasks.app.logger') as m:
                f = reader.NonbibFileReader('citation', data_files['citation'])
                x = f._get_bibcode('short')
                self.assertEqual(x, 'short')
                self.assertTrue(m.error.called)
                m.reset_mock()
                x = f._get_bibcode('1234567890123456789\tvalue\n')
                self.assertEqual('1234567890123456789', x)
                self.assertFalse(m.error.called)
                
    def test_get_rest(self):
        with patch('builtins.open', return_value=StringIO('')):
            with patch('adsdata.tasks.app.logger') as m:
                f = reader.NonbibFileReader('citation', data_files['citation'])
                x = f._get_rest('short')
                self.assertEqual(x, '')
                self.assertTrue(m.error.called)
                m.reset_mock()
                x = f._get_rest('1234567890123456789\tvalue\n')
                self.assertEqual('value', x)
                self.assertFalse(m.error.called)

    def test_bibgroup(self):
        with patch('builtins.open', return_value=StringIO('2003ASPC..295..361M\tChandra/Technical\n2021MNRAS.502..510J\tGTC\n2021MNRAS.502..510J\tKeck')):
            f = reader.NonbibFileReader('bibgroup', data_files['bibgroup'])
            self.assertEqual({'bibgroup': ["Chandra/Technical"]}, f.read_value_for('2003ASPC..295..361M'))
            self.assertEqual({'bibgroup': []}, f.read_value_for('2004zzzz..295..361M'))
            self.assertEqual({"bibgroup": ["GTC", "Keck"]}, f.read_value_for('2021MNRAS.502..510J'))
            self.assertEqual({"bibgroup": []}, f.read_value_for('2021ZZZZZ.502..510J'))

    def test_planetary_names(self):
        f = reader.NonbibFileReader('gpn', data_files['gpn'])
        self.assertEqual({'gpn': ['Moon/Crater/Langrenus/3273']}, f.read_value_for('2000Icar..146..420D'))
        self.assertEqual({'gpn': ['Mars/Patera/Apollinaris Patera/323', 'Mars/Fossa/Medusae Fossae/3795', 'Mars/Fossa/Sirenum Fossae/5575', 'Mars/Terra/Terra Cimmeria/5930', 'Mars/Terra/Terra Sirenum/5932', 'Mars/Crater/Copernicus/1297','Mars/Crater/Gusev/2289','Mars/Crater/Kepler/2991','Mars/Crater/New Plymouth/4231','Mars/Crater/Newton/4236'] },f.read_value_for('2004JGRE..10912009I'))


