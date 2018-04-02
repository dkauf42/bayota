import unittest

from sandbox.tables.TblJeeves import TblJeeves


class TddForTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.jeeves = TblJeeves()

    def test_correct_countyid_queried_from_AnneArundel_countyname_and_stateabbreviation(self):
        self.assertIn(11,
                      self.jeeves.countyid_from_countystatestrs(getfrom=['Adams, PA',
                                                                         'Anne Arundel, MD']).countyid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_countystatestrs(self):
        self.assertIn(100,
                      self.jeeves.lrsegids_from(countystatestrs=['Adams, PA',
                                                                 'Anne Arundel, MD']).lrsegid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_lrsegnames(self):
        self.assertIn(741,
                      self.jeeves.lrsegids_from(lrsegnames=['N42001PU2_2790_3290']).lrsegid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_countyids(self):
        self.assertIn(100,
                      self.jeeves.lrsegids_from(countyid=[11]).lrsegid.tolist())

    def test_generic_lrsegid_query_raises_error_for_more_than_one_keyword_argument(self):
        self.assertRaises(ValueError,
                          self.jeeves.lrsegids_from,
                          countystatestrs=['Adams, PA', 'Anne Arundel, MD'],
                          lrsegnames=['N42001PU2_2790_3290'])

    def test_query_for_lrsegs_from_geography(self):
        self.assertIn('N42001PU2_2790_3290',
                      self.jeeves.lrsegs_from_geography(scale='County',
                                                        areanames=['Adams, PA']).landriversegment.tolist())

    def test_query_for_agencies_from_lrsegs(self):
        self.assertIn('NONFED',
                      self.jeeves.agencies_from_lrsegs(lrsegnames=['N42001PU2_2790_3290']).agencycode.tolist())

    def test_query_all_sector_names(self):
        self.assertIn('Agriculture',
                      self.jeeves.get_all_sector_names().tolist())

    def test_query_all_agency_names(self):
        self.assertIn('NONFED',
                      self.jeeves.get_all_agency_names().tolist())

    def test_query_returns_geo_scale_list_containing_COUNTY(self):
        self.assertIn('County',
                      self.jeeves.get_all_geoscales().geographytype.tolist())

    def test_table_query_returns_geo_area_list_for_COUNTYNAME_containing_ANNEARUNDEL(self):
        self.assertIn('Anne Arundel, MD',
                      self.jeeves.get_geonames_of_geotype(geotype=['County']).tolist())

    def test_table_query_returns_geo_area_list_for_COUNTYID_containing_ANNEARUNDEL(self):
        self.assertIn('Anne Arundel, MD',
                      self.jeeves.get_geonames_of_geotype(geotype=[2]).tolist())

    def test_table_query_raises_error_when_specified_scale_does_not_exist(self):
        self.assertRaises(ValueError,
                          self.jeeves.get_geonames_of_geotype, ['MinorState'])

    def test_table_query_raises_error_when_no_scale_specified(self):
        self.assertRaises(ValueError,
                          self.jeeves.get_geonames_of_geotype)
