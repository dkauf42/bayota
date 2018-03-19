import unittest

from tables.TblQuery import TblQuery
from tables.QrySource import QrySource


class TddForQueries(unittest.TestCase):

    def setUp(self):
        # Load the Source Data and Base Condition tables
        self.tblqry = TblQuery()
        self.qrysrc = QrySource(self.tblqry.tables)

    def test_table_query_raises_error_when_no_scale_specified(self):
        self.assertRaises(ValueError, self.qrysrc.get_geoarea_names)

    def test_table_query_raises_error_when_specified_scale_does_not_exist(self):
        self.assertRaises(ValueError, self.qrysrc.get_geoarea_names, 'MinorState')

    def test_table_query_returns_geo_scale_list_containing_COUNTY(self):
        self.assertIn('County', self.qrysrc.get_geoscale_names())

    def test_table_query_returns_geo_area_list_for_COUNTY_containing_ANNEARUNDEL(self):
        self.assertIn('Anne Arundel, MD', self.qrysrc.get_geoarea_names(scale='County'))

    def test_table_query_returns_agency_list_of_correct_type(self):
        self.assertIsInstance(self.qrysrc.get_all_agency_names(), list)

    def test_table_query_returns_sector_list_of_correct_type(self):
        self.assertIsInstance(self.qrysrc.get_all_sector_names(), list)

    #def test_table_query_returns_correct_loadsources_type(self):
    #    self.assertIsInstance(self.tblqry.get_all_agency_names(), pd.Series)

    #def test_table_query_returns_correct_bmps(self):
    #    self.assertIn('CoverCrop', self.tblqry.instanceget_all_bmps())
