
from mock import patch
from mock import mock_open
import StringIO
import mock
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):

    def test_refereed(self):
        # using StringIO because it supports tell and seek (unlike simplier mocks)
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.OnlyTrueFileReader('filename')
            self.assertTrue(f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertTrue('T', f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.OnlyTrueFileReader('filename')
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertTrue(f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.OnlyTrueFileReader('filename')
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_canonical(self):
        pass

    def test_standard(self):
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\tA\nBBBBBBBBBBBBBBBBBBB\tB\nDDDDDDDDDDDDDDDDDDD\tD\nEEEEEEEEEEEEEEEEEEE\tE')):
            f = reader.StandardFileReader('foo', 'filename')
            self.assertEqual(['A'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\tA\nBBBBBBBBBBBBBBBBBBB\tB\nDDDDDDDDDDDDDDDDDDD\tD\nEEEEEEEEEEEEEEEEEEE\tE')):
            f = reader.StandardFileReader('foo', 'filename')
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\tA\nBBBBBBBBBBBBBBBBBBB\tB\nDDDDDDDDDDDDDDDDDDD\tD\nEEEEEEEEEEEEEEEEEEE\tE')):
            f = reader.StandardFileReader('foo', 'filename')
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))
