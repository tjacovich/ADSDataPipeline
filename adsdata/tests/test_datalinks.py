
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):

    def test_read(self):
        r = reader.StandardFileReader('pub_html', './adsdata/tests/data1/config/links/electr/all.links')
        links_value = r.read_value_for('1498esap.book.....R')
        self.assertEqual({'pub_html': {'link_type': 'ESOURCE',
                                       'link_sub_type': 'PUB_HTML',
                                       'url': 'https://doi.org/10.3931%2Fe-rara-477'}},
                         links_value)


