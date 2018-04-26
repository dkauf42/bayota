import unittest

from sandbox.util.jeeves import Jeeves
from sandbox.util.jeeves.sourcehooks.bmp import Bmp


class TddForBmp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        source = Jeeves.loadInSourceDataFromSQL()
        cls.bmp = Bmp(sourcedata=source)

    def test_names_query_contains_GRASSBUFFERS(self):
        self.assertIn('GrassBuffers',
                      self.bmp.all_names().tolist())
