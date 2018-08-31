import unittest

from CastJeeves.jeeves import Jeeves
from CastJeeves.sourcehooks.bmp import Bmp


class TddForBmp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        source = Jeeves.loadInSourceDataFromSQL()
        cls.bmp = Bmp(sourcedata=source)

    def test_names_query_contains_GRASSBUFFERS(self):
        self.assertIn('GrassBuffers',
                      self.bmp.all_names().tolist())
