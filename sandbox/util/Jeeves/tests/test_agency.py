import unittest

from sandbox.util.Jeeves.agency import Agency


class TddForAgency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.agency = Agency()

    def test_agency_names_query(self):
        self.assertIn('NONFED',
                      self.agency.all_names().tolist())

    def test_agencies_query_from_lrsegs(self):
        self.assertIn('NONFED',
                      self.agency.agencycodes_from_lrsegnames(lrsegnames=['N42001PU2_2790_3290']).agencycode.tolist())
