import unittest

from sandbox.util.Jeeves.sector import Sector


class TddForSector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.sector = Sector()

    def test_sector_names_query(self):
        self.assertIn('Agriculture',
                      self.sector.all_names().tolist())
