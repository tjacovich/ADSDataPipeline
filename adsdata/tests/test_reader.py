
from mock import patch
from mock import mock_open
import StringIO
import mock
import unittest

from adsdata import reader


class TestReader(unittest.TestCase):
    """ it is important to have comprehensive tests for reader

    tests use StringIO because it supports tell and seek (unlike simplier mocks) """
    
    def test_refereed(self):
        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename')
            self.assertTrue(f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertTrue('T', f.read_value_for('DDDDDDDDDDDDDDDDDDD'))

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename')
            self.assertTrue(f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertTrue(f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            

        with patch('__builtin__.open', return_value=StringIO.StringIO('AAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBB\nDDDDDDDDDDDDDDDDDDD\nEEEEEEEEEEEEEEEEEEE')):
            f = reader.StandardFileReader('filename')
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

    def test_canonical(self):
        pass

    def test_standard(self):
        # test that we can read values for bibcodes
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['A'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test we can skip bibcodes that are in the file
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertEqual(['D'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))

        # test that we receive no value when we read a bibcode that isn't present
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))            
            self.assertTrue(f.read_value_for('EEEEEEEEEEEEEEEEEEE'))            
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))

        # test that repeated bibcodes are properly rolled up
        with patch('__builtin__.open', return_value=StringIO.StringIO("""AAAAAAAAAAAAAAAAAAA\tA
AAAAAAAAAAAAAAAAAAA\tAA
AAAAAAAAAAAAAAAAAAA\tAAA
BBBBBBBBBBBBBBBBBBB\tB
DDDDDDDDDDDDDDDDDDD\tD
DDDDDDDDDDDDDDDDDDD\tDD
EEEEEEEEEEEEEEEEEEE\tE""")):
            f = reader.StandardFileReader('filename')
            self.assertEqual(['A', 'AA', 'AAA'], f.read_value_for('AAAAAAAAAAAAAAAAAAA'))
            self.assertEqual(['B'], f.read_value_for('BBBBBBBBBBBBBBBBBBB'))
            self.assertFalse(f.read_value_for('CCCCCCCCCCCCCCCCCCC'))
            self.assertEqual(['D', 'DD'], f.read_value_for('DDDDDDDDDDDDDDDDDDD'))
            self.assertEqual(['E'], f.read_value_for('EEEEEEEEEEEEEEEEEEE'))
            self.assertFalse(f.read_value_for('FFFFFFFFFFFFFFFFFFF'))
