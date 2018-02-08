import unittest
from util.OptionLoader import OptionLoader
from util.TblLoader import TblLoader


class TddForOptions(unittest.TestCase):

    def setUp(self):
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()
        self.optionloader = OptionLoader(self.tables)  # with no arguments

    def test_optionloader_returns_nofile_error(self):
        self.assertRaises(FileNotFoundError, self.optionloader.load_from_csv, 'hey')

    def test_optionloader_returns_correct_result(self):
        self.assertRaises(FileNotFoundError, self.optionloader.load_from_csv, '../test/options_AAcounty.txt')
