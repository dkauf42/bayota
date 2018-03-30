import unittest

# from sandbox.tables.TblLoader_fromSql import TblLoaderFromSQL
# from sandbox.sqltables.TableLoader import TableLoader
# from sandbox.tables.ExcelDataTable import ExcelDataTable
from sandbox.tables.TblJeeves import TblJeeves
# from collections import OrderedDict


class TddForTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.jeeves = TblJeeves()

    def test_correct_countyid_queried_from_AnneArundel_countyname_and_stateabbreviation(self):
        self.assertIn(11,
                      self.jeeves.countyid_from_areanames(areanames=['Adams, PA',
                                                                     'Anne Arundel, MD']).countyid.tolist())

    def test_correct_lrsegid_queried_from_AnneArundel_countyid(self):
        self.assertIn(100,
                      self.jeeves.lrsegids_from_areanames(areanames=['Adams, PA',
                                                                     'Anne Arundel, MD']).lrsegid.tolist())

    # def test_query_for_lrsegs_from_geography(self):
    #     self.assertIn('N42001PU2_2790_3290',
    #                   self.jeeves.lrsegs_from_geography(scale='County', areanames='Adams, PA'))

    def test_query_for_agencies_from_lrsegs(self):
        self.assertIn('NONFED',
                      self.jeeves.agencies_from_lrsegs(lrsegs=['N42001PU2_2790_3290']))

    def test_query_all_sector_names(self):
        self.assertIn('Agriculture',
                      self.jeeves.get_all_sector_names().tolist())

    # def test_table_query_raises_error_when_no_scale_specified(self):
    #     self.assertRaises(ValueError, self.qrysrc.get_geoarea_names)
    #
    # def test_table_query_raises_error_when_specified_scale_does_not_exist(self):
    #     self.assertWarns(RuntimeWarning, self.qrysrc.get_geoarea_names, 'MinorState')
    #
    # def test_table_query_returns_geo_scale_list_containing_COUNTY(self):
    #     self.assertIn('County', self.qrysrc.get_geoscale_names())
    #
    # def test_table_query_returns_geo_area_list_for_COUNTY_containing_ANNEARUNDEL(self):
    #     self.assertIn('Anne Arundel, MD', self.qrysrc.get_geoarea_names(scale='County'))
    #
    # def test_table_query_returns_agency_list_of_correct_type(self):
    #     self.assertIsInstance(self.qrysrc.get_all_agency_names(), list)
    #
    # def test_table_query_returns_sector_list_of_correct_type(self):
    #     self.assertIsInstance(self.qrysrc.get_all_sector_names(), list)
    #
    # def test_tables_loaded_are_correct_type(self):
    #     self.assertIsInstance(self.tables.basecond, ExcelDataTable)
    #
    # def test_table_data_are_correct_type(self):
    #     self.assertIsInstance(self.tables.basecond.data, OrderedDict)
    #
    # def test_sql_table_data_are_correct_type(self):
    #     self.assertIsInstance(self.tables.sourceDataFromSql, TableLoader)