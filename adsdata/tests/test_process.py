
import unittest
from mock import patch, mock_open

from adsmsg import NonBibRecord
from adsdata import reader
from adsdata.process import Processor
from adsdata.file_defs import data_files
from adsdata.memory_cache import Cache


class TestMemoryCache(unittest.TestCase):
    """test higher level operations for reading in a set of data for a bibcode"""
    
    def test_open(self):
        """can we open data files in the test directory"""
        with Processor(compute_metrics=False) as processor, patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            self.assertEqual(len(data_files), len(processor.readers))
            self.assertTrue(isinstance(processor.readers['citation'], reader.NonbibFileReader))
                            
        self.assertEqual(0, len(processor.readers))

    def test_read(self):
        """can we read in all the data for a bibcode"""
        with Processor(compute_metrics=False) as processor, patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            d = processor._read_next_bibcode('1057wjlf.book.....C')
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
        with Processor(compute_metrics=False) as processor, patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            d = processor._read_next_bibcode('1057wjlf.book.....C')
            c = processor._convert(d)
            nonbib = NonBibRecord(**c)
            print('nonbib = {}'.format(nonbib))

    def test_nonbib_record(self):
        self.maxDiff = None
        with Processor(compute_metrics=False) as processor, patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
            d = processor._read_next_bibcode('2003ASPC..295..361M')
            n = processor._convert(d)
            a = {"read_count": 4, "bibcode": "2003ASPC..295..361M",
                 "data_links_rows": [{"url": ["http://articles.adsabs.harvard.edu/pdf/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_PDF", 'item_count': 0, 'title': ['']},
                                     {"url": ["http://articles.adsabs.harvard.edu/full/2003ASPC..295..361M"], "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN", 'item_count': 0, 'title': ['']},
                                     {"url": [""], "link_type": "TOC", "link_sub_type": "NA", 'item_count': 0, 'title': ['']}],
                 "esource": ["ADS_PDF", "ADS_SCAN"], "property": ["ADS_OPENACCESS", "ARTICLE", "ESOURCE", "NOT REFEREED", "OPENACCESS", "TOC"], "boost": 0.15, 'citation_count': 0, 'norm_cites': 0, 'citation_count_norm': 0.0, 'data': [], 'total_link_counts': 0}
            self.assertEqual(a, n)

            d = processor._read_next_bibcode('2004MNRAS.354L..31M')
            v = processor._convert(d)
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

    def test_add_data_summary(self):
        self.maxDiff = None
        with Processor(compute_metrics=False) as processor, patch('adsputils.load_config', return_value={'INPUT_DATA_ROOT': './test/data1/config/'}):
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
            processor._add_data_summary(d)
            self.assertEqual(["CDS:1", "NED:1953", "SIMBAD:1", "Vizier:1"], d['data'])
    # "data_links_rows": [{"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"], "title": ["Source Paper", "Catalog Description"], "link_type": "ASSOCIATED", "link_sub_type": "NA"},
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

    def test_metrics_trivial_fields(self):
        d = {'canonical': "1998PPGeo..22..553A", 'refereed': {'refereed': False}, 'author': ["Arnfield, A. L."],
             'reads': [1, 2, 3, 4], 'download': [0, 1, 2, 3],
             'citations':  ['1998PPGeo..22..553B'], 'id': 11, 'reference': ["1997BoLMe..85..475M"]}
        m = mock_open(read_data='')
        m.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('builtins.open', m), Processor(compute_metrics=False) as processor:
            Cache.get('citation')['1998PPGeo..22..553A'] = ['1998PPGeo..22..553B']
            met = processor._compute_metrics(d)
            self.assertEqual(met['bibcode'], d['canonical'])
            self.assertEqual(met['citations'], d['citations'])
            self.assertEqual(met['reads'], d['reads'])
            self.assertEqual(met['downloads'], d['download'])
