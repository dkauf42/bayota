import unittest

from sandbox.tables.TblLoader import TblLoader
from sandbox.tables.ExcelDataTable import ExcelDataTable
from collections import OrderedDict


class TddForTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.tables = TblLoader()

    def test_tables_loaded_are_correct_type(self):
        self.assertIsInstance(self.tables.basecond, ExcelDataTable)

    def test_table_data_are_correct_type(self):
        self.assertIsInstance(self.tables.basecond.data, OrderedDict)
