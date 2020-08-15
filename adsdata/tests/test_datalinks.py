
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):

    def test_ads_pdf(self):
        self.maxDiff = None
        r = reader.NonbibFileReader('ads_pdf', './adsdata/tests/data1/config/links/ads_pdf/all.links')
        v = r.read_value_for('2003ASPC..295..361M')
        a = {'ads_pdf': {"url": ["http://articles.adsabs.harvard.edu/pdf/2003ASPC..295..361M"],
                         "link_type": "ESOURCE",
                         "link_sub_type": "ADS_PDF",
                         "property": ["ADS_OPENACCESS", "OPENACCESS"]}}
        self.assertEqual(a, v)

    def test_ads_scan(self):
        self.maxDiff = None
        r = reader.NonbibFileReader('ads_scan', './adsdata/tests/data1/config/links/ads_scan/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'ads_scan': {"url": ["http://articles.adsabs.harvard.edu/full/2004MNRAS.354L..31M"],
                          "link_type": "ESOURCE", "link_sub_type": "ADS_SCAN",
                          "property": ["ADS_OPENACCESS", "OPENACCESS"]}}
        self.assertEqual(a, v)

    def test_associated(self):
        self.maxDiff = None
        r = reader.NonbibFileReader('associated', './adsdata/tests/data1/config/links/associated/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'associated': {"url": ["2004MNRAS.354L..31M", "2005yCat..73549031M"],
                            "title": ["Source Paper", "Catalog Description"],
                            "link_type": "ASSOCIATED", "link_sub_type": "NA"}}
        self.assertEqual(a, v)

    def test_pub_html(self):
        self.maxDiff = None
        r = reader.NonbibFileReader('pub_html', './adsdata/tests/data1/config/links/electr/all.links')
        links_value = r.read_value_for('1498esap.book.....R')
        self.assertEqual({'pub_html': {'link_type': 'ESOURCE',
                                       'link_sub_type': 'PUB_HTML',
                                       'url': ['https://doi.org/10.3931%2Fe-rara-477']}},
                         links_value)

    def test_datasources(self):
        self.maxDiff = None
        r = reader.NonbibFileReader('data_link', './adsdata/tests/data1/config/links/facet_datasources/datasources.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'data_link': [{"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"],
                            "title": [""], "item_count": 1,
                            "link_type": "DATA",
                            "property": ["DATA"],
                            "link_sub_type": "CDS"},
                           {"url": ["https://$NED$/cgi-bin/objsearch?search_type=Search&refcode=2004MNRAS.354L..31M"], "property": ["DATA"],

                            "title": ["NED Objects (1953)"], "item_count": 1953, "link_type": "DATA", "link_sub_type": "NED"},
                           {"url": ["http://$SIMBAD$/simbo.pl?bibcode=2004MNRAS.354L..31M"], "property": ["DATA"],
                            "title": ["SIMBAD Objects (1)"], "item_count": 1, "link_type": "DATA", "link_sub_type": "SIMBAD"},
                           {"url": ["http://$VIZIER$/viz-bin/VizieR?-source=J/MNRAS/354/L31"], "property": ["DATA"],
                            "title": [""], "item_count": 1, "link_type": "DATA", "link_sub_type": "Vizier"}]}
        self.assertEqual(a, v)

    def test_inspire(self):
        self.maxDiff = None
        # what about property values?
        r = reader.NonbibFileReader('inspire', './adsdata/tests/data1/config/links/spires/all.links')
        v = r.read_value_for('2004MNRAS.354L..31M')
        a = {'inspire': {"url": ["http://inspirehep.net/search?p=find+j+MNRAA,354,L31"],
                         "link_type": "INSPIRE", "link_sub_type": "NA"}}
        self.assertEqual(a, v)


