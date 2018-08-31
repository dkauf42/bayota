import unittest

from CastJeeves.jeeves import Jeeves
from CastJeeves.sourcehooks.sector import Sector


class TddForSector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        source = Jeeves.loadInSourceDataFromSQL()
        cls.sector = Sector(sourcedata=source)

    def test_sector_names_query(self):
        self.assertIn('Agriculture',
                      self.sector.all_names().tolist())
