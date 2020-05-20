
import unittest

from adsmsg import NonBibRecord
from adsdata import process
from adsdata import reader


class TestMemoryCache(unittest.TestCase):
    """test higher level operations for reading in a set of data for a bibcode"""
    
    def test_open(self):
        """can we open data files in the test directory"""
        process.open_all('./adsdata/tests/data1/config/')
        for k in process.data_files:
            self.assertTrue('file_descriptor' in process.data_files[k])

        # spot check a few
        self.assertTrue(isinstance(process.data_files['canonical']['file_descriptor'], reader.StandardFileReader))
        self.assertTrue(isinstance(process.data_files['citation']['file_descriptor'], reader.StandardFileReader))
        self.assertTrue(isinstance(process.data_files['refereed']['file_descriptor'], reader.StandardFileReader))

    def test_read(self):
        """can we read in all the data for a bibcode"""
        process.open_all('./adsdata/tests/data1/config/')
        d = process.read_next()
        self.assertEqual(d['canonical'], '1057wjlf.book.....C')
        self.assertEqual(len(d['author']), 1)
        self.assertEqual(d['author'], ['Chao, C'])
        self.assertFalse(d['citation'])
        self.assertEqual(d['download'], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.assertFalse(d['grants'])
        self.assertFalse(d['ned_objects'])
        self.assertTrue(d['nonarticle'])
        self.assertFalse(d['ocrabstract'])
        self.assertFalse(d['private'])
        self.assertFalse(d['pub_openaccess'])
        self.assertEqual(d['readers'], ['4fc45951aa', '557ebfd055', '57fcb9018a'])
        self.assertEqual(d['reads'], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 6])
        self.assertFalse(d['refereed'])
        self.assertEqual(d['relevance'], {'norm_cites': 0, 'read_count': 25, 'boost': 0.32, 'citation_count': 0})

    def test_protobuf(self):
        process.open_all('./adsdata/tests/data1/config/')
        d = process.read_next()
        c = process.convert(d)
        nonbib = NonBibRecord(**c)
        print('nonbib = {}'.format(nonbib))

    def zztest_convert(self):
        self.assertEqual('2003ASPC..295..361M', process.convert({'canonical': '2003ASPC..295..361M'})['bibcode'])

    def test_nonbib_record(self):
        process.open_all(root_dir='./adsdata/tests/data1/config/')
        d = process.read_next_bibcode('2003ASPC..295..361M')
        n = process.convert(d)
        self.maxDiff = None
        self.assertEqual(n,  {"read_count": 4, "bibcode": "2003ASPC..295..361M", "data_links_rows": [{"url": ["http://articles.adsabs.harvard.edu/pdf/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF"}, {"url": ["http://articles.adsabs.harvard.edu/full/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN"}, {"url": [""], "link_type": "TOC", "link_sub_type": "NA"}], "esource": ["ADS_PDF", "ADS_SCAN"], "property": ["ADS_OPENACCESS", "ARTICLE", "ESOURCE", "NOT REFEREED", "OPENACCESS", "TOC"], "boost": 0.15, "readers": [], "reference": [], "simbad_objects": [], "grants": [], "ned_objects": [], 'citation_count': 0, 'norm_cites': 0})

