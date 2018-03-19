import unittest

from tables.TblLoader import TblLoader
from tables.ExcelDataTable import ExcelDataTable
from collections import OrderedDict


class TddForTables(unittest.TestCase):

    def setUp(self):
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()

    def test_tables_loaded_are_correct_type(self):
        self.assertIsInstance(self.tables.basecond, ExcelDataTable)

    def test_table_data_are_correct_type(self):
        self.assertIsInstance(self.tables.basecond.data, OrderedDict)
