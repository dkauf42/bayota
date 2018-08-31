import unittest

from CastJeeves.jeeves import Jeeves
from CastJeeves.sourcehooks.loadsource import LoadSource


class TddForLoadSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        source = Jeeves.loadInSourceDataFromSQL()
        cls.loadsource = LoadSource(sourcedata=source)

    def test_loadsources_query_from_lrseg_agency_sectors_contains_LEGUMEHAY(self):
        self.assertIn('Legume Hay',
                      self.loadsource.loadsources_from_lrseg_agency_sector(lrsegs=['N42001PU2_2790_3290'],
                                                                           agencies=['NONFED', 'FWS'],
                                                                           sectors=['Agriculture']).loadsource.tolist()
                      )
