import unittest

from sandbox.util.Jeeves.metadata import Metadata


class TddForMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.metadata = Metadata()

    def test_correct_metadata(self):
        pass
