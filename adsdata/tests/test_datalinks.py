
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):

    def test_ads_pdf(self):
        r = reader.StandardFileReader('ads_pdf', './adsdata/tests/data1/config/links/ads_pdf/all.links')
        v = r.read_value_for('2003ASPC..295..361M')
        a = {'ads_pdf': {"url": ["http://articles.adsabs.harvard.edu/pdf/2003ASPC..295..361M"],
                         "link_type": "ESOURCE",
                         "link_sub_type": "ADS_PDF",
                         "property": ["ADS_OPENACCESS", "ARTICLE", "OPENACCESS"]}}
        self.assertEqual(a, v)

    def test_ads_scan(self):
        r = reader.StandardFileReader('ads_scan', './adsdata/tests/data1/config/links/ads_scan/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'ads_scan': {"url": ["http://articles.adsabs.harvard.edu/full/2004MNRAS.354L..31M"],
                          "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN",
                          "property": ["ADS_OPENACCESS", "ARTICLE", "OPENACCESS"]}}
        self.assertEqual(a, v)

    def test_associated(self):
        r = reader.StandardFileReader('associated', './adsdata/tests/data1/config/links/associated/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'associated': {"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"],
                            "title": ["Source Paper", "Catalog Description"],
                            "link_type": "ASSOCIATED", "link_sub_type": "NA"}}
        self.assertEqual(a, v)

    def test_pub_html(self):
        r = reader.StandardFileReader('pub_html', './adsdata/tests/data1/config/links/electr/all.links')
        links_value = r.read_value_for('1498esap.book.....R')
        self.assertEqual({'pub_html': {'link_type': 'ESOURCE',
                                       'link_sub_type': 'PUB_HTML',
                                       'property': ['ADS_OPENACCESS', 'ARTICLE', 'OPENACCESS'],
                                       'url': ['https://doi.org/10.3931%2Fe-rara-477']}},
                         links_value)

    def test_datasources(self):
        r = reader.StandardFileReader('data_link', './adsdata/tests/data1/config/links/facet_datasources/datasources.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'data_link': {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"],
                           "title": [""], "item_count": 1,
                           "link_type": "DATA",
                           "property": ["DATA"],
                           "link_sub_type": "CDS"}}
        self.assertEqual(a, v)

    def test_inspire(self):
        # what about property values?
        r = reader.StandardFileReader('inspire', './adsdata/tests/data1/config/links/spires/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'inspire': {"url": ["http://inspirehep.net/search?p=find+j+MNRAA,354,L31"],
                         "link_type": "INSPIRE", "link_sub_type": "NA"}}
        self.assertEqual(a, v)


