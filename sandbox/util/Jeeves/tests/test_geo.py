import unittest

from sandbox.util.Jeeves.geo import Geo


class TddForGeo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.geo = Geo()

    def test_correct_countyid_queried_from_AnneArundel_countyname_and_stateabbreviation(self):
        self.assertIn(11,
                      self.geo.county.countyid_from_countystatestrs(getfrom=['Adams, PA',
                                                                             'Anne Arundel, MD']).countyid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_countystatestrs(self):
        self.assertIn(100,
                      self.geo.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD']).lrsegid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_lrsegnames(self):
        self.assertIn(741,
                      self.geo.lrsegids_from(lrsegnames=['N42001PU2_2790_3290']).lrsegid.tolist())

    def test_generic_lrsegid_query_returns_correct_from_countyids(self):
        self.assertIn(100,
                      self.geo.lrsegids_from(countyid=[11]).lrsegid.tolist())

    def test_generic_lrsegid_query_raises_error_for_more_than_one_keyword_argument(self):
        self.assertRaises(ValueError,
                          self.geo.lrsegids_from,
                          countystatestrs=['Adams, PA', 'Anne Arundel, MD'],
                          lrsegnames=['N42001PU2_2790_3290'])

    def test_lrsegs_query_from_geoscale_with_names(self):
        self.assertIn('N42001PU2_2790_3290',
                      self.geo.lrseg.names_from_ids(ids=
                                                    self.geo.lrsegids_from_geoscale_with_names(scale='County',
                                                                                               areanames=['Adams, PA']
                                                                                               )
                                                    ).landriversegment.tolist()
                      )

    def test_geo_scale_query_contains_COUNTY(self):
        self.assertIn('County',
                      self.geo.all_geotypes().geographytype.tolist())

    def test_geo_names_query_using_ID_for_COUNTYID_contains_ANNEARUNDEL(self):
        self.assertIn('Anne Arundel, MD',
                      self.geo.geonames_from_geotypeid(geotype=[2]).tolist())

    def test_geo_names_query_using_ID_raises_error_when_passed_a_name(self):
        self.assertRaises(ValueError,
                          self.geo.geonames_from_geotypeid, ['County'])

    def test_geo_names_query_using_name_for_COUNTYID_contains_ANNEARUNDEL(self):
        self.assertIn('Anne Arundel, MD',
                      self.geo.geonames_from_geotypename(geotype=['County']).tolist())

    def test_geo_names_query_raises_error_when_specified_scale_does_not_exist(self):
        self.assertRaises(ValueError,
                          self.geo.geonames_from_geotypeid, ['MinorState'])

    def test_geo_names_query_raises_error_when_no_scale_specified(self):
        self.assertRaises(ValueError,
                          self.geo.geonames_from_geotypeid)
