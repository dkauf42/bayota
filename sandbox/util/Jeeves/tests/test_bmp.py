import unittest

from sandbox.util.Jeeves.bmp import Bmp


class TddForBmp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.bmp = Bmp()

    def test_names_query_contains_GRASSBUFFERS(self):
        self.assertIn('GrassBuffers',
                      self.bmp.all_names().tolist())
