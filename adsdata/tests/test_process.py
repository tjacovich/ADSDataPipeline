import mock
from mock import patch
from mock import mock_open
import StringIO
import unittest

from adsdata import process
from adsdata import reader

class TestMemoryCache(unittest.TestCase):

    def test_open(self):
        process.open('./adsdata/tests/data1/')
        for k in process.data_files:
            self.assertTrue('file_descriptor' in process.data_files[k])

        self.assertTrue(isinstance(process.data_files['canonical']['file_descriptor'], reader.BibcodeFileReader))
        self.assertTrue(isinstance(process.data_files['citation']['file_descriptor'], reader.StandardFileReader))
        self.assertTrue(isinstance(process.data_files['refereed']['file_descriptor'], reader.OnlyTrueFileReader))


    def test_read(self):
        process.open('./adsdata/tests/data1/')
        d = process.read_next()
        self.assertEqual(d['canonical'], '1057wjlf.book.....C')
        self.assertEqual(len(d['author']), 1)
        self.assertEqual(d['author'], ['Chao, C'])
        self.assertEqual(d['download'], ['1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1'])
        self.assertFalse(d['refereed'])
        self.assertFalse(d['citation'])

        
