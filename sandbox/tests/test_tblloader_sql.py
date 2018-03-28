import unittest

from sandbox.tables.TblLoader_fromSql import TblLoaderFromSQL
from sandbox.sqltables.TableLoader import TableLoader
from sandbox.tables.ExcelDataTable import ExcelDataTable
from collections import OrderedDict


class TddForTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.tables = TblLoaderFromSQL()

    def test_tables_loaded_are_correct_type(self):
        print('test1')
        self.assertIsInstance(self.tables.basecond, ExcelDataTable)

    def test_table_data_are_correct_type(self):
        print('test2')
        self.assertIsInstance(self.tables.basecond.data, OrderedDict)

    def test_sql_table_data_are_correct_type(self):
        print('test3')
        self.assertIsInstance(self.tables.sourceDataFromSql, TableLoader)
