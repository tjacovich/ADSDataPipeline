
import unittest

from adsmsg import NonBibRecord
from adsdata import process
from adsdata import reader


class TestMemoryCache(unittest.TestCase):
    """test higher level operations for reading in a set of data for a bibcode"""
    
    def test_open(self):
        """can we open data files in the test directory"""
        process.close_all()
        process.open_all('./adsdata/tests/data1/config/')
        for k in process.data_files:
            self.assertTrue('file_descriptor' in process.data_files[k])

        # spot check a few
        self.assertTrue(isinstance(process.data_files['canonical']['file_descriptor'], reader.NonbibFileReader))
        self.assertTrue(isinstance(process.data_files['citation']['file_descriptor'], reader.NonbibFileReader))
        self.assertTrue(isinstance(process.data_files['refereed']['file_descriptor'], reader.NonbibFileReader))

    def test_read(self):
        """can we read in all the data for a bibcode"""
        process.close_all()
        process.open_all('./adsdata/tests/data1/config/')
        d = process.read_next_bibcode('1057wjlf.book.....C')
        self.assertEqual(d['canonical'], '1057wjlf.book.....C')
        self.assertEqual(len(d['author']), 1)
        self.assertEqual(d['author'], ['Chao, C'])
        self.assertFalse(d['citation'])
        self.assertEqual(d['download'], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.assertFalse(d['grants'])
        self.assertFalse(d['ned_objects'])
        self.assertTrue(d['nonarticle'])
        self.assertEqual(d['ocrabstract'], {'ocrabstract': False})
        self.assertEqual(d['private'], {'private': False})
        self.assertEqual(d['pub_openaccess'], {'pub_openaccess': False})
        self.assertEqual(d['readers'], ['4fc45951aa', '557ebfd055', '57fcb9018a'])
        self.assertEqual(d['reads'], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 6])
        self.assertEqual(d['refereed'], {'refereed': False})
        self.assertEqual(d['relevance'], {'norm_cites': 0, 'read_count': 25, 'boost': 0.32, 'citation_count': 0})

    def test_protobuf(self):
        """make sure protobuf are created without an exception"""
        process.open_all('./adsdata/tests/data1/config/')
        d = process.read_next()
        c = process.convert(d)
        nonbib = NonBibRecord(**c)
        print('nonbib = {}'.format(nonbib))

    def test_nonbib_record(self):
        process.close_all
        process.open_all(root_dir='./adsdata/tests/data1/config/')
        d = process.read_next_bibcode('2003ASPC..295..361M')
        n = process.convert(d)
        self.maxDiff = None
        a = {"read_count": 4, "bibcode": "2003ASPC..295..361M",
             "data_links_rows": [{"url": ["http://articles.adsabs.harvard.edu/pdf/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF", 'item_count': 0, 'title': ['']},
                                 {"url": ["http://articles.adsabs.harvard.edu/full/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN", 'item_count': 0, 'title': ['']},
                                 {"url": [""], "link_type": "TOC", "link_sub_type": "NA", 'item_count': 0, 'title': ['']}],
             "esource": ["ADS_PDF", "ADS_SCAN"], "property": ["ADS_OPENACCESS", "ARTICLE", "ESOURCE", "NOT REFEREED", "OPENACCESS", "TOC"], "boost": 0.15, 'citation_count': 0, 'norm_cites': 0, 'citation_count_norm': 0.0, 'data': [], 'total_link_counts': 0}
        self.assertEqual(a, n)

        d = process.read_next_bibcode('2004MNRAS.354L..31M')
        v = process.convert(d)
        a = {"bibcode": "2004MNRAS.354L..31M",
             "simbad_objects": ["3253618 G"],
             "read_count": 20,
             "data_links_rows": [{"url": ["http://dx.doi.org/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_HTML", 'item_count': 0, 'title': ['']},
                                 {"url": ["https://arxiv.org/abs/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_HTML", 'item_count': 0, 'title': ['']},
                                 {"url": ["https://academic.oup.com/mnras/pdf-lookup/doi/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_PDF", 'item_count': 0, 'title': ['']},
                                 {"url": ["http://articles.adsabs.harvard.edu/pdf/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF", 'item_count': 0, 'title': ['']},
                                 {"url": ["https://arxiv.org/pdf/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_PDF", 'item_count': 0, 'title': ['']},
                                 {"url": ["http://articles.adsabs.harvard.edu/full/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN", 'item_count': 0, 'title': ['']},
                                 {"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"], "title": ["Source Paper", "Catalog Description"], "link_type": "ASSOCIATED", "link_sub_type": "NA", 'item_count': 0},
                                 {"url": ["http://inspirehep.net/search?p=find+j+MNRAA,354,L31"], "link_type": "INSPIRE", "link_sub_type": "NA", 'item_count': 0, 'title': ['']},
                                 {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "CDS", 'title': ['']},
                                 {"url": ["https://$NED$/cgi-bin/objsearch?search_type=Search&refcode=2004MNRAS.354L..31M"], "title": ["NED Objects (1953)"], "item_count": 1953, "link_type": "DATA", "link_sub_type": "NED"},
                                 {"url": ["http://$SIMBAD$/simbo.pl?bibcode=2004MNRAS.354L..31M"], "title": ["SIMBAD Objects (1)"], "item_count": 1, "link_type": "DATA", "link_sub_type": "SIMBAD"},
                                 {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier", 'title': ['']}],
             "norm_cites": 10000,
             "data": ["CDS:1", "NED:1953", "SIMBAD:1", "Vizier:1"],
             "citation_count_norm": 49.5,
             "citation_count": 99,
             "property": ["ADS_OPENACCESS", "ARTICLE", "ASSOCIATED", "DATA", "EPRINT_OPENACCESS", "ESOURCE", "INSPIRE", "OPENACCESS", "PUB_OPENACCESS", "REFEREED"],
             "total_link_counts": 1956,
             "esource": ["ADS_PDF", "ADS_SCAN", "EPRINT_HTML", "EPRINT_PDF", "PUB_HTML", "PUB_PDF"],
             "boost": 0.4399999976158142}
        v_boost = v.pop('boost')
        a_boost = a.pop('boost')
        self.assertAlmostEqual(a_boost, v_boost)
        self.assertEqual(a, v)

        # consider video 1997kbls.confE..10C
        # consider library 1810hdla.book.....V
        # consider inspire 1908PASP...20....1.

        # why no data link on master for toc 1886Natur..34Q.131.

    def test_add_data_summary(self):
        data_links_rows = [{"url": ["http://dx.doi.org/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_HTML"},
                           {"url": ["https://arxiv.org/abs/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_HTML"},
                           {"url": ["https://academic.oup.com/mnras/pdf-lookup/doi/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_PDF"},                                                                 {"url": ["http://articles.adsabs.harvard.edu/pdf/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF"},
                           {"url": ["https://arxiv.org/pdf/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_PDF"},
                           {"url": ["http://articles.adsabs.harvard.edu/full/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN"},
                           {"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"], "title": ["Source Paper", "Catalog Description"], "link_type": "ASSOCIATED", "link_sub_type": "NA"},
                           {"url": ["http://inspirehep.net/search?p=find+j+MNRAA,354,L31"], "link_type": "INSPIRE", "link_sub_type": "NA"},
                           {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "CDS"},
                           {"url": ["https://$NED$/cgi-bin/objsearch?search_type=Search&refcode=2004MNRAS.354L..31M"], "title": ["NED Objects (1953)"], "item_count": 1953, "link_type": "DATA", "link_sub_type": "NED"},
                           {"url": ["http://$SIMBAD$/simbo.pl?bibcode=2004MNRAS.354L..31M"], "title": ["SIMBAD Objects (1)"], "item_count": 1, "link_type": "DATA", "link_sub_type": "SIMBAD"},
                           {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier"}]
        d = {'data_links_rows': data_links_rows}
        process.add_data_summary(d)
        self.assertEqual(["CDS:1", "NED:1953", "SIMBAD:1", "Vizier:1"], d['data'])
#"data_links_rows": [{"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"], "title": ["Source Paper", "Catalog Description"], "link_type": "ASSOCIATED", "link_sub_type": "NA"},
#                    {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "CDS"},
#                    {"url": ["https://$NED$/cgi-bin/objsearch?search_type=Search&refcode=2004MNRAS.354L..31M"], "title": ["NED Objects (1953)"], "item_count": 1953, "link_type": "DATA", "link_sub_type": "NED"},
#                    {"url": ["http://$SIMBAD$/simbo.pl?bibcode=2004MNRAS.354L..31M"], "title": ["SIMBAD Objects (1)"], "item_count": 1, "link_type": "DATA", "link_sub_type": "SIMBAD"},
#                    {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier"},
#                    {"url": ["http://articles.adsabs.harvard.edu/pdf/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF"},
#                    {"url": ["http://articles.adsabs.harvard.edu/full/2004MNRAS.354L..31M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN"},
#                    {"url": ["https://arxiv.org/abs/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_HTML"},
#                    {"url": ["https://arxiv.org/pdf/astro-ph/0405472"], "link_type": "ESOURCE", "link_sub_type": "EPRINT_PDF"},
#                    {"url": ["http://dx.doi.org/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_HTML"},
#                    {"url": ["https://academic.oup.com/mnras/pdf-lookup/doi/10.1111/j.1365-2966.2004.08374.x"], "link_type": "ESOURCE", "link_sub_type": "PUB_PDF"},
#                    {"url": ["http://inspirehep.net/search?p=find+j+MNRAA,354,L31"], "link_type": "INSPIRE", "link_sub_type": "NA"}], 

# "esource": ["ADS_PDF", "ADS_SCAN", "EPRINT_HTML", "EPRINT_PDF", "PUB_HTML", "PUB_PDF"],

# "property": ["ASSOCIATED", "DATA", "ESOURCE", "INSPIRE", "ARTICLE", "REFEREED", "PUB_OPENACCESS", "ADS_OPENACCESS", "EPRINT_OPENACCESS", "OPENACCESS"]
