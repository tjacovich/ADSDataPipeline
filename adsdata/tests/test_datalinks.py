from mock import patch
from mock import mock_open
import StringIO
import mock
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):

    def test_read(self):
        r = reader.StandardFileReader('./adsdata/tests/data1/config/links/electr/all.links')
        links_value = r.read_value_for('1498esap.book.....R')
        self.assertEqual(['https://doi.org/10.3931%2Fe-rara-477'], links_value)


